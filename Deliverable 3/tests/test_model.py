"""Pruebas de model.py sin descargar el modelo; las de generate requieren torch."""

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import model  # noqa: E402

HAS_TORCH = importlib.util.find_spec("torch") is not None


class AdapterZipTests(unittest.TestCase):
    def make_zip(self, folder, names):
        path = Path(folder) / "adapter.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name in names:
                archive.writestr(name, "{}")
        return path

    def test_rechaza_hash_distinto(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make_zip(folder, model.ADAPTER_FILES)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                model.extract_adapter(path, Path(folder) / "out")

    def test_extrae_si_hash_y_contenido_coinciden(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make_zip(folder, model.ADAPTER_FILES)
            out = model.extract_adapter(path, Path(folder) / "out", model.sha256_file(path))
            self.assertEqual({p.name for p in out.iterdir()}, model.ADAPTER_FILES)

    def test_rechaza_contenido_inesperado(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make_zip(folder, model.ADAPTER_FILES | {"extra.txt"})
            with self.assertRaisesRegex(ValueError, "contenido"):
                model.extract_adapter(path, Path(folder) / "out", model.sha256_file(path))

    def test_adapter_on_sin_adapter_falla_antes_de_generar(self):
        llm = model.QwenLLM(object(), object(), has_adapter=False)
        with self.assertRaisesRegex(ValueError, "sin adapter"):
            llm.generate("hola", adapter_on=True)


@unittest.skipUnless(HAS_TORCH, "requiere torch")
class GenerateTests(unittest.TestCase):
    def setUp(self):
        import torch

        class Batch(dict):
            def to(self, device):
                return self

        class Tokenizer:
            eos_token_id = 0

            def __init__(self):
                self.messages = None

            def apply_chat_template(self, messages, tokenize, add_generation_prompt):
                self.messages = messages
                assert tokenize is False and add_generation_prompt is True
                return "<plantilla>" + messages[0]["content"]

            def __call__(self, text, return_tensors, add_special_tokens):
                assert add_special_tokens is False
                return Batch(input_ids=torch.tensor([[1, 2, 3]]))

            def decode(self, ids, skip_special_tokens):
                return " " + ",".join(str(int(i)) for i in ids) + " "

        class Model:
            device = "cpu"

            def __init__(self):
                self.adapter_enabled = True
                self.calls = []

            @contextmanager
            def disable_adapter(self):
                self.adapter_enabled = False
                yield
                self.adapter_enabled = True

            def generate(self, input_ids, max_new_tokens, do_sample, pad_token_id):
                self.calls.append((self.adapter_enabled, max_new_tokens, do_sample))
                return torch.tensor([[1, 2, 3, 7, 8]])

        self.tokenizer, self.model = Tokenizer(), Model()
        self.llm = model.QwenLLM(self.model, self.tokenizer, has_adapter=True, max_new_tokens=50)

    def test_un_mensaje_user_y_solo_tokens_nuevos(self):
        self.assertEqual(self.llm.generate("enunciado", adapter_on=True), "7,8")
        self.assertEqual(self.tokenizer.messages, [{"role": "user", "content": "enunciado"}])
        stats = self.llm.last_stats
        self.assertEqual((stats.tokens_in, stats.tokens_out, stats.reached_limit), (3, 2, False))

    def test_apaga_el_adapter_solo_cuando_se_pide(self):
        self.llm.generate("a", adapter_on=False)
        self.llm.generate("b", adapter_on=True, max_new_tokens=2)
        self.assertEqual(self.model.calls, [(False, 50, False), (True, 2, False)])
        self.assertTrue(self.model.adapter_enabled)
        self.assertTrue(self.llm.last_stats.reached_limit)


if __name__ == "__main__":
    unittest.main()
