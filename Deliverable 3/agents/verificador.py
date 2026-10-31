"""Verificador: cobertura independiente, solicitud de auditoría y revisión semántica.

Cada invocación hace una llamada al LLM. Si pide ``audit``, el orquestador
ejecuta la herramienta y vuelve a llamar con el mapa y el informe. Este módulo
no ejecuta herramientas, reintentos ni revisiones del Formulador.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, model_validator

from agents.analista import (
    LLM,
    PROMPTS_DIR,
    AgentFormatError,
    AgentStep,
    LLMCall,
    extraer_json,
    load_prompt,
    render,
)
from schemas import (AuditReport, ContractModel, CoverageMap, DraftModel, DraftSections, ModelElement,
                     ProblemSpec, ReviewDecision)

DEFAULT_PROMPT = PROMPTS_DIR / "verificador_v2.md"


class VerifierOutput(ContractModel):
    """Control local del rol C; reutiliza los contratos compartidos sin cambiarlos.

    ``audit`` solicita audit_model sobre ``coverage`` y no es una aceptación.
    ``review`` entrega la decisión del agente, incluso en la variante no_review;
    impedir una devolución al Formulador le corresponde al orquestador.
    """

    action: Literal["audit", "review"]
    coverage: CoverageMap
    decision: Optional[ReviewDecision] = None
    reason: Optional[str] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def valid_action(self) -> VerifierOutput:
        if self.action == "audit":
            if self.decision is not None:
                raise ValueError("audit no admite decision")
            if not self.reason or not self.reason.strip():
                raise ValueError("audit requiere reason")
        else:
            if self.decision is None:
                raise ValueError("review requiere decision")
            if self.decision.candidate_id != self.coverage.candidate_id:
                raise ValueError("decision y coverage deben tener el mismo candidate_id")
            # revise y stop admiten mapas incompletos; accept no.
            if self.decision.action == "accept":
                if self.decision.issues:
                    raise ValueError("accept no admite issues; usa revise para pedir correcciones")
                if not self.coverage.elements or not self.coverage.links:
                    raise ValueError("accept requiere un CoverageMap con elements y links")
        return self


def _requisitos_sin_cubrir(spec: ProblemSpec, coverage: CoverageMap) -> list[str]:
    elements = {element.id for element in coverage.elements}
    linked = {link.requirement_id for link in coverage.links if link.element_id in elements}
    return [r.id for r in spec.requirements if r.id not in linked]


# ------------------------------------------------------- protocolo de texto
#
# Desde verificador_v3 el modelo no escribe JSON anidado: en el piloto T4,
# Qwen2.5-1.5B rompió el CoverageMap en todos los casos. El programa enumera
# las partes del candidate y el modelo responde líneas breves que aquí se
# convierten en CoverageMap y ReviewDecision.

_DOMAIN_HINT = re.compile(r"\\ge(?:q)?\s*0|>=\s*0|≥\s*0|\\in|\bbinari|\benter|\bcontinu|\{0,\s*1\}", re.IGNORECASE)
_LINK_LINE = re.compile(r"^[ \t*-]*(U[1-9][0-9]*)[ \t]*(?::|->|→|=>)[ \t]*(.+?)[ \t]*$", re.MULTILINE)
_VERBOSE_REQUIREMENT = re.compile(r"^(?:IDENTIFICADOR[^:]*REQUISITO|REQUISITO)\s*:\s*(U[1-9][0-9]*)\s*$", re.IGNORECASE)
_VERBOSE_PART = re.compile(r"^PARTES?\s*:\s*(.+)$", re.IGNORECASE)
_ACTION_LINE = re.compile(r"^[ \t*]*ACCI[OÓ]N[ \t*]*:[ \t*]*(\w+)", re.IGNORECASE | re.MULTILINE)
_ISSUE_LINE = re.compile(r"^[ \t*-]*PROBLEMA[ \t*]*:[ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
_REASON_LINE = re.compile(r"^[ \t*]*MOTIVO[ \t*]*:[ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
_TEXT_ACTIONS = {"auditar": "audit", "audit": "audit", "aceptar": "accept", "accept": "accept",
                 "revisar": "revise", "revise": "revise", "detener": "stop", "stop": "stop"}


def _lines(text: Optional[str]) -> list[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _math_excerpts(text: Optional[str]) -> list[str]:
    """Extrae ecuaciones, sin convertir delimitadores LaTeX en restricciones."""
    source = text or ""
    blocks = [match.group(1).strip() for match in
              re.finditer(r"\\\[(.*?)\\\]", source, re.DOTALL)
              if match.group(1).strip()]
    if blocks:
        return blocks
    return [line for line in _lines(source)
            if line not in (r"\[", r"\]", "$$")]


def elementos_candidate(draft: DraftModel) -> list[ModelElement]:
    """Objetivo, restricciones y líneas de dominio del candidate, con extractos literales."""
    sections = draft.sections or DraftSections()
    elements = []
    objective = _math_excerpts(sections.objective)
    if objective:
        elements.append(ModelElement(id="O1", kind="objective", excerpt=objective[0]))
    for index, line in enumerate(_math_excerpts(sections.constraints), 1):
        elements.append(ModelElement(id=f"C{index}", kind="constraint", excerpt=line))
    domains = [line for line in _lines(sections.variables) if _DOMAIN_HINT.search(line)]
    for index, line in enumerate(domains, 1):
        elements.append(ModelElement(id=f"D{index}", kind="domain", excerpt=line))
    return elements


def _format_elements(elements: list[ModelElement]) -> str:
    return "\n".join(f"{e.id}: {e.excerpt}" for e in elements) or "(el candidate no tiene partes reconocibles)"


def _format_requirements(spec: ProblemSpec) -> str:
    return "\n".join(f"{r.id} ({r.kind}): {r.text}" for r in spec.requirements)


def _coverage_suggestions(spec: ProblemSpec, elements: list[ModelElement]) -> str:
    """Propone coincidencias superficiales sin consultar respuestas de referencia.

    Son pistas para el Verificador, no vínculos aceptados ni prueba de
    equivalencia: una ecuación puede contener el mismo número y ser incorrecta.
    """
    def numbers(text: str) -> set[str]:
        values = re.findall(r"(?<![A-Za-z])\d[\d.,]*", text)
        return {re.sub(r"[.,](?=\d{3}(?:\D|$))", "", value).rstrip(".,")
                for value in values if value.rstrip(".,")}

    lines = []
    for requirement in spec.requirements:
        if requirement.kind == "objective":
            matches = [e.id for e in elements if e.kind == "objective"]
        elif requirement.kind == "domain":
            matches = [e.id for e in elements if e.kind == "domain"]
        else:
            expected = numbers(requirement.text)
            matches = [e.id for e in elements if e.kind == "constraint"
                       and expected and expected & numbers(e.excerpt)]
        lines.append(f"{requirement.id}: {', '.join(matches) if matches else 'ninguna'}")
    return "\n".join(lines)


def _format_links(coverage: CoverageMap) -> str:
    targets = {}
    for link in coverage.links:
        targets.setdefault(link.requirement_id, []).append(link.element_id)
    return "\n".join(f"{rid}: {', '.join(ids)}" for rid, ids in targets.items()) or "(sin vínculos)"


def _format_report(report: AuditReport) -> str:
    errors = [finding for finding in report.findings if finding.level == "error"]
    other = [finding for finding in report.findings if finding.level != "error"]
    lines = []
    for finding in [*errors, *other[:3]]:
        level = finding.level or finding.status
        where = " · ".join(x for x in (finding.requirement_id, finding.location) if x)
        lines.append(f"- [{level}] {finding.check}: {finding.message}" + (f" ({where})" if where else ""))
    if len(other) > 3:
        lines.append(f"- {len(other) - 3} avisos o comprobaciones no verificadas adicionales; el informe completo queda en la traza")
    return "\n".join(lines) or "- sin hallazgos"


def _parse_text(raw: str, spec: ProblemSpec, draft: DraftModel, elements: list[ModelElement],
                warnings: list[str], coverage: Optional[CoverageMap]) -> dict:
    actions = list(_ACTION_LINE.finditer(raw))
    match = actions[0] if actions else None
    action = _TEXT_ACTIONS.get(match.group(1).lower()) if match else None
    if action is None:
        raise ValueError("falta ACCION: auditar, aceptar, revisar o detener")
    if len(actions) > 1:
        warnings.append("acciones posteriores ignoradas; se conservó la primera decisión")
    # La respuesta puede contener explicaciones o una segunda tentativa. Solo
    # las líneas anteriores a la primera decisión declaran la cobertura.
    coverage_text = raw[:match.start()]
    decision_text = raw[:actions[1].start()] if len(actions) > 1 else raw
    # v5 permitía bloques requisito/parte después de ACCION. Se conserva
    # ese formato solo cuando no existe una lista de cobertura previa.
    link_text = coverage_text if _LINK_LINE.search(coverage_text) else decision_text
    if coverage is None:
        known = {e.id for e in elements}
        links, unknown = [], []
        for rid, targets in _LINK_LINE.findall(link_text):
            for target in re.findall(r"[A-Za-z]+[0-9]+", targets):
                target = target.upper()
                if target in known:
                    links.append({"requirement_id": rid, "element_id": target})
                else:
                    unknown.append(target)
        current_requirement = None
        verbose_links = 0
        for line in link_text.splitlines():
            line = line.strip()
            requirement = _VERBOSE_REQUIREMENT.fullmatch(line)
            if requirement:
                current_requirement = requirement.group(1).upper()
                continue
            part = _VERBOSE_PART.fullmatch(line)
            if part and current_requirement:
                for target in re.findall(r"[A-Za-z]+[0-9]+", part.group(1)):
                    target = target.upper()
                    if target in known:
                        links.append({"requirement_id": current_requirement, "element_id": target})
                        verbose_links += 1
                    else:
                        unknown.append(target)
                current_requirement = None
        if verbose_links:
            warnings.append("vínculos en bloques requisito/parte normalizados")
        if unknown:
            warnings.append("vínculos a partes inexistentes descartados: " + ", ".join(dict.fromkeys(unknown)))
        links = [dict(t) for t in dict.fromkeys(tuple(l.items()) for l in links)]
        coverage = CoverageMap(candidate_id=draft.candidate_id, elements=elements, links=links)
    if action in ("audit", "accept") and elements and spec.requirements and not coverage.links:
        ids = ", ".join(requirement.id for requirement in spec.requirements)
        parts = ", ".join(element.id for element in elements)
        raise ValueError(f"cobertura vacía: usa identificadores concretos ({ids}) y partes existentes ({parts})")
    reason = _REASON_LINE.search(decision_text)
    reason = reason.group(1).strip() if reason else None
    if action == "audit":
        return {"action": "audit", "coverage": coverage, "reason": reason or "comprobar el mapa con audit_model"}
    issues = []
    for line in _ISSUE_LINE.findall(decision_text):
        parts = [p.strip() for p in line.split("|")]
        rid = parts[0] if parts and re.fullmatch(r"U[1-9][0-9]*", parts[0] or "") else None
        rest = parts[1:] if rid or (parts and parts[0] in ("", "-")) else parts
        location = rest[0] if len(rest) > 2 and rest[0] not in ("", "-") else None
        body = rest[1:] if len(rest) > 2 else rest
        description = body[0] if body and body[0] else line.strip()
        suggestion = body[1] if len(body) > 1 and body[1] else None
        issues.append({"description": description, "requirement_id": rid,
                       "location": location, "suggestion": suggestion})
    missing = _requisitos_sin_cubrir(spec, coverage)
    if action == "accept" and (issues or missing):
        # El propio mapa del agente contradice la aceptación: se devuelve con esas omisiones.
        warnings.append("aceptar con problemas o requisitos sin vincular; se interpretó revisar")
        action = "revise"
    if action == "revise":
        known_issue = {i["requirement_id"] for i in issues}
        for rid in missing:
            if rid not in known_issue:
                text = next(r.text for r in spec.requirements if r.id == rid)
                issues.append({"description": f"{rid} no tiene una ecuación que lo represente: {text}",
                               "requirement_id": rid, "location": None,
                               "suggestion": f"Agregar la ecuación que exprese {rid}"})
        if not issues:
            raise ValueError("ACCION: revisar requiere al menos una línea PROBLEMA:")
    decision = {"action": action, "candidate_id": draft.candidate_id, "issues": issues, "reason": reason}
    return {"action": "review", "coverage": coverage, "decision": decision}


def verificar(
    llm: LLM,
    problem: str,
    spec: ProblemSpec,
    draft: DraftModel,
    *,
    adapter_on: bool,
    prompt_path: Path = DEFAULT_PROMPT,
    audit_allowed: bool = True,
    coverage: Optional[CoverageMap] = None,
    audit_report: Optional[AuditReport] = None,
    format_feedback: Optional[str] = None,
) -> AgentStep:
    """Devuelve AgentStep con VerifierOutput y la llamada para la traza.

    Sin informe, el agente construye el mapa y elige auditar o decidir. Con
    informe, ``coverage`` debe ser el mapa que recibió la herramienta: se
    conserva para evitar que la decisión use otro mapa tras la auditoría.
    ``audit_allowed=False`` sirve para no_audit o un presupuesto agotado.
    ``format_feedback`` transmite el fallo previo sin reintentar aquí.

    Un error en la respuesta produce AgentFormatError con la llamada cruda.
    Una combinación incoherente de argumentos produce ValueError antes de
    llamar al LLM. No se modifica el borrador ni se recibe el plan del Formulador.
    """
    if (coverage is None) != (audit_report is None):
        raise ValueError("coverage y audit_report deben recibirse juntos")
    if audit_report is not None:
        if not audit_allowed:
            raise ValueError("no se admite audit_report con audit_allowed=False")
        if coverage.candidate_id != draft.candidate_id or audit_report.candidate_id != draft.candidate_id:
            raise ValueError("el mapa, informe y borrador deben tener el mismo candidate_id")

    version, sections = load_prompt(prompt_path)
    text_protocol = "$elements" in sections["user"].template
    elements = elementos_candidate(draft) if text_protocol else []
    audit_block = (
        render(sections["audit_result"],
               coverage=(_format_links(coverage) if text_protocol
                         else coverage.model_dump_json(exclude_none=True)),
               audit_report=(_format_report(audit_report) if text_protocol
                             else audit_report.model_dump_json(exclude_none=True)))
        if audit_report is not None else ""
    )
    feedback_block = (
        render(sections["format_feedback"], feedback=format_feedback)
        if format_feedback else ""
    )
    prompt = render(
        sections["after_audit"] if audit_report is not None and "after_audit" in sections else sections["user"],
        problem=problem,
        spec=spec.model_dump_json(exclude_none=True),
        candidate_id=draft.candidate_id,
        candidate=draft.raw_text,
        parse_errors="\n".join(draft.parse_errors),
        control_block=render(sections[
            "audit_available" if audit_allowed and audit_report is None else "review_only"
        ]),
        audit_block=audit_block,
        feedback_block=feedback_block,
        elements=_format_elements(elements),
        requirements=_format_requirements(spec),
        coverage_skeleton="\n".join(f"{r.id}: O/C/D o ninguna" for r in spec.requirements),
        coverage_suggestions=_coverage_suggestions(spec, elements),
    )
    raw = llm.generate(prompt, adapter_on)
    step = AgentStep(output=None, calls=[LLMCall(version, prompt, adapter_on, raw)])

    def fail(message: str) -> AgentFormatError:
        return AgentFormatError(message, raw=raw, prompt_version=version,
                                calls=step.calls, warnings=step.warnings)

    try:
        if text_protocol:
            data = _parse_text(raw, spec, draft, elements, step.warnings, coverage)
            if data["action"] == "audit" and (not audit_allowed or audit_report is not None):
                raise ValueError("ACCION: auditar no está disponible en este paso; decide aceptar, revisar o detener")
            if data["action"] == "review" and audit_report is not None and audit_report.has_errors:
                decision = data["decision"]
                if decision["action"] == "accept":
                    decision["action"] = "revise"
                    step.warnings.append("aceptación contradice errores de audit_model; se interpretó revisar")
                if decision["action"] == "revise":
                    covered_issues = {issue["requirement_id"] for issue in decision["issues"]
                                      if issue["requirement_id"] is not None}
                    for finding in audit_report.findings:
                        if finding.level != "error" or finding.requirement_id in covered_issues:
                            continue
                        suggestion = ("Vincular el requisito a una parte del tipo correcto o agregarla"
                                      if finding.check == "cobertura_tipo_incorrecto" else
                                      "Agregar la ecuación que represente el requisito o corregir su vínculo"
                                      if finding.check == "requisito_sin_cubrir" else
                                      "Corregir el símbolo, índice o ecuación indicado por la auditoría")
                        decision["issues"].append({"description": f"{finding.check}: {finding.message}",
                                                   "requirement_id": finding.requirement_id,
                                                   "location": finding.location,
                                                   "suggestion": suggestion})
                        if finding.requirement_id is not None:
                            covered_issues.add(finding.requirement_id)
            output = VerifierOutput.model_validate(data)
            step.output = output
            return step
        data = extraer_json(raw)
        if audit_report is not None:
            if "coverage" in data:
                returned_map = CoverageMap.model_validate(data["coverage"])
                if returned_map != coverage:
                    raise ValueError("no se puede cambiar el CoverageMap después de auditar")
            data["coverage"] = coverage.model_dump()
        output = VerifierOutput.model_validate(data)
        if output.coverage.candidate_id != draft.candidate_id:
            raise ValueError("coverage.candidate_id no corresponde al borrador")
        if output.action == "audit" and (not audit_allowed or audit_report is not None):
            raise ValueError("audit no está disponible en este paso; entrega review")
        if output.action == "review" and output.decision.action == "accept":
            missing = _requisitos_sin_cubrir(spec, output.coverage)
            if missing:
                raise ValueError("accept con requisitos sin vincular en el CoverageMap: "
                                 + ", ".join(missing))
    except (ValueError, TypeError, AttributeError) as error:
        raise fail(f"VerifierOutput inválido: {error}") from None

    step.output = output
    return step
