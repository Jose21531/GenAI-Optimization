"""Insert verified paired FOM-5 v2 results into the one-page LaTeX report."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--summary', type=Path, default=ROOT / 'results/final/comparison_summary.json')
args = parser.parse_args()
result = json.loads(args.summary.read_text(encoding='utf-8'))
assert result['n_main'] == 30 and result['n_extended'] == 31
assert abs(result['baseline_mean'] - 0.5884) < 0.0001
assert result['improved'] + result['tied'] + result['worsened'] == 30
dimensions = result['qlora_dimensions']
values = {
    'EstadoDocumento': 'RESULTADOS FOM-5 v2 MEDIDOS',
    'TextoEstado': ('Una época QLoRA en 1050 entradas; evaluación pareada de 30 casos '
                    'con el mismo protocolo del baseline.'),
    'ScoreFinal': f"{result['qlora_mean']:.4f}",
    'ScoreDominios': f"{dimensions['decision_domains_v2']:.4f}",
    'ScoreObjetivo': f"{dimensions['objective_v2']:.4f}",
    'ScoreRestricciones': f"{dimensions['constraints_logic_v2']:.4f}",
    'ScoreAlgebra': f"{dimensions['algebra_validity_v2']:.4f}",
    'ScoreGeneralizacion': f"{dimensions['generalization_v2']:.4f}",
    'CoberturaFinal': f"{dimensions['requirement_coverage_v2']:.4f}",
    'ScoreDiagnostico': f"{result['diagnostic_qlora']:.3f}",
    'ScoreExtendido': f"{result['extended_qlora_mean']:.4f}",
    'TextoComparacion': (
        r'\textbf{Cambio pareado medio:} '
        + f"{result['delta_mean']:+.4f}/5 "
        + r'(IC bootstrap 95\%: '
        + f"{result['delta_bootstrap_95'][0]:+.4f} a {result['delta_bootstrap_95'][1]:+.4f}"
        + f"); {result['improved']} mejoran, {result['tied']} empatan y "
        + f"{result['worsened']} empeoran. "
        + 'El IC cuantifica variación entre estos 30 problemas, no entre semillas ni jueces.'
    ),
    'TextoHardware': (
        'Tesla T4 de 15 GB observada. Ajuste completo: 1050 ejemplos, una época, '
        '131 pasos, 982 s y 9.04 GiB de VRAM reservada. Las 31 respuestas '
        'FP16 quedaron por ID, ninguna agotó 1200 tokens; juez calibrado 5/5.'
    ),
}
path = ROOT / 'report/resultados.tex'
source = path.read_text(encoding='utf-8')
for name, value in values.items():
    pattern = rf'(\\newcommand\{{\\{name}\}}\{{)(.*)(\}})$'
    lines = source.splitlines(keepends=True)
    matches = 0
    for i, line in enumerate(lines):
        match = re.match(pattern, line.rstrip('\r\n'))
        if match:
            end = '\n' if line.endswith('\n') else ''
            lines[i] = match.group(1) + value + match.group(3) + end
            matches += 1
    assert matches == 1, name
    source = ''.join(lines)
path.write_text(source, encoding='utf-8')
print(path)
