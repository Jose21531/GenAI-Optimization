"""Decode one official MCP export result without printing its payload."""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import zipfile

parser=argparse.ArgumentParser()
parser.add_argument('result',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
result=json.loads(args.result.read_text(encoding='utf-8'))
assert not result.get('isError'), result
outputs=result['structuredContent']['outputs']
text=''.join(''.join(o.get('text',[])) for o in outputs if o.get('output_type')=='stream')
payload=json.loads(text)
blob=base64.b64decode(payload['zip_base64'])
assert hashlib.sha256(blob).hexdigest()==payload['sha256']
destination=root/'results/colab'
destination.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(blob)) as archive:
    for item in archive.infolist():
        assert (destination/item.filename).resolve().is_relative_to(destination.resolve())
    archive.extractall(destination)
print(json.dumps({'destination':str(destination),'sha256':payload['sha256'],'files':payload['files']},ensure_ascii=False))
