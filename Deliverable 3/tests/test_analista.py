"""Pruebas del Analista y de extract_data_spans con MockLLM, sin GPU."""

import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.analista import (  # noqa: E402
    PROMPTS_DIR,
    AgentFormatError,
    analizar,
    extraer_json,
    load_prompt,
)
from mock_llm import MockLLM  # noqa: E402
from tools.extract_data_spans import extract_data_spans, localizar_cita  # noqa: E402

PROBLEMA = (
    "Una panadería con 25 años de historia elabora pan y queques. Cada kilo de pan "
    "deja una utilidad de 1,5 y cada kilo de queque, 4. El horno funciona a lo más "
    "30 horas por semana; un kilo de pan requiere 0,2 horas de horno y uno de queque, "
    "0,5. Se deben producir al menos 100 kilos de pan. Se desea maximizar la utilidad."
)
NOEVIDENCE = PROMPTS_DIR / "analista_v3_noevidence.md"
ANALISTA_PROMPTS = sorted(PROMPTS_DIR.glob("analista_v*.md"))


def spec_respuesta(**cambios):
    spec = {
        "case_id": "otro_id",
        "sets": [{"name": "P", "description": "productos",
                  "evidence": {"text": "elabora pan y queques"}}],
        "data": [
            {"name": "u", "description": "utilidad por kilo", "indexed_by": ["P"],
             "unit": "por kilo", "evidence": {"text": "Cada kilo de pan deja una utilidad de 1,5"}},
            {"name": "H", "description": "horas de horno disponibles", "unit": "horas",
             "evidence": {"text": "a lo más 30 horas por semana"}},
        ],
        "decisions": [{"description": "kilos producidos", "symbol": "x",
                       "indexed_by": ["P"], "domain": "continua"}],
        "objective": {"sense": "max", "description": "utilidad total",
                      "evidence": {"text": "Se desea maximizar la utilidad"}},
        "requirements": [
            {"id": "U1", "kind": "objective", "text": "Maximizar la utilidad",
             "evidence": {"text": "Se desea maximizar la utilidad"}},
            {"id": "U2", "kind": "constraint", "text": "Horas de horno",
             "evidence": {"text": "El horno funciona a lo más 30 horas"}},
            {"id": "U3", "kind": "constraint", "text": "Mínimo de pan",
             "evidence": {"text": "Se deben fabricar 100 kilos"}},  # cita inventada
        ],
        "uncertainties": [],
    }
    spec.update(cambios)
    return spec


def deliver(**cambios):
    return json.dumps({"action": "deliver", "spec": spec_respuesta(**cambios)},
                      ensure_ascii=False)


class ExtraerJsonTests(unittest.TestCase):
    def test_vallas_y_prosa(self):
        raw = 'Claro, aquí está:\n```json\n{"action": "reread", "reason": "x"}\n```\nListo.'
        self.assertEqual(extraer_json(raw), {"action": "reread", "reason": "x"})

    def test_llaves_dentro_de_strings_y_previas(self):
        raw = r'Dominio \{0,1\}. {"a": "texto con } y {", "b": {"c": 1}}'
        self.assertEqual(extraer_json(raw), {"a": "texto con } y {", "b": {"c": 1}})

    def test_reparaciones_menores(self):
        raw = '{"a": [1, 2,], "b": True, "c": None, “d”: "\\sum x"}'
        self.assertEqual(extraer_json(raw), {"a": [1, 2], "b": True, "c": None, "d": "\\sum x"})

    def test_string_partido_sin_coma(self):
        # Cita partida en dos strings sin coma, observada en dev01.
        partido = '{"evidence": {"text": "aporta 0,10 kg de grasa;"\n  "el aceite, 0,95 kg"}}'
        self.assertEqual(extraer_json(partido),
                         {"evidence": {"text": "aporta 0,10 kg de grasa; el aceite, 0,95 kg"}})

    def test_truncado_o_ausente(self):
        with self.assertRaisesRegex(ValueError, "incompleto"):
            extraer_json('{"action": "deliver", "spec": {"sets": [')
        # Truncado después de objetos internos completos: no debe devolver uno de ellos.
        with self.assertRaisesRegex(ValueError, "incompleto"):
            extraer_json('```json\n{"action": "deliver", "spec": {"sets": [{"name": "I"}], "data": [')
        with self.assertRaisesRegex(ValueError, "no se encontró"):
            extraer_json("Conjuntos:\nI: productos")


