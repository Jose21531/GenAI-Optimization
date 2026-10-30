"""CLI de evaluación posterior. Ejecutar desde la raíz del repositorio."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.artifacts import REPO, VARIANTS, load_published
from eval.judge import MockJudge
from eval.pipeline import evaluate, load_items, prepare
from eval.pilot import export_audit_review, summarize_audit_review
from eval.provenance import write_generation_manifest
from eval.statistics import paired_difference


def parse_sources(values):
    result = {}
    for value in values:
        variant, separator, path = value.partition("=")
        if not separator or variant not in VARIANTS or not path or variant in result:
            raise ValueError("Usa --source variante=ruta, sin repetir variantes")
        result[variant] = Path(path)
    return result


def verify_archives(deliverable2):
    gold, archives = load_published(deliverable2)
    scores = {label: {i: float(r["score_fom5_v2"]) for i, r in rows.items()} for label, rows in archives.items()}
    return {"scope": "archived Entrega 2; no new model execution", "cases": len(gold),
            "means": {label: sum(rows.values()) / len(rows) for label, rows in scores.items()},
            "QLoRA_minus_baseline": paired_difference(scores["QLoRA"], scores["baseline"]),
            "all_60_archived_scores_reproduced": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    archived = commands.add_parser("verify-archives", help="Verificación CPU de datos y puntajes publicados")
    archived.add_argument("--deliverable2", type=Path, default=REPO / "Deliverable 2")
    manifest = commands.add_parser("manifest", help="Sellar procedencia de salidas de generación")
    manifest.add_argument("--mode", choices=("development", "official"), required=True)
    manifest.add_argument("--variant", choices=VARIANTS, required=True)
    manifest.add_argument("--predictions", type=Path, required=True)
    for name in ("preflight", "evaluate"):
        command = commands.add_parser(name)
        command.add_argument("--mode", choices=("development", "official"), required=True)
        command.add_argument("--source", action="append", required=True)
        command.add_argument("--deliverable2", type=Path, default=REPO / "Deliverable 2")
        if name == "evaluate":
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--mock", action="store_true", help="Solo desarrollo; no genera resultados reales")
    review = commands.add_parser("audit-review", help="Exportar hallazgos del piloto para revisión humana")
    review.add_argument("--trace", action="append", type=Path, required=True)
    review.add_argument("--output", type=Path, required=True)
    summary = commands.add_parser("audit-summary")
    summary.add_argument("--annotations", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "verify-archives":
            result = verify_archives(args.deliverable2)
        elif args.command == "manifest":
            items, _, _ = load_items(args.mode)
            path = write_generation_manifest(args.predictions, args.variant, items, mode=args.mode)
            result = {"manifest": str(path)}
        elif args.command in {"preflight", "evaluate"}:
            sources = parse_sources(args.source)
            if args.command == "preflight":
                items, _, _, _, _ = prepare(sources, mode=args.mode, deliverable2=args.deliverable2)
                result = {"mode": args.mode, "variants": sorted(sources), "cases_per_variant": len(items),
                          "note": "Entradas verificadas; no se cargó ni ejecutó el juez."}
            else:
                if args.mock and args.mode == "official":
                    raise ValueError("--mock está prohibido para resultados oficiales")
                result = evaluate(sources, args.output, mode=args.mode, deliverable2=args.deliverable2,
                                  judge=MockJudge() if args.mock else None)
        elif args.command == "audit-review":
            result = export_audit_review(args.trace, args.output)
        else:
            result = summarize_audit_review(args.annotations)
    except (ValueError, FileNotFoundError, RuntimeError) as error:
        parser.exit(2, f"Evaluación detenida: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return result


if __name__ == "__main__":
    main()
