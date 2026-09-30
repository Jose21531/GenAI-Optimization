"""Create a compact, explicit bundle; excludes environments and connection state."""
from pathlib import Path
import base64,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)
archive=OUT/'entrega2_qlora_reproducible.zip'
paths=[ROOT/'README.md',ROOT/'requirements-colab.txt',ROOT/'requirements-audit.txt',
       ROOT/'or_sft_dataset_v1_2_final.zip',ROOT/'qlora_qwen25_or_sft_v1_2_fixed.ipynb']
for folder in ['notebooks','docs','results/baseline','results/audit','results/final',
               'results/colab/final/user_only_run01/benchmark',
               'results/colab/final/user_only_run01/evaluation',
               'codex_missing_assets','report','scripts']:
    paths += [p for p in (ROOT/folder).glob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.csv','.txt','.md','.ipynb','.tex','.py'}]
report_pdf=ROOT/'output/pdf/entrega2_final.pdf'
if report_pdf.exists(): paths.append(report_pdf)
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(set(paths)):
        z.write(p,p.relative_to(ROOT).as_posix())
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
payload=base64.b64encode(archive.read_bytes()).decode()
code=f'''# Transferencia de los archivos autorizados a la cuenta de Colab activa.
from pathlib import Path
import base64, hashlib, zipfile, io
from google.colab import drive
drive.mount('/content/drive')
blob=base64.b64decode({payload!r})
assert hashlib.sha256(blob).hexdigest()=={digest!r}
package=Path('/content/drive/MyDrive/IA/entrega2_qlora')
package.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    for item in z.infolist():
        target=(package/item.filename).resolve()
        assert target.is_relative_to(package.resolve())
        if target.exists() and target.read_bytes()!=z.read(item):
            raise RuntimeError(f'Archivo distinto ya existe: {{target}}. Revisar antes de sobrescribir.')
    z.extractall(package)
dataset=package/'or_sft_dataset_v1_2_final.zip'
dest=package.parent/dataset.name
if dest.exists():
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==hashlib.sha256(dataset.read_bytes()).hexdigest()
else:
    dest.write_bytes(dataset.read_bytes())
print('Paquete guardado:', package)
print('SHA256:', {digest!r})
'''
request=ROOT/'tmp/colab_upload_bundle.json'
request.parent.mkdir(exist_ok=True)
request.write_text(json.dumps({'cellIndex':0,'language':'python','code':code}),encoding='utf-8')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest,'upload_request':str(request)}))
