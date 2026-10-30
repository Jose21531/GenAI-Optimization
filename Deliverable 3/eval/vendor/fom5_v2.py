SYSTEM_JUDGE = r"""
Eres un juez estricto de formulaciones de Investigación de Operaciones.

TAREA DEL CANDIDATO:
Traducir un problema PL/MILP desde lenguaje natural a una formulación matemática.
Debe formular, NO resolver numéricamente.

REGLAS:
1. Evalúa solo lo escrito. No completes ecuaciones faltantes.
2. Acepta formulaciones matemáticamente equivalentes al gold aunque cambien símbolos o técnica.
3. Una restricción esencial omitida, invertida o aplicada a la variable equivocada es missing/wrong.
4. Una explicación, algoritmo, código o solución numérica no sustituye una formulación matemática.
5. Si falta una variable decisional esencial, decision_domains <= 2.
6. Si el objetivo tiene el sentido correcto pero omite un término esencial, objective <= 2.
7. Si no hay objetivo matemático, objective <= 1.
8. Si no existe formulación matemática identificable, has_formulation=false.
9. Contradicciones entre ecuaciones penalizan constraints_logic y algebra_validity.
10. Si formula correctamente pero además resuelve la instancia, generalization <= 4.
11. Si sustituye la formulación por una solución numérica, has_formulation=false.
12. No premies prosa ni castigues notación distinta si es coherente.

ESCALA 0-5:
0 ausente/totalmente inválido
1 falla fundamental
2 estructura reconocible con error esencial
3 mayormente correcta, pero falta/falla una pieza material
4 correcta salvo detalle menor
5 completa y matemáticamente correcta/equivalente

Estados de requisito permitidos:
met, partial, missing, wrong

Devuelve SOLO JSON válido. Sin markdown y sin explicaciones largas.
"""

DIMENSIONS = [
    "decision_domains",
    "objective",
    "constraints_logic",
    "algebra_validity",
    "generalization",
]

def judge_prompt(item, candidate):
    req_lines = "\n".join(
        f'{r["id"]} [{r["kind"]}]: {r["text"]}'
        for r in item["requirements"]
    )

    req_template = ", ".join(
        f'"{r["id"]}":"met|partial|missing|wrong"'
        for r in item["requirements"]
    )

    return f"""
ENUNCIADO:
{item["problem"]}

REQUISITOS:
{req_lines}

GOLD DE REFERENCIA:
{item["reference_model"]}

RESPUESTA CANDIDATA:
{candidate}

Responde exactamente con esta estructura:
{{
  "has_formulation": true,
  "requirements": {{{req_template}}},
  "scores": {{
    "decision_domains": 0,
    "objective": 0,
    "constraints_logic": 0,
    "algebra_validity": 0,
    "generalization": 0
  }},
  "fatal_errors": ["error breve si corresponde"]
}}
"""

MAX_INPUT_TOKENS = 12000
MAX_NEW_TOKENS = 600

def _chat_text(messages):
    # Qwen3 permite desactivar thinking explícito.
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

def extract_json(text):
    text = str(text).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    if "</think>" in text:
        text = text.split("</think>", 1)[1].strip()

    start = text.find("{")
    if start < 0:
        raise ValueError("No se encontró inicio de JSON.")

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i+1])

    raise ValueError("JSON incompleto.")

def validate_parsed(item, parsed):
    if not isinstance(parsed, dict):
        raise ValueError("La respuesta parseada no es un objeto.")

    if "has_formulation" not in parsed:
        raise ValueError("Falta has_formulation.")

    reqs = parsed.get("requirements")
    if not isinstance(reqs, dict):
        raise ValueError("requirements debe ser un objeto {R1: estado, ...}.")

    expected = {r["id"] for r in item["requirements"]}
    got = set(reqs)

    if expected != got:
        raise ValueError(
            f"IDs de requisitos incorrectos. Esperados={expected}; recibidos={got}"
        )

    allowed = {"met", "partial", "missing", "wrong"}
    bad_status = {
        rid: status
        for rid, status in reqs.items()
        if str(status).lower().strip() not in allowed
    }
    if bad_status:
        raise ValueError(f"Estados inválidos: {bad_status}")

    scores = parsed.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("Falta scores.")

    for dim in DIMENSIONS:
        if dim not in scores:
            raise ValueError(f"Falta score: {dim}")
        value = float(scores[dim])
        if not (0 <= value <= 5):
            raise ValueError(f"Score fuera de rango en {dim}: {value}")

    if "fatal_errors" not in parsed:
        parsed["fatal_errors"] = []

    return parsed

