"""Regresiones CPU de evaluación. No carga pesos, no genera puntajes oficiales."""

import ast
import copy
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import yaml

from eval.artifacts import REPO, load_development, load_predictions, read_jsonl
from eval.judge import JudgeFailure, JudgeReply, MockJudge, QwenFOM5Judge, TORCH_VERSION, load_qwen3
from eval.legacy import calibration_spec, kernel_source, load_kernel
from eval.pipeline import evaluate
from eval.provenance import generation_context, write_generation_manifest
from eval.run_eval import main, parse_sources, verify_archives
from eval.statistics import paired_difference
from schemas import RunResult


def parsed_for(item, score=0):
    return {"has_formulation": score > 0,
            "requirements": {r["id"]: "met" if score else "missing" for r in item["requirements"]},
            "scores": {d: score for d in load_kernel().DIMENSIONS}, "fatal_errors": []}


class CountingJudge(MockJudge):
    def __init__(self, fail_on=None, calibration_score=0):
        self.calls = []
        self.fail_on = fail_on
        self.calibration_score = calibration_score

    def judge(self, item, candidate):
        self.calls.append(item["id"])
        if item["id"] == self.fail_on:
            raise RuntimeError("interrupción simulada")
        if item["id"].startswith("opt_"):
            parsed = parsed_for(item, self.calibration_score)
            return JudgeReply(parsed, json.dumps(parsed), 0, 0)
        return super().judge(item, candidate)


