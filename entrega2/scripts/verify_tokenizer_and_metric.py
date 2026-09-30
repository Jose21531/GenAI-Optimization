"""CPU verification with real Qwen tokenizer; no model weights or test inference."""
from pathlib import Path
import ast, csv, hashlib, json, math, os, zipfile
import numpy as np
from transformers import AutoTokenizer
from huggingface_hub import HfApi

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/audit'
CACHE=ROOT/'.tools/hf_cache'
MODEL='Qwen/Qwen2.5-1.5B-Instruct'
revision=HfApi().model_info(MODEL).sha
tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=revision,cache_dir=CACHE)
with zipfile.ZipFile(ROOT/'or_sft_dataset_v1_2_final.zip') as z:
    rows=[json.loads(s) for s in z.read('or_sft_1050_messages_v1_2.jsonl').decode().splitlines()]
def ids(messages,gen=False):
    return tokenizer(tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=gen),
                     add_special_tokens=False)['input_ids']
lengths=[len(ids(r['messages'])) for r in rows]
max_length=max(1024,math.ceil(max(lengths)/128)*128)
nb=json.loads((ROOT/'notebooks/01_qlora_experimento_controlado.ipynb').read_text(encoding='utf-8'))
source=next(''.join(c['source']) for c in nb['cells'] if 'def tokenize_record(' in ''.join(c['source']))
fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='tokenize_record')
namespace={'tokenizer':tokenizer,'MAX_LENGTH':max_length}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<notebook tokenize_record>','exec'),namespace)
supervised=[]
for row in rows:
    encoded=namespace['tokenize_record'](row)
    prefix=ids(row['messages'][:2],True)
    labels=encoded['labels']
    assert labels[:len(prefix)]==[-100]*len(prefix)
    assert labels[len(prefix):]==encoded['input_ids'][len(prefix):]
    decoded=tokenizer.decode(labels[len(prefix):],skip_special_tokens=True).strip()
    assert decoded==row['messages'][2]['content'].strip(),row['id']
    assert tokenizer.eos_token_id in labels[len(prefix):]
    assert not encoded['was_truncated']
    supervised.append(encoded['supervised_tokens'])
stats={'n':len(rows),'model_id':MODEL,'revision':revision,'mean':float(np.mean(lengths)),
    'p95':float(np.percentile(lengths,95)),'p99':float(np.percentile(lengths,99)),
    'max':max(lengths),'over_1024':sum(n>1024 for n in lengths),'max_length_required':max_length,
    'supervised_min':min(supervised),'supervised_mean':float(np.mean(supervised)),
    'supervised_max':max(supervised),'exact_assistant_decode_passed':len(rows),
    'eos_supervised_passed':len(rows),'scope':'CPU tokenizer and mask only; no GPU training'}
(OUT/'tokenizer_verified.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
with (OUT/'token_lengths_by_id.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['id','family_id','total_tokens','assistant_tokens'])
    w.writerows((r['id'],r['family_id'],n,s) for r,n,s in zip(rows,lengths,supervised))

# Recompute frozen metric from original stored judgments using unchanged authoritative aggregation.
assets=ROOT/'codex_missing_assets'
judge=json.loads((assets/'evaluador_fom5_local.ipynb').read_text(encoding='utf-8'))
agg_source=''.join(judge['cells'][14]['source'])
ns={'np':np}
exec(compile(agg_source,'authoritative cell 14','exec'),ns)
gold={r['id']:r for r in map(json.loads,(assets/'benchmark_30_v2.jsonl').read_text(encoding='utf-8').splitlines())}
diag=json.loads((ROOT/'results/baseline/caso_entrega1_evaluation_only.json').read_text(encoding='utf-8'))
gold[diag['id']]=diag
frozen=list(csv.DictReader((assets/'resultados_fom5_local.csv').open(encoding='utf-8-sig')))
for r in frozen:
    parsed=json.loads(r['judge_v2_raw'])
    calculated=ns['aggregate_v2'](gold[r['id']],parsed)
    for k,v in calculated.items():
        assert math.isclose(v,float(r[k]),abs_tol=1e-9),(r['id'],k,v,r[k])
(OUT/'metric_regression.json').write_text(json.dumps({'rows_recomputed':len(frozen),'all_fields_match':True,
    'aggregate_source_sha256':hashlib.sha256(agg_source.encode()).hexdigest(),
    'scope':'Stored judge JSON reaggregated; judge model not rerun'},indent=2),encoding='utf-8')
print(json.dumps(stats,indent=2))
print('Authoritative metric: all',len(frozen),'stored rows reproduced exactly.')
