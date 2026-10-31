"""Checkpoints de generación y separación del caso diagnóstico."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.diagnostic import diagnostic_gold, evaluate_diagnostic
from eval.judge import MockJudge
from orchestrator import OrchestratorConfig
from run import load_cases, run_variant
from schemas import RunResult


class GenerationRunnerTests(unittest.TestCase):
    def test_entrada_diagnostica_no_incluye_referencia(self):
        case = load_cases("diagnostic")["diagnostic_oftalmo"]
        gold, _ = diagnostic_gold()
        self.assertEqual(set(case), {"id", "title", "problem"})
        self.assertEqual(case["problem"], gold["problem"])
        self.assertNotIn("reference_model", case)

    def test_checkpoint_evita_duplicar_la_corrida(self):
        case = {"id": "diagnostic_oftalmo", "title": "Prueba", "problem": "Formule un modelo."}
        expected = RunResult(problem_id=case["id"], variant="full", final_text="Conjuntos:\nI",
                             status="aceptado", tokens_total=5)
        with tempfile.TemporaryDirectory() as temporary, patch("run.Orchestrator") as runner:
            runner.return_value.run.return_value = expected
            output = Path(temporary) / "full"
            traces = Path(temporary) / "traces"
            for _ in range(2):
                result = run_variant(None, OrchestratorConfig(), {case["id"]: case},
                                     "full", output, traces, mode="diagnostic",
                                     identity={"mode": "test"})
                self.assertEqual(result[case["id"]].final_text, expected.final_text)
            self.assertEqual(runner.return_value.run.call_count, 1)
            self.assertEqual(len((output / "outputs.jsonl").read_text(encoding="utf-8").splitlines()), 1)

    def test_juez_mock_solo_valida_intercambio(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagnostic.json"
            result = evaluate_diagnostic("Conjuntos: I", path, judge=MockJudge())
            self.assertFalse(result["valid_experiment"])
            self.assertEqual(result["scope"], "diagnostic; excluded from the official 30-case mean")
            self.assertEqual(len(result["calibration"]), 4)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), result)


if __name__ == "__main__":
    unittest.main()
