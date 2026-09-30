"""Stage the audited Deliverable 2 files in a clone of the course repository.

No credentials, Colab session state, local virtual environments, or model cache are copied.
"""
from pathlib import Path
import argparse
import shutil

SOURCE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('repository', type=Path)
args = parser.parse_args()
repo = args.repository.resolve()
assert (repo / '.git').is_dir(), 'Expected an existing Git clone'
target = repo / 'entrega2'
target.mkdir(exist_ok=True)

single = [
    'README.md',
    'requirements-colab.txt',
    'requirements-audit.txt',
    'or_sft_dataset_v1_2_final.zip',
    'qlora_qwen25_or_sft_v1_2_fixed.ipynb',
]
folders = [
    'notebooks', 'docs', 'scripts', 'codex_missing_assets',
    'results/baseline', 'results/audit', 'results/final',
    'results/colab/final/user_only_run01', 'report',
]
files = [SOURCE / name for name in single]
for folder in folders:
    files.extend(p for p in (SOURCE / folder).rglob('*') if p.is_file())
pdf = SOURCE / 'output/pdf/entrega2_final.pdf'
if pdf.exists():
    files.append(pdf)
video = SOURCE / 'output/video/demo_entrega2.mp4'
if video.exists():
    files.append(video)
allowed = {'.txt', '.md', '.json', '.jsonl', '.csv', '.ipynb', '.tex',
           '.py', '.zip', '.pdf', '.mp4'}
copied = 0
for file in sorted(set(files)):
    if not file.exists() or file.suffix not in allowed:
        continue
    if file == SOURCE / 'report/entrega2.pdf' and not pdf.exists():
        continue
    relative = file.relative_to(SOURCE)
    destination = target / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, destination)
    copied += 1
if pdf.exists():
    shutil.copy2(pdf, repo / 'deliverables/Deliverable2.pdf')
print(f'Staged {copied} files in {target}')
