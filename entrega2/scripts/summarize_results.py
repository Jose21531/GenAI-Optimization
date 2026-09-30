"""Summarize real paired scores; refuses incomplete or mismatched test sets."""
from pathlib import Path
import argparse,csv,json,math,statistics
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def summarize(final_csv,out):
    final=read_csv(final_csv)
    assert len(final)==31 and len({r['id'] for r in final})==31
    assert {r['variant'] for r in final}=={'qlora_final'}
    baseline=read_csv(ROOT/'results/baseline/baseline_30.csv')
    base={r['id']:r for r in baseline}
    lookup={r['id']:r for r in final}
    assert set(lookup)==set(base)|{'diagnostic_oftalmo'}
    assert all(not r.get('judge_v2_error') for r in final)
    numeric=['score_fom5_v2','requirement_coverage_v2','decision_domains_v2',
             'objective_v2','constraints_logic_v2','algebra_validity_v2','generalization_v2']
    for r in final:
        for key in numeric:
            value=float(r[key]); assert math.isfinite(value), (r['id'],key)
            assert 0<=value<=(1 if key=='requirement_coverage_v2' else 5)
    pairs=[{'id':i,'baseline':float(base[i]['score_fom5_v2']),
            'qlora':float(lookup[i]['score_fom5_v2']),
            'delta':float(lookup[i]['score_fom5_v2'])-float(base[i]['score_fom5_v2'])} for i in sorted(base)]
    historically_exposed={'opt_01','opt_16','opt_30'}
    secondary=[r for r in pairs if r['id'] not in historically_exposed]
    assert len(secondary)==27
    delta=np.array([r['delta'] for r in pairs])
    rng=np.random.default_rng(42)
    samples=rng.choice(delta,size=(10000,30),replace=True).mean(axis=1)
    official=[lookup[i] for i in sorted(base)]
    summary={'n_main':30,'n_diagnostic':1,'n_extended':31,
        'baseline_mean':statistics.mean(r['baseline'] for r in pairs),
        'qlora_mean':statistics.mean(r['qlora'] for r in pairs),
        'delta_mean':float(delta.mean()),'delta_bootstrap_95':np.quantile(samples,[.025,.975]).tolist(),
        'improved':int((delta>0).sum()),'tied':int((delta==0).sum()),'worsened':int((delta<0).sum()),
        'qlora_dimensions':{k:statistics.mean(float(r[k]) for r in official) for k in numeric[1:]},
        'diagnostic_qlora':float(lookup['diagnostic_oftalmo']['score_fom5_v2']),
        'diagnostic_baseline_deterministic':0.65,'diagnostic_entrega1_historical_sampled':0.369,
        'extended_qlora_mean':statistics.mean(float(r['score_fom5_v2']) for r in final),
        'extended_baseline_deterministic_mean':(sum(r['baseline'] for r in pairs)+0.65)/31,
        'worst_qlora_case':min(pairs,key=lambda r:r['qlora']),
        'largest_gain_case':max(pairs,key=lambda r:r['delta']),
        'secondary_27_excluding_documented_exposure':{
            'n':len(secondary),
            'excluded_ids':sorted(historically_exposed),
            'baseline_mean':statistics.mean(r['baseline'] for r in secondary),
            'qlora_mean':statistics.mean(r['qlora'] for r in secondary),
            'delta_mean':statistics.mean(r['delta'] for r in secondary),
        },
        'interpretation':'Bootstrap across fixed paired inputs, not training-seed or judge uncertainty.',
        'source_final_csv':str(Path(final_csv).resolve())}
    out.mkdir(parents=True,exist_ok=True)
    (out/'comparison_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'paired_comparison_30.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=pairs[0].keys()); w.writeheader(); w.writerows(pairs)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--csv',required=True,type=Path)
    p.add_argument('--output',type=Path,default=ROOT/'results/final')
    args=p.parse_args()
    summarize(args.csv,args.output)
