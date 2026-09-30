"""Export one small named Drive file via official MCP without traversing checkpoints."""
from pathlib import Path
import argparse
import json

parser=argparse.ArgumentParser()
parser.add_argument('relative_path')
parser.add_argument('--index',type=int,default=23)
args=parser.parse_args()
assert args.relative_path in {
    'pilot/run01/validation_adapted_no_gold.jsonl',
    'pilot/run01/validation_base_no_gold.jsonl',
    'pilot/run01/validation_comparison.json',
    'pilot/run01/train_metrics.json',
    'pilot/run01/eval_metrics.json',
    'pilot/run01/manifest.json',
    'pilot/run01/completed.json',
    'pilot/user_only_run01/validation_adapted_no_gold.jsonl',
    'pilot/user_only_run01/validation_comparison.json',
    'pilot/user_only_run01/train_metrics.json',
    'pilot/user_only_run01/eval_metrics.json',
    'pilot/user_only_run01/manifest.json',
    'pilot/user_only_run01/completed.json',
    'final/user_only_run01/manifest.json',
    'final/user_only_run01/completed.json',
    'final/user_only_run01/train_metrics.json',
    'final/user_only_run01/benchmark/generation_manifest.json',
    'final/user_only_run01/benchmark/final_generations_31.jsonl',
    'final/user_only_run01/benchmark/live_demo.json',
    'final/user_only_run01/evaluation/evaluation_manifest.json',
    'final/user_only_run01/evaluation/calibracion_fom5_local.csv',
    'final/user_only_run01/evaluation/qlora_fom5_v2_checkpoint.jsonl',
    'final/user_only_run01/evaluation/qlora_fom5_v2_final.csv',
}
code=f'''from pathlib import Path
import base64,zlib,hashlib,json
p=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')/{args.relative_path!r}
b=p.read_bytes()
print(json.dumps({{'name':{args.relative_path!r},'sha256':hashlib.sha256(b).hexdigest(),
                  'data':base64.b64encode(zlib.compress(b,9)).decode()}}))
'''
root=Path(__file__).resolve().parents[1]
(root/'tmp/colab_export_targeted.json').write_text(json.dumps({'cellIndex':args.index,'language':'python','code':code}),encoding='utf-8')
print(args.relative_path)
