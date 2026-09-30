"""Build inference and evaluation notebooks without changing the frozen judge."""
from pathlib import Path
import ast, hashlib, json, textwrap

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'codex_missing_assets'
original=json.loads((ASSETS/'evaluador_fom5_local.ipynb').read_text(encoding='utf-8'))
baseline_nb=json.loads((ASSETS/'qwen_baseline_30_pipeline.ipynb').read_text(encoding='utf-8'))

def cell(s,kind='code'):
    s=textwrap.dedent(s).strip()+'\n'
    if kind=='code' and not s.startswith('%pip'): ast.parse(s)
    c={'cell_type':kind,'metadata':{},'source':s.splitlines(keepends=True)}
    if kind=='code': c.update(execution_count=None,outputs=[])
    return c

def save(name,cells):
    for i,c in enumerate(cells): c['id']=f'eval-{i:02d}'
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
        'language_info':{'name':'python'},'accelerator':'GPU'},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks'/name).write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')

cells=[cell('''
# Test final: generación aislada de los golds

Ejecutar **solo después de congelar y entrenar el adapter final**.
Se usa exactamente el formato de entrada del baseline: mensaje user, FP16 y
1200 tokens máximos, sin muestreo. QLoRA modifica únicamente los pesos mediante
el adapter; la inferencia vuelve a FP16 para coincidir con el baseline.

Archivos requeridos en Drive: `codex_missing_assets/benchmark_30_generation_only.jsonl`,
`results/baseline/caso_entrega1_generation_only.jsonl`, adapter y manifest final.
No se carga ningún archivo con referencias ni requisitos.
''','markdown'),cell('%pip -q install "transformers==4.51.3" "peft==0.15.2" "accelerate==1.6.0"'),cell('''
from google.colab import drive
drive.mount('/content/drive')
from pathlib import Path
import json, hashlib, time, gc, contextlib, subprocess
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
from peft import PeftModel

PACKAGE=Path('/content/drive/MyDrive/IA/entrega2_qlora')
PROJECT=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
FINAL_RUN=PROJECT/'final/user_only_run01'
OUT=FINAL_RUN/'benchmark'
OUT.mkdir(exist_ok=True)
manifest=json.loads((FINAL_RUN/'manifest.json').read_text())
completed=json.loads((FINAL_RUN/'completed.json').read_text())
frozen=json.loads((PROJECT/'frozen_config.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert completed['manifest_sha256']==sha(FINAL_RUN/'manifest.json')
assert manifest['mode']=='final' and manifest['epochs']==frozen['epochs']
for filename,digest in completed['adapter_hashes'].items():
    assert sha(FINAL_RUN/'final_adapter'/filename)==digest
def read_jsonl(p):
    return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
items=read_jsonl(PACKAGE/'codex_missing_assets/benchmark_30_generation_only.jsonl')
assert len(items)==len({x['id'] for x in items})==30
items+=read_jsonl(PACKAGE/'results/baseline/caso_entrega1_generation_only.jsonl')
assert len(items)==len({x['id'] for x in items})==31
for item in items:
    assert set(item)<={'id','title','problem','model_class','difficulty'}, 'Archivo de generación con campos extra'
assert torch.cuda.is_available()
set_seed(42)
tokenizer=AutoTokenizer.from_pretrained(manifest['model_id'],revision=manifest['revision'])
if tokenizer.pad_token is None: tokenizer.pad_token=tokenizer.eos_token
base=AutoModelForCausalLM.from_pretrained(manifest['model_id'],revision=manifest['revision'],
                                       torch_dtype=torch.float16,device_map={'':0})
model=PeftModel.from_pretrained(base,FINAL_RUN/'final_adapter',is_trainable=False)
model.eval()
model.config.use_cache=True
generation_manifest={'variant':'qlora_final','messages':'user_only','max_new_tokens':1200,
    'do_sample':False,'dtype':'float16','model_revision':manifest['revision'],
    'adapter_manifest_sha256':sha(FINAL_RUN/'completed.json'),
    'inputs_sha256':sha(PACKAGE/'codex_missing_assets/benchmark_30_generation_only.jsonl'),
    'diagnostic_sha256':sha(PACKAGE/'results/baseline/caso_entrega1_generation_only.jsonl'),
    'gpu':torch.cuda.get_device_name(0),'generation_config':model.generation_config.to_dict()}
manifest_file=OUT/'generation_manifest.json'
if manifest_file.exists():
    assert json.loads(manifest_file.read_text())==generation_manifest
else:
    manifest_file.write_text(json.dumps(generation_manifest,indent=2),encoding='utf-8')
''')]
# The generation function is copied, byte-for-byte, from the frozen baseline notebook.
base_source=''.join(baseline_nb['cells'][8]['source'])
fn=next(n for n in ast.parse(base_source).body if isinstance(n,ast.FunctionDef) and n.name=='generate_direct')
function_source=ast.get_source_segment(base_source,fn)
cells += [cell(function_source),cell('''
destination=OUT/'final_generations_31.jsonl'
outputs=read_jsonl(destination) if destination.exists() else []
assert len(outputs)==len({r['id'] for r in outputs})
by_id={r['id']:r for r in outputs}
assert set(by_id)<={item['id'] for item in items}
for item in items:
    if item['id'] in by_id: continue
    result=generate_direct(item['problem'])
    result.update(id=item['id'],title=item['title'],split='benchmark' if item['id'].startswith('opt_') else 'diagnostic',
                  variant='qlora_final',model=manifest['model_id'],problem_sha256=hashlib.sha256(item['problem'].encode()).hexdigest(),
                  reached_token_budget=result['output_tokens']>=1200)
    # An exhausted budget is a flag, not proof that EOS was absent.
    with destination.open('a',encoding='utf-8') as f: f.write(json.dumps(result,ensure_ascii=False)+'\\n')
    by_id[item['id']]=result
    print(item['id'],result['output_tokens'],'tokens',round(result['latency_sec'],1),'s')
assert len(by_id)==31
print('31 salidas persistidas. Ahora ejecutar el juez en una sesión limpia.')
'''),cell('''
## Demostración reproducible (opcional, después del test)

La entrada diagnóstica fue fijada desde la Entrega 1, no elegida tras ver la mejora.
La celda siguiente ejecuta base y adapter sobre esa misma entrada. La regeneración
base se informa como nueva ejecución; no sobrescribe el baseline histórico.
''','markdown'),cell('''
RUN_LIVE_DEMO=False
if RUN_LIVE_DEMO:
    diagnostic=next(x for x in items if x['id']=='diagnostic_oftalmo')
    with model.disable_adapter():
        base_demo=generate_direct(diagnostic['problem'])
    adapted_demo=generate_direct(diagnostic['problem'])
    from IPython.display import display, Markdown
    display(Markdown('### Baseline directo (ejecución nueva)\\n'+base_demo['candidate']))
    display(Markdown('### QLoRA final (misma entrada)\\n'+adapted_demo['candidate']))
    (OUT/'live_demo.json').write_text(json.dumps({'id':diagnostic['id'],'baseline_new_run':base_demo,
        'qlora':adapted_demo},ensure_ascii=False,indent=2),encoding='utf-8')
''')]
save('02_generacion_final_31.ipynb',cells)