class AnalistaTests(unittest.TestCase):
    def test_deliver_valida_y_ubica_citas(self):
        llm = MockLLM([deliver()])
        step = analizar(llm, "dev01", PROBLEMA, adapter_on=False)
        spec = step.output.spec
        self.assertEqual(step.output.action, "deliver")
        self.assertEqual(spec.case_id, "dev01")
        self.assertEqual(spec.requirement_ids(), ["U1", "U2", "U3"])
        for evidence in [spec.sets[0].evidence, spec.data[0].evidence, spec.requirements[1].evidence]:
            self.assertEqual(PROBLEMA[evidence.start:evidence.end], evidence.text)
        inventada = spec.requirements[2].evidence
        self.assertIsNone(inventada.start)
        self.assertTrue(any("no encontrada" in w and "requirements[2]" in w for w in step.warnings))

    def test_registra_llamada_y_adapter(self):
        for adapter_on in (False, True):
            llm = MockLLM([deliver()])
            step = analizar(llm, "dev01", PROBLEMA, adapter_on=adapter_on)
            self.assertEqual(llm.calls[0][1], adapter_on)
            call = step.calls[0]
            self.assertEqual((call.prompt_version, call.adapter_on), ("analista_v3", adapter_on))
            self.assertIn(PROBLEMA, call.prompt)
            self.assertEqual(call.raw, deliver())

    def test_reread_sin_spans(self):
        llm = MockLLM(['{"action": "reread", "reason": "no ubico las horas por kilo"}'])
        step = analizar(llm, "dev01", PROBLEMA, adapter_on=False)
        self.assertEqual(step.output.action, "reread")
        self.assertIsNone(step.output.spec)
        self.assertNotIn("extract_data_spans. Son candidatos", llm.calls[0][0])

    def test_reread_despues_de_spans_es_fallo_de_formato(self):
        llm = MockLLM(['{"action": "reread", "reason": "otra vez"}'])
        with self.assertRaises(AgentFormatError) as caught:
            analizar(llm, "dev01", PROBLEMA, adapter_on=False,
                     spans=extract_data_spans(PROBLEMA))
        self.assertIn("otra vez", caught.exception.raw)

    def test_spans_son_candidatos_en_el_prompt(self):
        llm = MockLLM([deliver()])
        analizar(llm, "dev01", PROBLEMA, adapter_on=False, spans=extract_data_spans(PROBLEMA))
        prompt = llm.calls[0][0]
        self.assertIn("Son candidatos", prompt)
        self.assertIn('"25" (valor 25, unidad años)', prompt)
        self.assertIn('"0,2" (valor 0.2, unidad horas)', prompt)

    def test_question_solo_si_hay_aclaracion(self):
        llm = MockLLM([deliver(), deliver()])
        first = analizar(llm, "dev01", PROBLEMA, adapter_on=False)
        analizar(llm, "dev01", PROBLEMA, adapter_on=False, question="¿El mínimo es por semana?",
                 previous_spec=first.output.spec)
        self.assertNotIn("aclaración", llm.calls[0][0])
        prompt = llm.calls[1][0]
        self.assertIn("¿El mínimo es por semana?", prompt)
        # El análisis anterior llega compacto, sin case_id ni offsets.
        self.assertIn('"text": "Horas de horno"', prompt)
        self.assertNotIn('"case_id"', prompt)
        self.assertNotIn('"start"', prompt)

    def test_aclaracion_exige_el_analisis_anterior(self):
        with self.assertRaisesRegex(ValueError, "previous_spec"):
            analizar(MockLLM([deliver()]), "dev01", PROBLEMA, adapter_on=False, question="¿?")

    def test_salida_con_formato_de_formulacion_falla(self):
        raw = "Conjuntos:\n\\(P\\): productos.\n\nParámetros:\n\\(u_i\\): utilidad."
        with self.assertRaises(AgentFormatError) as caught:
            analizar(MockLLM([raw]), "dev01", PROBLEMA, adapter_on=True)
        self.assertEqual(caught.exception.raw, raw)
        self.assertEqual(caught.exception.prompt_version, "analista_v3")

    def test_spec_invalido_falla(self):
        with self.assertRaisesRegex(AgentFormatError, "AnalystOutput"):
            analizar(MockLLM([deliver(requirements=[])]), "dev01", PROBLEMA, adapter_on=False)
        with self.assertRaises(AgentFormatError):
            analizar(MockLLM(['{"action": "reread"}']), "dev01", PROBLEMA, adapter_on=False)

    def test_normaliza_formas_frecuentes(self):
        spec = spec_respuesta(
            requirements=[{"id": "R1", "kind": "objetivo", "text": "Maximizar"},
                          {"id": 2, "kind": "restricción", "text": "Horno"}],
            objective={"sense": "maximizar", "description": "utilidad"},
            decisions=[{"description": "kilos", "indexed_by": "P", "domain": "continuo"}],
            uncertainties=None,
            reference_model="no debe pasar",
        )
        raw = json.dumps({"action": "entregar", "spec": spec}, ensure_ascii=False)
        step = analizar(MockLLM([raw]), "dev01", PROBLEMA, adapter_on=False)
        out = step.output.spec
        self.assertEqual(out.requirement_ids(), ["U1", "U2"])
        self.assertEqual([r.kind for r in out.requirements], ["objective", "constraint"])
        self.assertEqual(out.objective.sense, "max")
        self.assertEqual((out.decisions[0].indexed_by, out.decisions[0].domain), (["P"], "continua"))
        self.assertIn("clave descartada: spec.reference_model", step.warnings)

    def test_spec_aplanado_y_cita_normalizada(self):
        spec = spec_respuesta(objective={"sense": "max", "description": "utilidad",
                                         "evidence": "se desea  MAXIMIZAR la utilidad."})
        raw = json.dumps({"action": "deliver", **spec}, ensure_ascii=False)
        step = analizar(MockLLM([raw]), "dev01", PROBLEMA, adapter_on=False)
        self.assertEqual(step.output.spec.objective.evidence.text, "Se desea maximizar la utilidad.")
        self.assertTrue(any("normalizada" in w for w in step.warnings))

    def test_noevidence_no_pide_citas(self):
        sin_citas = spec_respuesta()
        for key in ("sets", "data", "requirements"):
            for item in sin_citas[key]:
                item.pop("evidence", None)
        sin_citas["objective"].pop("evidence")
        llm = MockLLM([json.dumps({"action": "deliver", "spec": sin_citas})])
        step = analizar(llm, "dev01", PROBLEMA, adapter_on=False, prompt_path=NOEVIDENCE)
        self.assertEqual(step.calls[0].prompt_version, "analista_v3_noevidence")
        self.assertNotIn("evidence", llm.calls[0][0])
        self.assertTrue(all(r.evidence is None for r in step.output.spec.requirements))


