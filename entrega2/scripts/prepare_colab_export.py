"""Prepare an MCP cell exporting small experiment evidence, excluding weights."""
from pathlib import Path
import argparse
import json

parser=argparse.ArgumentParser()
parser.add_argument('--index',type=int,default=20)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
code='''from pathlib import Path
import io, zipfile, base64, hashlib, json
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
buffer=io.BytesIO()
included=[]
with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(work.rglob('*')):
        if not path.is_file() or path.suffix not in {'.json','.jsonl','.txt','.csv','.log'}:
            continue
        rel=path.relative_to(work)
        if 'checkpoints' in rel.parts or path.stat().st_size>2000000:
            continue
        archive.write(path,rel.as_posix())
        included.append(rel.as_posix())
blob=buffer.getvalue()
print(json.dumps({'sha256':hashlib.sha256(blob).hexdigest(),'files':included,'zip_base64':base64.b64encode(blob).decode()}))
'''
(root/'tmp/colab_export_results.json').write_text(json.dumps({'cellIndex':args.index,'language':'python','code':code}),encoding='utf-8')
