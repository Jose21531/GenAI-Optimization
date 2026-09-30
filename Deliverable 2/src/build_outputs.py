"""Consolida respuestas y juicios congelados en dos CSV comparables.

El baseline oficial se recupera del CSV recibido; nunca se vuelve a ejecutar aquí.
La salida QLoRA corresponde a la corrida final sobre los mismos 30 casos y el
diagnóstico separado. Este script no invoca un modelo ni modifica un juicio.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = ROOT / "outputs"
DATA = ROOT / "data"
FIELDS = [
    "id", "title", "split", "variant", "model", "source", "problem_sha256",
    "candidate", "score_fom5_v2", "decision_domains_v2", "objective_v2",
    "constraints_logic_v2", "algebra_validity_v2", "generalization_v2",
    "requirement_coverage_v2", "objective_coverage", "constraint_coverage",
    "domain_coverage", "fatal_errors_v2", "judge_v2_raw", "judge_model",
    "prompt_tokens", "output_tokens", "latency_sec", "judge_input_tokens",
    "judge_output_tokens", "judge_latency_sec",
]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in FIELDS} for row in rows)


def main() -> None:
    problems = {}
    for name in ("benchmark_30_generation_only.jsonl", "caso_entrega1_generation_only.jsonl"):
        for line in (DATA / name).read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            assert item["id"] not in problems
            problems[item["id"]] = item
    assert len(problems) == 31

    base_source = read_csv(EVIDENCE / "resultados_fom5_local_original.csv")
    base = [row for row in base_source if row["variant"] == "baseline_direct_deterministic"
            and row["split"] in {"benchmark", "diagnostic"}]
    assert len(base) == 31 and len({row["id"] for row in base}) == 31
    assert sum(row["split"] == "benchmark" for row in base) == 30
    assert abs(sum(float(row["score_fom5_v2"]) for row in base if row["split"] == "benchmark") / 30 - .5884) < 1e-10

    improved = read_csv(EVIDENCE / "qlora_fom5_v2_final_original.csv")
    assert len(improved) == 31 and {row["variant"] for row in improved} == {"qlora_final"}
    assert {row["id"] for row in improved} == {row["id"] for row in base} == set(problems)
    for rows, source in ((base, "baseline_oficial_congelado"), (improved, "qlora_final_run01")):
        for row in rows:
            assert row["candidate"].strip() and row["judge_v2_raw"].strip()
            assert not row.get("judge_v2_error")
            digest = hashlib.sha256(problems[row["id"]]["problem"].encode()).hexdigest()
            if row.get("problem_sha256"):
                assert row["problem_sha256"] == digest
            row["problem_sha256"] = digest
            row["source"] = source
    assert abs(sum(float(row["score_fom5_v2"]) for row in improved if row["split"] == "benchmark") / 30 - .8023666666666667) < 1e-10
    OUT.mkdir(exist_ok=True)
    write_csv(OUT / "baseline_31_respuestas_y_fom5.csv", base)
    write_csv(OUT / "qlora_31_respuestas_y_fom5.csv", improved)
    print("Exportados 30 benchmark + 1 diagnóstico en cada variante; scores preservados.")


if __name__ == "__main__":
    main()
