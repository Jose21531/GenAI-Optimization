"""Contratos compartidos por los agentes, las herramientas y el orquestador.

El texto evaluable de la Entrega 2 permanece en ``DraftModel.raw_text``. El plan,
la cobertura y las decisiones de control son artefactos separados. Cualquier
cambio de este archivo debe coordinarse con los tres responsables (AGENTS.md).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    """Rechaza campos inesperados, incluidos datos oficiales del benchmark."""

    model_config = ConfigDict(extra="forbid")


Variant = Literal["full", "no_evidence", "no_plan", "no_audit", "no_review"]
VarDomain = Literal["continua", "entera", "binaria"]
RequirementKind = Literal["objective", "constraint", "domain"]
ObjectiveSense = Literal["min", "max"]
REQ_ID_PATTERN = r"^U[1-9][0-9]*$"


class Evidence(ContractModel):
    """Cita literal del enunciado; su correspondencia se comprueba con el texto."""

    text: str = Field(min_length=1)
    start: Optional[int] = Field(default=None, ge=0)
    end: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def valid_offsets(self) -> Evidence:
        if (self.start is None) != (self.end is None):
            raise ValueError("start y end deben aparecer juntos")
        if self.start is not None and self.end <= self.start:
            raise ValueError("end debe ser mayor que start")
        return self


class SetSpec(ContractModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    evidence: Optional[Evidence] = None


class DataItem(ContractModel):
    """Dato paramétrico extraído; name es el símbolo sugerido."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    indexed_by: list[str] = Field(default_factory=list)
    unit: Optional[str] = None
    evidence: Optional[Evidence] = None


class DecisionSpec(ContractModel):
    description: str = Field(min_length=1)
    symbol: Optional[str] = None
    indexed_by: list[str] = Field(default_factory=list)
    domain: Optional[VarDomain] = None
    evidence: Optional[Evidence] = None


class ObjectiveSpec(ContractModel):
    sense: ObjectiveSense
    description: str = Field(min_length=1)
    evidence: Optional[Evidence] = None


class Requirement(ContractModel):
    id: str = Field(pattern=REQ_ID_PATTERN)
    kind: RequirementKind
    text: str = Field(min_length=1)
    evidence: Optional[Evidence] = None


class ProblemSpec(ContractModel):
    """Análisis del enunciado; nunca contiene requisitos oficiales del juez."""

    case_id: str = Field(min_length=1)
    sets: list[SetSpec] = Field(default_factory=list)
    data: list[DataItem] = Field(default_factory=list)
    decisions: list[DecisionSpec] = Field(default_factory=list)
    objective: ObjectiveSpec
    requirements: list[Requirement] = Field(min_length=1)
    uncertainties: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_requirement_ids(self) -> ProblemSpec:
        ids = [requirement.id for requirement in self.requirements]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de requisito repetidos")
        return self

    def requirement_ids(self) -> list[str]:
        return [requirement.id for requirement in self.requirements]


class AnalystOutput(ContractModel):
    action: Literal["deliver", "reread"]
    spec: Optional[ProblemSpec] = None
    reason: Optional[str] = None

    @model_validator(mode="after")
    def valid_action(self) -> AnalystOutput:
        if self.action == "deliver" and self.spec is None:
            raise ValueError("deliver requiere spec")
        if self.action == "reread" and not self.reason:
            raise ValueError("reread requiere reason")
        return self


class PlanItem(ContractModel):
    """Mensaje interno de planificación; no se antepone al candidate."""

    requirement_id: str = Field(pattern=REQ_ID_PATTERN)
    equation: str = Field(min_length=1)


class DraftSections(ContractModel):
    """Secciones opcionales extraídas del texto nativo por un parser."""

    sets: Optional[str] = None
    parameters: Optional[str] = None
    variables: Optional[str] = None
    objective: Optional[str] = None
    constraints: Optional[str] = None


class DraftModel(ContractModel):
    """Borrador con texto nativo; metadatos añadidos por el orquestador."""

    candidate_id: str = Field(min_length=1)
    raw_text: str = Field(min_length=1)
    sections: Optional[DraftSections] = None
    parse_ok: bool = False
    parse_errors: list[str] = Field(default_factory=list)


