"""Contratos y control del Verificador con MockLLM, sin GPU ni herramientas reales."""

import copy
import inspect
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.analista import AgentFormatError, load_prompt  # noqa: E402
from agents.verificador import DEFAULT_PROMPT, VerifierOutput, verificar  # noqa: E402
from mock_llm import MockLLM, archivos_abiertos  # noqa: E402
from schemas import AuditReport, CoverageMap, DraftModel, ProblemSpec  # noqa: E402

PROBLEM = (
    "Una planta produce cajas de varios tipos. Cada caja del tipo p deja una "
    "utilidad b_p y requiere a_p horas. Hay H horas disponibles. Se busca "
    "maximizar la utilidad. Las cantidades son continuas y no negativas."
)
SPEC = ProblemSpec.model_validate({
    "case_id": "verificador-dev",
    "sets": [{"name": "P", "description": "tipos de cajas"}],
    "data": [{"name": "b", "description": "utilidad por caja", "indexed_by": ["P"]},
             {"name": "a", "description": "horas por caja", "indexed_by": ["P"]},
             {"name": "H", "description": "horas disponibles", "unit": "horas"}],
    "decisions": [{"description": "cajas producidas", "symbol": "x",
                   "indexed_by": ["P"], "domain": "continua"}],
    "objective": {"sense": "max", "description": "utilidad total"},
    "requirements": [
        {"id": "U1", "kind": "objective", "text": "Maximizar la utilidad"},
        {"id": "U2", "kind": "constraint", "text": "Respetar las horas disponibles"},
        {"id": "U3", "kind": "domain", "text": "Cantidades continuas no negativas"},
    ],
})
CANDIDATE = (
    "Conjuntos:\nP: tipos de cajas.\n"
    "Parámetros:\nb_p: utilidad; a_p: horas; H: horas disponibles.\n"
    "Variables de decisión:\nx_p >= 0, continua para todo p en P.\n"
    "Función objetivo:\nmax sum_{p en P} b_p x_p\n"
    "Restricciones:\nsum_{p en P} a_p x_p <= H"
)
DRAFT = DraftModel(candidate_id="verificador-dev-1", raw_text=CANDIDATE, parse_ok=True)
MAP = {
    "candidate_id": DRAFT.candidate_id,
    "elements": [
        {"id": "O1", "kind": "objective", "excerpt": "max sum_{p en P} b_p x_p"},
        {"id": "C1", "kind": "constraint", "excerpt": "sum_{p en P} a_p x_p <= H"},
        {"id": "D1", "kind": "domain", "excerpt": "x_p >= 0, continua para todo p en P."},
    ],
    "links": [{"requirement_id": "U1", "element_id": "O1"},
              {"requirement_id": "U2", "element_id": "C1"},
              {"requirement_id": "U3", "element_id": "D1"}],
}
ISSUE = {"description": "Falta un límite de producción indicado en el enunciado",
         "location": "Restricciones", "suggestion": "Agregar el límite omitido"}


def decision(action="accept", **updates):
    out = {"action": action, "candidate_id": DRAFT.candidate_id,
           "issues": [dict(ISSUE)] if action == "revise" else [],
           "reason": "Resultado de la inspección semántica"}
    out.update(updates)
    return out


def review(action="accept", **updates):
    out = {"action": "review", "coverage": copy.deepcopy(MAP), "decision": decision(action)}
    out.update(updates)
    return out


def audit_request():
    return {"action": "audit", "coverage": copy.deepcopy(MAP),
            "reason": "Comprobar símbolos e índices del borrador"}


def run(payload, **options):
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    llm = MockLLM([raw])
    kwargs = dict(adapter_on=False)
    kwargs.update(options)
    return llm, verificar(llm, PROBLEM, SPEC, DRAFT, **kwargs)


