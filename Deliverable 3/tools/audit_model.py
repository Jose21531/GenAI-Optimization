"""Auditoría determinista y conservadora del análisis, borrador y cobertura.

No resuelve modelos ni demuestra equivalencia. Los chequeos de notación usan
un subconjunto explícito de LaTeX/texto; las formas no soportadas quedan como
no_verificado. Los hallazgos sintácticos son avisos durante el desarrollo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import get_args

from agents.formulador import separar_secciones
from schemas import AuditReport, CheckName, CoverageMap, DraftModel, Finding, ProblemSpec

SYNTAX_CHECKS = (
    "simbolo_no_declarado", "variable_sin_dominio", "aridad_inconsistente",
    "variable_no_usada", "dato_sin_parametro", "parametro_no_usado",
    "indice_de_parametro_invalido", "indice_libre", "no_lineal",
)
_NAME = r"[A-Za-z][A-Za-z0-9]*"
_SYMBOL = re.compile(rf"(?<![A-Za-z\\])(?P<name>{_NAME})(?P<sub>_\{{[^{{}}]+\}}|_[A-Za-z0-9]+)?")
_BIND = re.compile(r"([a-z](?:\s*,\s*[a-z])*)\s*(?:\\in|∈|\bin\b|\ben\b)\s*([A-Z][A-Za-z0-9]*)")
_SUM = re.compile(r"(?:\\sum|\bsum)_\{([^{}]+)\}(?:\^\{[^{}]+\}|\^\d+)?")
_QUANT = re.compile(r"(?:\\forall|∀|\bforall\b)")
_DOMAIN = re.compile(r"\\in\s*(?:RR|ZZ|\{\s*0\s*,\s*1\s*\})|[≥]|>=\s*0|\\geq?\s*0|continua|entera|binaria", re.I)
_COMMANDS = {"sum", "max", "min", "forall", "in", "le", "leq", "ge", "geq",
             "quad", "qquad", "cdot", "times", "frac", "mathbb"}
_RESERVED = _COMMANDS | {"en", "RR", "ZZ", "R", "Z", "sujeto", "todo", "para"}


@dataclass
class _Decl:
    name: str
    indices: tuple[str, ...]
    text: str


def _plain(text: str) -> str:
    text = re.sub(r"\\mathbb\s*\{([RZ])\}", lambda m: m[1] * 2, text)
    text = re.sub(r"\\(?:left|right)\b", "", text)
    for token in (r"\(", r"\)", r"\[", r"\]", "$", "**", "`"):
        text = text.replace(token, "")
    return text.replace(r"\{", "{").replace(r"\}", "}")


def _indices(sub: str) -> tuple[str, ...]:
    if not sub:
        return ()
    body = sub[1:].strip("{}")
    if re.fullmatch(r"[a-z0-9]{1,2}", body):
        return tuple(body)
    return tuple(s.strip() for s in body.split(","))


def _declarations(text: str) -> tuple[dict[str, _Decl], bool]:
    declarations = {}
    reliable = True
    for line in _plain(text).splitlines():
        line = line.strip().lstrip("-* ")
        if not line:
            continue
        # Una declaración por línea, con descripción después de dos puntos.
        prefix, separator, _ = line.partition(":")
        match = _SYMBOL.match(prefix)
        if not separator or match is None:
            reliable = False
            continue
        if re.search(r";\s*[A-Za-z].*:", line):
            reliable = False
        decl = _Decl(match["name"], _indices(match["sub"] or ""), line)
        if decl.name in declarations:
            reliable = False
        declarations[decl.name] = decl
        rest = prefix[match.end():]
        if re.search(r",\s*[A-Za-z]+_", rest) or re.search(r"\\text|\\mathrm", prefix):
            reliable = False
    return declarations, reliable


def _sum_indices(subscript: str) -> set[str]:
    bound = {i for m in _BIND.finditer(subscript) for i in re.findall(r"[a-z]", m[1])}
    numeric = re.match(r"([a-z])\s*=", subscript)
    return bound | ({numeric[1]} if numeric else set())


def _scope_end(body: str, start: int) -> int:
    """Fin del término que sigue a una sumatoria: un operador o paréntesis de cierre a nivel 0."""
    depth = 0
    for k in range(start, len(body)):
        char = body[k]
        if char in "({[":
            depth += 1
        elif char in ")}]":
            depth -= 1
            if depth < 0:
                return k
        elif depth == 0 and body[start:k].strip() and (
                char in "+-=<>≤≥" or re.match(r"\\(?:leq?|geq?)\b", body[k:])):
            return k
    return len(body)


def _out_of_scope(plain: str) -> set[str]:
    """Índices ligados solo por una sumatoria que aparecen después de su alcance."""
    body = _QUANT.split(plain)[0]
    quantified = {i for m in _BIND.finditer(plain[len(body):]) for i in re.findall(r"[a-z]", m[1])}
    sums = list(_SUM.finditer(body))
    free = set()
    for position, match in enumerate(sums):
        end = _scope_end(body, match.end())
        for index in _sum_indices(match[1]) - quantified:
            # Una sumatoria posterior con el mismo índice abre un alcance nuevo.
            stop = next((s.start() for s in sums[position + 1:]
                         if s.start() >= end and index in _sum_indices(s[1])), len(body))
            region = _SUM.sub(" ", body[end:stop])
            if any(index in _indices(m["sub"] or "") for m in _SYMBOL.finditer(region)):
                free.add(index)
    return free


def _expression(text: str) -> tuple[list[re.Match], set[str], str, bool, set[str]]:
    plain = _plain(text)
    bindings = set()
    for match in _BIND.finditer(plain):
        bindings.update(re.findall(r"[a-z]", match[1]))
    for match in _SUM.finditer(plain):
        numeric = re.match(r"([a-z])\s*=", match[1])
        if numeric:
            bindings.add(numeric[1])
    # Eliminar solo los ligadores, conservando expresiones a cada lado.
    cleaned = _SUM.sub("", plain)
    cleaned = _QUANT.split(cleaned)[0]
    commands = re.findall(r"\\([A-Za-z]+)", cleaned)
    reliable = all(command in _COMMANDS for command in commands)
    if re.search(r"(?:\\sum|\bsum)_", cleaned):
        reliable = False
    cleaned = re.sub(r"\\[A-Za-z]+", lambda m: " " + m[0][1:] + " ", cleaned)
    tokens = [m for m in _SYMBOL.finditer(cleaned) if m["name"] not in _RESERVED]
    if any(len(m["name"]) > 1 and m["name"] not in {"sin", "cos", "log", "exp", "sqrt", "abs"}
           for m in tokens):
        reliable = False
    if re.search(r"\\text|\\begin|\\end|\\frac|[^\x00-\x7f]", plain):
        reliable = False
    if any(re.search(r"[^a-z0-9, ]", (m["sub"] or "").strip("_{}")) for m in tokens):
        reliable = False
    if any(len(index) > 1 and not index.isdigit() for m in tokens for index in _indices(m["sub"] or "")):
        reliable = False
    return tokens, bindings, cleaned, reliable, _out_of_scope(plain)


def audit_model(spec: ProblemSpec, draft: DraftModel, coverage: CoverageMap) -> AuditReport:
    """Cruza artefactos en memoria; nunca abre archivos de datos.

    Las referencias inválidas son errores. Una cobertura incompleta produce
    hallazgos, incluso si el mapa omite todas las ecuaciones. Los avisos de
    sintaxis no constituyen aprobación; véase docs/audit_model.md.
    """
    report = AuditReport(candidate_id=draft.candidate_id, checks_run=list(get_args(CheckName)))

    def finding(check, message, *, level="aviso", **details):
        report.findings.append(Finding(check=check, level=level, message=message, **details))

    unverified = set()

    def unknown(check, message, location=None):
        key = (check, location)
        if key not in unverified:
            unverified.add(key)
            report.findings.append(Finding(check=check, status="no_verificado",
                                           message=message, location=location))

    requirements = {r.id: r for r in spec.requirements}
    elements = {}
    valid_elements = set()
    if coverage.candidate_id != draft.candidate_id:
        finding("referencia_invalida", "El mapa corresponde a otro borrador",
                level="error", location=coverage.candidate_id)
    for element in coverage.elements:
        if element.id in elements:
            finding("referencia_invalida", "ID de elemento repetido", level="error", location=element.id)
        elements[element.id] = element
        if element.excerpt not in draft.raw_text:
            finding("referencia_invalida", "El fragmento no existe literalmente en el borrador",
                    level="error", location=element.id)
        elif coverage.candidate_id == draft.candidate_id:
            valid_elements.add(element.id)
    linked_requirements, linked_constraints = set(), set()
    for link in coverage.links:
        req, element = requirements.get(link.requirement_id), elements.get(link.element_id)
        if req is None or element is None:
            finding("referencia_invalida", "El vínculo cita un requisito o elemento inexistente",
                    level="error", requirement_id=link.requirement_id, location=link.element_id)
            continue
        if req.kind != element.kind:
            finding("cobertura_tipo_incorrecto", f"Se vinculó {req.kind} con {element.kind}",
                    level="error", requirement_id=req.id, location=element.id)
            continue
        if element.id in valid_elements:
            linked_requirements.add(req.id)
            linked_constraints.add(element.id)
    for requirement in spec.requirements:
        if requirement.id not in linked_requirements:
            finding("requisito_sin_cubrir", requirement.text, level="error", requirement_id=requirement.id)
    for element in coverage.elements:
        if element.kind == "constraint" and element.id not in linked_constraints:
            finding("restriccion_sin_requisito", "Posible adición injustificada; inspeccionar el enunciado",
                    location=element.id)

    sections, errors = separar_secciones(draft.raw_text)
    # Un mapa vacío tampoco demuestra que no existan restricciones.
    if sections.constraints:
        for line in sections.constraints.splitlines():
            if not re.search(r"<=|>=|=|\\(?:leq?|geq?)\b|[≤≥]", line):
                continue
            if not any(e.kind == "constraint" and e.excerpt in line for e in coverage.elements):
                unknown("restriccion_sin_requisito", "Ecuación no inventariada de forma comprobable en el mapa", line)
    else:
        unknown("restriccion_sin_requisito", "No se pudo inventariar la sección de restricciones")
    if errors:
        for check in SYNTAX_CHECKS:
            unknown(check, "No se pueden analizar las cinco secciones: " + "; ".join(errors))
        return report

    sets, sets_ok = _declarations(sections.sets)
    parameters, params_ok = _declarations(sections.parameters)
    variables, vars_ok = _declarations(sections.variables)
    declarations_ok = sets_ok and params_ok and vars_ok and bool(variables)
    declarations = sets | parameters | variables
    for group in (sets.keys() & parameters.keys(), sets.keys() & variables.keys(),
                  parameters.keys() & variables.keys()):
        if group:
            declarations_ok = False
    body = sections.objective + "\n" + sections.constraints
    expressions = [_expression(line) for line in body.splitlines() if _plain(line).strip()]
    expressions_ok = bool(expressions) and all(e[3] for e in expressions)
    if not declarations_ok:
        for check in SYNTAX_CHECKS:
            unknown(check, "Declaraciones fuera del subconjunto soportado o símbolos ambiguos")
    if not expressions_ok:
        for check in ("simbolo_no_declarado", "aridad_inconsistente", "variable_no_usada",
                      "parametro_no_usado", "indice_libre", "no_lineal"):
            unknown(check, "Expresiones fuera del subconjunto soportado")

    used = {m["name"] for tokens, *_ in expressions for m in tokens}
    for name, declaration in variables.items():
        if not _DOMAIN.search(declaration.text):
            finding("variable_sin_dominio", "No se reconoció un dominio explícito",
                    symbol=name, location=declaration.text)
        if name not in used and declarations_ok and expressions_ok:
            finding("variable_no_usada", "Variable sin uso reconocido; justificar si es auxiliar",
                    symbol=name, location=declaration.text)
    for name, declaration in parameters.items():
        if name not in used and declarations_ok and expressions_ok:
            finding("parametro_no_usado", "Parámetro sin uso reconocido", symbol=name, location=declaration.text)
        bindings = {i: s for m in _BIND.finditer(declaration.text) for i in re.findall(r"[a-z]", m[1]) for s in [m[2]]}
        for index in declaration.indices:
            if index not in bindings:
                unknown("indice_de_parametro_invalido", "No se reconoce el conjunto del índice", declaration.text)
            elif bindings[index] not in sets:
                finding("indice_de_parametro_invalido", "Índice asociado a un conjunto no declarado",
                        symbol=name, location=declaration.text)
    for datum in spec.data:
        if datum.name not in parameters:
            finding("dato_sin_parametro", "No se reconoce el símbolo sugerido; inspeccionar posibles alias",
                    symbol=datum.name, location=datum.description)
        for set_name in datum.indexed_by:
            if set_name not in sets:
                finding("indice_de_parametro_invalido", "Conjunto del dato no declarado en el borrador",
                        symbol=datum.name, location=set_name)

    for binding in _BIND.finditer(body):
        if binding[2] not in sets:
            finding("simbolo_no_declarado", "Conjunto de un ligador sin declaración reconocida",
                    symbol=binding[2], location=binding[0])
    for tokens, bindings, expression, reliable, out_of_scope in expressions:
        if not reliable or not declarations_ok:
            continue
        for index in sorted(out_of_scope):
            finding("indice_libre", "Índice usado fuera del alcance de la sumatoria que lo liga",
                    symbol=index, location=expression)
        for token in tokens:
            name, indices = token["name"], _indices(token["sub"] or "")
            if name not in declarations and name not in bindings:
                finding("simbolo_no_declarado", "Símbolo sin declaración reconocida", symbol=name, location=expression)
            if name in variables and len(indices) != len(variables[name].indices):
                finding("aridad_inconsistente", "Aridad distinta entre declaración y uso",
                        symbol=name, location=token[0])
            for index in indices:
                if re.fullmatch(r"[a-z]", index) and index not in bindings:
                    finding("indice_libre", "Índice sin ligador reconocido en esta ecuación",
                            symbol=index, location=expression)
        if _SUM.search(expression) or ("+" in expression and bindings):
            unknown("indice_libre", "El alcance de los ligadores requiere inspección", expression)
        for left, right in zip(tokens, tokens[1:]):
            gap = expression[left.end():right.start()]
            if left["name"] in variables and right["name"] in variables and re.fullmatch(
                    r"[\s()]*(?:\*|cdot|times)?[\s()]*", gap):
                finding("no_lineal", "Producto entre variables", location=expression)
        for token in tokens:
            tail = expression[token.end():]
            # Variable junto a un paréntesis: puede multiplicar una expresión con variables.
            if token["name"] in variables and (re.match(r"\s*\(", tail)
                                               or re.search(r"\)\s*$", expression[:token.start()])):
                unknown("no_lineal", "Variable multiplicada por una expresión entre paréntesis", expression)
            if token["name"] in variables and re.match(r"\s*\^\s*\{?(?:[2-9]|[1-9][0-9])", tail):
                finding("no_lineal", "Potencia no lineal de una variable", symbol=token["name"], location=expression)
            if token["name"] in variables and re.search(r"/\s*$", expression[:token.start()]):
                finding("no_lineal", "División por una variable", symbol=token["name"], location=expression)
        if any(t["name"] in {"sin", "cos", "log", "exp", "sqrt", "abs"} for t in tokens):
            finding("no_lineal", "Función no lineal reconocida; revisar su argumento", location=expression)
        if re.search(r"[(){}]\s*\*|\*\s*[({]|\^|/", expression):
            unknown("no_lineal", "Operación cuyo grado no se puede demostrar con este parser", expression)
    return report