@torch.inference_mode()
def judge_local(item, candidate, max_retries=2):
    prompt = judge_prompt(item, candidate)
    messages = [
        {"role": "system", "content": SYSTEM_JUDGE},
        {"role": "user", "content": prompt},
    ]

    last_error = None
    last_raw = None

    for attempt in range(max_retries):
        local_messages = list(messages)
        if attempt > 0:
            local_messages.append({
                "role": "user",
                "content": (
                    "La salida anterior no pudo parsearse. "
                    "Repite el mismo juicio y devuelve SOLO el JSON solicitado, "
                    "completo y sin texto adicional."
                ),
            })

        text = _chat_text(local_messages)
        inputs = tokenizer(text, return_tensors="pt", add_special_tokens=False)

        n_input = int(inputs["input_ids"].shape[1])
        if n_input > MAX_INPUT_TOKENS:
            raise ValueError(
                f"Prompt de {n_input} tokens supera MAX_INPUT_TOKENS={MAX_INPUT_TOKENS}. "
                "No se truncó silenciosamente."
            )

        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        try:
            output = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

            generated = output[0, inputs["input_ids"].shape[1]:]
            raw = tokenizer.decode(generated, skip_special_tokens=True).strip()
            last_raw = raw

            parsed = validate_parsed(item, extract_json(raw))
            return parsed, raw, n_input, int(generated.shape[0])

        except Exception as e:
            last_error = str(e)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    raise RuntimeError(
        f"Judge local falló tras {max_retries} intentos: {last_error}\n"
        f"Última salida: {last_raw}"
    )

STATUS_VALUE = {
    "met": 1.0,
    "partial": 0.5,
    "missing": 0.0,
    "wrong": 0.0,
}

def safe_score(value):
    return max(0.0, min(5.0, float(value)))

def aggregate_v2(item, parsed):
    status = {
        rid: STATUS_VALUE[str(st).lower().strip()]
        for rid, st in parsed["requirements"].items()
    }

    by_kind = {"objective": [], "constraint": [], "domain": []}

    for req in item["requirements"]:
        by_kind[req["kind"]].append(
            status.get(req["id"], 0.0)
        )

    obj_cov = np.mean(by_kind["objective"]) if by_kind["objective"] else 1.0
    con_cov = np.mean(by_kind["constraint"]) if by_kind["constraint"] else 1.0
    dom_cov = np.mean(by_kind["domain"]) if by_kind["domain"] else 1.0

    raw = parsed["scores"]

    decision = safe_score(raw["decision_domains"])
    objective = min(safe_score(raw["objective"]), 5.0 * obj_cov)
    constraints = min(safe_score(raw["constraints_logic"]), 5.0 * con_cov)
    algebra = safe_score(raw["algebra_validity"])
    generalization = safe_score(raw["generalization"])

    if by_kind["domain"]:
        decision = min(decision, 5.0 * dom_cov)

    score = (
        0.15 * decision
        + 0.20 * objective
        + 0.35 * constraints
        + 0.15 * algebra
        + 0.15 * generalization
    )

    if not bool(parsed["has_formulation"]):
        algebra = min(algebra, 1.0)
        generalization = min(generalization, 1.0)

        score = min(
            1.5,
            0.15 * decision
            + 0.20 * objective
            + 0.35 * constraints
            + 0.15 * algebra
            + 0.15 * generalization
        )

    all_cov = np.mean(list(status.values())) if status else np.nan

    return {
        "score_fom5_v2": round(float(score), 3),
        "decision_domains_v2": float(decision),
        "objective_v2": float(objective),
        "constraints_logic_v2": float(constraints),
        "algebra_validity_v2": float(algebra),
        "generalization_v2": float(generalization),
        "requirement_coverage_v2": float(all_cov),
        "objective_coverage": float(obj_cov),
        "constraint_coverage": float(con_cov),
        "domain_coverage": float(dom_cov),
    }

