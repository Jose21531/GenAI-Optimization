"""Verificador: cobertura independiente, solicitud de auditoría y revisión semántica.

Cada invocación hace una llamada al LLM. Si pide ``audit``, el orquestador
ejecuta la herramienta y vuelve a llamar con el mapa y el informe. Este módulo
no ejecuta herramientas, reintentos ni revisiones del Formulador.
"""

from __future__ import annotations

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
from schemas import AuditReport, ContractModel, CoverageMap, DraftModel, ProblemSpec, ReviewDecision

DEFAULT_PROMPT = PROMPTS_DIR / "verificador_v1.md"


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
        return self


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
    audit_block = (
        render(sections["audit_result"],
               coverage=coverage.model_dump_json(exclude_none=True),
               audit_report=audit_report.model_dump_json(exclude_none=True))
        if audit_report is not None else ""
    )
    feedback_block = (
        render(sections["format_feedback"], feedback=format_feedback)
        if format_feedback else ""
    )
    prompt = render(
        sections["user"],
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
    )
    raw = llm.generate(prompt, adapter_on)
    step = AgentStep(output=None, calls=[LLMCall(version, prompt, adapter_on, raw)])

    def fail(message: str) -> AgentFormatError:
        return AgentFormatError(message, raw=raw, prompt_version=version,
                                calls=step.calls, warnings=step.warnings)

    try:
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
    except (ValueError, TypeError, AttributeError) as error:
        raise fail(f"VerifierOutput inválido: {error}") from None

    step.output = output
    return step
