"""Pruebas de los límites entre roles del contrato compartido."""

import sys
import unittest
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schemas import (  # noqa: E402
    AnalystOutput,
    AuditReport,
    DraftModel,
    Finding,
    FormulatorOutput,
    PlanItem,
    ProblemSpec,
    ReviewDecision,
)


def minimal_spec():
    return {
        "case_id": "dev01",
        "objective": {"sense": "max", "description": "Maximizar cobertura"},
        "requirements": [
            {"id": "U1", "kind": "objective", "text": "Maximizar cobertura"}
        ],
    }


class SharedContractTests(unittest.TestCase):
    def test_requirements_use_internal_ids_and_reject_gold_fields(self):
        self.assertEqual(ProblemSpec.model_validate(minimal_spec()).requirement_ids(), ["U1"])
        with self.assertRaises(ValidationError):
            ProblemSpec.model_validate({**minimal_spec(), "requirements": [
                {"id": "R1", "kind": "objective", "text": "Oficial"}
            ]})
        with self.assertRaises(ValidationError):
            ProblemSpec.model_validate({**minimal_spec(), "reference_model": "gold"})

    def test_analyst_action_requires_spec(self):
        with self.assertRaises(ValidationError):
            AnalystOutput(action="deliver")
        self.assertEqual(
            AnalystOutput(action="deliver", spec=ProblemSpec.model_validate(minimal_spec())).action,
            "deliver",
        )

    def test_candidate_remains_native_text_and_plan_is_separate(self):
        candidate = "Conjuntos:\nI\nParámetros:\np_i\nVariables de decisión:\nx_i\nFunción objetivo:\nmax\nRestricciones:\n..."
        draft = DraftModel(candidate_id="dev01-1", raw_text=candidate)
        output = FormulatorOutput(
            action="formulate", draft=draft,
            plan=[PlanItem(requirement_id="U1", equation="objetivo")],
        )
        self.assertEqual(output.draft.raw_text, candidate)
        self.assertNotIn("plan", DraftModel.model_fields)
        with self.assertRaises(ValidationError):
            DraftModel(candidate_id="dev01-1", raw_text=candidate, plan=[])

    def test_audit_does_not_turn_unverified_into_an_error_or_a_pass(self):
        unknown = Finding(
            check="indice_libre", status="no_verificado",
            message="No se pudo analizar la notación",
        )
        report = AuditReport(candidate_id="dev01-1", findings=[unknown])
        self.assertFalse(report.has_errors)
        self.assertEqual(report.findings[0].status, "no_verificado")
        with self.assertRaises(ValidationError):
            Finding(
                check="indice_libre", status="no_verificado", level="error",
                message="Estado contradictorio",
            )

    def test_revision_requires_a_concrete_issue(self):
        with self.assertRaises(ValidationError):
            ReviewDecision(action="revise", candidate_id="dev01-1")
        self.assertEqual(
            ReviewDecision(action="accept", candidate_id="dev01-1").action,
            "accept",
        )


if __name__ == "__main__":
    unittest.main()
