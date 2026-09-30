"""Prepare guarded Colab launcher cells for generation and judge phases."""
from pathlib import Path
import ast
import hashlib
import json

root=Path(__file__).resolve().parents[1]
for mode,index,filename in [('generation',29,'02_generacion_final_31.ipynb'),
                            ('judge',30,'03_evaluacion_fom5_v2_final.ipynb')]:
    notebook=root/'notebooks'/filename
    digest=hashlib.sha256(notebook.read_bytes()).hexdigest()
    prerequisite='''
assert json.loads((work/'worker_final_user_only.json').read_text())['status']=='completed'
assert (work/'final/user_only_run01/completed.json').exists()
''' if mode=='generation' else '''
assert json.loads((work/'worker_generation.json').read_text())['status']=='completed'
generated=work/'final/user_only_run01/benchmark/final_generations_31.jsonl'
assert len(generated.read_text(encoding='utf-8').splitlines())==31
'''
    code=f'''from pathlib import Path
import os,sys,json,hashlib,subprocess
package=Path('/content/drive/MyDrive/IA/entrega2_qlora')
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
{prerequisite}
notebook=package/'notebooks/{filename}'
assert hashlib.sha256(notebook.read_bytes()).hexdigest()=={digest!r}
runner=package/'scripts/run_evaluation_notebook.py'
assert hashlib.sha256(runner.read_bytes()).hexdigest()=='0376aa93b50f21c2a757231783d03459a13fe962e9aecfc6cb734096aadd9bb3'
state=work/'worker_{mode}.json'
assert not state.exists(), 'La fase ya fue iniciada; inspeccionar estado y salidas.'
log=work/'worker_{mode}.log'
with log.open('ab') as handle:
    process=subprocess.Popen([sys.executable,'-u',str(runner),'--mode',{mode!r},
        '--notebook',str(notebook),'--state',str(state)],stdout=handle,
        stderr=subprocess.STDOUT,env={{**os.environ,'TOKENIZERS_PARALLELISM':'false'}})
print(json.dumps({{'mode':{mode!r},'pid':process.pid,'state':str(state),'notebook_sha256':{digest!r}}}))
'''
    ast.parse(code)
    (root/f'tmp/colab_launch_{mode}.json').write_text(json.dumps({'cellIndex':index,'language':'python','code':code}),encoding='utf-8')
    print(mode,digest)