cells=[cell('''
# Evaluación final con FOM-5 v2 autoritativo

Ejecutar en Colab limpio después de guardar las 31 generaciones. Qwen3-14B solo
actúa como juez post-hoc. Se conservan sin cambios prompt, parser, retries,
topes y agregación del notebook original. Se calibra con sus cinco casos.
El CSV congelado conserva sus resultados; las 31 respuestas nuevas se puntúan aquí.
No modificar el juez después de observar estos resultados.
''','markdown'),cell('%pip -q install "transformers==4.51.3" "accelerate==1.6.0" "bitsandbytes==0.45.5"'),cell('''
from google.colab import drive
drive.mount('/content/drive')
import json, re, time, gc, hashlib, importlib.metadata as metadata
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from tqdm.auto import tqdm
from huggingface_hub import HfApi
assert torch.cuda.is_available()
PACKAGE=Path('/content/drive/MyDrive/IA/entrega2_qlora')
PROJECT=Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
FINAL_RUN=PROJECT/'final/user_only_run01'
OUT_DIR=FINAL_RUN/'evaluation'
OUT_DIR.mkdir(exist_ok=True)
old_df=pd.read_csv(PACKAGE/'codex_missing_assets/resultados_fom5_local.csv')
new_df=pd.read_json(FINAL_RUN/'benchmark/final_generations_31.jsonl',lines=True)
assert len(new_df)==31 and new_df['id'].nunique()==31
assert set(new_df['variant'])=={'qlora_final'}
GOLD=[json.loads(s) for s in (PACKAGE/'codex_missing_assets/benchmark_30_v2.jsonl').read_text(encoding='utf-8').splitlines()]
GOLD.append(json.loads((PACKAGE/'results/baseline/caso_entrega1_evaluation_only.json').read_text(encoding='utf-8')))
GOLD_LOOKUP={r['id']:r for r in GOLD}
generation_only=[json.loads(s) for s in (PACKAGE/'codex_missing_assets/benchmark_30_generation_only.jsonl').read_text(encoding='utf-8').splitlines()]
for row in generation_only:
    assert row['problem']==GOLD_LOOKUP[row['id']]['problem']
for row in new_df.to_dict('records'):
    assert row['problem_sha256']==hashlib.sha256(GOLD_LOOKUP[row['id']]['problem'].encode()).hexdigest()
assert set(new_df['id'])==set(GOLD_LOOKUP)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fingerprint={'generations_sha256':sha(FINAL_RUN/'benchmark/final_generations_31.jsonl'),
    'evaluator_sha256':sha(PACKAGE/'codex_missing_assets/evaluador_fom5_local.ipynb'),
    'gold_sha256':sha(PACKAGE/'codex_missing_assets/benchmark_30_v2.jsonl'),
    'diagnostic_gold_sha256':sha(PACKAGE/'results/baseline/caso_entrega1_evaluation_only.json'),
    'judge_revision':HfApi().model_info('Qwen/Qwen3-14B').sha,
    'gpu':torch.cuda.get_device_name(0),
    'versions':{p:metadata.version(p) for p in ['torch','transformers','accelerate','bitsandbytes']}}
fp=OUT_DIR/'evaluation_manifest.json'
if fp.exists(): assert json.loads(fp.read_text())==fingerprint, 'Estado distinto: no mezclar evaluaciones.'
else: fp.write_text(json.dumps(fingerprint,indent=2),encoding='utf-8')
''')]
load_source=''.join(original['cells'][9]['source'])
load_source=load_source.replace('    use_fast=True,','    use_fast=True,\n    revision=fingerprint["judge_revision"],')
load_source=load_source.replace('    quantization_config=quant_config,','    quantization_config=quant_config,\n    revision=fingerprint["judge_revision"],')
cells.append(cell(load_source))
for index in [11,12,14,16]:
    cells.append(cell(''.join(original['cells'][index]['source'])))
