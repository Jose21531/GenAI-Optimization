"""Preparación de revisión humana del auditor, solo sobre casos de desarrollo."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from eval.artifacts import ROOT, canonical_hash, load_development, read_jsonl, sha256
from schemas import AuditReport, CoverageMap, DraftModel, ProblemSpec, TraceEvent


def export_audit_review(traces, output: Path, *, root=ROOT):
    development = load_development(root)
    rows, seen = [], set()
    for source in traces:
        path = Path(source)
        digest = sha256(path)
        events = [TraceEvent.model_validate(r) for r in read_jsonl(path)]
        if any(e.problem_id not in development for e in events):
            raise ValueError("La calibración del auditor solo admite trazas de los ocho dev_cases")
        for event in events:
            if event.actor != "audit_model" or event.event != "herramienta":
                continue
            if not isinstance(event.input, dict) or not isinstance(event.output, dict):
                raise ValueError("La traza de auditoría debe tener entrada y observación estructuradas")
            if "error" in event.output:
                continue
            report = AuditReport.model_validate(event.output)
            draft = DraftModel.model_validate(event.input["draft"])
            spec = ProblemSpec.model_validate(event.input["spec"])
            coverage = CoverageMap.model_validate(event.input["coverage"])
            if len({draft.candidate_id, report.candidate_id, coverage.candidate_id}) != 1:
                raise ValueError("Traza de auditoría con identificadores incompatibles")
            if spec.case_id != event.problem_id:
                raise ValueError("El análisis de la traza corresponde a otro caso")
            for position, finding in enumerate(report.findings):
                identifier = canonical_hash([digest, event.step, position])
                if identifier in seen:
                    raise ValueError("La misma traza/hallazgo fue incluida dos veces")
                seen.add(identifier)
                payload = finding.model_dump(mode="json")
                rows.append({"id": identifier, "case_id": event.problem_id, "variant": event.variant,
                             "trace_sha256": digest, "candidate": draft.raw_text,
                             "problem": development[event.problem_id]["problem"],
                             "spec": spec.model_dump(mode="json"), "coverage": coverage.model_dump(mode="json"),
                             "finding": payload, "finding_sha256": canonical_hash(payload),
                             "assessment": "unverified" if finding.status == "no_verificado" else None,
                             "review_note": ""})
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with Path(output).open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    return {"review_rows": len(rows), "needs_human_label": sum(r["assessment"] is None for r in rows),
            "note": "Un hallazgo no se etiqueta como falso positivo sin revisión humana."}


def summarize_audit_review(path: Path):
    groups = defaultdict(lambda: {"true_positive": 0, "false_positive": 0, "uncertain": 0, "unverified": 0})
    seen, cases = set(), set()
    for row in read_jsonl(path):
        if row["id"] in seen or row["case_id"] not in {f"dev{i:02}" for i in range(1, 9)}:
            raise ValueError("Revisión duplicada o ajena al desarrollo")
        seen.add(row["id"])
        cases.add(row["case_id"])
        finding = row["finding"]
        if canonical_hash(finding) != row["finding_sha256"]:
            raise ValueError("Se modificó el hallazgo; solo se deben completar assessment y review_note")
        label = row["assessment"]
        allowed = {"unverified"} if finding["status"] == "no_verificado" else {"true_positive", "false_positive", "uncertain"}
        if label not in allowed:
            raise ValueError("Falta completar la revisión humana de un hallazgo")
        groups[finding["check"]][label] += 1
    for counts in groups.values():
        verified = counts["true_positive"] + counts["false_positive"]
        counts["precision_on_reviewed"] = counts["true_positive"] / verified if verified else None
    return {"observed_cases": sorted(cases), "checks": dict(groups),
            "note": "No modifica severidades ni congela configuración; revisar también los casos inciertos."}
