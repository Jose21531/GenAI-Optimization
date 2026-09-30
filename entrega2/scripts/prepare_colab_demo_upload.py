"""Prepare a small, hash-checked demo-script transfer through Colab MCP."""
from pathlib import Path
import base64
import hashlib
import json

root = Path(__file__).resolve().parents[1]
source = root / 'scripts/demo_same_input.py'
blob = source.read_bytes()
digest = hashlib.sha256(blob).hexdigest()
encoded = base64.b64encode(blob).decode()
code = f'''from pathlib import Path
import base64,hashlib
b=base64.b64decode({encoded!r})
assert hashlib.sha256(b).hexdigest()=={digest!r}
p=Path('/content/drive/MyDrive/IA/entrega2_qlora/scripts/demo_same_input.py')
assert not p.exists() or p.read_bytes()==b, 'Script distinto ya existe'
p.parent.mkdir(parents=True,exist_ok=True)
p.write_bytes(b)
print(str(p),len(b),hashlib.sha256(b).hexdigest())
'''
destination = root / 'tmp/colab_upload_demo_script.json'
destination.write_text(json.dumps({'cellIndex': 33, 'language': 'python', 'code': code}),
                       encoding='utf-8')
print(digest)
