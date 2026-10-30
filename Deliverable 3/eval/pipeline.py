"""Evaluación posterior con calibración fija, checkpoints y comparación pareada."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from uuid import uuid4

import numpy as np

from eval.artifacts import (PUBLISHED_HASHES, REPO, ROOT, VARIANTS, by_id, canonical_hash, input_hash,
                            load_development, load_predictions, load_published, read_jsonl)
from eval.judge import JudgeFailure, QwenFOM5Judge, load_qwen3
from eval.legacy import (CALIBRATION_SHA256, JUDGE_MODEL, JUDGE_REVISION,
                         KERNEL_SHA256, calibration_spec, load_kernel, text_bytes)
from eval.provenance import verify_generation_manifest
from eval.statistics import summarize


def _write_json(path, value):
    temporary = Path(str(path) + ".tmp-" + uuid4().hex)
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _append(path, value):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()


def load_items(mode, *, root=ROOT, deliverable2=REPO / "Deliverable 2"):
    official, archived = load_published(deliverable2)
    if mode == "official":
        # Comprobar que los textos de generación coinciden con el benchmark.
        inputs = by_id(read_jsonl(root / "data/benchmark_30_generation_only.jsonl"))
        if any(set(row) != {"id", "title", "problem"} for row in inputs.values()):
            raise ValueError("Las entradas de generación deben contener solo id, title y problem")
        if input_hash(inputs) != input_hash(official):
            raise ValueError("Los enunciados de generación no corresponden al benchmark publicado")
        return official, official, archived
    if mode != "development":
        raise ValueError("Modo desconocido")
    return load_development(root), official, archived


def prepare(sources, *, mode, root=ROOT, deliverable2=REPO / "Deliverable 2"):
    if not sources or any(v not in VARIANTS for v in sources):
        raise ValueError("Se requieren variantes conocidas sin nombres arbitrarios")
    if mode == "official" and set(sources) != set(VARIANTS):
        raise ValueError("La evaluación oficial requiere las cinco variantes completas")
    items, official, archived = load_items(mode, root=root, deliverable2=deliverable2)
    manifests, predictions = {}, {}
    for variant in sorted(sources):
        path = Path(sources[variant])
        manifests[variant] = verify_generation_manifest(path, variant, items, mode=mode, root=root)
        predictions[variant] = load_predictions(path, variant, items)
    return items, official, archived, manifests, predictions


def _judge(judge, item, candidate, calls, context):
    try:
        reply = judge.judge(item, candidate)
    except JudgeFailure as error:
        _append(calls, dict(context, error=str(error), attempts=error.attempts))
        raise
    except Exception as error:
        _append(calls, dict(context, error=str(error)))
        raise
    _append(calls, dict(context, raw=reply.raw, attempts=reply.attempts,
                        input_tokens=reply.input_tokens, output_tokens=reply.output_tokens,
                        latency_sec=reply.latency_sec))
    kernel = load_kernel()
    # Los puntajes se calculan desde el JSON crudo, no desde un score del backend.
    parsed = kernel.validate_parsed(item, kernel.extract_json(reply.raw))
    if parsed != reply.parsed:
        raise ValueError("El JSON crudo y el juicio parseado no coinciden")
    return reply, parsed, kernel.aggregate_v2(item, parsed)


def _calibrate(judge, official, archived, destination, calls, identity):
    results = []
    for identifier, variant, maximum in calibration_spec():
        row = archived["baseline"][identifier]
        if row["variant"] != variant:
            raise ValueError("La respuesta archivada de calibración no corresponde a la original")
        reply, parsed, scores = _judge(judge, official[identifier], row["candidate"], calls,
                                      {"phase": "calibration", "id": identifier, "identity": identity})
        record = {"id": identifier, "variant": variant, "score": scores["score_fom5_v2"],
                  "maximum": maximum, "passes": scores["score_fom5_v2"] <= maximum,
                  "judge_v2_raw": reply.raw, "execution_kind": judge.kind}
        _append(destination, record)
        results.append(record)
    if not all(r["passes"] for r in results):
        raise ValueError("Calibración FOM-5 v2 fallida; se detuvo antes de evaluar candidatos nuevos")
    return results


def _base_record(variant, identifier, generation, identity):
    return {"id": identifier, "variant": variant, "evaluation_identity": identity,
            "candidate": generation["final_text"],
            "candidate_sha256": hashlib.sha256(generation["final_text"].encode()).hexdigest(),
            "generation_status": generation["status"],
            "rounds": generation["rounds"], "clarifications": generation["clarifications"],
            "tool_calls": generation["tool_calls"], "tokens_total": generation["tokens_total"],
            "latency_ms_total": generation["latency_ms_total"]}


def _checkpoint(path, variant, predictions, items, identity):
    rows = by_id(read_jsonl(path)) if path.exists() else {}
    kernel = load_kernel()
    for identifier, row in rows.items():
        if identifier not in items:
            raise ValueError("El checkpoint contiene un ID ajeno a esta evaluación")
        expected = _base_record(variant, identifier, predictions[identifier], identity)
        if any(row.get(k) != v for k, v in expected.items()):
            raise ValueError("Checkpoint incompatible con variante, candidate, configuración o identidad")
        parsed = kernel.validate_parsed(items[identifier], kernel.extract_json(row["judge_v2_raw"]))
        scores = kernel.aggregate_v2(items[identifier], parsed)
        if any(row.get(k) != v for k, v in scores.items()):
            raise ValueError("Los puntajes del checkpoint no coinciden con el juicio original")
    return rows


def evaluate(sources, output: Path, *, mode="development", judge=None,
             root=ROOT, deliverable2=REPO / "Deliverable 2"):
    """Evalúa todos los IDs, incluso salidas de generación fallidas o vacías.

    Nunca atribuye cero a un fallo del juez: conserva el checkpoint y propaga
    el fallo. Un backend mock solo se admite en desarrollo y queda rotulado.
    """
    items, official, archived, manifests, predictions = prepare(
        sources, mode=mode, root=root, deliverable2=deliverable2)
    if judge is not None and mode == "official" and (not isinstance(judge, QwenFOM5Judge) or judge.kind != "real"):
        raise ValueError("Una evaluación oficial exige el juez Qwen3 real; no admite MockJudge")
    judge = judge or load_qwen3()
    if judge.kind not in {"real", "mock"}:
        raise ValueError("Backend de evaluación desconocido")
    if judge.kind == "real" and (not isinstance(judge, QwenFOM5Judge)
                                 or judge.model_id != JUDGE_MODEL or judge.revision != JUDGE_REVISION):
        raise ValueError("La evaluación real debe usar el juez Qwen3 y su revisión publicados")
    metadata = {"schema_version": 1, "mode": mode, "execution_kind": judge.kind,
                "judge_model": judge.model_id, "judge_revision": judge.revision,
                "kernel_sha256": KERNEL_SHA256, "calibration_sha256": CALIBRATION_SHA256,
                "published_artifacts": PUBLISHED_HASHES,
                "evaluation_sources": {p.name: hashlib.sha256(text_bytes(p)).hexdigest()
                                       for p in sorted(Path(__file__).parent.glob("*.py"))},
                "protocol": {"max_input_tokens": 12000, "max_new_tokens": 600, "do_sample": False,
                             "attempts": 2, "enable_thinking": False},
                "inputs_sha256": input_hash(items), "sources": manifests,
                "runtime": {"python": sys.version.split()[0], "numpy": np.__version__,
                            "backend": getattr(judge, "runtime", {})},
                "expected_ids": sorted(items), "variants": sorted(sources)}
    identity = canonical_hash(metadata)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest_file = output / "evaluation.json"
    if manifest_file.exists():
        existing = json.loads(manifest_file.read_text(encoding="utf-8"))
        if existing.get("identity") != identity or existing.get("metadata") != metadata:
            raise ValueError("Este directorio pertenece a otra evaluación; no se reutilizan sus juicios")
    elif any(output.iterdir()):
        raise ValueError("El directorio de evaluación contiene archivos sin manifiesto")
    scored = {}
    # Validar todos los checkpoints antes de cualquier llamada de juez.
    for variant in sorted(sources):
        folder = output / variant
        scored[variant] = _checkpoint(folder / "judgments.jsonl", variant, predictions[variant], items, identity)
    _write_json(manifest_file, {"identity": identity, "metadata": metadata, "status": "running"})
    calls = output / "judge_calls.jsonl"
    calibration_file = output / f"calibration-{uuid4().hex}.jsonl"
    try:
        # Como en Entrega 2, la calibración vuelve a ejecutarse al reanudar.
        _calibrate(judge, official, archived, calibration_file, calls, identity)
        for variant in sorted(sources):
            folder = output / variant
            folder.mkdir(exist_ok=True)
            for identifier in sorted(items):
                if identifier in scored[variant]:
                    continue
                generation = predictions[variant][identifier]
                reply, parsed, scores = _judge(judge, items[identifier], generation["final_text"], calls,
                    {"phase": "evaluation", "id": identifier, "variant": variant, "identity": identity})
                record = _base_record(variant, identifier, generation, identity)
                record.update(scores)
                record.update(judge_v2_raw=reply.raw, judge_model=judge.model_id,
                              judge_input_tokens=reply.input_tokens, judge_output_tokens=reply.output_tokens,
                              judge_latency_sec=reply.latency_sec, fatal_errors_v2=parsed.get("fatal_errors", []),
                              execution_kind=judge.kind)
                _append(folder / "judgments.jsonl", record)
                scored[variant][identifier] = record
            with (folder / "scored.csv").open("w", encoding="utf-8-sig", newline="") as stream:
                fields = list(next(iter(scored[variant].values())))
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                for identifier in sorted(items):
                    row = dict(scored[variant][identifier])
                    row["fatal_errors_v2"] = json.dumps(row["fatal_errors_v2"], ensure_ascii=False)
                    writer.writerow(row)
        summary = summarize(scored, archived if mode == "official" else None)
        summary.update(mode=mode, execution_kind=judge.kind, identity=identity,
                       valid_experiment=judge.kind == "real", official_result=mode == "official" and judge.kind == "real")
        _write_json(output / "summary.json", summary)
        _write_json(manifest_file, {"identity": identity, "metadata": metadata, "status": "complete"})
        return summary
    except Exception as error:
        _write_json(manifest_file, {"identity": identity, "metadata": metadata,
                                    "status": "failed", "error": str(error)})
        raise