cells.append(cell('''
assert CALIBRATION_OK, 'Calibración fallida: detener, conservar evidencia y diagnosticar sin cambiar rúbrica.'
destination=OUT_DIR/'qlora_fom5_v2_checkpoint.jsonl'
records=[json.loads(s) for s in destination.read_text(encoding='utf-8').splitlines()] if destination.exists() else []
assert len(records)==len({r['id'] for r in records})
done={r['id'] for r in records}
assert done<=set(new_df['id'])
for rec in tqdm(new_df.to_dict('records')):
    if rec['id'] in done: continue
    started=time.perf_counter()
    # Un fallo aborta sin puntuar como cero ni reducir el denominador.
    parsed,raw,in_tokens,out_tokens=judge_local(GOLD_LOOKUP[rec['id']],rec['candidate'])
    rec.update(aggregate_v2(GOLD_LOOKUP[rec['id']],parsed))
    rec.update(judge_v2_raw=raw,judge_v2_error=None,judge_model=JUDGE_MODEL,
               judge_input_tokens=in_tokens,judge_output_tokens=out_tokens,
               judge_latency_sec=time.perf_counter()-started,
               fatal_errors_v2=json.dumps(parsed['fatal_errors'],ensure_ascii=False))
    with destination.open('a',encoding='utf-8') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\\n')
    records.append(rec);done.add(rec['id'])
assert len(records)==31
final_df=pd.DataFrame(records)
final_df.to_csv(OUT_DIR/'qlora_fom5_v2_final.csv',index=False,encoding='utf-8-sig')
comparison=old_df[(old_df['split']=='benchmark') & (old_df['variant']=='baseline_direct_deterministic')][['id','score_fom5_v2']].merge(
    final_df[final_df['split']=='benchmark'][['id','score_fom5_v2']],on='id',validate='one_to_one',suffixes=('_base','_qlora'))
assert len(comparison)==30
comparison['delta']=comparison['score_fom5_v2_qlora']-comparison['score_fom5_v2_base']
comparison.to_csv(OUT_DIR/'paired_comparison_30.csv',index=False,encoding='utf-8-sig')
print('Principal n=30:')
display(comparison)
print(comparison.mean(numeric_only=True))
print('Caso Entrega 1:')
display(final_df[final_df['id']=='diagnostic_oftalmo'][['id','score_fom5_v2','fatal_errors_v2']])
print('Extendido n=31:',final_df['score_fom5_v2'].mean())
'''))
save('03_evaluacion_fom5_v2_final.ipynb',cells)
provenance={str(i):hashlib.sha256(''.join(original['cells'][i]['source']).encode()).hexdigest() for i in [11,12,14,16]}
(ROOT/'results/audit/evaluator_source_hashes.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
print('Generated inference and evaluation notebooks; authoritative cells unchanged.')
