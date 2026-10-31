"""Comparación pareada: mismas semillas, remuestreos y nivel que Entrega 2."""

from __future__ import annotations

from collections import Counter

import numpy as np


def paired_difference(target, reference):
    if set(target) != set(reference) or not target:
        raise ValueError("La comparación requiere los mismos IDs y no admite conjuntos vacíos")
    delta = np.array([float(target[i]) - float(reference[i]) for i in sorted(target)])
    ci = np.quantile(np.random.default_rng(42).choice(delta, size=(10000, len(delta)),
                                                   replace=True).mean(axis=1), [.025, .975])
    return {"n": len(delta), "mean_difference": float(delta.mean()),
            "ci95": [float(x) for x in ci], "improve": int((delta > 0).sum()),
            "tie": int((delta == 0).sum()), "worse": int((delta < 0).sum()),
            "bootstrap_samples": 10000, "bootstrap_seed": 42}


def summarize(scored, archived=None):
    if not scored:
        raise ValueError("No hay variantes evaluadas")
    identifiers = set(next(iter(scored.values())))
    if any(set(rows) != identifiers for rows in scored.values()):
        raise ValueError("No se comparan variantes incompletas ni con IDs diferentes")
    scores = {label: {i: float(row["score_fom5_v2"]) for i, row in rows.items()}
              for label, rows in scored.items()}
    groups = {}
    for label, rows in scored.items():
        values = list(scores[label].values())
        groups[label] = {"n": len(values), "mean_fom5_v2": float(np.mean(values)),
                         "zero_scores": sum(v == 0 for v in values),
                         "generation_statuses": dict(Counter(r["generation_status"] for r in rows.values())),
                         "mean_generation_tokens": float(np.mean([r["tokens_total"] for r in rows.values()])),
                         "mean_generation_latency_ms": float(np.mean([r["latency_ms_total"] for r in rows.values()]))}
    comparisons = {}
    if archived is not None:
        for label, rows in archived.items():
            if set(rows) != identifiers:
                raise ValueError("Los resultados archivados y nuevos no tienen los mismos IDs")
            scores[label] = {i: float(r["score_fom5_v2"]) for i, r in rows.items()}
            groups[label] = {"n": len(rows), "mean_fom5_v2": float(np.mean(list(scores[label].values()))),
                             "zero_scores": sum(v == 0 for v in scores[label].values())}
        for label in scored:
            comparisons[label] = {reference: paired_difference(scores[label], scores[reference])
                                  for reference in archived}
    if "full" in scores:
        for label in scored:
            if label != "full":
                comparisons.setdefault(label, {})["full"] = paired_difference(scores[label], scores["full"])
    return {"groups": groups, "paired_comparisons": comparisons,
            "note": "Comparaciones descriptivas; un IC que incluye cero no demuestra una mejora."}
