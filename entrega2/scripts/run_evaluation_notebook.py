"""Run frozen generation or judge notebook after training, saving phase status."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import time
import traceback

parser=argparse.ArgumentParser()
parser.add_argument('--mode',choices=['generation','judge'],required=True)
parser.add_argument('--notebook',type=Path,required=True)
parser.add_argument('--state',type=Path,required=True)
args=parser.parse_args()
raw=args.notebook.read_bytes()
notebook=json.loads(raw)
last=5 if args.mode=='generation' else 9
state={'mode':args.mode,'pid':os.getpid(),'notebook_sha256':hashlib.sha256(raw).hexdigest(),
       'started_at':time.time(),'status':'running'}

def save_state():
    temporary=args.state.with_suffix('.tmp')
    temporary.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    temporary.replace(args.state)

scope={'__name__':'__main__','display':lambda value:print(value,flush=True)}
save_state()
try:
    for index in range(2,last):
        cell=notebook['cells'][index]
        assert cell['cell_type']=='code'
        code=''.join(cell['source'])
        if index==2:
            assert "drive.mount('/content/drive')" in code
            code=code.replace("drive.mount('/content/drive')",
                              "assert __import__('pathlib').Path('/content/drive/MyDrive').is_dir(), 'Mount Drive in parent notebook first'")
        state.update(cell=index,updated_at=time.time())
        save_state()
        print(f'--- {args.mode} cell {index} ---',flush=True)
        exec(compile(code,f'{args.notebook}:cell{index}','exec'),scope)
    state.update(status='completed',finished_at=time.time())
    save_state()
except BaseException:
    state.update(status='failed',finished_at=time.time(),traceback=traceback.format_exc())
    save_state()
    traceback.print_exc()
    raise
