"""Guarded Colab transfer and launch of the second pilot variant."""
from pathlib import Path
import ast
import base64
import hashlib
import json

root=Path(__file__).resolve().parents[1]
source=root/'notebooks/04_qlora_user_only_controlado.ipynb'
blob=source.read_bytes()
digest=hashlib.sha256(blob).hexdigest()
payload=base64.b64encode(blob).decode()
code=f'''from pathlib import Path
import os, sys, json, hashlib, zipfile, base64, subprocess
package=Path('/content/drive/MyDrive/IA/entrega2_qlora')
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
original=work/'pilot/run01'
assert (original/'completed.json').exists()
assert json.loads((work/'worker_pilot.json').read_text())['status']=='completed'
old=json.loads((original/'validation_comparison.json').read_text())
assert old['n_generation_pairs']==10 and old['adapted_truncated']>=old['base_truncated']
path=package/'notebooks/04_qlora_user_only_controlado.ipynb'
blob=base64.b64decode({payload!r})
assert hashlib.sha256(blob).hexdigest()=={digest!r}
if path.exists():
    assert path.read_bytes()==blob, 'Una versión distinta ya existe; inspeccionarla.'
else:
    path.write_bytes(blob)
manifest=json.loads((original/'manifest.json').read_text())
assert manifest['revision']==json.loads((work/'model_revision.json').read_text())['revision']
archive=Path('/content/drive/MyDrive/IA/or_sft_dataset_v1_2_final.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['dataset_sha256']
source_base=original/'validation_base_no_gold.jsonl'
base=[json.loads(line) for line in source_base.read_text().splitlines()]
with zipfile.ZipFile(archive) as z:
    validation=[json.loads(line) for line in z.read('or_sft_val_210_family_split_v1_2.jsonl').decode().splitlines()]
first={{}}
for row in validation:
    first.setdefault(row['family_id'],row)
assert [x['id'] for x in base]==[x['id'] for x in first.values()]
assert all(x['problem']==row['messages'][1]['content'] for x,row in zip(base,first.values()))
target=work/'pilot/user_only_run01'
target.mkdir(parents=True,exist_ok=True)
destination=target/source_base.name
if destination.exists():
    assert destination.read_bytes()==source_base.read_bytes()
else:
    destination.write_bytes(source_base.read_bytes())
(target/'base_generation_reuse.json').write_text(json.dumps({{
 'source':str(source_base),'sha256':hashlib.sha256(source_base.read_bytes()).hexdigest(),
 'reason':'identical base weights, revision, no-gold user-only prompt, generation config and 10 inputs',
 'n':len(base),'same_id_and_problem_text':True}},ensure_ascii=False,indent=2))
state=work/'worker_pilot_user_only.json'
assert not state.exists(), 'Variante ya iniciada: inspeccionar estado antes de reanudar.'
runner=package/'scripts/run_training_notebook.py'
assert runner.is_file()
log=work/'worker_pilot_user_only.log'
with log.open('ab') as handle:
    process=subprocess.Popen([sys.executable,'-u',str(runner),'--notebook',str(path),
        '--mode','pilot','--state',str(state)],stdout=handle,stderr=subprocess.STDOUT,
        env={{**os.environ,'TOKENIZERS_PARALLELISM':'false'}})
print(json.dumps({{'variant':'user_only','pid':process.pid,'state':str(state),
                  'notebook_sha256':{digest!r},'baseline_reused_sha256':hashlib.sha256(source_base.read_bytes()).hexdigest()}}))
'''
ast.parse(code)
(root/'tmp/colab_user_only_launch.json').write_text(json.dumps({'cellIndex':24,'language':'python','code':code}),encoding='utf-8')
print(digest)
