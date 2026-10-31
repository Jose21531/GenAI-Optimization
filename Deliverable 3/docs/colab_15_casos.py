# Celda de Colab (T4): generación oficial de los 15 primeros casos, alternando variantes por caso.
# Pegar en una celda nueva del cuaderno y ejecutar. Vuelve de inmediato; la corrida sigue en segundo plano.
# José:      MIS_VARIANTES = ['full', 'no_evidence', 'no_plan']
# Compañera: MIS_VARIANTES = ['no_audit', 'no_review']
# Requiere el secreto de Colab GITHUB_TOKEN (permiso Contents: read/write) para guardar cada caso en el repo;
# sin él, la corrida sigue pero los resultados quedan solo en esta sesión.
# Para continuar en otra cuenta tras un corte: pegar la misma celda con las mismas variantes.

MIS_VARIANTES = ['full', 'no_evidence', 'no_plan']
N_CASOS = 15

import subprocess, sys, os
from pathlib import Path
REPO = Path('/content/GenAI-Optimization')
URL = 'https://github.com/Jose21531/GenAI-Optimization.git'
BRANCH = 'resultados-oficiales'

def git(*args, check=True):
    return subprocess.run(['git', '-C', str(REPO), *args], check=check, capture_output=True, text=True)

subprocess.run('pkill -f d3_driver_15.py', shell=True)
if not REPO.exists():
    subprocess.run(['git', 'clone', '-q', URL, str(REPO)], check=True)
git('fetch', '-q', '--tags', '--force', 'origin')
git('reset', '-q', '--hard')
remote = git('ls-remote', '--exit-code', '--heads', 'origin', BRANCH, check=False).returncode == 0
git('checkout', '-q', '-B', BRANCH, f'origin/{BRANCH}' if remote else 'v3-freeze')
git('config', 'user.name', 'Colab Entrega 3')
git('config', 'user.email', 'colab@users.noreply.github.com')
try:
    from google.colab import userdata
    token = userdata.get('GITHUB_TOKEN')
except Exception:
    token = None
if token:
    git('remote', 'set-url', '--push', 'origin', f'https://x-access-token:{token}@github.com/Jose21531/GenAI-Optimization.git')
print('Código:', git('rev-parse', '--short', 'HEAD').stdout.strip(), '| v3-freeze:',
      git('rev-parse', '--short', 'v3-freeze^{commit}').stdout.strip(), '| guardar en repo:', bool(token))

import torch
if str(torch.__version__) != '2.6.0+cu124':
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r',
                    str(REPO / 'Deliverable 3/eval/requirements-gpu.txt'), 'peft==0.15.2'], check=True)
    raise SystemExit('Dependencias instaladas: reinicia el entorno (Entorno de ejecución → Reiniciar) y vuelve a ejecutar esta celda.')
assert 'T4' in torch.cuda.get_device_name(0), 'Conecta una GPU T4.'

driver = r'''
import sys, json, tempfile
from pathlib import Path
D3 = Path("/content/GenAI-Optimization/Deliverable 3"); sys.path.insert(0, str(D3))
from model import extract_adapter, load_qwen
from run import load_cases, load_config, run_variant, _identity
from gitsync import checkpoint
variants, n, sync = sys.argv[1].split(","), int(sys.argv[2]), sys.argv[3] == "1"
cases = load_cases("official"); config, _ = load_config("official")
zipf = D3.parent / "Deliverable 2/adapter_qlora_qwen25_final.zip"
identity = _identity("official", cases, zipf)          # identidad de los 30: la carpeta se completa después
llm = load_qwen(extract_adapter(zipf, Path(tempfile.mkdtemp()) / "adapter"))
ids = sorted(cases)[:n]
out, tr = D3 / "results/official", D3 / "traces/official"
def done(v):
    p = out / v / "outputs.jsonl"
    return len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else 0
for k in range(1, n + 1):
    for v in variants:
        subset = {i: cases[i] for i in ids[:max(k, done(v))]}
        # mode distinto de "official": no escribe el manifiesto de 30 casos todavía
        run_variant(llm, config, subset, v, out / v, tr / v, mode="official15", identity=identity)
        if sync:
            ok = checkpoint([out / v, tr / v], f"Resultados oficiales {v}: {ids[k-1]}")
            print("subido" if ok else "pendiente de subir", v, ids[k-1], flush=True)
print("FIN", flush=True)
'''
Path('/content/d3_driver_15.py').write_text(driver)
log = open('/content/d3_15.log', 'a')
proc = subprocess.Popen([sys.executable, '/content/d3_driver_15.py', ','.join(MIS_VARIANTES), str(N_CASOS), '1' if token else '0'],
                        stdout=log, stderr=subprocess.STDOUT, cwd=str(REPO), start_new_session=True)
print('Corrida en segundo plano, PID', proc.pid, '· variantes', MIS_VARIANTES, '· casos 1 a', N_CASOS)
print("Para ver el avance: !grep -E 'opt_|subido|FIN|Error' /content/d3_15.log | tail -20")
