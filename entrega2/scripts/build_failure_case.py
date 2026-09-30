"""Preserve the complete Entrega 1 input and actual before/after answers."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
baseline = ROOT / 'results/baseline'
generation = ROOT / 'results/colab/final/user_only_run01/benchmark/final_generations_31.jsonl'
items = [json.loads(line) for line in generation.read_text(encoding='utf-8').splitlines()]
adapted = next(row for row in items if row['id'] == 'diagnostic_oftalmo')
problem = json.loads((baseline / 'caso_entrega1_generation_only.jsonl').read_text(encoding='utf-8').strip())
assert problem['id'] == adapted['id']
assert 'p_j' in adapted['candidate'] and r'\sum_{i\in I}\sum_{j\in J}d_{ij}x_{ij}' in adapted['candidate']
score = 'pendiente de juicio'
csv_path = ROOT / 'results/colab/final/user_only_run01/evaluation/qlora_fom5_v2_final.csv'
if csv_path.exists():
    with csv_path.open(encoding='utf-8-sig', newline='') as handle:
        row = next(row for row in csv.DictReader(handle) if row['id'] == problem['id'])
    score = row['score_fom5_v2']
sections = [
    '# Falla real después de QLoRA: localización oftalmológica',
    '',
    'Caso fijado antes del entrenamiento por la Entrega 1. No pertenece a la media principal de 30 casos.',
    '',
    '## Enunciado exacto',
    '', problem['problem'], '',
    '## Baseline directo determinista recuperado',
    '', 'FOM-5 v2 histórico: 0.650/5.', '',
    (baseline / 'baseline_direct_deterministic.txt').read_text(encoding='utf-8'),
    '', '## QLoRA final, generación nueva', '',
    f"FOM-5 v2: {score}/5. Tokens: {adapted['output_tokens']}; latencia: {adapted['latency_sec']:.1f} s.",
    '', adapted['candidate'], '',
    '## Qué sigue mal', '',
    'El adapter sí introduce la variable binaria de apertura, la asignación única y el vínculo '
    '$x_{ij}\\le y_i$. Sin embargo, define $p_j$ y luego no lo multiplica en el objetivo: '
    'minimiza $\\sum_{ij}d_{ij}x_{ij}$ en lugar de $\\sum_{ij}p_jd_{ij}x_{ij}$. '
    'Por tanto, pondera igual todos los sectores y puede seleccionar centros distintos. '
    'No es una formulación matemáticamente equivalente.',
]
out = ROOT / 'results/final/failure_case_diagnostic.md'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(sections) + '\n', encoding='utf-8')
print(out)

if csv_path.exists():
    with csv_path.open(encoding='utf-8-sig', newline='') as handle:
        degraded = next(row for row in csv.DictReader(handle) if row['id'] == 'opt_02')
    official = [json.loads(line) for line in
                (ROOT / 'codex_missing_assets/benchmark_30_v2.jsonl')
                .read_text(encoding='utf-8').splitlines()]
    item = next(row for row in official if row['id'] == 'opt_02')
    another = ROOT / 'results/final/failure_case_opt02.md'
    another.write_text('\n'.join([
        '# Degradación post-ajuste en el benchmark: opt_02', '',
        'Baseline directo determinista: 1.300/5. QLoRA: '
        + degraded['score_fom5_v2'] + '/5 (FOM-5 v2).', '',
        '## Enunciado exacto', '', item['problem'], '',
        '## Respuesta QLoRA exacta', '', degraded['candidate'], '',
        '## Error matemático', '',
        'La hora extraordinaria debe ser una variable continua $h\\in[0,20]$ que amplía '
        'solo la disponibilidad laboral: $2x_A+3x_B+x_C\\le140+h$, con costo $10h$ '
        'en la ganancia neta. La respuesta usa $y_k\\in[0,1]$ como supuesto indicador '
        'de horas extras y le impone vínculos artificiales con cada producto. Además omite '
        '$x_C\\ge10$ y no representa correctamente las capacidades de máquina y materia prima. '
        'El juez le asignó 0.000/5, frente a 1.300/5 del baseline; el caso muestra '
        'una degradación real, no solo una mejora incompleta.', '',
        '## Juicio bruto', '', '```json', degraded['judge_v2_raw'], '```', ''
    ]), encoding='utf-8')
    print(another)
