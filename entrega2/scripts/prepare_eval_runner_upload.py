"""Prepare a small guarded upload of the evaluation phase executor."""
from pathlib import Path
import ast
import base64
import hashlib
import json

root=Path(__file__).resolve().parents[1]
blob=(root/'scripts/run_evaluation_notebook.py').read_bytes()
digest=hashlib.sha256(blob).hexdigest()
payload=base64.b64encode(blob).decode()
code=f'''from pathlib import Path
import base64,hashlib
p=Path('/content/drive/MyDrive/IA/entrega2_qlora/scripts/run_evaluation_notebook.py')
b=base64.b64decode({payload!r})
assert hashlib.sha256(b).hexdigest()=={digest!r}
if p.exists():
    assert p.read_bytes()==b, 'Ejecutor diferente ya existente.'
else:
    p.write_bytes(b)
print('Evaluador listo:',hashlib.sha256(p.read_bytes()).hexdigest())
'''
ast.parse(code)
(root/'tmp/colab_upload_eval_runner.json').write_text(json.dumps({'cellIndex':28,'language':'python','code':code}),encoding='utf-8')
