"""Puntúa por separado el caso de centros oftalmológicos con FOM-5 v2."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from eval.artifacts import REPO, ROOT, load_published
from eval.judge import load_qwen3
from eval.legacy import calibration_spec, load_kernel

DIAGNOSTIC_ID = "diagnostic_oftalmo"
GOLD_PATH = ROOT / "data/diagnostic_oftalmo_gold.json"


def archived_diagnostic():
    """Devuelve las dos respuestas archivadas después de verificar Entrega 2."""
    load_published()
    result = {}
    for label, filename in (("baseline", "baseline_respuestas_fom5.csv"),
                            ("QLoRA", "qlora_respuestas_fom5.csv")):
        with (REPO / "Deliverable 2/output" / filename).open(encoding="utf-8-sig", newline="") as stream:
            selected = [row for row in csv.DictReader(stream) if row["id"] == DIAGNOSTIC_ID
                        and row["split"] == "diagnostic"]
        if len(selected) != 1:
            raise ValueError(f"Falta la fila diagnóstica archivada: {label}")
        result[label] = selected[0]
    return result


def diagnostic_gold():
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    if gold["id"] != DIAGNOSTIC_ID or len(gold["requirements"]) != 6:
        raise ValueError("Gold diagnóstico incompatible")
    archived = archived_diagnostic()
    problem_hash = hashlib.sha256(gold["problem"].encode()).hexdigest()
    if any(row["problem_sha256"] != problem_hash for row in archived.values()):
        raise ValueError("El enunciado diagnóstico no corresponde a Entrega 2")
    return gold, archived


def evaluate_diagnostic(candidate: str, output: Path, *, judge=None):
    """Calibra el juez original y guarda su juicio sin sumar el caso a los 30."""
    if not isinstance(candidate, str) or not candidate.strip():
        raise ValueError("Se requiere una formulación no vacía")
    output = Path(output)
    candidate_hash = hashlib.sha256(candidate.encode()).hexdigest()
    if output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing.get("candidate_sha256") != candidate_hash:
            raise ValueError("El resultado guardado corresponde a otra formulación")
        return existing
    gold, archived = diagnostic_gold()
    official, published = load_published()
    judge = judge or load_qwen3()
    kernel = load_kernel()
    calibration = []
    for identifier, variant, maximum in calibration_spec():
        source = published["baseline"][identifier]
        if source["variant"] != variant:
            raise ValueError("La respuesta de calibración no coincide con la publicada")
        reply = judge.judge(official[identifier], source["candidate"])
        parsed = kernel.validate_parsed(official[identifier], kernel.extract_json(reply.raw))
        score = kernel.aggregate_v2(official[identifier], parsed)["score_fom5_v2"]
        calibration.append({"id": identifier, "score": score, "maximum": maximum,
                            "passes": score <= maximum, "judge_v2_raw": reply.raw})
    if not all(row["passes"] for row in calibration):
        raise ValueError("Calibración FOM-5 v2 fallida")
    reply = judge.judge(gold, candidate)
    parsed = kernel.validate_parsed(gold, kernel.extract_json(reply.raw))
    scores = kernel.aggregate_v2(gold, parsed)
    payload = {
        "id": DIAGNOSTIC_ID,
        "scope": "diagnostic; excluded from the official 30-case mean",
        "execution_kind": judge.kind,
        "valid_experiment": judge.kind == "real",
        "judge_model": judge.model_id,
        "judge_revision": judge.revision,
        "candidate_sha256": candidate_hash,
        "candidate": candidate,
        "baseline_archived": float(archived["baseline"]["score_fom5_v2"]),
        "qlora_archived": float(archived["QLoRA"]["score_fom5_v2"]),
        "scores": scores,
        "judge_v2_raw": reply.raw,
        "calibration": calibration,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return payload
