"""Reaggregate every new raw judge JSON with the preserved FOM-5 v2 function."""
from pathlib import Path
import csv
import json
import math

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'results/colab/final/user_only_run01/evaluation/qlora_fom5_v2_final.csv'
NOTEBOOK = ROOT / 'notebooks/03_evaluacion_fom5_v2_final.ipynb'
notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
code = ''.join(notebook['cells'][6]['source'])
scope = {'np': np}
exec(compile(code, str(NOTEBOOK) + ':cell6', 'exec'), scope)
aggregate = scope['aggregate_v2']

gold = [json.loads(line) for line in
        (ROOT / 'codex_missing_assets/benchmark_30_v2.jsonl').read_text(encoding='utf-8').splitlines()]
gold.append(json.loads((ROOT / 'results/baseline/caso_entrega1_evaluation_only.json')
                       .read_text(encoding='utf-8')))
lookup = {item['id']: item for item in gold}
with CSV.open(encoding='utf-8-sig', newline='') as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == len({row['id'] for row in rows}) == len(lookup) == 31
assert {row['id'] for row in rows} == set(lookup)
for row in rows:
    assert row.get('judge_v2_error', '') in ('', 'None'), row['id']
    raw = row['judge_v2_raw'].strip()
    if '</think>' in raw:
        raw = raw.split('</think>', 1)[1].strip()
    start = raw.index('{')
    parsed, _ = json.JSONDecoder().raw_decode(raw[start:])
    item = lookup[row['id']]
    assert parsed['has_formulation'] in (True, False)
    assert set(parsed['requirements']) == {req['id'] for req in item['requirements']}
    assert {str(v).lower().strip() for v in parsed['requirements'].values()} <= {
        'met', 'partial', 'missing', 'wrong'}
    expected = aggregate(item, parsed)
    for key, value in expected.items():
        actual = float(row[key])
        assert math.isfinite(actual) and abs(actual - value) < 1e-9, (row['id'], key, actual, value)
print('31/31 juicios JSON reagrupados exactamente con FOM-5 v2.')
