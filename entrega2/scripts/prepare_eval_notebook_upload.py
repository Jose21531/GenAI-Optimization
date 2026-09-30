"""Guarded upload of final inference/judge notebooks after freezing variant."""
from pathlib import Path
import ast
import base64
import hashlib
import json
import zipfile

root=Path(__file__).resolve().parents[1]
prior=root/'output/entrega2_qlora_reproducible.zip'
files=['notebooks/02_generacion_final_31.ipynb','notebooks/03_evaluacion_fom5_v2_final.ipynb']
records=[]
with zipfile.ZipFile(prior) as archive:
    for name in files:
        original=archive.read(name)
        updated=(root/name).read_bytes()
        assert original!=updated
        records.append({'name':name,'old_sha256':hashlib.sha256(original).hexdigest(),
                        'new_sha256':hashlib.sha256(updated).hexdigest(),
                        'data':base64.b64encode(updated).decode()})
code=f'''from pathlib import Path
import base64,hashlib,json
package=Path('/content/drive/MyDrive/IA/entrega2_qlora')
records={records!r}
for record in records:
    target=(package/record['name']).resolve()
    assert target.is_relative_to(package.resolve())
    old=hashlib.sha256(target.read_bytes()).hexdigest()
    assert old in (record['old_sha256'],record['new_sha256']), (target,old)
    updated=base64.b64decode(record['data'])
    assert hashlib.sha256(updated).hexdigest()==record['new_sha256']
    if old==record['old_sha256']:
        target.with_suffix('.before_user_only.ipynb').write_bytes(target.read_bytes())
        target.write_bytes(updated)
    print(record['name'],record['new_sha256'])
'''
ast.parse(code)
(root/'tmp/colab_upload_eval_notebooks.json').write_text(json.dumps({'cellIndex':27,'language':'python','code':code}),encoding='utf-8')
print([(r['name'],r['new_sha256']) for r in records])
