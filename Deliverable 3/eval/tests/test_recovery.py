"""Recuperación explícita de colas truncadas: no elimina registros válidos."""

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eval.artifacts import read_jsonl
from eval.pipeline import _append
from eval.recovery import recover_jsonl_tail
from eval.run_eval import main


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.path = self.folder / "judgments.jsonl"
        self.prefix = b'{"id":"dev01"}\n{"id":"dev02"}\n'

    def test_recupera_solo_cola_y_preserva_respaldo_y_registro(self):
        original = self.prefix + b'{"id":"dev03","judge_v2_raw":"'
        self.path.write_bytes(original)
        event = recover_jsonl_tail(self.path)
        self.assertEqual(self.path.read_bytes(), self.prefix)
        self.assertEqual((self.folder / event["backup"]).read_bytes(), original)
        self.assertEqual(event["original_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(event["discarded_bytes"], len(original) - len(self.prefix))
        self.assertEqual(event["retained_records"], 2)
        self.assertEqual(json.loads(Path(event["recovery_log"]).read_text(encoding="utf-8"))["status"], "recovered")

    def test_error_intermedio_no_modifica_archivo_ni_crea_respaldo(self):
        original = b'{"id":"dev01"}\nno es JSON\n{"id":'
        self.path.write_bytes(original)
        with self.assertRaises(ValueError):
            recover_jsonl_tail(self.path)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.folder.iterdir()), [self.path])

    def test_registro_valido_sin_salto_final_no_se_descarta(self):
        original = b'{"id":"dev01"}'
        self.path.write_bytes(original)
        with self.assertRaises(ValueError):
            recover_jsonl_tail(self.path)
        self.assertEqual(self.path.read_bytes(), original)
        _append(self.path, {"id": "dev02"})
        self.assertEqual(read_jsonl(self.path), [{"id": "dev01"}, {"id": "dev02"}])

    def test_sintaxis_invalida_completa_no_se_confunde_con_truncamiento(self):
        for tail in (b'bad json', b'{"id":}', b'{"id":"x",}', b'[]', b'{"id":\n', b'\xff'):
            with self.subTest(tail=tail):
                original = self.prefix + tail
                self.path.write_bytes(original)
                with self.assertRaises(ValueError):
                    recover_jsonl_tail(self.path)
                self.assertEqual(self.path.read_bytes(), original)

    def test_recupera_un_caracter_utf8_cortado_al_final(self):
        original = self.prefix + b'{"text":"' + "🚀".encode("utf-8")[:2]
        self.path.write_bytes(original)
        recover_jsonl_tail(self.path)
        self.assertEqual(self.path.read_bytes(), self.prefix)

    def test_truncamiento_de_literales_numeros_y_escape_unicode(self):
        for tail in (b'{"a":tru', b'{"a":nul', b'{"a":1e+', b'{"a":-', b'{"a":"\\u00'):
            with self.subTest(tail=tail):
                self.path.write_bytes(self.prefix + tail)
                recover_jsonl_tail(self.path)
                self.assertEqual(self.path.read_bytes(), self.prefix)

    def test_cli_solicita_recuperacion_explicita_y_devuelve_log(self):
        self.path.write_bytes(self.prefix + b'{"id":')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            main(["recover-jsonl", "--path", str(self.path)])
        self.assertEqual(json.loads(output.getvalue())["status"], "recovered")


if __name__ == "__main__":
    unittest.main()
