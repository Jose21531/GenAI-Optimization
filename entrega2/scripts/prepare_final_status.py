"""Concise status cell for frozen 1050-instance Colab run."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
code='''from pathlib import Path
import json, subprocess, time
work=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
state=work/'worker_final_user_only.json'
if state.exists():
    info=json.loads(state.read_text())
    run=work/'final/user_only_run01'
    log=(work/'worker_final_user_only.log').read_text(errors='replace')
    metrics=run/'training_log.jsonl'
    records=[json.loads(line) for line in metrics.read_text().splitlines()] if metrics.exists() else []
    evidence={p.name:p.stat().st_size for p in run.glob('*.json*')} if run.exists() else {}
    print(json.dumps({'state':info,'latest_log':records[-1] if records else None,
        'evidence':evidence,'tail':log[-850:]},ensure_ascii=False))
print('gpu',subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used','--format=csv,noheader'],text=True).strip())
print('utc_seconds',time.time())
'''
(root/'tmp/colab_final_status.json').write_text(json.dumps({'cellIndex':26,'language':'python','code':code}),encoding='utf-8')
