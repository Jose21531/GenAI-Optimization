"""Decode one targeted MCP file export without printing the binary payload."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import zlib

parser=argparse.ArgumentParser()
parser.add_argument('result',type=Path)
args=parser.parse_args()
raw=json.loads(args.result.read_text(encoding='utf-8'))
assert not raw.get('isError'),raw
content=raw['structuredContent']['outputs']
value=json.loads(''.join(''.join(c.get('text',[])) for c in content if c.get('output_type')=='stream'))
blob=zlib.decompress(base64.b64decode(value['data']))
assert hashlib.sha256(blob).hexdigest()==value['sha256']
root=Path(__file__).resolve().parents[1]
destination=(root/'results/colab'/value['name']).resolve()
assert destination.is_relative_to((root/'results/colab').resolve())
destination.parent.mkdir(parents=True,exist_ok=True)
destination.write_bytes(blob)
print(json.dumps({'file':str(destination),'bytes':len(blob),'sha256':value['sha256']}))
