"""Analista: lee el enunciado y entrega un ProblemSpec o pide releer los datos.

El módulo también define las piezas que comparte con el Formulador: el
protocolo del LLM, el registro de llamadas y la carga de prompts versionados.
Los textos de prompt viven en ``prompts/``; aquí solo se rellenan plantillas.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from typing import Any, Optional, Protocol

from pydantic import BaseModel, ValidationError

from schemas import (
    AnalystOutput,
    DataItem,
    DecisionSpec,
    Evidence,
    ObjectiveSpec,
    ProblemSpec,
    Requirement,
    SetSpec,
)
from tools.extract_data_spans import Span, localizar_cita

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
DEFAULT_PROMPT = PROMPTS_DIR / "analista_v1.md"


class LLM(Protocol):
    """Interfaz que model.py ofrece a los agentes; prompt es el mensaje user."""

    def generate(self, prompt: str, adapter_on: bool) -> str: ...


@dataclass
class LLMCall:
    prompt_version: str
    prompt: str
    adapter_on: bool
    raw: str


@dataclass
class AgentStep:
    """Salida validada y llamadas que el orquestador convierte en TraceEvent."""

    output: Any
    calls: list[LLMCall] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class AgentFormatError(Exception):
    """La salida del modelo no cumple el contrato; el orquestador decide reintentar."""

    def __init__(self, message: str, *, raw: str, prompt_version: str):
        super().__init__(message)
        self.raw = raw
        self.prompt_version = prompt_version


# ---------------------------------------------------------------- prompts

_SECTION = re.compile(r"^<!--\s*seccion:\s*(\w+)\s*-->\s*$", re.MULTILINE)


def load_prompt(path: Path) -> tuple[str, dict[str, Template]]:
    """Devuelve la versión (nombre del archivo) y sus secciones.

    El texto anterior a la primera marca es documentación y no se envía.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    parts = _SECTION.split(text)
    sections = {
        name: Template(body.strip("\n"))
        for name, body in zip(parts[1::2], parts[2::2])
    }
    if not sections:
        raise ValueError(f"{path.name} no tiene secciones")
    return path.stem, sections


def render(template: Template, **values: str) -> str:
    """Rellena la plantilla; los bloques vacíos no dejan líneas en blanco repetidas."""
    return re.sub(r"\n{3,}", "\n\n", template.substitute(**values)).strip()


# ------------------------------------------------------------------- JSON

_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)


def _balanced_object(text: str, start: int) -> Optional[str]:
    depth = 0
    in_string = escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _repair(candidate: str) -> str:
    """Corrige errores frecuentes de modelos pequeños sin reinterpretar contenido."""
    repaired = candidate.replace("“", '"').replace("”", '"')
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"\bTrue\b", "true", repaired)
    repaired = re.sub(r"\bFalse\b", "false", repaired)
    repaired = re.sub(r"\bNone\b", "null", repaired)
    # Barras de LaTeX como \sum o \le no son escapes JSON válidos.
    return re.sub(r'\\(?!["\\/]|u[0-9a-fA-F]{4}|[bfnrt](?![A-Za-z]))', r"\\\\", repaired)


def extraer_json(raw: str) -> dict:
    """Primer objeto JSON del texto; tolera vallas, prosa y errores menores."""
    text = _FENCE.sub("", raw)
    incomplete = False
    for match in re.finditer(r"\{", text):
        candidate = _balanced_object(text, match.start())
        if candidate is None:
            incomplete = True
            continue
        for attempt in (candidate, _repair(candidate)):
            try:
                parsed = json.loads(attempt)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    raise ValueError("JSON incompleto" if incomplete else "no se encontró un objeto JSON")


# ------------------------------------------------------------ normalización

_ACTIONS = {"entregar": "deliver", "releer": "reread"}
_KINDS = {
    "objetivo": "objective", "restriccion": "constraint",
    "restricción": "constraint", "dominio": "domain",
}
_DOMAINS = {
    "continuo": "continua", "continuous": "continua", "real": "continua",
    "entero": "entera", "integer": "entera",
    "binario": "binaria", "binary": "binaria",
}
_SENSES = {"minimizar": "min", "minimize": "min", "maximizar": "max", "maximize": "max"}
_CHILDREN: dict[type[BaseModel], dict[str, type[BaseModel]]] = {
    ProblemSpec: {
        "sets": SetSpec, "data": DataItem, "decisions": DecisionSpec,
        "objective": ObjectiveSpec, "requirements": Requirement,
    },
}
_REQ_NUMBER = re.compile(r"^[A-Za-z]?\s*(\d+)$")


def _alias(value: Any, table: dict[str, str]) -> Any:
    return table.get(value.strip().lower(), value) if isinstance(value, str) else value


def _prune(obj: Any, model: type[BaseModel], where: str, warnings: list[str]) -> Any:
    """Quita claves que el contrato no admite y ajusta formas frecuentes."""
    if not isinstance(obj, dict):
        return obj
    children = _CHILDREN.get(model, {})
    clean = {}
    for key, value in obj.items():
        if key not in model.model_fields:
            warnings.append(f"clave descartada: {where}.{key}")
            continue
        if value is None:
            # null equivale a omitir: las listas toman su valor por defecto.
            continue
        if key == "indexed_by" and isinstance(value, str):
            value = [value]
        if key == "evidence":
            value = _evidence(value)
            if value is None:
                continue
        elif key in children:
            child = children[key]
            if isinstance(value, list):
                value = [_prune(item, child, f"{where}.{key}[{i}]", warnings)
                         for i, item in enumerate(value)]
            else:
                value = _prune(value, child, f"{where}.{key}", warnings)
        clean[key] = value
    return clean


