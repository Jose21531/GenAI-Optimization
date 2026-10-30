"""Pruebas del Formulador con MockLLM, sin GPU."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.analista import PROMPTS_DIR, AgentFormatError, load_prompt  # noqa: E402
from agents.formulador import (  # noqa: E402
    formatear_spec,
    formular,
    limpiar_candidate,
    separar_secciones,
)
from mock_llm import MockLLM, archivos_abiertos  # noqa: E402
from schemas import Issue, ProblemSpec  # noqa: E402

PROBLEMA = (
    "Una cooperativa cultiva tomates y lechugas. Cada hectárea de tomate deja 900 y cada "
    "hectárea de lechuga, 600. Se dispone de 40 hectáreas. Se desea maximizar la ganancia."
)
SPEC = ProblemSpec.model_validate({
    "case_id": "dev00",
    "sets": [{"name": "C", "description": "cultivos"}],
    "data": [{"name": "g", "description": "ganancia por hectárea", "indexed_by": ["C"]},
             {"name": "L", "description": "hectáreas disponibles", "unit": "hectáreas"}],
    "decisions": [{"description": "hectáreas cultivadas", "symbol": "x",
                   "indexed_by": ["C"], "domain": "continua"}],
    "objective": {"sense": "max", "description": "ganancia total"},
    "requirements": [
        {"id": "U1", "kind": "objective", "text": "Maximizar la ganancia"},
        {"id": "U2", "kind": "constraint", "text": "No superar las hectáreas"},
        {"id": "U3", "kind": "domain", "text": "Hectáreas no negativas"},
    ],
})
DECISION = (
    "DECISION: formular\n"
    "U1 -> \\max \\sum_{c\\in C} g_c x_c\n"
    "- U2 → \\sum_{c\\in C} x_c \\le L\n"
    "U9 -> inventada\n"
)
CANDIDATE = (
    "Conjuntos:\n\\(C\\): cultivos.\n\n"
    "Parámetros:\n\\(g_c\\): ganancia por hectárea.\n\\(L\\): hectáreas disponibles.\n\n"
    "Variables de decisión:\n\\(x_c\\ge 0\\): hectáreas cultivadas.\n\n"
    "Función objetivo:\n\\[\n\\max \\sum_{c\\in C} g_c x_c\n\\]\n\n"
    "Restricciones:\n\\[\n\\sum_{c\\in C} x_c \\le L\n\\]"
)
NOPLAN = PROMPTS_DIR / "formulador_v1_noplan.md"


def run(responses, **kwargs):
    llm = MockLLM(responses)
    options = dict(candidate_id="dev00-1", adapter_plan=False, adapter_candidate=True)
    options.update(kwargs)
    return llm, formular(llm, PROBLEMA, SPEC, **options)


class FormularTests(unittest.TestCase):
    def test_formula_con_plan_separado(self):
        llm, step = run([DECISION, "Aquí está la formulación:\n\n" + CANDIDATE])
        out = step.output
        self.assertEqual(out.action, "formulate")
        self.assertEqual([(p.requirement_id, p.equation) for p in out.plan],
                         [("U1", "\\max \\sum_{c\\in C} g_c x_c"), ("U2", "\\sum_{c\\in C} x_c \\le L"),
                          ("U9", "inventada")])
        self.assertIn("plan con IDs fuera del ProblemSpec: U9", step.warnings)
        self.assertIn("requisitos sin línea de plan: U3", step.warnings)
        self.assertEqual(out.draft.raw_text, CANDIDATE)
        self.assertEqual(out.draft.candidate_id, "dev00-1")
        self.assertTrue(out.draft.parse_ok, out.draft.parse_errors)
        self.assertEqual(out.draft.sections.sets, "\\(C\\): cultivos.")
        self.assertNotIn("->", out.draft.raw_text)

    def test_dos_llamadas_con_su_adapter_y_contenido(self):
        llm, step = run([DECISION, CANDIDATE])
        self.assertEqual([c.adapter_on for c in step.calls], [False, True])
        self.assertEqual([a for _, a in llm.calls], [False, True])
        self.assertEqual({c.prompt_version for c in step.calls}, {"formulador_v2"})
        decision_prompt, candidate_prompt = (c.prompt for c in step.calls)
        self.assertIn("U1 (objetivo): Maximizar la ganancia", decision_prompt)
        self.assertTrue(candidate_prompt.startswith(PROBLEMA))
        self.assertIn("U2 -> \\sum_{c\\in C} x_c \\le L", candidate_prompt)
        self.assertTrue(candidate_prompt.rstrip().endswith("sin obtener valores óptimos."))

    def test_plan_en_bucle_se_deduplica_y_acota(self):
        # Caso observado en la prueba temprana (dev07): la misma ecuación con IDs crecientes.
        bucle = "DECISION: formular\nU1 -> \\max g x\nU2 -> x \\le L\n" + "".join(
            f"U{i} -> \\sum_i p_i c_i \\neq 0\n" for i in range(3, 29))
        _, step = run([bucle, CANDIDATE])
        self.assertEqual([p.requirement_id for p in step.output.plan], ["U1", "U2", "U3"])
        self.assertIn("plan: 25 línea(s) con ecuación repetida descartada(s)", step.warnings)
        distintas = "DECISION: formular\n" + "".join(f"U{i} -> x_{i} \\le L\n" for i in range(1, 12))
        _, step = run([distintas, CANDIDATE])
        self.assertEqual(len(step.output.plan), 6)
        self.assertIn("plan truncado en 6 líneas (el doble de los requisitos)", step.warnings)

    def test_aclarar_hace_una_sola_llamada(self):
        raw = "DECISION: aclarar\nPREGUNTA: ¿El límite de 40 hectáreas es por cultivo o total?"
        llm, step = run([raw])
        self.assertEqual(len(llm.calls), 1)
        self.assertEqual(step.output.action, "clarify")
        self.assertEqual(step.output.question, "¿El límite de 40 hectáreas es por cultivo o total?")
        self.assertIsNone(step.output.draft)

    def test_decision_ausente_o_incompleta(self):
        _, step = run(["U1 -> \\max g x\nU2 -> x \\le L", CANDIDATE])
        self.assertEqual(step.output.action, "formulate")
        self.assertTrue(any("falta DECISION" in w for w in step.warnings))
        with self.assertRaises(AgentFormatError) as caught:
            run(["Voy a formular el modelo."])
        self.assertEqual(caught.exception.raw, "Voy a formular el modelo.")
        with self.assertRaisesRegex(AgentFormatError, "PREGUNTA"):
            run(["DECISION: aclarar"])

    def test_candidate_vacio_es_fallo_de_formato(self):
        with self.assertRaisesRegex(AgentFormatError, "vacío"):
            run([DECISION, "   \n"])

    def test_fallo_conserva_todas_las_llamadas(self):
        # Revisión del PR #4: la excepción solo guardaba la última respuesta.
        with self.assertRaises(AgentFormatError) as caught:
            run([DECISION, "   \n"])
        error = caught.exception
        self.assertEqual([c.raw for c in error.calls], [DECISION, "   \n"])
        self.assertEqual([c.adapter_on for c in error.calls], [False, True])
        self.assertIn("plan con IDs fuera del ProblemSpec: U9", error.warnings)
        self.assertEqual(error.raw, "   \n")

    def test_dudas_del_analista_llegan_a_ambos_prompts(self):
        # Revisión del PR #4: formatear_spec omitía uncertainties.
        duda = "No queda claro si el límite de 40 hectáreas es por cultivo o total."
        spec = SPEC.model_copy(update={"uncertainties": [duda]})
        llm = MockLLM([DECISION, CANDIDATE])
        formular(llm, PROBLEMA, spec, candidate_id="dev00-1", adapter_plan=False, adapter_candidate=True)
        for prompt, _ in llm.calls:
            self.assertIn(f"Dudas del Analista:\n- {duda}", prompt)
        _, sin_dudas = run([DECISION, CANDIDATE])
        self.assertNotIn("Dudas del Analista", sin_dudas.calls[0].prompt)

    def test_candidate_incompleto_no_lanza_y_se_marca(self):
        incompleto = CANDIDATE.replace("Función objetivo:", "Objetivo:")
        _, step = run([DECISION, incompleto + "\nU1 -> resto del plan"])
        draft = step.output.draft
        self.assertFalse(draft.parse_ok)
        self.assertIn("falta el encabezado Función objetivo:", draft.parse_errors)
        self.assertIn("el candidate contiene líneas de plan Uk ->", draft.parse_errors)

    def test_noplan_no_pide_ni_envia_plan(self):
        llm, step = run(["DECISION: formular", CANDIDATE], prompt_path=NOPLAN)
        decision_prompt, candidate_prompt = (c.prompt for c in step.calls)
        self.assertEqual(step.calls[0].prompt_version, "formulador_v1_noplan")
        self.assertEqual(step.output.plan, [])
        self.assertNotIn("->", decision_prompt)
        self.assertNotIn("Ecuaciones planificadas", candidate_prompt)
        self.assertEqual(step.output.draft.raw_text, CANDIDATE)
        self.assertEqual(step.warnings, [])

    def test_v1_sin_plan_avisa(self):
        _, step = run(["DECISION: formular", CANDIDATE])
        self.assertIn("el prompt pide plan, pero no llegó ninguna línea Uk ->", step.warnings)

    def test_revision_incluye_borrador_y_observaciones(self):
        issue = Issue(description="Falta el límite de hectáreas", requirement_id="U2",
                      location="Restricciones", suggestion="Agregar \\sum x_c \\le L")
        _, step = run([DECISION, CANDIDATE], previous_draft="Conjuntos:\nBORRADOR VIEJO",
                      observations=[issue, "Revisar dominios"])
        for call in step.calls:
            self.assertIn("BORRADOR VIEJO", call.prompt)
            self.assertIn("- U2 · Restricciones · Falta el límite de hectáreas "
                          "Corrección: Agregar \\sum x_c \\le L", call.prompt)
            self.assertIn("- Revisar dominios", call.prompt)
        _, primera = run([DECISION, CANDIDATE])
        self.assertNotIn("Borrador anterior", primera.calls[1].prompt)
        self.assertNotIn("Observaciones", primera.calls[1].prompt)


class CandidateParserTests(unittest.TestCase):
    def test_limpia_vallas_y_preambulo(self):
        raw = "Claro.\n```\n**Conjuntos:**\nC\n**Parametros:**\ng\n```"
        self.assertEqual(limpiar_candidate(raw), "**Conjuntos:**\nC\n**Parametros:**\ng")

    def test_tolera_acentos_y_markdown(self):
        text = ("### Conjuntos:\nC\nParametros:\ng\nVariables de decision:\nx\n"
                "Funcion objetivo: \\max g x\nRestricciones:\nx \\le L")
        sections, errors = separar_secciones(text)
        self.assertEqual(errors, [])
        self.assertEqual(sections.objective, "\\max g x")
        self.assertEqual(sections.constraints, "x \\le L")

    def test_detecta_orden_repeticion_y_vacios(self):
        desordenado = CANDIDATE.replace("Conjuntos:", "TMP:").replace("Restricciones:", "Conjuntos:")
        desordenado = desordenado.replace("TMP:", "Restricciones:")
        _, errors = separar_secciones(desordenado)
        self.assertIn("los encabezados no siguen el orden de la Entrega 2", errors)
        _, errors = separar_secciones(CANDIDATE + "\nRestricciones:\notra")
        self.assertIn("encabezado repetido: Restricciones:", errors)
        _, errors = separar_secciones(CANDIDATE.replace("\\(C\\): cultivos.", ""))
        self.assertIn("sección vacía: Conjuntos", errors)

    def test_resumen_del_spec_no_usa_encabezados_del_candidate(self):
        resumen = formatear_spec(SPEC)
        self.assertIn("x[C] continua: hectáreas cultivadas", resumen)
        self.assertIn("L hectáreas disponibles (hectáreas)", resumen)
        _, errors = separar_secciones(resumen)
        self.assertEqual(len(errors), 5)


class PromptFormuladorTests(unittest.TestCase):
    def test_secciones(self):
        base = {"decision", "candidate", "previous", "observations"}
        for version in ("formulador_v1.md", "formulador_v2.md"):
            self.assertEqual(set(load_prompt(PROMPTS_DIR / version)[1]), base | {"plan"})
        self.assertEqual(set(load_prompt(NOPLAN)[1]), base)

    def test_formular_solo_abre_prompts(self):
        with archivos_abiertos() as abiertos:
            run([DECISION, CANDIDATE])
        self.assertTrue(abiertos)
        self.assertTrue(all(p.is_relative_to(PROMPTS_DIR) for p in abiertos), abiertos)


if __name__ == "__main__":
    unittest.main()
