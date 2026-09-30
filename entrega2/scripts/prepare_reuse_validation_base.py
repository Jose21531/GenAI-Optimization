"""Prepare guarded reuse of identical base generations for development."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
code='''from pathlib import Path
import hashlib, json, zipfile
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
pilot=work/'pilot/run01'
assert (pilot/'completed.json').exists(), 'Terminar el piloto antes de crear la comparación development.'
source=pilot/'validation_base_no_gold.jsonl'
rows=[json.loads(line) for line in source.read_text().splitlines()]
assert len(rows)==10
model=json.loads((work/'model_revision.json').read_text())
manifest=json.loads((pilot/'manifest.json').read_text())
assert model['revision']==manifest['revision']
assert manifest['development_generation']=={'messages':'user_only','do_sample':False,'max_new_tokens':1200,'repetition_penalty':1.0}
archive=Path('/content/drive/MyDrive/IA/or_sft_dataset_v1_2_final.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['dataset_sha256']
with zipfile.ZipFile(archive) as z:
    validation=[json.loads(line) for line in z.read('or_sft_val_210_family_split_v1_2.jsonl').decode().splitlines()]
first={}
for row in validation:
    first.setdefault(row['family_id'],row)
expected=list(first.values())
assert [x['id'] for x in rows]==[x['id'] for x in expected]
assert all(x['problem']==y['messages'][1]['content'] for x,y in zip(rows,expected))
target=work/'development/run01'
target.mkdir(parents=True,exist_ok=True)
destination=target/source.name
assert not destination.exists()
destination.write_bytes(source.read_bytes())
evidence={'method':'reuse identical no-gold base generations','source':str(source),
 'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'n':len(rows),
 'model_revision':model['revision'],'max_new_tokens':1200,
 'validation_family_ids':list(first),'same_input_ids':True,'same_problem_texts':True}
(target/'base_generation_reuse.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
print(json.dumps(evidence,ensure_ascii=False))
'''
(root/'tmp/colab_reuse_validation_base.json').write_text(json.dumps({'cellIndex':22,'language':'python','code':code}),encoding='utf-8')
