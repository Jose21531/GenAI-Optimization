"""Regresiones deterministas; no se usa ningún modelo de lenguaje."""

import copy
import sys
import unittest
from pathlib import Path
from typing import get_args

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mock_llm import archivos_abiertos
from schemas import CheckName, CoverageMap, DraftModel, ProblemSpec
from tools.audit_model import audit_model
from eval.audit_dev_fixtures import development_artifacts


def artifacts():
    spec = ProblemSpec.model_validate({
        "case_id": "audit-dev", "objective": {"sense": "max", "description": "utilidad"},
        "sets": [{"name": "I", "description": "productos"}],
        "data": [{"name": "c", "description": "utilidad", "indexed_by": ["I"]},
                 {"name": "H", "description": "capacidad"}],
        "requirements": [{"id": "U1", "kind": "objective", "text": "maximizar"},
                         {"id": "U2", "kind": "constraint", "text": "capacidad"},
                         {"id": "U3", "kind": "domain", "text": "no negatividad"}],
    })
    text = ("Conjuntos:\nI: productos.\nParámetros:\nc_i: utilidad, i \\in I.\nH: capacidad.\n"
            "Variables de decisión:\nx_i >= 0: producción, i \\in I.\n"
            "Función objetivo:\nmax sum_{i in I} c_i x_i\n"
            "Restricciones:\nsum_{i in I} x_i <= H")
    draft = DraftModel(candidate_id="audit-1", raw_text=text)
    coverage = CoverageMap.model_validate({"candidate_id": draft.candidate_id,
        "elements": [{"id": "O1", "kind": "objective", "excerpt": "max sum_{i in I} c_i x_i"},
                     {"id": "C1", "kind": "constraint", "excerpt": "sum_{i in I} x_i <= H"},
                     {"id": "D1", "kind": "domain", "excerpt": "x_i >= 0"}],
        "links": [{"requirement_id": "U1", "element_id": "O1"},
                  {"requirement_id": "U2", "element_id": "C1"},
                  {"requirement_id": "U3", "element_id": "D1"}]})
    return spec, draft, coverage


def checks(report, check):
    return [f for f in report.findings if f.check == check and f.status == "hallazgo"]


