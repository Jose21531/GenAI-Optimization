"""Run the reviewed training notebook in a fresh Colab subprocess.

The parent notebook mounts Drive and installs dependencies first. Each phase
starts a new interpreter and base model. Progress survives MCP call timeouts.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import time
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('--notebook', type=Path, required=True)
parser.add_argument('--mode', choices=['pilot', 'development', 'final'], required=True)
parser.add_argument('--state', type=Path, required=True)
args = parser.parse_args()
raw = args.notebook.read_bytes()
notebook = json.loads(raw)
state = {'mode': args.mode, 'pid': os.getpid(), 'notebook_sha256': hashlib.sha256(raw).hexdigest(),
         'started_at': time.time(), 'status': 'running'}

def save_state():
    temp = args.state.with_suffix('.tmp')
    temp.write_text(json.dumps(state, indent=2), encoding='utf-8')
    temp.replace(args.state)

scope = {'__name__': '__main__'}
save_state()
try:
    # Cell 1 installs dependencies; cell 14 requires mathematical review.
    for index in range(2, 13):
        cell = notebook['cells'][index]
        assert cell['cell_type'] == 'code'
        source = ''.join(cell['source'])
        if index == 2:
            assert "RUN_MODE = 'pilot'" in source
            source = source.replace("RUN_MODE = 'pilot'", f"RUN_MODE = {args.mode!r}")
            source = source.replace("drive.mount('/content/drive')",
                                    "assert __import__('pathlib').Path('/content/drive/MyDrive').is_dir(), 'Mount Drive in parent notebook first'")
        state.update(cell=index, updated_at=time.time())
        save_state()
        print(f'\n--- Executing reviewed notebook cell {index} ({args.mode}) ---', flush=True)
        exec(compile(source, f'{args.notebook}:cell{index}', 'exec'), scope)
    state.update(status='completed', finished_at=time.time())
    save_state()
except BaseException:
    state.update(status='failed', finished_at=time.time(), traceback=traceback.format_exc())
    save_state()
    traceback.print_exc()
    raise
