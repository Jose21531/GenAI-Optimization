"""Insert reviewed notebook cells through the connected official Colab MCP.

Preserves existing cells. Stores remote IDs so an interrupted insertion resumes
without duplicating cells. Does not execute notebook code.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'tmp/colab_mcp'
parser = argparse.ArgumentParser()
parser.add_argument('notebook', type=Path)
parser.add_argument('--index', type=int, required=True)
parser.add_argument('--mapping', type=Path, required=True)
args = parser.parse_args()
raw = args.notebook.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
notebook = json.loads(raw)
mapping = {'sha256': digest, 'notebook': str(args.notebook), 'cells': []}
if args.mapping.exists():
    mapping = json.loads(args.mapping.read_text(encoding='utf-8'))
    assert mapping['sha256'] == digest, 'Notebook changed; inspect existing cells first.'
for index, cell in enumerate(notebook['cells']):
    if index < len(mapping['cells']):
        continue
    source = ''.join(cell['source'])
    if cell['cell_type'] == 'code':
        name = 'add_code_cell'
        arguments = {'cellIndex': args.index + index, 'language': 'python', 'code': source}
    else:
        name = 'add_text_cell'
        arguments = {'cellIndex': args.index + index, 'content': source}
    ident = str(time.time_ns()) + '_' + uuid.uuid4().hex[:6]
    request = STATE / f'request_{ident}.json'
    temporary = request.with_suffix('.tmp')
    temporary.write_text(json.dumps({'name': name, 'arguments': arguments}), encoding='utf-8')
    temporary.replace(request)
    result_path = STATE / f'result_{ident}.json'
    deadline = time.monotonic() + 240
    while not result_path.exists():
        if time.monotonic() > deadline:
            raise TimeoutError(f'Inspect {result_path} before retrying insertion.')
        time.sleep(0.5)
    result = json.loads(result_path.read_text(encoding='utf-8'))
    assert not result.get('isError'), result
    remote = result['structuredContent']['newCellId']
    mapping['cells'].append({'index': index, 'type': cell['cell_type'], 'id': remote})
    args.mapping.parent.mkdir(parents=True, exist_ok=True)
    args.mapping.write_text(json.dumps(mapping, indent=2), encoding='utf-8')
    print(f'Inserted {index}: {remote}', flush=True)