class AuditModelTests(unittest.TestCase):
    def test_ocho_controles_de_desarrollo_sin_falsos_hallazgos(self):
        fixtures = development_artifacts()
        self.assertEqual(set(fixtures), {f"dev{i:02}" for i in range(1, 9)})
        for case_id, args in fixtures.items():
            with self.subTest(case_id=case_id):
                report = audit_model(*args)
                self.assertEqual([f.model_dump() for f in report.findings if f.status == "hallazgo"], [])

    def test_modelo_soportado_sin_hallazgos_y_todos_los_chequeos_registrados(self):
        report = audit_model(*artifacts())
        self.assertEqual(set(report.checks_run), set(get_args(CheckName)))
        self.assertEqual(report.findings, [])

    def test_sin_lecturas_de_archivos_ni_mutaciones(self):
        args = artifacts()
        before = [a.model_dump() for a in args]
        with archivos_abiertos() as opened:
            audit_model(*args)
        self.assertEqual(opened, [])
        self.assertEqual(before, [a.model_dump() for a in args])

    def test_mapa_de_otro_borrador_no_cubre_requisitos(self):
        spec, draft, coverage = artifacts()
        coverage.candidate_id = "otro"
        report = audit_model(spec, draft, coverage)
        self.assertTrue(report.has_errors)
        self.assertEqual(len(checks(report, "requisito_sin_cubrir")), 3)

    def test_citas_inventadas_y_vinculos_inexistentes(self):
        spec, draft, coverage = artifacts()
        coverage.elements[1].excerpt = "ecuación inventada"
        coverage.links[0].element_id = "NO_EXISTE"
        report = audit_model(spec, draft, coverage)
        self.assertEqual(len(checks(report, "referencia_invalida")), 2)
        self.assertEqual({f.requirement_id for f in checks(report, "requisito_sin_cubrir")}, {"U1", "U2"})

    def test_ids_repetidos_y_tipo_incorrecto(self):
        spec, draft, coverage = artifacts()
        coverage.elements.append(coverage.elements[0].model_copy())
        coverage.links[1].element_id = "O1"
        report = audit_model(spec, draft, coverage)
        self.assertTrue(checks(report, "referencia_invalida"))
        self.assertTrue(checks(report, "cobertura_tipo_incorrecto"))

    def test_restriccion_sin_requisito_es_aviso(self):
        spec, draft, coverage = artifacts()
        coverage.links = coverage.links[:1] + coverage.links[2:]
        report = audit_model(spec, draft, coverage)
        f = checks(report, "restriccion_sin_requisito")[0]
        self.assertEqual(f.level, "aviso")
        self.assertEqual(f.location, "C1")

    def test_mapa_vacio_no_equivale_a_ausencia_de_restricciones(self):
        spec, draft, _ = artifacts()
        report = audit_model(spec, draft, CoverageMap(candidate_id=draft.candidate_id))
        self.assertEqual(len(checks(report, "requisito_sin_cubrir")), 3)
        self.assertTrue(any(f.check == "restriccion_sin_requisito" and f.status == "no_verificado"
                            for f in report.findings))

    def test_simbolo_no_declarado_y_variable_sin_dominio(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("c_i x_i", "c_i z_i").replace("x_i >= 0:", "x_i:")
        report = audit_model(spec, draft, coverage)
        self.assertIn("z", [f.symbol for f in checks(report, "simbolo_no_declarado")])
        self.assertEqual(checks(report, "variable_sin_dominio")[0].symbol, "x")

    def test_aridad_y_variables_no_usadas(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("x_i >= 0:", "y_i >= 0: producción auxiliar.\nx_i >= 0:")
        draft.raw_text = draft.raw_text.replace("c_i x_i", "c_i x_ij")
        report = audit_model(spec, draft, coverage)
        self.assertTrue(checks(report, "aridad_inconsistente"))
        self.assertIn("y", [f.symbol for f in checks(report, "variable_no_usada")])

    def test_parametro_no_usado_dato_sin_parametro_y_conjunto_invalido(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("H: capacidad.", "H: capacidad.\nB: dato extra.")
        spec.data[0].name = "d"
        spec.data[0].indexed_by = ["J"]
        report = audit_model(spec, draft, coverage)
        self.assertIn("B", [f.symbol for f in checks(report, "parametro_no_usado")])
        self.assertIn("d", [f.symbol for f in checks(report, "dato_sin_parametro")])
        self.assertTrue(checks(report, "indice_de_parametro_invalido"))

    def test_indices_sin_conjunto_no_se_dan_por_verificados(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("c_i: utilidad, i \\in I.", "c_i: utilidad.")
        report = audit_model(spec, draft, coverage)
        self.assertTrue(any(f.check == "indice_de_parametro_invalido" and f.status == "no_verificado"
                            for f in report.findings))

    def test_indice_libre_y_ligador_con_conjunto_no_declarado(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("sum_{i in I} x_i <= H", "x_j <= H")
        report = audit_model(spec, draft, coverage)
        self.assertIn("j", [f.symbol for f in checks(report, "indice_libre")])
        draft.raw_text = draft.raw_text.replace("sum_{i in I}", "sum_{i in Q}")
        report = audit_model(spec, draft, coverage)
        self.assertIn("Q", [f.symbol for f in checks(report, "simbolo_no_declarado")])

    def test_productos_potencias_y_divisiones_entre_variables(self):
        for expression in ("x_i x_i", "x_i * x_i", "x_i^2", "1 / x_i"):
            with self.subTest(expression=expression):
                spec, draft, coverage = artifacts()
                draft.raw_text = draft.raw_text.replace("c_i x_i", expression)
                report = audit_model(spec, draft, coverage)
                self.assertTrue(checks(report, "no_lineal"))
                self.assertTrue(all(f.level == "aviso" for f in checks(report, "no_lineal")))

    def test_producto_con_parentesis_no_queda_sin_aviso(self):
        for expression in ("c_i x_i (x_i)", "(x_i)(x_i)", "c_i x_i (1 - x_i)"):
            with self.subTest(expression=expression):
                spec, draft, coverage = artifacts()
                draft.raw_text = draft.raw_text.replace("c_i x_i", expression)
                report = audit_model(spec, draft, coverage)
                self.assertTrue([f for f in report.findings if f.check == "no_lineal"])

    def test_indice_fuera_del_alcance_de_la_sumatoria(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("c_i x_i", "c_i x_i - x_i")
        report = audit_model(spec, draft, coverage)
        self.assertIn("i", [f.symbol for f in checks(report, "indice_libre")])
        for inside in ("(c_i x_i - x_i)", r"\left(c_i x_i - x_i\right)"):
            with self.subTest(inside=inside):
                spec, draft, coverage = artifacts()
                draft.raw_text = draft.raw_text.replace("c_i x_i", inside)
                report = audit_model(spec, draft, coverage)
                self.assertFalse(checks(report, "indice_libre"))

    def test_latex_y_dominio_entero(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("sum_{i in I}", r"\sum_{i\in I}")
        draft.raw_text = draft.raw_text.replace("x_i >= 0", r"x_i \in \mathbb{Z}")
        report = audit_model(spec, draft, coverage)
        self.assertFalse(checks(report, "variable_sin_dominio"))
        self.assertFalse(checks(report, "indice_libre"))

    def test_parser_no_soportado_no_declara_que_los_chequeos_pasaron(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = "Notación libre sin encabezados ni declaraciones fiables"
        report = audit_model(spec, draft, coverage)
        unknown = [f for f in report.findings if f.status == "no_verificado"]
        self.assertEqual(len([f for f in unknown if f.check in get_args(CheckName)]), 10)
        self.assertTrue(all(f.level is None for f in unknown))

    def test_notacion_compleja_preserva_no_verificado(self):
        spec, draft, coverage = artifacts()
        draft.raw_text = draft.raw_text.replace("c_i x_i", r"\frac{x_i}{H}")
        report = audit_model(spec, draft, coverage)
        self.assertTrue(any(f.check == "no_lineal" and f.status == "no_verificado" for f in report.findings))


if __name__ == "__main__":
    unittest.main()
