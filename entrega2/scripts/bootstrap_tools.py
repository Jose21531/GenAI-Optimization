"""Download official, portable tools into this project's .tools directory."""
from pathlib import Path
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '.tools'
DEST.mkdir(exist_ok=True)

def download(url, path):
    if not path.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'or-sft-reproducibility'})
        with urllib.request.urlopen(req, timeout=90) as src, path.open('wb') as dst:
            while block := src.read(1024 * 1024):
                dst.write(block)
    return path

pyzip = download('https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip', DEST / 'python.zip')
pydir = DEST / 'python'
pydir.mkdir(exist_ok=True)
with zipfile.ZipFile(pyzip) as z:
    z.extractall(pydir)
(pydir / 'python312._pth').write_text('python312.zip\n.\nLib/site-packages\nimport site\n', encoding='utf-8')
download('https://bootstrap.pypa.io/get-pip.py', DEST / 'get-pip.py')
req = urllib.request.Request('https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest', headers={'User-Agent': 'or-sft-reproducibility'})
with urllib.request.urlopen(req, timeout=90) as src:
    release = json.load(src)
asset = next(a for a in release['assets'] if 'x86_64-pc-windows-msvc' in a['name'] and a['name'].endswith('.zip'))
texzip = download(asset['browser_download_url'], DEST / asset['name'])
with zipfile.ZipFile(texzip) as z:
    z.extractall(DEST / 'tectonic')
(DEST / 'tool_sources.json').write_text(json.dumps({'python':'3.12.10','tectonic':release['tag_name'],'tectonic_url':asset['browser_download_url']}, indent=2), encoding='utf-8')
print('Portable Python and Tectonic downloaded in', DEST)