class FormulatorOutput(ContractModel):
    """Contenedor del orquestador para mensajes separados del Formulador."""

    action: Literal["formulate", "clarify"]
    draft: Optional[DraftModel] = None
    plan: list[PlanItem] = Field(default_factory=list)
    question: Optional[str] = None

    @model_validator(mode="after")
    def valid_action(self) -> FormulatorOutput:
        if self.action == "formulate" and self.draft is None:
            raise ValueError("formulate requiere draft")
        if self.action == "clarify" and not self.question:
            raise ValueError("clarify requiere question")
        return self


class ModelElement(ContractModel):
    """Parte del candidate identificada independientemente por el Verificador."""

    id: str = Field(min_length=1)
    kind: RequirementKind
    excerpt: str = Field(min_length=1)


class CoverageLink(ContractModel):
    requirement_id: str = Field(pattern=REQ_ID_PATTERN)
    element_id: str = Field(min_length=1)


class CoverageMap(ContractModel):
    """Inventario y vínculos que audit_model contrasta con ProblemSpec y candidate."""

    candidate_id: str = Field(min_length=1)
    elements: list[ModelElement] = Field(default_factory=list)
    links: list[CoverageLink] = Field(default_factory=list)


CheckName = Literal[
    "simbolo_no_declarado",
    "variable_sin_dominio",
    "aridad_inconsistente",
    "variable_no_usada",
    "dato_sin_parametro",
    "parametro_no_usado",
    "indice_de_parametro_invalido",
    "indice_libre",
    "no_lineal",
    "requisito_sin_cubrir",
    "restriccion_sin_requisito",
    "referencia_invalida",
    "cobertura_tipo_incorrecto",
]


class Finding(ContractModel):
    check: CheckName
    status: Literal["hallazgo", "no_verificado"] = "hallazgo"
    level: Optional[Literal["error", "aviso"]] = None
    message: str = Field(min_length=1)
    symbol: Optional[str] = None
    requirement_id: Optional[str] = Field(default=None, pattern=REQ_ID_PATTERN)
    location: Optional[str] = None

    @model_validator(mode="after")
    def valid_status(self) -> Finding:
        if self.status == "hallazgo" and self.level is None:
            raise ValueError("un hallazgo requiere level")
        if self.status == "no_verificado" and self.level is not None:
            raise ValueError("no_verificado no tiene gravedad")
        return self


class AuditReport(ContractModel):
    candidate_id: str = Field(min_length=1)
    checks_run: list[CheckName] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(f.status == "hallazgo" and f.level == "error" for f in self.findings)


class Issue(ContractModel):
    description: str = Field(min_length=1)
    requirement_id: Optional[str] = Field(default=None, pattern=REQ_ID_PATTERN)
    location: Optional[str] = None
    suggestion: Optional[str] = None


class ReviewDecision(ContractModel):
    action: Literal["accept", "revise", "stop"]
    candidate_id: str = Field(min_length=1)
    issues: list[Issue] = Field(default_factory=list)
    reason: Optional[str] = None

    @model_validator(mode="after")
    def valid_action(self) -> ReviewDecision:
        if self.action == "revise" and not self.issues:
            raise ValueError("revise requiere al menos un issue")
        return self


class TraceEvent(ContractModel):
    """Evento que el orquestador serializa como una línea JSONL."""

    run_id: str = Field(min_length=1)
    problem_id: str = Field(min_length=1)
    variant: Variant
    step: int = Field(ge=0)
    round: int = Field(default=0, ge=0)
    actor: Literal[
        "orquestador", "analista", "formulador", "verificador",
        "extract_data_spans", "audit_model",
    ]
    event: Literal[
        "llamada", "respuesta", "herramienta", "decision", "reintento",
        "fallo_formato", "presupuesto_agotado", "fin",
    ]
    prompt_version: Optional[str] = None
    adapter_on: Optional[bool] = None
    input: Optional[Any] = None
    output: Optional[Any] = None
    decision: Optional[str] = None
    tokens_in: Optional[int] = Field(default=None, ge=0)
    tokens_out: Optional[int] = Field(default=None, ge=0)
    latency_ms: Optional[float] = Field(default=None, ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunResult(ContractModel):
    problem_id: str = Field(min_length=1)
    variant: Variant
    final_text: str
    status: Literal["aceptado", "presupuesto_agotado", "detenido", "fallo_formato"]
    rounds: int = Field(default=0, ge=0)
    clarifications: int = Field(default=0, ge=0)
    tool_calls: int = Field(default=0, ge=0)
    tokens_total: int = Field(default=0, ge=0)
    latency_ms_total: float = Field(default=0.0, ge=0)
