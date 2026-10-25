"""Formato, aislamiento y novedad de los casos de desarrollo."""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.extract_data_spans import extract_data_spans  # noqa: E402

DEV = ROOT / "dev_cases"
MAX_OVERLAP = 0.10


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def trigrams(text):
    words = re.findall(r"\w+", text.lower())
    return {tuple(words[i:i + 3]) for i in range(len(words) - 2)}


def overlap(a, b):
    x, y = trigrams(a), trigrams(b)
    return len(x & y) / len(x | y)


class DevCasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = read_jsonl(DEV / "inputs.jsonl")
        cls.refs = {r["id"]: r for r in read_jsonl(DEV / "reference" / "dev_reference.jsonl")}
        cls.official = {r["id"]: r["problem"]
                        for r in read_jsonl(ROOT / "data" / "benchmark_30_generation_only.jsonl")}

    def test_entradas_tienen_solo_campos_de_generacion(self):
        self.assertEqual([c["id"] for c in self.inputs], [f"dev0{i}" for i in range(1, 9)])
        for case in self.inputs:
            self.assertEqual(set(case), {"id", "title", "problem"})
            self.assertTrue(case["problem"].strip())

    def test_referencias_completas(self):
        self.assertEqual(set(self.refs), {c["id"] for c in self.inputs})
        for ref in self.refs.values():
            kinds = [r["kind"] for r in ref["requirements"]]
            self.assertEqual(kinds.count("objective"), 1, ref["id"])
            self.assertTrue(set(kinds) <= {"objective", "constraint", "domain"})
            self.assertEqual([r["id"] for r in ref["requirements"]],
                             [f"R{i}" for i in range(1, len(kinds) + 1)])

    def test_distractores_presentes_y_detectados_como_candidatos(self):
        problems = {c["id"]: c["problem"] for c in self.inputs}
        con_distractor = [i for i, r in self.refs.items() if r["distractors"]]
        self.assertGreaterEqual(len(con_distractor), 1)
        for case_id in con_distractor:
            spans = extract_data_spans(problems[case_id])
            for distractor in self.refs[case_id]["distractors"]:
                self.assertIn(distractor, problems[case_id])
                number = re.search(r"\d+", distractor)
                if number:
                    self.assertIn(number.group(0), [s.text for s in spans], (case_id, distractor))

    def test_casos_nuevos_frente_al_benchmark(self):
        for case in self.inputs:
            for official_id, problem in self.official.items():
                self.assertLess(overlap(case["problem"], problem), MAX_OVERLAP,
                                (case["id"], official_id))

    def test_dev02_distinto_de_opt02(self):
        dev02 = next(c for c in self.inputs if c["id"] == "dev02")
        self.assertLess(overlap(dev02["problem"], self.official["opt_02"]), 0.05)
        self.assertIn("opt_02", self.refs["dev02"]["notes"])


if __name__ == "__main__":
    unittest.main()