class VerificadorTests(unittest.TestCase):
    def test_entrega_accept_revise_y_stop_sin_cambiar_la_decision(self):
        for action in ("accept", "revise", "stop"):
            with self.subTest(action=action):
                llm, step = run(review(action))
                self.assertIsInstance(step.output, VerifierOutput)
                self.assertEqual(step.output.action, "review")
                self.assertEqual(step.output.decision.action, action)
                self.assertEqual(step.output.coverage.model_dump(), MAP)
                self.assertEqual(len(llm.calls), 1)

    def test_conserva_una_omision_del_analista_sin_inventar_id(self):
        _, step = run(review("revise"))
        issue = step.output.decision.issues[0]
        self.assertIsNone(issue.requirement_id)
        self.assertEqual(issue.location, "Restricciones")
        self.assertEqual(issue.suggestion, ISSUE["suggestion"])

    def test_recibe_spec_completo_enunciado_y_texto_sin_plan(self):
        spec = SPEC.model_copy(update={"uncertainties": ["¿Las horas son semanales?"]})
        llm = MockLLM([json.dumps(review())])
        snapshot = DRAFT.model_dump()
        verificar(llm, PROBLEM, spec, DRAFT, adapter_on=True)
        prompt = llm.calls[0][0]
        self.assertIn(PROBLEM, prompt)
        self.assertIn(CANDIDATE, prompt)
        self.assertIn(spec.model_dump_json(exclude_none=True), prompt)
        self.assertNotIn("plan", inspect.signature(verificar).parameters)
        self.assertEqual(DRAFT.model_dump(), snapshot)

    def test_registra_prompt_version_adapter_y_salida_cruda(self):
        for adapter in (False, True):
            raw = json.dumps(review())
            llm, step = run(raw, adapter_on=adapter)
            call = step.calls[0]
            self.assertEqual(call.prompt_version, "verificador_v2")
            self.assertEqual(call.adapter_on, adapter)
            self.assertEqual(call.raw, raw)
            self.assertEqual(llm.calls, [(call.prompt, adapter)])

    def test_pide_audit_sin_ejecutar_la_herramienta(self):
        llm, step = run(audit_request())
        self.assertEqual(step.output.action, "audit")
        self.assertIsNone(step.output.decision)
        self.assertTrue(step.output.reason)
        self.assertEqual(len(llm.calls), 1)

    def test_continua_con_mapa_auditado_y_conserva_no_verificado(self):
        report = AuditReport.model_validate({
            "candidate_id": DRAFT.candidate_id,
            "checks_run": ["indice_libre"],
            "findings": [{"check": "indice_libre", "status": "no_verificado",
                          "message": "No se pudo interpretar el cuantificador"}],
        })
        coverage = CoverageMap.model_validate(MAP)
        llm, step = run({"action": "review", "decision": decision("stop")},
                        coverage=coverage, audit_report=report)
        self.assertEqual(step.output.coverage, coverage)
        self.assertEqual(step.output.decision.action, "stop")
        self.assertIn(report.model_dump_json(exclude_none=True), llm.calls[0][0])
        self.assertIn('"status":"no_verificado"', llm.calls[0][0])
        self.assertIn("no es un chequeo aprobado", llm.calls[0][0])
        self.assertEqual(report.findings[0].level, None)

    def test_informe_con_error_llega_al_llm_sin_sustituir_su_decision(self):
        report = AuditReport.model_validate({
            "candidate_id": DRAFT.candidate_id,
            "checks_run": ["no_lineal"],
            "findings": [{"check": "no_lineal", "level": "error",
                          "message": "Producto entre variables en C1"}],
        })
        llm, step = run({"action": "review", "decision": decision("revise")},
                        coverage=CoverageMap.model_validate(MAP), audit_report=report)
        self.assertIn("Producto entre variables en C1", llm.calls[0][0])
        self.assertEqual(step.output.decision.action, "revise")

    def test_no_audit_entrega_diagnostico_sin_informe(self):
        llm, step = run(review("revise"), audit_allowed=False)
        self.assertEqual(step.output.decision.action, "revise")
        self.assertIn("No puedes pedir audit_model", llm.calls[0][0])
        self.assertNotIn("Informe de audit_model:", llm.calls[0][0])

    def test_no_audit_rechaza_solicitud_con_la_llamada_en_el_error(self):
        raw = json.dumps(audit_request())
        with self.assertRaises(AgentFormatError) as caught:
            run(raw, audit_allowed=False)
        self.assertIn("audit no está disponible", str(caught.exception))
        self.assertEqual([c.raw for c in caught.exception.calls], [raw])

    def test_no_permite_una_segunda_solicitud_de_auditoria(self):
        with self.assertRaisesRegex(AgentFormatError, "audit no está disponible"):
            run(audit_request(), coverage=CoverageMap.model_validate(MAP),
                audit_report=AuditReport(candidate_id=DRAFT.candidate_id))

    def test_continuacion_rechaza_sustitucion_del_mapa(self):
        payload = review()
        payload["coverage"]["links"] = []
        with self.assertRaisesRegex(AgentFormatError, "no se puede cambiar"):
            run(payload, coverage=CoverageMap.model_validate(MAP),
                audit_report=AuditReport(candidate_id=DRAFT.candidate_id))

    def test_continuacion_admite_repetir_el_mismo_mapa(self):
        _, step = run(review(), coverage=CoverageMap.model_validate(MAP),
                      audit_report=AuditReport(candidate_id=DRAFT.candidate_id))
        self.assertEqual(step.output.coverage.model_dump(), MAP)

    def test_argumentos_de_auditoria_incoherentes_fallan_antes_del_llm(self):
        coverage = CoverageMap.model_validate(MAP)
        report = AuditReport(candidate_id=DRAFT.candidate_id)
        wrong_map = coverage.model_copy(update={"candidate_id": "otro"})
        wrong_report = report.model_copy(update={"candidate_id": "otro"})
        cases = [dict(coverage=coverage), dict(audit_report=report),
                 dict(coverage=wrong_map, audit_report=report),
                 dict(coverage=coverage, audit_report=wrong_report),
                 dict(coverage=coverage, audit_report=report, audit_allowed=False)]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                llm = MockLLM([])
                with self.assertRaises(ValueError):
                    verificar(llm, PROBLEM, SPEC, DRAFT, adapter_on=False, **kwargs)
                self.assertEqual(llm.calls, [])

    def test_rechaza_identificador_de_otro_candidate_en_la_salida(self):
        payload = review()
        payload["coverage"]["candidate_id"] = "otro"
        payload["decision"]["candidate_id"] = "otro"
        with self.assertRaisesRegex(AgentFormatError, "no corresponde al borrador"):
            run(payload)
        payload["coverage"]["candidate_id"] = DRAFT.candidate_id
        with self.assertRaisesRegex(AgentFormatError, "mismo candidate_id"):
            run(payload)

    def test_cobertura_incompleta_no_se_rellena_automaticamente(self):
        payload = review("revise")
        payload["coverage"]["links"] = payload["coverage"]["links"][:1]
        _, step = run(payload)
        self.assertEqual(step.output.coverage.model_dump(), payload["coverage"])
        self.assertEqual(step.output.decision.action, "revise")

    def test_json_invalido_o_truncado_conserva_la_llamada(self):
        for raw in ("No puedo revisar", '{"action":"review","decision":{'):
            with self.subTest(raw=raw), self.assertRaises(AgentFormatError) as caught:
                run(raw)
            self.assertEqual(caught.exception.raw, raw)
            self.assertEqual(len(caught.exception.calls), 1)
            self.assertEqual(caught.exception.prompt_version, "verificador_v2")

    def test_rechaza_tipos_y_combinaciones_de_control_invalidas(self):
        no_issues = review("revise")
        no_issues["decision"]["issues"] = []
        bad_audit = audit_request()
        bad_audit["decision"] = decision()
        bad_reason = audit_request()
        bad_reason["reason"] = " "
        bad_action = review()
        bad_action["action"] = "accept"
        cases = [review(coverage=1), review(coverage={}), review(decision=1),
                 review(decision=None), bad_action, no_issues,
                 bad_audit, bad_reason, review(unexpected="campo extra")]
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(AgentFormatError):
                run(payload)

    def test_accept_inconsistente_se_rechaza(self):
        empty = {"candidate_id": DRAFT.candidate_id, "elements": [], "links": []}
        partial = copy.deepcopy(MAP)
        partial["links"] = partial["links"][:2]
        dangling = copy.deepcopy(MAP)
        dangling["elements"] = dangling["elements"][:2]
        cases = [review(coverage=empty), review(coverage=partial), review(coverage=dangling),
                 review(decision=decision("accept", issues=[dict(ISSUE)]))]
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(AgentFormatError):
                run(payload)

    def test_revise_y_stop_admiten_mapas_incompletos(self):
        empty = {"candidate_id": DRAFT.candidate_id, "elements": [], "links": []}
        for action in ("revise", "stop"):
            with self.subTest(action=action):
                _, step = run(review(action, coverage=empty))
                self.assertEqual(step.output.decision.action, action)

    def test_accept_tras_auditar_con_mapa_incompleto_se_rechaza(self):
        partial = copy.deepcopy(MAP)
        partial["links"] = partial["links"][:1]
        coverage = CoverageMap.model_validate(partial)
        report = AuditReport(candidate_id=DRAFT.candidate_id)
        llm = MockLLM([json.dumps({"action": "review", "decision": decision()})])
        with self.assertRaises(AgentFormatError):
            verificar(llm, PROBLEM, SPEC, DRAFT, adapter_on=False,
                      coverage=coverage, audit_report=report)

    def test_feedback_cambia_el_prompt_sin_reintentos_internos(self):
        llm = MockLLM(["JSON incompleto", json.dumps(review())])
        with self.assertRaises(AgentFormatError) as caught:
            verificar(llm, PROBLEM, SPEC, DRAFT, adapter_on=False)
        self.assertEqual(len(llm.calls), 1)
        step = verificar(llm, PROBLEM, SPEC, DRAFT, adapter_on=False,
                         format_feedback=str(caught.exception))
        self.assertEqual(len(llm.calls), 2)
        self.assertIn(str(caught.exception), step.calls[0].prompt)
        self.assertNotEqual(llm.calls[0][0], llm.calls[1][0])

    def test_errores_del_parser_llegan_al_modelo(self):
        draft = DRAFT.model_copy(update={"parse_ok": False,
                                       "parse_errors": ["falta Variables de decisión:"]})
        llm = MockLLM([json.dumps(review("revise"))])
        step = verificar(llm, PROBLEM, SPEC, draft, adapter_on=False)
        self.assertIn("falta Variables de decisión:", llm.calls[0][0])
        self.assertEqual(step.output.decision.action, "revise")


