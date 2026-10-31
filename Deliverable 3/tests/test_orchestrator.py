"""Recorridos completos con respuestas guionizadas, sin GPU ni datasets oficiales."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mock_llm import MockLLM, archivos_abiertos
from orchestrator import Adapters, Budgets, Orchestrator, OrchestratorConfig, TokenLimits
from schemas import AuditReport, TraceEvent
from test_verificador import CANDIDATE, MAP, PROBLEM, SPEC

CASE = {"id": "dev-flow", "title": "Cajas", "problem": PROBLEM}
FORMULATE = "DECISION: formular\nU1 -> max sum_{p en P} b_p x_p\nU2 -> sum_{p en P} a_p x_p <= H"
CLARIFY = "DECISION: aclarar\nPREGUNTA: ¿El límite de horas es total?"
REREAD = json.dumps({"action": "reread", "reason": "Revisar horas y unidades"})


def analyst(evidence=True):
    data = SPEC.model_dump(exclude_none=True)
    if evidence:
        quotes = ["maximizar la utilidad", "Hay H horas disponibles", "continuas y no negativas"]
        for requirement, quote in zip(data["requirements"], quotes):
            requirement["evidence"] = {"text": quote}
    return json.dumps({"action": "deliver", "spec": data})


def verifier(action="accept", round=0, audit=False, continuation=False):
    coverage = copy.deepcopy(MAP)
    candidate_id = f"run-r{round}"
    coverage["candidate_id"] = candidate_id
    if audit:
        return json.dumps({"action": "audit", "coverage": coverage, "reason": "Comprobar índices"})
    decision = {"action": action, "candidate_id": candidate_id, "reason": "Revisión semántica",
                "issues": [{"requirement_id": "U2", "description": "Revisar capacidad",
                            "location": "Restricciones", "suggestion": "Corregir el límite"}]
                          if action == "revise" else []}
    payload = {"action": "review", "decision": decision}
    if not continuation:
        payload["coverage"] = coverage
    return json.dumps(payload)


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.trace = Path(self.temp.name) / "trace.jsonl"

    def run_flow(self, responses, *, config=None, variant="full", **kwargs):
        llm = responses if hasattr(responses, "generate") else MockLLM(responses)
        runner = Orchestrator(llm, config, **kwargs)
        result = runner.run(CASE, run_id="run", trace_path=self.trace, variant=variant)
        return result, runner, llm

    def test_camino_completo_y_traza_jsonl_valida(self):
        result, runner, llm = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier()])
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.final_text, CANDIDATE)
        self.assertEqual(len(llm.calls), 4)
        events = [TraceEvent.model_validate_json(line) for line in self.trace.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([e.step for e in events], list(range(len(events))))
        self.assertEqual(events[-1].event, "fin")
        self.assertEqual(events[-1].output["final_text"], CANDIDATE)
        self.assertEqual(len(events), len(runner.last_events))
        calls = [e for e in events if e.event == "llamada" and e.actor != "orquestador"]
        self.assertEqual([e.adapter_on for e in calls], [False, False, True, True])

    def test_auditoria_se_ejecuta_solo_si_el_verificador_la_pide(self):
        result, runner, llm = self.run_flow([analyst(), FORMULATE, CANDIDATE,
                                           verifier(audit=True), verifier(continuation=True)])
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.tool_calls, 1)
        events = [e for e in runner.last_events if e.actor == "audit_model"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].output["candidate_id"], "run-r0")
        self.assertIn("Informe de audit_model:", llm.calls[-1][0])

    def test_corrida_con_auditoria_solo_abre_prompts_y_su_traza(self):
        with archivos_abiertos() as opened:
            result, _, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE,
                                         verifier(audit=True), verifier(continuation=True)])
        self.assertEqual(result.status, "aceptado")
        self.assertTrue(opened)
        self.assertTrue(all(p.is_relative_to(ROOT / "prompts") or p == self.trace.resolve() for p in opened))

    def test_relectura_invoca_extract_data_spans_una_vez(self):
        result, runner, llm = self.run_flow([REREAD, analyst(), FORMULATE, CANDIDATE, verifier()])
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.tool_calls, 1)
        self.assertIn("Fragmentos numéricos detectados", llm.calls[1][0])
        self.assertEqual(len([e for e in runner.last_events if e.actor == "extract_data_spans"]), 1)

    def test_aclaracion_reenvia_el_spec_anterior(self):
        result, _, llm = self.run_flow([analyst(), CLARIFY, analyst(), FORMULATE, CANDIDATE, verifier()])
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.clarifications, 1)
        self.assertIn("Análisis anterior:", llm.calls[2][0])
        self.assertIn("¿El límite de horas es total?", llm.calls[2][0])
        self.assertIn("No quedan aclaraciones disponibles", llm.calls[3][0])

    def test_revision_reenvia_borrador_e_issues_y_conserva_salida_nueva(self):
        revised = CANDIDATE.replace("tipos de cajas", "tipos de cajas fabricadas")
        result, _, llm = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier("revise"),
                                       FORMULATE, revised, verifier(round=1)])
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.rounds, 1)
        self.assertEqual(result.final_text, revised)
        self.assertIn(CANDIDATE, llm.calls[4][0])
        self.assertIn("Corregir el límite", llm.calls[5][0])

    def test_agotar_revision_conserva_el_ultimo_candidate(self):
        revised = CANDIDATE.replace("tipos de cajas", "tipos de cajas fabricadas")
        result, runner, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier("revise"),
                                         FORMULATE, revised, verifier("revise", round=1)])
        self.assertEqual(result.status, "presupuesto_agotado")
        self.assertEqual(result.final_text, revised)
        self.assertEqual(result.rounds, 1)
        self.assertTrue(any(e.event == "presupuesto_agotado" and e.output["budget"] == "revisions"
                            for e in runner.last_events))

    def test_no_review_conserva_diagnostico_sin_devolver_al_formulador(self):
        result, runner, llm = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier("revise")], variant="no_review")
        self.assertEqual(result.status, "presupuesto_agotado")
        self.assertEqual(result.rounds, 0)
        self.assertEqual(len(llm.calls), 4)
        self.assertEqual(result.final_text, CANDIDATE)
        decisions = [e for e in runner.last_events if e.actor == "verificador" and e.event == "decision"]
        self.assertEqual(decisions[0].output["artifact"]["decision"]["issues"][0]["suggestion"], "Corregir el límite")

    def test_no_audit_no_ejecuta_herramienta_y_no_afirma_que_paso(self):
        def forbidden(*args):
            raise AssertionError("No debe ejecutar la herramienta")
        result, _, llm = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier()], variant="no_audit", audit_fn=forbidden)
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.tool_calls, 0)
        self.assertIn("No puedes pedir audit_model", llm.calls[-1][0])
        self.assertNotIn("Informe de audit_model:", llm.calls[-1][0])

    def test_no_audit_rechaza_peticion_y_reintenta_sin_ejecutarla(self):
        result, _, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier(audit=True), verifier()], variant="no_audit")
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.tool_calls, 0)

    def test_no_evidence_cambia_solo_el_prompt_del_analista(self):
        result, runner, _ = self.run_flow([analyst(evidence=False), FORMULATE, CANDIDATE, verifier()], variant="no_evidence")
        self.assertEqual(result.status, "aceptado")
        versions = [e.prompt_version for e in runner.last_events if e.event == "llamada" and e.actor != "orquestador"]
        self.assertEqual(versions, ["analista_v4_noevidence", "formulador_v2", "formulador_v2", "verificador_v2"])

    def test_no_plan_conserva_el_formato_del_candidate(self):
        result, runner, llm = self.run_flow([analyst(), "DECISION: formular", CANDIDATE, verifier()], variant="no_plan")
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(result.final_text, CANDIDATE)
        self.assertNotIn("Ecuaciones planificadas", llm.calls[2][0])
        self.assertIn("formulador_v1_noplan", [e.prompt_version for e in runner.last_events])

    def test_reintento_incluye_error_y_conserva_llamada_fallida(self):
        result, runner, llm = self.run_flow(["salida inválida", analyst(), FORMULATE, CANDIDATE, verifier()])
        self.assertEqual(result.status, "aceptado")
        self.assertEqual(len([e for e in runner.last_events if e.event == "fallo_formato"]), 1)
        self.assertIn("La respuesta anterior no cumplió", llm.calls[1][0])
        self.assertNotEqual(llm.calls[0][0], llm.calls[1][0])

    def test_full_rechaza_citas_ausentes_como_fallo_de_formato(self):
        config = OrchestratorConfig(budgets=Budgets(format_retries=0))
        result, _, llm = self.run_flow([analyst(evidence=False)], config=config)
        self.assertEqual(result.status, "fallo_formato")
        self.assertEqual(result.final_text, "")
        self.assertEqual(len(llm.calls), 1)

    def test_candidate_incompleto_se_reintenta_y_no_se_acepta_en_silencio(self):
        result, runner, _ = self.run_flow([analyst(), FORMULATE, "Conjuntos:\nP: cajas.",
                                         FORMULATE, CANDIDATE, verifier()])
        self.assertEqual(result.status, "aceptado")
        self.assertTrue(any(e.event == "fallo_formato" and e.actor == "formulador" for e in runner.last_events))

    def test_fallo_en_segunda_llamada_conserva_las_dos_y_sus_respuestas(self):
        result, runner, llm = self.run_flow([analyst(), FORMULATE, "   ", FORMULATE, CANDIDATE, verifier()])
        self.assertEqual(result.status, "aceptado")
        responses = [e for e in runner.last_events if e.event == "respuesta"]
        self.assertEqual(len(responses), 6)
        self.assertEqual(responses[1].output["raw"], FORMULATE)
        self.assertEqual(responses[2].output["raw"], "   ")
        self.assertIn("candidate está vacío", llm.calls[3][0])

    def test_fallo_de_formato_agotado_preserva_candidate_incompleto(self):
        config = OrchestratorConfig(budgets=Budgets(format_retries=0))
        invalid = "Conjuntos:\nP: cajas."
        result, _, _ = self.run_flow([analyst(), FORMULATE, invalid], config=config)
        self.assertEqual(result.status, "fallo_formato")
        self.assertEqual(result.final_text, invalid)

    def test_presupuesto_de_reintentos_es_global(self):
        result, _, llm = self.run_flow(["mal JSON", analyst(), FORMULATE, "Conjuntos:\nP: cajas."])
        self.assertEqual(result.status, "fallo_formato")
        self.assertEqual(len(llm.calls), 4)

    def test_no_repite_aclaraciones_si_no_queda_presupuesto(self):
        config = OrchestratorConfig(budgets=Budgets(clarifications=0))
        result, _, llm = self.run_flow([analyst(), CLARIFY], config=config)
        self.assertEqual(result.status, "presupuesto_agotado")
        self.assertEqual(result.clarifications, 0)
        self.assertEqual(len(llm.calls), 2)

    def test_no_repite_relecturas_si_no_queda_presupuesto(self):
        config = OrchestratorConfig(budgets=Budgets(rereads=0))
        result, _, _ = self.run_flow([REREAD], config=config)
        self.assertEqual(result.status, "presupuesto_agotado")
        self.assertEqual(result.tool_calls, 0)

    def test_limite_total_de_llamadas_impide_bucles(self):
        config = OrchestratorConfig(budgets=Budgets(model_calls=2))
        result, _, llm = self.run_flow([analyst(), FORMULATE], config=config)
        self.assertEqual(result.status, "presupuesto_agotado")
        self.assertEqual(len(llm.calls), 2)

    def test_stop_del_agente_conserva_la_formulacion(self):
        result, _, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier("stop")])
        self.assertEqual(result.status, "detenido")
        self.assertEqual(result.final_text, CANDIDATE)

    def test_auditoria_de_otro_borrador_detiene_sin_perder_candidate(self):
        result, _, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier(audit=True)],
                                     audit_fn=lambda *args: AuditReport(candidate_id="otro"))
        self.assertEqual(result.status, "detenido")
        self.assertEqual(result.final_text, CANDIDATE)

    def test_fallo_de_herramienta_se_registra(self):
        def broken(*args):
            raise RuntimeError("auditor no disponible")
        result, runner, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier(audit=True)], audit_fn=broken)
        self.assertEqual(result.status, "detenido")
        self.assertTrue(any(e.actor == "audit_model" and "error" in e.output for e in runner.last_events))

    def test_informe_con_tipo_invalido_se_registra_y_detiene(self):
        result, _, _ = self.run_flow([analyst(), FORMULATE, CANDIDATE, verifier(audit=True)], audit_fn=lambda *args: {})
        self.assertEqual(result.status, "detenido")
        self.assertEqual(result.final_text, CANDIDATE)

    def test_respuesta_no_textual_del_modelo_se_registra_y_detiene(self):
        result, runner, _ = self.run_flow(MockLLM(lambda *args: None))
        self.assertEqual(result.status, "detenido")
        self.assertTrue(any(e.event == "respuesta" and "error" in e.output for e in runner.last_events))

    def test_fallo_del_llm_no_aborta_la_traza(self):
        def broken(*args):
            raise RuntimeError("modelo no disponible")
        result, runner, _ = self.run_flow(MockLLM(broken))
        self.assertEqual(result.status, "detenido")
        self.assertEqual(runner.last_events[-1].event, "fin")

    def test_metricas_se_capturan_en_cada_llamada_y_limites_por_etapa(self):
        class MeasuredLLM(MockLLM):
            def __init__(self):
                super().__init__([analyst(), FORMULATE, CANDIDATE, verifier()])
                self.limits = []
            def generate(self, prompt, adapter_on, max_new_tokens=None):
                raw = super().generate(prompt, adapter_on)
                self.limits.append(max_new_tokens)
                self.last_stats = SimpleNamespace(tokens_in=len(self.calls), tokens_out=2,
                                                 latency_ms=10.0, reached_limit=False)
                return raw
        config = OrchestratorConfig(token_limits=TokenLimits(analista=111, formulador_plan=222,
                                                             formulador_candidate=333, verificador=444))
        result, runner, llm = self.run_flow(MeasuredLLM(), config=config)
        self.assertEqual(result.tokens_total, 18)
        self.assertEqual(result.latency_ms_total, 40)
        self.assertEqual(llm.limits, [111, 222, 333, 444])
        responses = [e for e in runner.last_events if e.event == "respuesta"]
        self.assertEqual([e.tokens_in for e in responses], [1, 2, 3, 4])

    def test_no_sobrescribe_una_traza_anterior(self):
        self.trace.write_text("conservar", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.run_flow([])
        self.assertEqual(self.trace.read_text(encoding="utf-8"), "conservar")

    def test_entrada_y_variante_invalidas_no_invocan_el_modelo(self):
        runner = Orchestrator(MockLLM([]))
        for case in (dict(CASE, extra="dato reservado"), {"id": "x", "problem": "x"}, dict(CASE, problem="")):
            with self.subTest(case=case), self.assertRaises(ValueError):
                runner.run(case, trace_path=self.trace)
        with self.assertRaises(ValueError):
            runner.run(CASE, variant="otra", trace_path=self.trace)
        with self.assertRaises(ValueError):
            runner.run(CASE, run_id="../ruta", trace_path=self.trace)
        self.assertEqual(runner.llm.calls, [])

    def test_config_mapeada_resuelve_prompts_y_adapters_por_llamada(self):
        config = OrchestratorConfig.from_mapping({
            "model": {"adapter_enabled": {"analista": False, "formulador_plan": False,
                                             "formulador_candidate": True, "verificador": False}},
            "prompts": {"verificador": "prompts/verificador_v2.md"},
            "generation": {"do_sample": False, "max_new_tokens": {"analista": 1500}},
        })
        self.assertEqual(config.prompts.verificador, ROOT / "prompts/verificador_v2.md")
        self.assertFalse(config.adapters.verificador)
        self.assertEqual(config.token_limits.analista, 1500)
        for mapping in ({"model": {"id": "otro-modelo"}}, {"generation": {"do_sample": True}}):
            with self.assertRaises(ValueError):
                OrchestratorConfig.from_mapping(mapping)


if __name__ == "__main__":
    unittest.main()
