"""Datos del evaluador, archivos archivados y contrato de salidas de generación."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from eval.legacy import load_kernel
from schemas import RunResult

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
VARIANTS = ("full", "no_evidence", "no_plan", "no_audit", "no_review")
PUBLISHED_HASHES = {
    "data/benchmark_30.jsonl": "c3d6ffff05a2b3b14ef21bb989d8cf23704af0be0ee8226bd149acee5915a834",
    "output/baseline_respuestas_fom5.csv": "17d9c5422af2ec014c65a82888759c7aba35f3a1dd7c31a0fcae8fb981c56bf7",
    "output/qlora_respuestas_fom5.csv": "c4adc2089f952a83c0692f5c7bc91841706616ae0d7b2c1d65abb59e6c2a9706",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return parse_jsonl(Path(path).read_text(encoding="utf-8"), str(path))


def parse_jsonl(text: str, source: str) -> list[dict]:
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            raise ValueError(f"{source}:{number}: línea vacía o checkpoint incompleto")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{source}:{number}: JSON incompleto o inválido") from error
        if not isinstance(record, dict):
            raise ValueError(f"{source}:{number}: se requiere un objeto JSON")
        rows.append(record)
    return rows


def by_id(rows, key="id"):
    result = {}
    for number, row in enumerate(rows, 1):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"Fila {number}: falta {key} o no es un identificador válido")
        identifier = row[key]
        if identifier in result:
            raise ValueError(f"ID duplicado: {identifier}")
        result[identifier] = row
    return result


def load_published(deliverable2: Path = REPO / "Deliverable 2"):
    deliverable2 = Path(deliverable2)
    for relative, expected in PUBLISHED_HASHES.items():
        if sha256(deliverable2 / relative) != expected:
            raise ValueError(f"El archivo publicado cambió: {relative}")
    gold = by_id(read_jsonl(deliverable2 / "data/benchmark_30.jsonl"))
    if set(gold) != {f"opt_{i:02}" for i in range(1, 31)}:
        raise ValueError("El benchmark publicado debe contener sus 30 IDs oficiales")
    archived = {}
    kernel = load_kernel()
    for label, filename in (("baseline", "baseline_respuestas_fom5.csv"), ("QLoRA", "qlora_respuestas_fom5.csv")):
        with (deliverable2 / "output" / filename).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        selected = by_id([r for r in rows if r["split"] == "benchmark"])
        if set(selected) != set(gold):
            raise ValueError(f"IDs archivados incompatibles: {label}")
        for identifier, row in selected.items():
            problem_hash = hashlib.sha256(gold[identifier]["problem"].encode()).hexdigest()
            if row["problem_sha256"] != problem_hash:
                raise ValueError(f"Enunciado archivado incompatible: {identifier}")
            parsed = kernel.validate_parsed(gold[identifier], kernel.extract_json(row["judge_v2_raw"]))
            scores = kernel.aggregate_v2(gold[identifier], parsed)
            if any(abs(float(row[k]) - value) > 1e-9 for k, value in scores.items()):
                raise ValueError(f"La agregación archivada no se reproduce: {label}/{identifier}")
        archived[label] = selected
    return gold, archived


def load_development(root: Path = ROOT):
    inputs = by_id(read_jsonl(root / "dev_cases/inputs.jsonl"))
    references = by_id(read_jsonl(root / "dev_cases/reference/dev_reference.jsonl"))
    expected = {f"dev{i:02}" for i in range(1, 9)}
    if set(inputs) != expected or set(references) != expected:
        raise ValueError("Se requieren los ocho casos de desarrollo")
    return {key: dict(references[key], **inputs[key]) for key in sorted(expected)}


def input_hash(items) -> str:
    return canonical_hash([{k: items[i][k] for k in ("id", "title", "problem")} for i in sorted(items)])


def load_predictions(path: Path, variant: str, items):
    if variant not in VARIANTS:
        raise ValueError(f"Variante desconocida: {variant}")
    results = [RunResult.model_validate(row) for row in read_jsonl(path)]
    if any(not math.isfinite(r.latency_ms_total) for r in results):
        raise ValueError("Las métricas de generación deben ser finitas")
    mapped = by_id([r.model_dump(mode="json") for r in results], "problem_id")
    if set(mapped) != set(items) or any(r.variant != variant for r in results):
        raise ValueError(f"{variant}: faltan IDs, sobran IDs o hay variantes mezcladas")
    return mapped
