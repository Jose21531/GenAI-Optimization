"""Prepare concise status cell for a long Colab experiment."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
code='''from pathlib import Path
import json, re, time, subprocess
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
for phase in ('pilot','development','final'):
    state=work/f'worker_{phase}.json'
    if not state.exists(): continue
    info=json.loads(state.read_text())
    log=(work/f'worker_{phase}.log').read_text(errors='replace')
    generated=re.findall(r'(?m)^F\\d\\d_\\d\\d$',log)
    metrics=work/phase/'run01'/'training_log.jsonl'
    latest=json.loads(metrics.read_text().splitlines()[-1]) if metrics.exists() and metrics.read_text().splitlines() else None
    outputs=work/phase/'run01'
    evidence={p.name:p.stat().st_size for p in outputs.glob('*.json*')} if outputs.exists() else {}
    print(json.dumps({'phase':phase,'state':info,'generated':generated[-12:],
         'latest_log':latest,'evidence':evidence,'tail':log[-500:]},ensure_ascii=False))
print('gpu',subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used','--format=csv,noheader'],text=True).strip())
print('utc_seconds',time.time())
'''
(root/'tmp/colab_status.json').write_text(json.dumps({'cellIndex':21,'language':'python','code':code}),encoding='utf-8')