class LegacyTests(unittest.TestCase):
    def test_juez_y_calibracion_identicos_al_notebook_publicado(self):
        notebook = json.loads((REPO / "Deliverable 2/Deliverable_2.ipynb").read_text(encoding="utf-8"))
        self.assertEqual(kernel_source(), "".join(notebook["cells"][15]["source"]))
        tree = ast.parse("".join(notebook["cells"][16]["source"]))
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "calibration_spec" for t in n.targets))
        self.assertEqual(calibration_spec(), [list(row) for row in ast.literal_eval(node.value)])

    def test_los_60_puntajes_archivados_se_reproducen_sin_incluir_diagnostico(self):
        result = verify_archives(REPO / "Deliverable 2")
        self.assertEqual(result["cases"], 30)
        self.assertTrue(result["all_60_archived_scores_reproduced"])
        self.assertAlmostEqual(result["means"]["baseline"], 0.5884)
        self.assertAlmostEqual(result["means"]["QLoRA"], 0.8023666666666667)
        difference = result["QLoRA_minus_baseline"]
        self.assertEqual((difference["improve"], difference["tie"], difference["worse"]), (14, 8, 8))
        self.assertAlmostEqual(difference["ci95"][0], -0.21357)
        self.assertAlmostEqual(difference["ci95"][1], 0.7007266666666662)

    def test_hash_rechaza_modificaciones_del_kernel(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "fom5_v2.py").write_text("SYSTEM_JUDGE = 'otro'", encoding="utf-8")
            with mock.patch("eval.legacy.VENDOR", folder), self.assertRaises(ValueError):
                load_kernel()

    def test_caps_originales_de_cobertura_y_ausencia_de_formulacion(self):
        item = {"requirements": [{"id": "R1", "kind": "objective"},
                                 {"id": "R2", "kind": "constraint"},
                                 {"id": "R3", "kind": "domain"}]}
        kernel = load_kernel()
        parsed = parsed_for(item, 5)
        self.assertEqual(kernel.aggregate_v2(item, parsed)["score_fom5_v2"], 5)
        parsed["requirements"]["R2"] = "missing"
        self.assertEqual(kernel.aggregate_v2(item, parsed)["score_fom5_v2"], 3.25)
        parsed["has_formulation"] = False
        self.assertEqual(kernel.aggregate_v2(item, parsed)["score_fom5_v2"], 1.5)

    def test_comparacion_rechaza_ids_distintos(self):
        with self.assertRaises(ValueError):
            paired_difference({"a": 1}, {"b": 1})


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.items = load_development()
        self.sources = {"full": self.predictions("full")}
        self.output = self.folder / "evaluation"

    def predictions(self, variant):
        path = self.folder / f"{variant}.jsonl"
        rows = [RunResult(problem_id=i, variant=variant, final_text="Formulación sintética para probar intercambio",
                          status="fallo_formato" if i == "dev08" else "aceptado", tokens_total=10,
                          latency_ms_total=20).model_dump(mode="json") for i in sorted(self.items)]
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        write_generation_manifest(path, variant, self.items, mode="development")
        return path

    def test_flujo_completo_calibra_primero_y_conserva_todos_los_estados(self):
        judge = CountingJudge()
        result = evaluate(self.sources, self.output, judge=judge)
        self.assertEqual(judge.calls[:4], [r[0] for r in calibration_spec()])
        self.assertEqual(judge.calls[4:], sorted(self.items))
        self.assertFalse(result["valid_experiment"])
        self.assertFalse(result["official_result"])
        self.assertEqual(result["execution_kind"], "mock")
        self.assertEqual(result["groups"]["full"]["generation_statuses"], {"aceptado": 7, "fallo_formato": 1})
        self.assertEqual(len(read_jsonl(self.output / "full/judgments.jsonl")), 8)
        self.assertEqual(json.loads((self.output / "evaluation.json").read_text())["status"], "complete")

    def test_calibracion_fallida_detiene_antes_de_evaluar_los_dev_cases(self):
        judge = CountingJudge(calibration_score=5)
        with self.assertRaisesRegex(ValueError, "Calibración"):
            evaluate(self.sources, self.output, judge=judge)
        self.assertEqual(judge.calls, [r[0] for r in calibration_spec()])
        self.assertFalse((self.output / "full/judgments.jsonl").exists())
        self.assertEqual(json.loads((self.output / "evaluation.json").read_text())["status"], "failed")

    def test_interrupcion_no_asigna_cero_y_reanuda_solo_los_casos_pendientes(self):
        with self.assertRaisesRegex(RuntimeError, "interrupción"):
            evaluate(self.sources, self.output, judge=CountingJudge(fail_on="dev03"))
        checkpoint = self.output / "full/judgments.jsonl"
        self.assertEqual([r["id"] for r in read_jsonl(checkpoint)], ["dev01", "dev02"])
        judge = CountingJudge()
        evaluate(self.sources, self.output, judge=judge)
        self.assertEqual(judge.calls[:4], [r[0] for r in calibration_spec()])
        self.assertEqual(judge.calls[4:], sorted(self.items)[2:])
        self.assertEqual(len(read_jsonl(checkpoint)), 8)
        self.assertTrue(any("error" in row for row in read_jsonl(self.output / "judge_calls.jsonl")))

    def test_cambio_de_salidas_rechaza_manifiesto_antes_de_llamar_al_juez(self):
        self.sources["full"].write_text(self.sources["full"].read_text() + " ", encoding="utf-8")
        judge = CountingJudge()
        with self.assertRaises(ValueError):
            evaluate(self.sources, self.output, judge=judge)
        self.assertEqual(judge.calls, [])

    def test_no_mezcla_identidades_de_backends_al_reanudar(self):
        evaluate(self.sources, self.output, judge=CountingJudge())
        judge = CountingJudge()
        judge.revision = "otro-backend"
        with self.assertRaisesRegex(ValueError, "otra evaluación"):
            evaluate(self.sources, self.output, judge=judge)
        self.assertEqual(judge.calls, [])

    def test_rechaza_checkpoints_duplicados_truncados_o_con_score_alterado(self):
        evaluate(self.sources, self.output, judge=CountingJudge())
        path = self.output / "full/judgments.jsonl"
        original = path.read_text(encoding="utf-8")
        changed = read_jsonl(path)
        changed[0]["score_fom5_v2"] = 4
        variants = [original + original.splitlines()[0] + "\n", original + '{"id":',
                    "".join(json.dumps(r) + "\n" for r in changed)]
        for text in variants:
            with self.subTest(text=text[:20]):
                path.write_text(text, encoding="utf-8")
                judge = CountingJudge()
                with self.assertRaises(ValueError):
                    evaluate(self.sources, self.output, judge=judge)
                self.assertEqual(judge.calls, [])

    def test_claves_ausentes_en_checkpoint_son_errores_de_formato(self):
        evaluate(self.sources, self.output, judge=CountingJudge())
        path = self.output / "full/judgments.jsonl"
        original = read_jsonl(path)
        for key in ("id", "judge_v2_raw", "fatal_errors_v2"):
            with self.subTest(key=key):
                rows = copy.deepcopy(original)
                rows[0].pop(key)
                path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
                judge = CountingJudge()
                with self.assertRaisesRegex(ValueError, key):
                    evaluate(self.sources, self.output, judge=judge)
                self.assertEqual(judge.calls, [])
        with contextlib.redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as caught:
                main(["evaluate", "--mode", "development", "--source", "full=" + str(self.sources["full"]),
                      "--output", str(self.output), "--mock"])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("Evaluación detenida", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())
        invalid_annotations = self.folder / "invalid-review.jsonl"
        invalid_annotations.write_text("{}\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as caught:
                main(["audit-summary", "--annotations", str(invalid_annotations)])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("falta el campo requerido", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_reanudar_con_ultima_fila_valida_sin_salto_final(self):
        with self.assertRaises(RuntimeError):
            evaluate(self.sources, self.output, judge=CountingJudge(fail_on="dev03"))
        checkpoint = self.output / "full/judgments.jsonl"
        checkpoint.write_bytes(checkpoint.read_bytes().rstrip(b"\n"))
        evaluate(self.sources, self.output, judge=CountingJudge())
        self.assertEqual(len(read_jsonl(checkpoint)), 8)

    def test_recuperacion_explicita_permite_reanudar_tras_linea_cortada(self):
        from eval.recovery import recover_jsonl_tail
        with self.assertRaises(RuntimeError):
            evaluate(self.sources, self.output, judge=CountingJudge(fail_on="dev03"))
        checkpoint = self.output / "full/judgments.jsonl"
        checkpoint.write_bytes(checkpoint.read_bytes() + b'{"id":"dev03","judge_v2_raw":"')
        with self.assertRaises(ValueError):
            evaluate(self.sources, self.output, judge=CountingJudge())
        recover_jsonl_tail(checkpoint)
        result = evaluate(self.sources, self.output, judge=CountingJudge())
        self.assertEqual(result["groups"]["full"]["n"], 8)

    def test_no_sobrescribe_un_directorio_sin_manifiesto(self):
        self.output.mkdir()
        (self.output / "conservar.txt").write_text("conservar", encoding="utf-8")
        with self.assertRaises(ValueError):
            evaluate(self.sources, self.output, judge=CountingJudge())
        self.assertEqual((self.output / "conservar.txt").read_text(), "conservar")

    def test_dev_compara_ablaciones_solo_con_ids_pareados(self):
        self.sources["no_plan"] = self.predictions("no_plan")
        result = evaluate(self.sources, self.output, judge=CountingJudge())
        self.assertEqual(result["paired_comparisons"]["no_plan"]["full"]["n"], 8)
        self.assertNotIn("baseline", result["groups"])

    def test_faltan_variantes_oficiales_y_no_se_invoca_el_juez(self):
        judge = CountingJudge()
        with self.assertRaisesRegex(ValueError, "cinco variantes"):
            evaluate(self.sources, self.output, mode="official", judge=judge)
        self.assertEqual(judge.calls, [])

    def test_no_admite_mock_como_resultado_oficial_incluso_con_preflight_simulado(self):
        with mock.patch("eval.pipeline.prepare", return_value=(self.items, {}, {}, {}, {})):
            with self.assertRaisesRegex(ValueError, "no admite MockJudge"):
                evaluate(self.sources, self.output, mode="official", judge=CountingJudge())

    def test_predicciones_incompletas_duplicadas_y_variante_incorrecta(self):
        rows = read_jsonl(self.sources["full"])
        wrong = copy.deepcopy(rows)
        wrong[0]["variant"] = "no_plan"
        infinite = copy.deepcopy(rows)
        infinite[0]["latency_ms_total"] = float("inf")
        for records in (rows[:-1], rows + [rows[0]], wrong, infinite):
            with self.subTest(count=len(records)):
                path = self.folder / "bad.jsonl"
                path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_predictions(path, "full", self.items)

    def test_parser_de_fuentes_no_admite_variantes_repetidas(self):
        self.assertEqual(parse_sources(["full=a.jsonl"]), {"full": Path("a.jsonl")})
        for values in (["full=a", "full=b"], ["arbitraria=a"], ["full"]):
            with self.assertRaises(ValueError):
                parse_sources(values)


class FreezeTests(unittest.TestCase):
    def test_config_y_codigo_modificados_despues_del_tag_no_se_admiten(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            root = repo / "Deliverable 3"
            (root / "config").mkdir(parents=True)
            (root / "prompts").mkdir()
            (root / "prompts/verificador_v2.md").write_text("prompt", encoding="utf-8")
            for name in ("schemas.py", "model.py", "orchestrator.py", "run.py"):
                (root / name).write_text("# módulo congelado\n", encoding="utf-8")
            config = {"model": {"id": "Qwen/Qwen2.5-1.5B-Instruct",
                       "revision": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
                       "adapter_sha256": "68583e9dffa6647a5c0b89a74168363264daf246e4337ef1ae0c644243391151"},
                      "generation": {"do_sample": False},
                      "prompts": {"verificador": "prompts/verificador_v2.md"}}
            frozen = root / "config/frozen.yaml"
            frozen.write_text(yaml.safe_dump(config), encoding="utf-8")
            for args in (["init", "-q"], ["add", "."],
                         ["-c", "user.name=Eval Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "freeze"],
                         ["tag", "v3-freeze"]):
                subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
            context = generation_context("official", root)
            self.assertTrue(context["freeze_commit"])
            (root / "run.py").write_text("# cambio posterior\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "después de v3-freeze"):
                generation_context("official", root)

    def test_no_se_inventa_una_configuracion_congelada(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "frozen.yaml"):
                generation_context("official", Path(temp))


class BackendTests(unittest.TestCase):
    def test_rechaza_otras_gpu_y_torch_distinto_antes_de_cargar_pesos(self):
        for available, device, version, message in (
                (False, "CPU", TORCH_VERSION, "T4"),
                (True, "NVIDIA A100", TORCH_VERSION, "T4"),
                (True, "Tesla T4", "otra-version", TORCH_VERSION)):
            torch = SimpleNamespace(__version__=version,
                cuda=SimpleNamespace(is_available=lambda: available, get_device_name=lambda _: device))
            with self.subTest(device=device, version=version), mock.patch.dict(sys.modules, {"torch": torch}):
                with self.assertRaisesRegex(RuntimeError, message.replace("+", r"\+")):
                    load_qwen3()

    def backend(self, outputs, length=10, fallback=False):
        class Tensor:
            shape = (1, length)
            def to(self, device):
                return self
        class Generated:
            shape = (3,)
            def __init__(self, raw):
                self.raw = raw
        class Output:
            def __init__(self, raw):
                self.generated = Generated(raw)
            def __getitem__(self, key):
                return self.generated
        class Tokenizer:
            eos_token_id = 42
            def apply_chat_template(self, messages, **kwargs):
                if fallback and "enable_thinking" in kwargs:
                    raise TypeError("plantilla antigua")
                self.options = kwargs
                return json.dumps(messages)
            def __call__(self, text, **kwargs):
                return {"input_ids": Tensor()}
            def decode(self, generated, **kwargs):
                return generated.raw
        class Model:
            device = "cpu"
            def __init__(self):
                self.calls = []
            def generate(self, **kwargs):
                self.calls.append(kwargs)
                return Output(outputs[len(self.calls) - 1])
        torch = SimpleNamespace(inference_mode=lambda: lambda function: function,
                                cuda=SimpleNamespace(is_available=lambda: False))
        model, tokenizer = Model(), Tokenizer()
        return QwenFOM5Judge(model, tokenizer, torch), model, tokenizer

    def test_se_conservan_limites_decodificacion_y_reintento_originales(self):
        item = next(iter(load_development().values()))
        raw = json.dumps(parsed_for(item))
        backend, model, tokenizer = self.backend(["JSON inválido", raw])
        reply = backend.judge(item, "candidate")
        self.assertEqual(len(model.calls), 2)
        self.assertEqual(len(reply.attempts), 2)
        self.assertEqual(tokenizer.options["enable_thinking"], False)
        self.assertEqual(model.calls[0]["max_new_tokens"], 600)
        self.assertEqual(model.calls[0]["do_sample"], False)
        self.assertEqual(reply.attempts[0]["raw"], "JSON inválido")
        self.assertIn("La salida anterior no pudo parsearse", reply.attempts[1]["messages"][-1]["content"])

    def test_prompt_demasiado_largo_no_se_trunca(self):
        backend, model, _ = self.backend([], length=12001)
        with self.assertRaises(JudgeFailure) as caught:
            backend.judge(next(iter(load_development().values())), "candidate")
        self.assertIn("No se truncó", str(caught.exception))
        self.assertEqual(model.calls, [])

    def test_dos_fallos_conservan_ambas_salidas_sin_inventar_un_score(self):
        backend, model, _ = self.backend(["mal", "también mal"])
        with self.assertRaises(JudgeFailure) as caught:
            backend.judge(next(iter(load_development().values())), "candidate")
        self.assertEqual(len(model.calls), 2)
        self.assertEqual([a["raw"] for a in caught.exception.attempts], ["mal", "también mal"])

    def test_plantilla_antigua_usa_el_fallback_original(self):
        item = next(iter(load_development().values()))
        backend, _, tokenizer = self.backend([json.dumps(parsed_for(item))], fallback=True)
        backend.judge(item, "candidate")
        self.assertNotIn("enable_thinking", tokenizer.options)


if __name__ == "__main__":
    unittest.main()
