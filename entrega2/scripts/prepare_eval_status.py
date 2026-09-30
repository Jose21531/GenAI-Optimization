"""Prepare concise generation and judge status cell."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
code='''from pathlib import Path
import json, subprocess, time
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
final=work/'final/user_only_run01'
for phase in ('generation','judge'):
    state=work/f'worker_{phase}.json'
    if not state.exists(): continue
    info=json.loads(state.read_text())
    log=work/f'worker_{phase}.log'
    output=final/('benchmark/final_generations_31.jsonl' if phase=='generation' else 'evaluation/qlora_fom5_v2_checkpoint.jsonl')
    lines=len(output.read_text(encoding='utf-8').splitlines()) if output.exists() else 0
    print(json.dumps({'phase':phase,'state':info,'saved_cases':lines,
       'log_tail':log.read_text(errors='replace')[-750:] if log.exists() else ''},ensure_ascii=False))
print('gpu',subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used','--format=csv,noheader'],text=True).strip())
print('utc_seconds',time.time())
'''
(root/'tmp/colab_eval_status.json').write_text(json.dumps({'cellIndex':31,'language':'python','code':code}),encoding='utf-8')
