"""Formulador: decide formular o aclarar, planifica y escribe el candidate.

Hace dos llamadas al modelo. La primera devuelve la decisión y el plan interno
``Uk -> ecuación``; la segunda, el candidate con los cinco encabezados de la
Entrega 2. El plan se registra aparte y nunca se antepone al candidate.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Sequence, Union

from pydantic import ValidationError

from agents.analista import (
    LLM,
    PROMPTS_DIR,
    AgentFormatError,
    AgentStep,
    LLMCall,
    load_prompt,
    render,
)
from schemas import DraftModel, DraftSections, FormulatorOutput, Issue, PlanItem, ProblemSpec

DEFAULT_PROMPT = PROMPTS_DIR / "formulador_v1.md"

# Encabezados de la Entrega 2, en orden; se toleran acentos omitidos y marcas
# de Markdown alrededor del encabezado.
SECTIONS = (
    ("sets", "Conjuntos", r"Conjuntos"),
    ("parameters", "Parámetros", r"Par[aá]metros"),
    ("variables", "Variables de decisión", r"Variables\s+de\s+decisi[oó]n"),
    ("objective", "Función objetivo", r"Funci[oó]n\s+objetivo"),
    ("constraints", "Restricciones", r"Restricciones"),
)
_HEADING = {
    key: re.compile(rf"^[ \t#*]*{pattern}[ \t]*:[ \t*]*", re.IGNORECASE | re.MULTILINE)
    for key, _, pattern in SECTIONS
}
_DECISION = re.compile(r"^[ \t*]*DECISI[OÓ]N[ \t*]*:[ \t*]*(\w+)", re.IGNORECASE | re.MULTILINE)
_QUESTION = re.compile(r"^[ \t*]*PREGUNTA[ \t*]*:[ \t*]*(.+)", re.IGNORECASE | re.MULTILINE | re.DOTALL)
_PLAN_LINE = re.compile(r"^[ \t]*[-*]?[ \t]*(U[1-9][0-9]*)[ \t]*(?:->|→|=>)[ \t]*(.+?)[ \t]*$", re.MULTILINE)
_DECISIONS = {"formular": "formulate", "formulate": "formulate", "aclarar": "clarify", "clarify": "clarify"}
_KINDS = {"objective": "objetivo", "constraint": "restricción", "domain": "dominio"}


# ------------------------------------------------------------- candidate

def separar_secciones(text: str) -> tuple[DraftSections, list[str]]:
    """Divide el candidate por encabezados; devuelve las secciones y los errores."""
    errors = []
    found = []
    for key, label, _ in SECTIONS:
        matches = list(_HEADING[key].finditer(text))
        if not matches:
            errors.append(f"falta el encabezado {label}:")
            continue
        if len(matches) > 1:
            errors.append(f"encabezado repetido: {label}:")
        found.append((matches[0].start(), matches[0].end(), key, label))
    if [key for *_, key, _ in found] != [key for *_, key, _ in sorted(found)]:
        errors.append("los encabezados no siguen el orden de la Entrega 2")
    found.sort()
    contents = {}
    for index, (_, end, key, label) in enumerate(found):
        stop = found[index + 1][0] if index + 1 < len(found) else len(text)
        contents[key] = text[end:stop].strip() or None
        if contents[key] is None:
            errors.append(f"sección vacía: {label}")
    return DraftSections(**contents), errors


def limpiar_candidate(raw: str) -> str:
    """Recorta lo anterior al encabezado Conjuntos y las vallas de código."""
    text = re.sub(r"^```\w*[ \t]*\n?|\n?```[ \t]*$", "", raw.strip()).strip()
    first = _HEADING["sets"].search(text)
    return text[first.start():].strip() if first else text


# ---------------------------------------------------------------- formato

def formatear_spec(spec: ProblemSpec) -> str:
    """Resumen del ProblemSpec en texto; los rótulos evitan los encabezados del candidate."""
    def indexed(name: str, sets: list[str]) -> str:
        return f"{name}[{','.join(sets)}]" if sets else name

    lines = []
    if spec.sets:
        lines.append("Índices: " + "; ".join(f"{s.name} ({s.description})" for s in spec.sets))
    if spec.data:
        lines.append("Datos: " + "; ".join(
            f"{indexed(d.name, d.indexed_by)} {d.description}" + (f" ({d.unit})" if d.unit else "")
            for d in spec.data))
    if spec.decisions:
        lines.append("Decisiones: " + "; ".join(
            f"{indexed(d.symbol or '?', d.indexed_by)}"
            + (f" {d.domain}" if d.domain else "") + f": {d.description}"
            for d in spec.decisions))
    lines.append(f"Objetivo: {spec.objective.sense} {spec.objective.description}")
    lines.append("Requisitos:")
    lines.extend(f"{r.id} ({_KINDS[r.kind]}): {r.text}" for r in spec.requirements)
    return "\n".join(lines)


def _format_observation(item: Union[str, Issue]) -> str:
    if isinstance(item, str):
        return f"- {item}"
    parts = [item.requirement_id, item.location, item.description]
    text = " · ".join(p for p in parts if p)
    return f"- {text}" + (f" Corrección: {item.suggestion}" if item.suggestion else "")


def _parse_plan(raw: str, spec: ProblemSpec, warnings: list[str]) -> list[PlanItem]:
    known = set(spec.requirement_ids())
    plan = []
    for rid, equation in _PLAN_LINE.findall(raw):
        if rid in known:
            plan.append(PlanItem(requirement_id=rid, equation=equation))
        else:
            warnings.append(f"plan descartado: {rid} no existe en el ProblemSpec")
    missing = sorted(known - {item.requirement_id for item in plan}, key=lambda r: int(r[1:]))
    if plan and missing:
        warnings.append("requisitos sin línea de plan: " + ", ".join(missing))
    return plan


# ------------------------------------------------------------------ agente

def formular(
    llm: LLM,
    problem: str,
    spec: ProblemSpec,
    *,
    candidate_id: str,
    adapter_plan: bool,
    adapter_candidate: bool,
    prompt_path: Path = DEFAULT_PROMPT,
    observations: Optional[Sequence[Union[str, Issue]]] = None,
    previous_draft: Optional[str] = None,
) -> AgentStep:
    """Devuelve AgentStep con un FormulatorOutput.

    ``observations`` son los issues del Verificador o avisos del orquestador;
    ``previous_draft`` es el candidate que se está revisando.
    """
    version, sections = load_prompt(prompt_path)
    blocks = {
        "problem": problem,
        "spec_block": formatear_spec(spec),
        "previous_block": (sections["previous"].substitute(previous_draft=previous_draft)
                           if previous_draft else ""),
        "observations_block": (sections["observations"].substitute(
            observations="\n".join(map(_format_observation, observations)))
            if observations else ""),
    }
    step = AgentStep(output=None)

    def call(section: str, adapter_on: bool, **extra: str) -> str:
        prompt = render(sections[section], **blocks, **extra)
        raw = llm.generate(prompt, adapter_on)
        step.calls.append(LLMCall(version, prompt, adapter_on, raw))
        return raw

    def fail(message: str) -> AgentFormatError:
        return AgentFormatError(message, raw=step.calls[-1].raw, prompt_version=version)

    raw = call("decision", adapter_plan)
    plan = _parse_plan(raw, spec, step.warnings)
    decision = _DECISION.search(raw)
    action = _DECISIONS.get(decision.group(1).lower()) if decision else None
    if action is None:
        if not plan:
            raise fail("falta DECISION: formular o DECISION: aclarar")
        action = "formulate"
        step.warnings.append("falta DECISION; se interpretó formular porque hay plan")

    if action == "clarify":
        question = _QUESTION.search(raw)
        if not question or not question.group(1).strip():
            raise fail("DECISION: aclarar requiere PREGUNTA:")
        step.output = FormulatorOutput(action="clarify", question=question.group(1).strip())
        return step

    plan_block = ""
    if not plan and "plan" in sections:
        step.warnings.append("el prompt pide plan, pero no llegó ninguna línea Uk ->")
    if plan and "plan" in sections:
        plan_block = sections["plan"].substitute(
            plan="\n".join(f"{item.requirement_id} -> {item.equation}" for item in plan))
    raw = call("candidate", adapter_candidate, plan_block=plan_block)
    candidate = limpiar_candidate(raw)
    if not candidate:
        raise fail("el candidate está vacío")
    draft_sections, errors = separar_secciones(candidate)
    if _PLAN_LINE.search(candidate):
        errors.append("el candidate contiene líneas de plan Uk ->")
    if candidate != raw.strip():
        step.warnings.append("se recortó texto fuera de la formulación")
    try:
        step.output = FormulatorOutput(
            action="formulate",
            plan=plan,
            draft=DraftModel(candidate_id=candidate_id, raw_text=candidate,
                             sections=draft_sections, parse_ok=not errors,
                             parse_errors=errors),
        )
    except ValidationError as error:
        raise fail(f"FormulatorOutput inválido: {error}") from None
    return step
