"""Revisión humana del auditor y separación desarrollo/benchmark."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eval.artifacts import read_jsonl
from eval.audit_dev_fixtures import development_artifacts
from eval.pilot import export_audit_review, summarize_audit_review
from schemas import Finding, TraceEvent
from tools.audit_model import audit_model


class PilotReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        spec, draft, coverage = development_artifacts()["dev01"]
        report = audit_model(spec, draft, coverage)
        report.findings = [Finding(check="indice_libre", level="aviso", message="Inspeccionar índice", symbol="j", location="C1"),
                           Finding(check="no_lineal", status="no_verificado", message="Notación no soportada")]
        self.event = TraceEvent(run_id="pilot", problem_id="dev01", variant="full", step=0,
            actor="audit_model", event="herramienta",
            input={"spec": spec.model_dump(), "draft": draft.model_dump(), "coverage": coverage.model_dump()},
            output=report.model_dump())
        self.trace = self.folder / "trace.jsonl"
        self.trace.write_text(self.event.model_dump_json() + "\n", encoding="utf-8")
        self.review = self.folder / "review.jsonl"

    def test_no_etiqueta_hallazgos_como_falsos_sin_revision(self):
        exported = export_audit_review([self.trace], self.review)
        self.assertEqual(exported["needs_human_label"], 1)
        rows = read_jsonl(self.review)
        self.assertIsNone(rows[0]["assessment"])
        self.assertEqual(rows[1]["assessment"], "unverified")
        with self.assertRaises(ValueError):
            summarize_audit_review(self.review)

    def test_resumen_distingue_falsos_positivos_y_no_verificado(self):
        export_audit_review([self.trace], self.review)
        rows = read_jsonl(self.review)
        rows[0]["assessment"] = "false_positive"
        rows[0]["review_note"] = "El índice sí está cuantificado"
        self.review.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        result = summarize_audit_review(self.review)
        self.assertEqual(result["checks"]["indice_libre"]["false_positive"], 1)
        self.assertEqual(result["checks"]["indice_libre"]["precision_on_reviewed"], 0)
        self.assertEqual(result["checks"]["no_lineal"]["unverified"], 1)

    def test_rechaza_trazas_oficiales_y_fuentes_duplicadas(self):
        self.event.problem_id = "opt_01"
        self.trace.write_text(self.event.model_dump_json() + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "ocho dev_cases"):
            export_audit_review([self.trace], self.review)
        self.assertFalse(self.review.exists())
        self.event.problem_id = "dev01"
        self.trace.write_text(self.event.model_dump_json() + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "dos veces"):
            export_audit_review([self.trace, self.trace], self.review)

    def test_no_sobrescribe_anotaciones_y_detecta_hallazgo_alterado(self):
        export_audit_review([self.trace], self.review)
        with self.assertRaises(FileExistsError):
            export_audit_review([self.trace], self.review)
        rows = read_jsonl(self.review)
        rows[0]["finding"]["message"] = "mensaje cambiado"
        self.review.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "modificó el hallazgo"):
            summarize_audit_review(self.review)


if __name__ == "__main__":
    unittest.main()