class PromptTests(unittest.TestCase):
    def test_prompts_cargan_y_aceptan_signos_pesos(self):
        for path in ANALISTA_PROMPTS:
            version, sections = load_prompt(path)
            self.assertEqual(version, path.stem)
            self.assertEqual(set(sections), {"user", "spans", "question"})
            texto = "Cuesta $ 10 por hora y US$5 por kilo."
            prompt = sections["user"].substitute(problem=texto, spans_block="", question_block="")
            self.assertIn(texto, prompt)
            self.assertNotIn("# analista", prompt)

    def test_prompts_dicen_que_los_spans_son_candidatos(self):
        for path in ANALISTA_PROMPTS:
            _, sections = load_prompt(path)
            spans = sections["spans"].template
            self.assertIn("candidatos", spans)
            self.assertIn("no afecta decisiones, objetivo ni restricciones", spans)


class ExtractDataSpansTests(unittest.TestCase):
    def test_notacion_espanola_y_unidades(self):
        texto = ("Barrio Norte está a 1,3 km; Centro tiene 30 mil habitantes. Se fabrican "
                 "1.200 unidades con un 15% de merma, a $ 10 por hora y 2.5 kg por lote. "
                 "Se instalan dos centros desde 2019.")
        spans = {s.text: s for s in extract_data_spans(texto)}
        esperado = {
            "1,3": (1.3, "km"), "30 mil": (30000, "habitantes"), "1.200": (1200, "unidades"),
            "15%": (15, "%"), "$ 10": (10, "$"), "2.5": (2.5, "kg"),
            "dos": (2, "centros"), "2019": (2019, None),
        }
        self.assertEqual({k: (spans[k].value, spans[k].unit) for k in esperado}, esperado)
        for span in spans.values():
            self.assertEqual(texto[span.start:span.end], span.text)

    def test_ignora_identificadores(self):
        texto = "Los productos P1 y P2 usan el recurso R3 y 90 m3 de agua (familia F01_02)."
        self.assertEqual([s.text for s in extract_data_spans(texto)], ["90"])

    def test_localizar_cita(self):
        start, end = localizar_cita(PROBLEMA, "elabora pan")
        self.assertEqual(PROBLEMA[start:end], "elabora pan")
        tolerante = localizar_cita(PROBLEMA, '"el HORNO funciona\n a lo más."')
        self.assertEqual(PROBLEMA[tolerante[0]:tolerante[1]], "El horno funciona a lo más")
        self.assertIsNone(localizar_cita(PROBLEMA, "se venden tortas"))
        self.assertIsNone(localizar_cita(PROBLEMA, "  "))


