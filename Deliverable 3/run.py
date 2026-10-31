"""Genera formulaciones de Entrega 3 y conserva salidas/trazas por caso.

Desde la raíz del repositorio, por ejemplo:
python "Deliverable 3/run.py" --mode development --variants full
python "Deliverable 3/run.py" --mode official --variants full no_evidence no_plan no_audit no_review
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import yaml

from eval.artifacts import VARIANTS, by_id, canonical_hash, read_jsonl
from eval.provenance import generation_context, generation_manifest, manifest_path, write_generation_manifest
from model import ADAPTER_SHA256, extract_adapter, load_qwen, sha256_file
from orchestrator import Orchestrator, OrchestratorConfig
from schemas import RunResult

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
INPUTS = {
    "development": ROOT / "dev_cases/inputs.jsonl",
    "official": ROOT / "data/benchmark_30_generation_only.jsonl",
    "diagnostic": ROOT / "data/diagnostic_oftalmo_input.jsonl",
}


def load_cases(mode: str) -> dict[str, dict[str, str]]:
    """Carga exclusivamente id, título y enunciado; nunca abre el gold."""
    if mode not in INPUTS:
        raise ValueError(f"Modo desconocido: {mode}")
    rows = by_id(read_jsonl(INPUTS[mode]))
    expected = ({f"opt_{i:02}" for i in range(1, 31)} if mode == "official" else
                {f"dev{i:02}" for i in range(1, 9)} if mode == "development" else
                {"diagnostic_oftalmo"})
    if set(rows) != expected or any(set(row) != {"id", "title", "problem"} for row in rows.values()):
        raise ValueError(f"{mode}: IDs o campos de entrada inesperados")
    return {identifier: rows[identifier] for identifier in sorted(rows)}


def load_config(mode: str) -> tuple[OrchestratorConfig, Path]:
    name = "frozen.yaml" if mode == "official" else "development.yaml"
    path = ROOT / "config" / name
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return OrchestratorConfig.from_mapping(raw), path


def _read_completed(path: Path, variant: str, cases: dict) -> dict[str, RunResult]:
    if not path.exists():
        return {}
    rows = [RunResult.model_validate(row) for row in read_jsonl(path)]
    completed = {}
    for row in rows:
        if row.variant != variant or row.problem_id not in cases or row.problem_id in completed:
            raise ValueError(f"Checkpoint incompatible o duplicado: {path}")
        completed[row.problem_id] = row
    return completed


def _identity(mode: str, cases: dict, adapter_zip: Path) -> dict:
    context_mode = "development" if mode == "diagnostic" else mode
    return {
        "mode": mode,
        "generation": generation_context(context_mode),
        "inputs_sha256": canonical_hash(list(cases.values())),
        "adapter_zip_sha256": sha256_file(adapter_zip),
    }


def _ensure_identity(path: Path, identity: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != identity:
            raise ValueError(f"La carpeta pertenece a otra configuración o código: {path.parent}")
        return
    if any(path.parent.iterdir()):
        raise ValueError(f"La carpeta contiene archivos sin identidad: {path.parent}")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(identity, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def run_variant(llm, config: OrchestratorConfig, cases: dict[str, dict[str, str]],
                variant: str, output_dir: Path, trace_dir: Path, *, mode: str,
                identity: dict) -> dict[str, RunResult]:
    """Reanuda por ID y escribe cada resultado inmediatamente después de su traza."""
    if variant not in VARIANTS:
        raise ValueError(f"Variante desconocida: {variant}")
    output_dir = Path(output_dir)
    trace_dir = Path(trace_dir)
    _ensure_identity(output_dir / "generation.json", identity)
    trace_dir.mkdir(parents=True, exist_ok=True)
    predictions = output_dir / "outputs.jsonl"
    completed = _read_completed(predictions, variant, cases)
    orchestrator = Orchestrator(llm, config)
    for identifier, case in cases.items():
        if identifier in completed:
            print(f"{variant}/{identifier}: conservado", flush=True)
            continue
        run_id = f"{mode}-{variant}-{identifier}-{uuid4().hex[:8]}"
        trace_path = trace_dir / f"{run_id}.jsonl"
        print(f"{variant}/{identifier}: ejecutando", flush=True)
        result = orchestrator.run(case, variant=variant, run_id=run_id, trace_path=trace_path)
        with predictions.open("a", encoding="utf-8") as stream:
            stream.write(result.model_dump_json() + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        completed[identifier] = result
        print(f"{variant}/{identifier}: {result.status}; {result.tokens_total} tokens", flush=True)
    if len(completed) == len(cases) and mode in {"development", "official"}:
        manifest = manifest_path(predictions)
        expected = generation_manifest(predictions, variant, cases, mode=mode)
        if manifest.exists():
            if json.loads(manifest.read_text(encoding="utf-8")) != expected:
                raise ValueError(f"Manifiesto incompatible: {manifest}")
        else:
            write_generation_manifest(predictions, variant, cases, mode=mode)
    return completed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=tuple(INPUTS), required=True)
    parser.add_argument("--variants", choices=VARIANTS, nargs="+", required=True)
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--trace-root", type=Path, default=None)
    parser.add_argument("--adapter-zip", type=Path,
                        default=REPO / "Deliverable 2/adapter_qlora_qwen25_final.zip")
    args = parser.parse_args(argv)
    if len(args.variants) != len(set(args.variants)):
        parser.error("No repitas variantes")
    import torch

    if not torch.cuda.is_available() or "T4" not in torch.cuda.get_device_name(0):
        parser.error("Esta corrida requiere Colab con GPU T4")
    if not args.adapter_zip.is_file() or sha256_file(args.adapter_zip) != ADAPTER_SHA256:
        parser.error("Falta el adapter público o su SHA-256 no coincide")
    cases = load_cases(args.mode)
    config, _ = load_config(args.mode)
    identity = _identity(args.mode, cases, args.adapter_zip)
    output_root = args.output_root or ROOT / "results" / args.mode
    trace_root = args.trace_root or ROOT / "traces" / args.mode
    with tempfile.TemporaryDirectory(prefix="d3-adapter-") as temporary:
        adapter = extract_adapter(args.adapter_zip, Path(temporary) / "adapter")
        llm = load_qwen(adapter)
        for variant in args.variants:
            run_variant(llm, config, cases, variant, output_root / variant,
                        trace_root / variant, mode=args.mode, identity=identity)


if __name__ == "__main__":
    main()
