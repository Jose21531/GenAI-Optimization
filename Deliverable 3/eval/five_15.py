"""FOM-5 v2: cinco variantes sobre los primeros 15 casos del benchmark.

Conserva el juez, la calibración y la agregación originales. Las comparaciones
con baseline y Entrega 2 usan los mismos 15 IDs y respuestas archivadas.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.artifacts import (REPO, VARIANTS, canonical_hash, load_predictions,
                            load_published, read_jsonl, sha256)
from eval.judge import QwenFOM5Judge, load_qwen3
from eval.legacy import (CALIBRATION_SHA256, JUDGE_MODEL, JUDGE_REVISION,
                         KERNEL_SHA256)
from eval.pipeline import (_append, _base_record, _calibrate, _checkpoint,
                           _judge, _write_json)
from eval.statistics import paired_difference
from model import ADAPTER_SHA256, sha256_file
from run import _identity, load_cases


def parse_sources(values: list[str]) -> dict[str, Path]:
    sources = {}
    for value in values:
        name, sep, filename = value.partition("=")
        if not sep or name not in VARIANTS or name in sources or not filename:
            raise ValueError("Usa --source variante=ruta para cada una de las cinco variantes")
        sources[name] = Path(filename)
    if set(sources) != set(VARIANTS):
        raise ValueError("Faltan variantes: se requieren full y cuatro ablaciones")
    return sources


def prepare(sources: dict[str, Path]):
    cases = load_cases("official")
    gold, archived = load_published()
    if set(cases) != set(gold) or any(cases[i]["problem"] != gold[i]["problem"] for i in cases):
        raise ValueError("Los enunciados de generación no coinciden con los del evaluador")
    adapter = REPO / "Deliverable 2/adapter_qlora_qwen25_final.zip"
    if sha256_file(adapter) != ADAPTER_SHA256:
        raise ValueError("El adapter público cambió")
    identity = _identity("official", cases, adapter)
    first15 = {f"opt_{n:02}" for n in range(1, 16)}
    predictions, input_hashes = {}, {}
    for variant, path in sources.items():
        items = {i: gold[i] for i in sorted(first15)}
        predictions[variant] = load_predictions(path, variant, items)
        actual_identity = json.loads((path.parent / "generation.json").read_text(encoding="utf-8"))
        if actual_identity != identity:
            raise ValueError(f"Identidad de generación incompatible: {variant}")
        subset_manifest = json.loads((path.parent / "subset_manifest.json").read_text(encoding="utf-8"))
        if subset_manifest != {"design": "five_variants_first15", "variant": variant,
                               "ids": sorted(first15), "outputs_sha256": sha256(path),
                               "generation_identity": identity}:
            raise ValueError(f"Manifiesto del subconjunto incompatible: {variant}")
        input_hashes[variant] = sha256(path)
    return cases, gold, archived, predictions, input_hashes


def write_scores(path: Path, records: dict[str, dict]):
    rows = [dict(records[i]) for i in sorted(records)]
    for row in rows:
        row["fatal_errors_v2"] = json.dumps(row["fatal_errors_v2"], ensure_ascii=False)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_summary(scored, archived):
    scores = {name: {i: float(row["score_fom5_v2"]) for i, row in records.items()}
              for name, records in scored.items()}
    baseline = {i: float(row["score_fom5_v2"]) for i, row in archived["baseline"].items()}
    qlora = {i: float(row["score_fom5_v2"]) for i, row in archived["QLoRA"].items()}
    first15 = {f"opt_{n:02}" for n in range(1, 16)}
    baseline15 = {i: baseline[i] for i in first15}
    qlora15 = {i: qlora[i] for i in first15}
    full15 = scores["full"]
    summary = {
        "design": "five_variants_first15",
        "n": 15,
        "ids": sorted(first15),
        "judge": "FOM-5 v2 / Qwen3-14B",
        "valid_real_judge": True,
        "archived_first15": {"baseline_mean": sum(baseline15.values()) / 15,
                             "qlora_mean": sum(qlora15.values()) / 15},
        "archived_30": {"baseline_mean": sum(baseline.values()) / 30,
                        "qlora_mean": sum(qlora.values()) / 30},
        "variants": {},
    }
    for variant in VARIANTS:
        records = scored[variant]
        summary.setdefault("cost", {})[variant] = {
            "n": len(records),
            "generation_statuses": {status: sum(row["generation_status"] == status
                                                 for row in records.values())
                                    for status in sorted({row["generation_status"]
                                                          for row in records.values()})},
            "empty_candidates": sum(not row["candidate"].strip() for row in records.values()),
            "tokens_total": sum(row["tokens_total"] for row in records.values()),
            "latency_sec_total": sum(row["latency_ms_total"] for row in records.values()) / 1000,
            "judge_tokens": sum(row["judge_input_tokens"] + row["judge_output_tokens"]
                                for row in records.values()),
        }
        summary["variants"][variant] = {
            "n": 15,
            "mean": sum(scores[variant].values()) / 15,
            "vs_baseline": paired_difference(scores[variant], baseline15),
            "vs_qlora": paired_difference(scores[variant], qlora15),
        }
        if variant != "full":
            summary["variants"][variant]["vs_full"] = paired_difference(scores[variant], full15)
    return summary


def evaluate(sources: dict[str, Path], output: Path):
    _, gold, archived, predictions, hashes = prepare(sources)
    judge = load_qwen3()
    if not isinstance(judge, QwenFOM5Judge) or judge.kind != "real" or \
            judge.model_id != JUDGE_MODEL or judge.revision != JUDGE_REVISION:
        raise ValueError("La medición exige el juez Qwen3 real y su revisión original")
    metadata = {"design": "five_variants_first15", "sources_sha256": hashes,
                "judge": JUDGE_MODEL, "judge_revision": JUDGE_REVISION,
                "kernel_sha256": KERNEL_SHA256,
                "calibration_sha256": CALIBRATION_SHA256,
                "generation_identity": json.loads((sources["full"].parent / "generation.json").read_text(encoding="utf-8"))}
    identity = canonical_hash(metadata)
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "evaluation.json"
    if manifest.exists():
        if json.loads(manifest.read_text(encoding="utf-8"))["identity"] != identity:
            raise ValueError("El directorio pertenece a otra medición")
    elif any(output.iterdir()):
        raise ValueError("El directorio de evaluación no está vacío ni tiene identidad")
    scored = {}
    for variant in VARIANTS:
        items = {i: gold[i] for i in predictions[variant]}
        scored[variant] = _checkpoint(output / variant / "judgments.jsonl", variant,
                                      predictions[variant], items, identity)
    _write_json(manifest, {"identity": identity, "metadata": metadata, "status": "running"})
    calls = output / "judge_calls.jsonl"
    calibration = output / f"calibration-{uuid4().hex}.jsonl"
    try:
        _calibrate(judge, gold, archived, calibration, calls, identity)
        for variant in VARIANTS:
            folder = output / variant
            folder.mkdir(exist_ok=True)
            for identifier in sorted(predictions[variant]):
                if identifier in scored[variant]:
                    continue
                generation = predictions[variant][identifier]
                reply, parsed, scores = _judge(judge, gold[identifier], generation["final_text"],
                                               calls, {"phase": "evaluation", "id": identifier,
                                                       "variant": variant, "identity": identity})
                record = _base_record(variant, identifier, generation, identity)
                record.update(scores)
                record.update(judge_v2_raw=reply.raw, judge_model=judge.model_id,
                              judge_input_tokens=reply.input_tokens,
                              judge_output_tokens=reply.output_tokens,
                              judge_latency_sec=reply.latency_sec,
                              fatal_errors_v2=parsed.get("fatal_errors", []),
                              execution_kind=judge.kind)
                _append(folder / "judgments.jsonl", record)
                scored[variant][identifier] = record
            write_scores(folder / "scored.csv", scored[variant])
        summary = make_summary(scored, archived)
        summary.update(identity=identity, source_sha256=hashes)
        _write_json(output / "summary.json", summary)
        _write_json(manifest, {"identity": identity, "metadata": metadata, "status": "complete"})
        return summary
    except Exception as error:
        _write_json(manifest, {"identity": identity, "metadata": metadata,
                               "status": "failed", "error": str(error)})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = evaluate(parse_sources(args.source), args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
