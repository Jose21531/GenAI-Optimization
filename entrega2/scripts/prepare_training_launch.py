"""Prepare a reviewable MCP cell to launch the notebook in a fresh process."""
from pathlib import Path
import ast
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
runner = (ROOT/'scripts/run_training_notebook.py').read_bytes()
ast.parse(runner.decode())
payload = base64.b64encode(runner).decode()
code = f'''# Ejecuta las mismas celdas revisadas; guarda progreso aunque expire una llamada MCP.
from pathlib import Path
import base64, json, subprocess, sys, os
package = Path('/content/drive/MyDrive/IA/entrega2_qlora')
runner_path = package/'scripts/run_training_notebook.py'
runner_bytes = base64.b64decode({payload!r})
if runner_path.exists():
    assert runner_path.read_bytes()==runner_bytes, 'Revisar la versión del ejecutor existente.'
else:
    runner_path.write_bytes(runner_bytes)

def start_training_phase(mode):
    assert mode in ('pilot', 'development', 'final')
    work = Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
    work.mkdir(parents=True,exist_ok=True)
    state_path = work/f'worker_{{mode}}.json'
    if state_path.exists():
        previous=json.loads(state_path.read_text())
        assert previous['status']!='completed', 'Fase ya completada: revisar resultados.'
        if previous['status']=='running':
            try:
                os.kill(previous['pid'],0)
            except ProcessLookupError:
                pass
            else:
                raise RuntimeError('Ya hay un proceso activo para esta fase.')
    log_path = work/f'worker_{{mode}}.log'
    with log_path.open('ab') as log:
        worker = subprocess.Popen([sys.executable, '-u', str(runner_path),
            '--notebook', str(package/'notebooks/01_qlora_experimento_controlado.ipynb'),
            '--mode', mode, '--state', str(state_path)], stdout=log, stderr=subprocess.STDOUT,
            env={{**os.environ,'TOKENIZERS_PARALLELISM':'false'}})
    print(json.dumps({{'mode':mode,'pid':worker.pid,'state':str(state_path),'log':str(log_path)}}))

start_training_phase('pilot')
'''
ast.parse(code)
(ROOT/'tmp/colab_launch_training.json').write_text(json.dumps({'cellIndex':17,'language':'python','code':code}),encoding='utf-8')
poll = '''from pathlib import Path
import json
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
for phase in ('pilot','development','final'):
    state=work/f'worker_{phase}.json'
    if state.exists():
        print(state.read_text())
        log=work/f'worker_{phase}.log'
        if log.exists():
            print(log.read_text(errors='replace')[-5000:])
'''
(ROOT/'tmp/colab_poll_training.json').write_text(json.dumps({'cellIndex':18,'language':'python','code':poll}),encoding='utf-8')
print('Launch and progress MCP cell arguments prepared.')