class PromptAndIsolationTests(unittest.TestCase):
    def test_prompt_versionado_carga_todas_las_secciones(self):
        version, sections = load_prompt(DEFAULT_PROMPT)
        self.assertEqual(version, "verificador_v2")
        self.assertEqual(set(sections), {"user", "audit_available", "review_only",
                                         "audit_result", "format_feedback"})

    def test_solo_abre_el_prompt_en_revision_y_continuacion(self):
        for kwargs in ({}, {"coverage": CoverageMap.model_validate(MAP),
                            "audit_report": AuditReport(candidate_id=DRAFT.candidate_id)}):
            with self.subTest(kwargs=kwargs), archivos_abiertos() as opened:
                run(review(), **kwargs)
            self.assertEqual(opened, [DEFAULT_PROMPT.resolve()])

    def test_preserva_signos_pesos_en_los_datos_de_entrada(self):
        text = PROBLEM + " El costo es US$5 y el presupuesto es $ 100."
        llm = MockLLM([json.dumps(review())])
        verificar(llm, text, SPEC, DRAFT, adapter_on=False)
        self.assertIn(text, llm.calls[0][0])
        self.assertNotIn("# verificador_v2", llm.calls[0][0])

    def test_ejemplos_de_decision_no_contienen_lista_de_opciones(self):
        _, step = run(review())
        self.assertNotIn('"action":"accept o revise o stop"', step.calls[0].prompt)
        self.assertTrue((DEFAULT_PROMPT.parent / "verificador_v1.md").is_file())


if __name__ == "__main__":
    unittest.main()
