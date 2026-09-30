"""Freeze the user-only recipe from pilot evidence, then train on all 1050."""
from pathlib import Path
import ast
import json

root=Path(__file__).resolve().parents[1]
code='''from pathlib import Path
import json, hashlib, subprocess, sys, os
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
pilot=work/'pilot/user_only_run01'
state=json.loads((work/'worker_pilot_user_only.json').read_text())
assert state['status']=='completed'
assert (pilot/'completed.json').exists()
manifest=json.loads((pilot/'manifest.json').read_text())
metrics=json.loads((pilot/'validation_comparison.json').read_text())
assert manifest['mode']=='pilot' and manifest['training_messages']=='user_only'
assert metrics['n_generation_pairs']==10 and metrics['adapted_truncated']==1
assert metrics['base_truncated']==5 and metrics['adapted_repeated_lines']==36
assert hashlib.sha256(Path('/content/drive/MyDrive/IA/or_sft_dataset_v1_2_final.zip').read_bytes()).hexdigest()==manifest['dataset_sha256']
frozen={k:manifest[k] for k in ['dataset_sha256','revision','lora_r','lora_alpha','lora_dropout',
                                 'learning_rate','grad_accum','max_length','seed']}
frozen.update(epochs=1,source_run=str(pilot),training_messages='user_only',
              selected_from='two pilot variants, no development phase',
              mathematical_review='Exploratory scaling only: user-only pilot reduced truncation from 5/10 to 1/10, but 10 held-out families retained serious algebraic and logical errors. No claim of mathematical success; final benchmark will decide.',
              pilot_base_eval_loss=metrics['base_eval_loss'],
              pilot_adapted_eval_loss=metrics['adapted_eval_loss'])
frozen_path=work/'frozen_config.json'
if frozen_path.exists():
    assert json.loads(frozen_path.read_text())==frozen,'Different recipe already frozen: inspect before overwriting.'
else:
    frozen_path.write_text(json.dumps(frozen,ensure_ascii=False,indent=2))
notebook=Path('/content/drive/MyDrive/IA/entrega2_qlora/notebooks/04_qlora_user_only_controlado.ipynb')
assert hashlib.sha256(notebook.read_bytes()).hexdigest()=='6a08289fb374171b83afeaa00aab44c8c61614a9e7e1aa122a66d10d345f7c9e'
target=work/'final/user_only_run01'
assert not target.exists(), 'Final ya iniciado; revisar checkpoint y estado.'
state_path=work/'worker_final_user_only.json'
assert not state_path.exists()
runner=Path('/content/drive/MyDrive/IA/entrega2_qlora/scripts/run_training_notebook.py')
log=work/'worker_final_user_only.log'
with log.open('ab') as handle:
    worker=subprocess.Popen([sys.executable,'-u',str(runner),'--notebook',str(notebook),
        '--mode','final','--state',str(state_path)],stdout=handle,stderr=subprocess.STDOUT,
        env={**os.environ,'TOKENIZERS_PARALLELISM':'false'})
print(json.dumps({'pid':worker.pid,'mode':'final','n_train':1050,'epochs':1,
                  'state':str(state_path),'frozen_sha256':hashlib.sha256(frozen_path.read_bytes()).hexdigest()}))
'''
ast.parse(code)
(root/'tmp/colab_final_frozen_launch.json').write_text(json.dumps({'cellIndex':26,'language':'python','code':code}),encoding='utf-8')