PROHIBIDO = re.compile(
    r"Deliverable[ %_]*2|benchmark_30|reference_model|casos_benchmark|_fom5"
    r"|judge_v2|dev_cases[\\/\"' ,]*reference",
    re.IGNORECASE,
)


class AislamientoTests(unittest.TestCase):
    """Generación no lee gold del benchmark ni referencias de dev_cases."""

    def test_codigo_y_prompts_no_mencionan_gold(self):
        archivos = [p for carpeta in ("agents", "tools", "prompts")
                    for p in (ROOT / carpeta).rglob("*") if p.suffix in {".py", ".md"}]
        self.assertTrue(any(p.name == "analista.py" for p in archivos))
        hallazgos = [f"{p.relative_to(ROOT)}: {m.group(0)}"
                     for p in archivos
                     for m in PROHIBIDO.finditer(p.read_text(encoding="utf-8"))]
        self.assertEqual(hallazgos, [])

    def test_analizar_solo_abre_prompts(self):
        abiertos = []
        original = io.open

        def registrar(file, *args, **kwargs):
            abiertos.append(Path(file).resolve())
            return original(file, *args, **kwargs)

        with mock.patch("io.open", side_effect=registrar):
            analizar(MockLLM([deliver()]), "dev01", PROBLEMA, adapter_on=False,
                     spans=extract_data_spans(PROBLEMA))
        self.assertTrue(abiertos, "no se registró la lectura del prompt")
        self.assertTrue(all(p.is_relative_to(PROMPTS_DIR) for p in abiertos), abiertos)


if __name__ == "__main__":
    unittest.main()
