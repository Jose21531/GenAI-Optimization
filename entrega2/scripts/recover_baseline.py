"""Recover frozen evidence and exact diagnostic text; no model inference."""
from pathlib import Path
import ast, base64, csv, gzip, hashlib, json, math, statistics

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'codex_missing_assets'
OUT=ROOT/'results/baseline'
OUT.mkdir(parents=True,exist_ok=True)
read_jsonl=lambda p:[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
rows=list(csv.DictReader((ASSETS/'resultados_fom5_local.csv').open(encoding='utf-8-sig')))
baseline=[r for r in rows if r['split']=='benchmark' and r['variant']=='baseline_direct_deterministic']
generation=read_jsonl(ASSETS/'benchmark_30_generation_only.jsonl')
assert len(baseline)==len(generation)==30
assert {r['id'] for r in baseline}=={r['id'] for r in generation}
assert len({r['id'] for r in baseline})==30
assert all(not r.get('judge_v2_error') for r in baseline)
assert all(not {'gold','requirements','reference_model'} & set(r) for r in generation)
values=[float(r['score_fom5_v2']) for r in baseline]
assert abs(statistics.mean(values)-0.5884)<0.00001
dims=['decision_domains','objective','constraints_logic','algebra_validity','generalization']
summary={'n':30,'mean_fom5_v2':statistics.mean(values),'median':statistics.median(values),
    'std_sample':statistics.stdev(values),'mean_coverage':statistics.mean(float(r['requirement_coverage_v2']) for r in baseline),
    'dimensions':{d:statistics.mean(float(r[d+'_v2']) for r in baseline) for d in dims},
    'zero_scores':values.count(0),'source':'codex_missing_assets/resultados_fom5_local.csv',
    'filter':{'split':'benchmark','variant':'baseline_direct_deterministic'},
    'source_sha256':hashlib.sha256((ASSETS/'resultados_fom5_local.csv').read_bytes()).hexdigest(),
    'status':'recovered_frozen_results_not_new_inference'}
diagnostic=[r for r in rows if r['id']=='diagnostic_oftalmo']
summary['diagnostic']=[{'variant':r['variant'],'score_fom5_v2':float(r['score_fom5_v2']),
                        'coverage':float(r['requirement_coverage_v2'])} for r in diagnostic]
for r in diagnostic:
    (OUT/(r['variant']+'.txt')).write_text(r['candidate'],encoding='utf-8')
(OUT/'baseline_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'baseline_30.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=baseline[0].keys()); writer.writeheader(); writer.writerows(baseline)
nb=json.loads((ASSETS/'qwen_baseline_30_pipeline.ipynb').read_text(encoding='utf-8'))
tree=ast.parse(''.join(nb['cells'][6]['source']))
constants={node.targets[0].id:ast.literal_eval(node.value) for node in tree.body
    if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name)
    and node.targets[0].id in {'OPH_PROBLEM','OPH_REFERENCE','HISTORICAL_OPH_RESPONSE'}}
case={'id':'diagnostic_oftalmo','title':'Centros oftalmológicos - Entrega 1','problem':constants['OPH_PROBLEM'],
      'model_class':'MILP','difficulty':'media'}
(OUT/'caso_entrega1_generation_only.jsonl').write_text(json.dumps(case,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'caso_entrega1_reference.txt').write_text(constants['OPH_REFERENCE'],encoding='utf-8')
(OUT/'baseline_generation_config.json').write_text(json.dumps({
    'model_id':'Qwen/Qwen2.5-1.5B-Instruct','dtype':'float16','quantization':None,
    'messages':'user_only','max_new_tokens':1200,'do_sample':False,
    'system_prompt':None,'revision':'not pinned in original notebook; record resolved revision in new runs',
    'source':'qwen_baseline_30_pipeline.ipynb cells 7-8'},ensure_ascii=False,indent=2),encoding='utf-8')
# Recover embedded diagnostic gold without executing notebook code.
judge_nb=json.loads((ASSETS/'evaluador_fom5_local.ipynb').read_text(encoding='utf-8'))
gold_tree=ast.parse(''.join(judge_nb['cells'][3]['source']))
blob=next(node.args[0].value for node in ast.walk(gold_tree) if isinstance(node,ast.Call)
          and isinstance(node.func,ast.Attribute) and node.func.attr=='b64decode')
gold=json.loads(gzip.decompress(base64.b64decode(blob)))
if isinstance(gold,dict):
    gold=list(gold.values())
diag_gold=next(x for x in gold if x['id']=='diagnostic_oftalmo')
assert diag_gold['problem']==case['problem']
(OUT/'caso_entrega1_evaluation_only.json').write_text(json.dumps(diag_gold,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
