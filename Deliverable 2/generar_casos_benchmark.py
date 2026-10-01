# Genera casos_benchmark.md desde data/benchmark_30.jsonl y output/*.csv.
# Uso, desde la carpeta "Deliverable 2":  python generar_casos_benchmark.py .
import json, csv, re, sys
from pathlib import Path
csv.field_size_limit(10**9)
D = sys.argv[1]
bench = [json.loads(l) for l in open(f"{D}/data/benchmark_30.jsonl", encoding="utf-8")]
def cargar(f):
    return {r["id"]: r for r in csv.DictReader(open(f, encoding="utf-8-sig"))}
base = cargar(f"{D}/output/baseline_respuestas_fom5.csv")
qlo = cargar(f"{D}/output/qlora_respuestas_fom5.csv")
ESTADO = {"met": "cumple", "partial": "parcial", "missing": "ausente", "wrong": "incorrecto"}

def req_estados(row):
    try:
        return json.loads(row["judge_v2_raw"]).get("requirements", {})
    except Exception:
        m = re.search(r"\{.*\}", row.get("judge_v2_raw", ""), re.S)
        try:
            return json.loads(m.group(0)).get("requirements", {}) if m else {}
        except Exception:
            return {}

def fatales(row):
    try:
        v = json.loads(row.get("fatal_errors_v2") or "[]")
        return v if isinstance(v, list) else [str(v)]
    except Exception:
        return [row.get("fatal_errors_v2", "")] if row.get("fatal_errors_v2") else []

def f(x): return float(x)
def ancla(i): return i
def veredicto(d): return "mejora" if d > 0 else ("empeora" if d < 0 else "igual")

filas = []
for b in bench:
    sb, sq = f(base[b["id"]]["score_fom5_v2"]), f(qlo[b["id"]]["score_fom5_v2"])
    filas.append((b, sb, sq, sq - sb))

mb = sum(x[1] for x in filas) / 30; mq = sum(x[2] for x in filas) / 30
n_m = sum(x[3] > 0 for x in filas); n_i = sum(x[3] == 0 for x in filas); n_e = sum(x[3] < 0 for x in filas)

out = []
out.append("# Casos del benchmark: enunciado, respuestas y puntaje\n")
out.append("Este archivo permite revisar, problema por problema, qué recibió el modelo, qué respondió con y sin QLoRA y cómo lo evaluó el juez FOM-5 v2. "
           "Se genera a partir de [`data/benchmark_30.jsonl`](data/benchmark_30.jsonl) y de los CSV de [`output/`](output/). "
           "Los CSV conservan las respuestas originales; esta vista normaliza espacios finales y delimitadores de código para mantener legible el Markdown.\n")
out.append("- **Baseline:** Qwen2.5-1.5B-Instruct con prompting directo (adapter apagado).")
out.append("- **QLoRA:** el mismo modelo con el adapter entrenado.")
out.append("- **Puntaje:** FOM-5 v2, de 0 a 5. Ambos generadores recibieron solo el enunciado; la referencia y los requisitos se usaron únicamente en la evaluación.")
out.append(f"**Resumen de los 30 casos:** media {mb:.2f} → {mq:.2f} · {n_m} mejoran, {n_i} quedan igual, {n_e} empeoran. "
           "El caso de la Entrega 1 aparece al final, fuera de la media.\n")
out.append("## Índice\n")
out.append("| ID | Problema | Tipo | Baseline | QLoRA | Cambio |")
out.append("|---|---|:---:|---:|---:|---|")
for b, sb, sq, d in filas:
    out.append(f"| [{b['id']}](#{ancla(b['id'])}) | {b['title']} | {b.get('model_class','')} | {sb:.2f} | {sq:.2f} | {veredicto(d)} ({d:+.2f}) |")
diag_b, diag_q = base.get("diagnostic_oftalmo"), qlo.get("diagnostic_oftalmo")
if diag_b and diag_q:
    out.append(f"| [diagnóstico](#diagnostico-oftalmo) | Centros oftalmológicos (Entrega 1) | MILP | {f(diag_b['score_fom5_v2']):.2f} | {f(diag_q['score_fom5_v2']):.2f} | fuera de la media |")
out.append("")

def bloque(titulo, row, reqs_def):
    s = []
    s.append(f"**{titulo} — {f(row['score_fom5_v2']):.2f}/5** "
             f"(decisiones {row['decision_domains_v2']}, objetivo {row['objective_v2']}, restricciones {row['constraints_logic_v2']}, "
             f"álgebra {row['algebra_validity_v2']}, generalización {row['generalization_v2']})\n")
    s.append("<details><summary>Ver respuesta</summary>\n")
    candidate = "\n".join(line.rstrip() for line in row["candidate"].strip().splitlines())
    s.append("```text\n" + candidate.replace("```", "ˋˋˋ") + "\n```\n")
    s.append("</details>\n")
    return s

for b, sb, sq, d in filas:
    out.append(f"---\n\n## {b['id']}\n")
    out.append(f"### {b['title']}\n")
    out.append(f"Tipo: {b.get('model_class','')} · Dificultad: {b.get('difficulty','')} · Baseline **{sb:.2f}** → QLoRA **{sq:.2f}** ({veredicto(d)})\n")
    out.append("**Enunciado**\n")
    parrafos = [" ".join(x.split()) for x in re.split(r"\n\s*\n", b["problem"].strip())]
    out.append("> " + "\n>\n> ".join(parrafos) + "\n")
    eb, eq = req_estados(base[b["id"]]), req_estados(qlo[b["id"]])
    out.append("**Requisitos y cumplimiento según el juez**\n")
    out.append("| Req. | Tipo | Requisito | Baseline | QLoRA |")
    out.append("|---|---|---|---|---|")
    for r in b["requirements"]:
        out.append(f"| {r['id']} | {r['kind']} | {r['text']} | {ESTADO.get(eb.get(r['id']), eb.get(r['id'],'—'))} | {ESTADO.get(eq.get(r['id']), eq.get(r['id'],'—'))} |")
    out.append("")
    out.append("<details><summary>Formulación de referencia</summary>\n")
    reference = "\n".join(line.rstrip() for line in b["reference_model"].strip().splitlines())
    out.append(reference + "\n")
    out.append("</details>\n")
    out += bloque("Baseline", base[b["id"]], b["requirements"])
    out += bloque("QLoRA", qlo[b["id"]], b["requirements"])
    fq = [x for x in fatales(qlo[b["id"]]) if x]
    if fq:
        out.append("Observación del juez sobre QLoRA: " + " ".join(fq) + "\n")

if diag_b and diag_q:
    out.append("---\n\n## diagnostico-oftalmo\n")
    out.append("### Centros oftalmológicos (caso de la Entrega 1, fuera de la media)\n")
    out.append("Es el caso que motivó el proyecto. Se reporta aparte porque se conocía antes del entrenamiento y porque las familias de localización están en los datos de entrenamiento.\n")
    out += bloque("Baseline", diag_b, [])
    out += bloque("QLoRA", diag_q, [])

Path(f"{D}/casos_benchmark.md").write_bytes(("\n".join(out).rstrip("\n") + "\n").encode("utf-8"))
print("ok", len(out), "líneas")
