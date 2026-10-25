"""Fragmentos numéricos y citas literales del enunciado.

La herramienta solo localiza cantidades y sus unidades; no decide cuáles
importan ni interpreta ecuaciones. El Analista trata la lista como candidatos.
"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Span(BaseModel):
    """Cantidad encontrada en el enunciado; text == problem[start:end]."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    value: Optional[float] = None
    unit: Optional[str] = None
    context: str


CONTEXT_CHARS = 40

# Un dígito pegado a una letra o a otro dígito forma parte de un identificador
# (P1, F01, m3) y no es un dato. Los miles usan punto y los decimales coma.
_NUMERO = re.compile(
    r"(?<![\w.,$])"
    r"(?P<moneda>(?:US)?\$\s?)?"
    r"(?P<num>\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?)"
    r"(?:\s?(?P<pct>%))?"
    r"(?:\s(?P<escala>mil(?:l(?:ón|ones))?)\b)?"
)
_PALABRA = re.compile(
    r"(?<!\w)(?P<num>dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|"
    r"quince|veinte|treinta|cuarenta|cincuenta|cien)(?!\w)",
    re.IGNORECASE,
)
_UNIDAD = re.compile(r"\s*(?P<unit>[^\W\d_][\w/³²]*)")
_MILES = re.compile(r"^\d{1,3}(?:\.\d{3})+(?:,\d+)?$")

_PALABRAS_VALOR = {
    "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
    "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "quince": 15,
    "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50, "cien": 100,
}
_ESCALAS = {"mil": 1e3, "millón": 1e6, "millones": 1e6}
_NO_UNIDAD = {
    "a", "al", "cada", "como", "con", "de", "del", "desde", "e", "el", "en",
    "entre", "es", "hasta", "la", "las", "lo", "los", "más", "menos", "ni",
    "o", "para", "por", "que", "se", "según", "sin", "son", "u", "un", "una", "y",
}


def _valor(num: str) -> float:
    if _MILES.match(num):
        return float(num.replace(".", "").replace(",", "."))
    return float(num.replace(",", "."))


def _unidad_siguiente(problem: str, end: int) -> Optional[str]:
    match = _UNIDAD.match(problem, end)
    if match is None or match.group("unit").lower() in _NO_UNIDAD:
        return None
    return match.group("unit")


def _contexto(problem: str, start: int, end: int) -> str:
    fragment = problem[max(0, start - CONTEXT_CHARS):end + CONTEXT_CHARS]
    return " ".join(fragment.split())


def extract_data_spans(problem: str) -> list[Span]:
    """Devuelve las cantidades del enunciado en orden de aparición."""
    spans = []
    for match in _NUMERO.finditer(problem):
        value = _valor(match.group("num"))
        if match.group("escala"):
            value *= _ESCALAS[match.group("escala")]
        if match.group("pct"):
            unit = "%"
        elif match.group("moneda"):
            unit = "$"
        else:
            unit = _unidad_siguiente(problem, match.end())
        spans.append(Span(
            text=match.group(0), start=match.start(), end=match.end(),
            value=value, unit=unit,
            context=_contexto(problem, match.start(), match.end()),
        ))
    for match in _PALABRA.finditer(problem):
        spans.append(Span(
            text=match.group(0), start=match.start(), end=match.end(),
            value=float(_PALABRAS_VALOR[match.group("num").lower()]),
            unit=_unidad_siguiente(problem, match.end()),
            context=_contexto(problem, match.start(), match.end()),
        ))
    return sorted(spans, key=lambda span: span.start)


def localizar_cita(problem: str, quote: str) -> Optional[tuple[int, int]]:
    """Ubica una cita en el enunciado; tolera espacios, mayúsculas y comillas."""
    cita = quote.strip().strip("\"'«»“”").strip()
    cita = cita.removesuffix("...").removesuffix("…").strip()
    if not cita:
        return None
    index = problem.find(cita)
    if index >= 0:
        return index, index + len(cita)
    for variante in (cita, cita.rstrip(".")):
        tokens = variante.split()
        if not tokens:
            continue
        match = re.search(r"\s+".join(map(re.escape, tokens)), problem, re.IGNORECASE)
        if match:
            return match.start(), match.end()
    return None