def _evidence(value: Any) -> Optional[dict]:
    """El modelo escribe solo la cita; los offsets los calcula el código."""
    if isinstance(value, str):
        value = {"text": value}
    if not isinstance(value, dict) or not str(value.get("text") or "").strip():
        return None
    return {"text": str(value["text"])}


def _apply_aliases(spec: dict, warnings: list[str]) -> None:
    for requirement in spec.get("requirements") or []:
        if not isinstance(requirement, dict):
            continue
        requirement["kind"] = _alias(requirement.get("kind"), _KINDS)
        rid = requirement.get("id")
        if isinstance(rid, (str, int)) and not str(rid).startswith("U"):
            number = _REQ_NUMBER.match(str(rid).strip())
            if number:
                requirement["id"] = f"U{int(number.group(1))}"
                warnings.append(f"ID de requisito {rid!r} renombrado a {requirement['id']}")
    for decision in spec.get("decisions") or []:
        if isinstance(decision, dict):
            decision["domain"] = _alias(decision.get("domain"), _DOMAINS)
    if isinstance(spec.get("objective"), dict):
        spec["objective"]["sense"] = _alias(spec["objective"].get("sense"), _SENSES)


def _locate_evidence(spec: dict, problem: str, warnings: list[str]) -> None:
    """Fija start/end y reemplaza la cita por el texto literal encontrado."""
    def visit(obj: Any, where: str) -> None:
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                visit(item, f"{where}[{i}]")
            return
        if not isinstance(obj, dict):
            return
        evidence = obj.get("evidence")
        if isinstance(evidence, dict):
            span = localizar_cita(problem, evidence["text"])
            if span is None:
                warnings.append(f"cita no encontrada en el enunciado: {where}")
            else:
                literal = problem[span[0]:span[1]]
                if literal != evidence["text"]:
                    warnings.append(f"cita normalizada al texto literal: {where}")
                obj["evidence"] = {"text": literal, "start": span[0], "end": span[1]}
        for key, value in obj.items():
            if key != "evidence":
                visit(value, f"{where}.{key}")
    visit(spec, "spec")


def _normalize(data: dict, case_id: str, problem: str, warnings: list[str]) -> dict:
    action = _alias(data.get("action"), _ACTIONS)
    spec = data.get("spec")
    if spec is None and "requirements" in data:
        # Algunos modelos aplanan el spec junto a la acción.
        spec = {key: value for key, value in data.items()
                if key in ProblemSpec.model_fields}
        warnings.append("spec aplanado en la raíz; se reagrupó")
    if action is None and isinstance(spec, dict):
        action = "deliver"
        warnings.append("falta action; se interpretó deliver porque hay spec")
    if action != "deliver":
        return {"action": action, "reason": data.get("reason")}
    if not isinstance(spec, dict):
        return {"action": action, "spec": spec}
    spec = _prune(spec, ProblemSpec, "spec", warnings)
    spec["case_id"] = case_id
    _apply_aliases(spec, warnings)
    _locate_evidence(spec, problem, warnings)
    return {"action": action, "spec": spec}


# ------------------------------------------------------------------ agente

def _format_spans(spans: list[Span]) -> str:
    lines = []
    for span in spans:
        unit = f", unidad {span.unit}" if span.unit else ""
        lines.append(f'- "{span.text}" (valor {span.value:g}{unit}): ...{span.context}...')
    return "\n".join(lines)


def analizar(
    llm: LLM,
    case_id: str,
    problem: str,
    *,
    adapter_on: bool,
    prompt_path: Path = DEFAULT_PROMPT,
    spans: Optional[list[Span]] = None,
    question: Optional[str] = None,
) -> AgentStep:
    """Una llamada al modelo. Devuelve AgentStep con un AnalystOutput.

    ``spans`` es la observación de extract_data_spans, si el Analista la pidió;
    ``question`` es la aclaración que solicitó el Formulador.
    """
    version, sections = load_prompt(prompt_path)
    spans_block = (sections["spans"].substitute(spans=_format_spans(spans))
                   if spans is not None else "")
    question_block = (sections["question"].substitute(question=question)
                      if question else "")
    prompt = render(sections["user"], problem=problem, spans_block=spans_block,
                    question_block=question_block)
    raw = llm.generate(prompt, adapter_on)
    step = AgentStep(output=None, calls=[LLMCall(version, prompt, adapter_on, raw)])

    def fail(message: str) -> AgentFormatError:
        return AgentFormatError(message, raw=raw, prompt_version=version)

    try:
        data = extraer_json(raw)
    except ValueError as error:
        raise fail(f"salida sin JSON válido: {error}") from None
    normalized = _normalize(data, case_id, problem, step.warnings)
    if normalized["action"] == "reread" and spans is not None:
        raise fail("reread no permitido: los fragmentos ya fueron entregados")
    try:
        step.output = AnalystOutput.model_validate(normalized)
    except ValidationError as error:
        raise fail(f"AnalystOutput inválido: {error}") from None
    return step
