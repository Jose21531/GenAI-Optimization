"""Fetch one allowlisted Drive artifact through the connected Colab MCP session."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / '.tools/colab-mcp/.venv/Scripts/python.exe'


def command(*args):
    result = subprocess.run([str(PYTHON), '-X', 'utf8', *map(str, args)],
                            cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


parser = argparse.ArgumentParser()
parser.add_argument('relative_path')
parser.add_argument('--timeout', type=int, default=120)
args = parser.parse_args()

command(ROOT / 'scripts/prepare_targeted_export.py', args.relative_path)
request = json.loads((ROOT / 'tmp/colab_export_targeted.json').read_text(encoding='utf-8'))
update_args = ROOT / 'tmp/colab_update_export.json'
update_args.write_text(json.dumps({'cellId': 'I5MlA4zTq_4s',
                                  'content': request['code']}), encoding='utf-8')
command(ROOT / 'scripts/colab_call.py', 'update_cell', '--args-file', update_args,
        '--wait', '8', '--compact')
response = command(ROOT / 'scripts/colab_call.py', 'run_code_cell', '--args-file',
                   ROOT / 'tmp/colab_run_export_adapted.json', '--wait', '0', '--compact')
result_path = Path(json.loads(response)['pending_result'])
deadline = time.monotonic() + args.timeout
while not result_path.exists() and time.monotonic() < deadline:
    time.sleep(0.5)
if not result_path.exists():
    raise TimeoutError(f'No result from Colab MCP: {result_path}')
print(command(ROOT / 'scripts/unpack_targeted_export.py', result_path))
