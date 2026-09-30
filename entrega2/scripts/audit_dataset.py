"""Reproducible structural/diversity audit; never opens the official benchmark."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def audit(zip_path, output):
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        checksums = {}
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            expected, name = line.split(maxsplit=1)
            checksums[name.strip()] = hashlib.sha256(z.read(name.strip())).hexdigest() == expected
        assert all(checksums.values()), 'Archive checksum mismatch'
        def rows(name):
            return [json.loads(line) for line in z.read(name).decode('utf-8').splitlines() if line.strip()]
        rich = rows('or_sft_1050_rich_v1_2.jsonl')
        full = rows('or_sft_1050_messages_v1_2.jsonl')
        train = rows('or_sft_train_840_family_split_v1_2.jsonl')
        val = rows('or_sft_val_210_family_split_v1_2.jsonl')
        pilot = rows('or_sft_pilot_200_v1_2.jsonl')
    by_id = {r['id']: r for r in rich}
    assert len(by_id) == len(rich) == 1050
    assert len({r['problem'] for r in rich}) == 1050
    family = defaultdict(list)
    for row in rich:
        family[row['family_id']].append(row)
    assert len(family) == 50 and {len(rs) for rs in family.values()} == {21}
    for row in full + train + val + pilot:
        assert [m['role'] for m in row['messages']] == ['system', 'user', 'assistant']
        ref = by_id[row['id']]
        assert row['messages'][1]['content'] == ref['problem']
        assert row['messages'][2]['content'] == ref['answer']
        assert row['family_id'] == ref['family_id']
    train_ids = {r['id'] for r in train}
    val_ids = {r['id'] for r in val}
    tf = {r['family_id'] for r in train}
    vf = {r['family_id'] for r in val}
    assert not train_ids & val_ids and train_ids | val_ids == set(by_id)
    assert len(train_ids) == 840 and len(val_ids) == 210 and not tf & vf
    assert len(pilot) == len({r['id'] for r in pilot}) == 200
    assert set(Counter(r['family_id'] for r in pilot).values()) == {4}
    normalized = lambda s: re.sub(r'\d+(?:[.,]\d+)?', '<N>', s)
    result = {
        'archive_sha256': hashlib.sha256(Path(zip_path).read_bytes()).hexdigest(),
        'checksum_files_verified': len(checksums), 'n': len(rich), 'families': len(family),
        'examples_per_family': 21, 'unique_problems': len({r['problem'] for r in rich}),
        'unique_targets': len({r['answer'] for r in rich}),
        'unique_problems_numbers_removed': len({normalized(r['problem']) for r in rich}),
        'model_type': dict(Counter(r['model_type'] for r in rich)),
        'difficulty': dict(Counter(r['difficulty'] for r in rich)),
        'train_families': sorted(tf), 'validation_families': sorted(vf),
        'train_n': len(train), 'validation_n': len(val), 'pilot_n': len(pilot),
        'family_overlap': sorted(tf & vf),
        'system_prompts': sorted({r['messages'][0]['content'] for r in full}),
        'scope': 'All rows checked structurally; manual semantic review of 50 representative pairs. Not a proof of feasibility of every numeric instance.',
        'benchmark_similarity': 'Not rerun: benchmark files absent. Prior archive claims are not new measurements.',
    }
    (output / 'dataset_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    with (output / 'family_diversity.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['family_id','family','split','n','model_type','difficulty','unique_targets','unique_numeric_normalized_prompts'])
        for fid, rs in sorted(family.items()):
            writer.writerow([fid,rs[0]['family'],'validation' if fid in vf else 'train',len(rs),rs[0]['model_type'],rs[0]['difficulty'],len({r['answer'] for r in rs}),len({normalized(r['problem']) for r in rs})])
    print(json.dumps({k:v for k,v in result.items() if k!='system_prompts'},ensure_ascii=False,indent=2))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', type=Path, default=ROOT/'or_sft_dataset_v1_2_final.zip')
    parser.add_argument('--output', type=Path, default=ROOT/'results/audit')
    args = parser.parse_args()
    audit(args.zip, args.output)
