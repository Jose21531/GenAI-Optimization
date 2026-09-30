"""One-time guarded correction before any optimizer step in pilot run01."""
from pathlib import Path
import base64
import json

root=Path(__file__).resolve().parents[1]
notebook=root/'notebooks/01_qlora_experimento_controlado.ipynb'
payload=base64.b64encode(notebook.read_bytes()).decode()
code=f'''from pathlib import Path
import os, signal, json, base64, hashlib, time
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
state_path=work/'worker_pilot.json'
state=json.loads(state_path.read_text())
assert state['pid']==4547 and state['cell']==11 and state['status']=='running', state
run=work/'pilot/run01'
assert not list((run/'checkpoints').glob('checkpoint-*')), 'No interrumpir entrenamiento ya iniciado.'
print('Métricas previas a la corrección:', (run/'base_eval_metrics.json').read_text())
os.kill(state['pid'],signal.SIGTERM)
state.update(status='interrupted_before_training',reason='Explicit label_names required for PEFT validation loss')
state_path.write_text(json.dumps(state,indent=2))
(work/'worker_pilot_before_label_fix.json').write_text(json.dumps(state,indent=2))
for name in ['base_eval_metrics.json','validation_base_no_gold.jsonl']:
    source=run/name
    if source.exists():
        backup=run/(name+'.before_label_fix')
        assert not backup.exists()
        source.rename(backup)
destination=Path('/content/drive/MyDrive/IA/entrega2_qlora/notebooks/01_qlora_experimento_controlado.ipynb')
assert hashlib.sha256(destination.read_bytes()).hexdigest()=='a370fb9a5b42340b2253bd84e7b91b0d9b357104cccfa99d7f880526ee73eee4'
destination.with_suffix('.before_label_fix.ipynb').write_bytes(destination.read_bytes())
destination.write_bytes(base64.b64decode({payload!r}))
print('Notebook corregido:',hashlib.sha256(destination.read_bytes()).hexdigest())
'''
(root/'tmp/colab_label_fix.json').write_text(json.dumps({'cellIndex':19,'language':'python','code':code}),encoding='utf-8')
n=json.loads(notebook.read_bytes())
mapping=json.loads((root/'tmp/colab_pilot_cells.json').read_text())
(root/'tmp/colab_update_trainer.json').write_text(json.dumps({'cellId':mapping['cells'][11]['id'],'content':''.join(n['cells'][11]['source'])}),encoding='utf-8')
