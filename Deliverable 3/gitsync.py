"""Checkpoints en el repositorio para reanudar una corrida desde otra sesión.

Cada sesión de Colab escribe en carpetas propias de su variante; por eso dos
personas pueden subir a la misma rama de resultados y ``pull --rebase`` integra
sus commits sin conflictos. Un push fallido no detiene la corrida: el commit
queda local y se reintenta en el siguiente checkpoint.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Iterable


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], check=check,
                          capture_output=True, text=True)


def repo_root(path: Path) -> Path:
    return Path(_git(Path(path), "rev-parse", "--show-toplevel").stdout.strip())


def checkpoint(paths: Iterable[Path], message: str, *, attempts: int = 4) -> bool:
    """Confirma ``paths`` y los sube a la rama actual. Devuelve True si quedó en origin."""
    paths = [Path(p).resolve() for p in paths if Path(p).exists()]
    if not paths:
        return False
    repo = repo_root(paths[0])
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch == "HEAD":
        raise ValueError("checkpoint requiere una rama de resultados, no un HEAD separado")
    _git(repo, "add", "--", *map(str, paths))
    if _git(repo, "diff", "--cached", "--quiet", check=False).returncode != 0:
        _git(repo, "commit", "-q", "-m", message)
    for attempt in range(attempts):
        # La primera subida crea la rama remota; antes no hay nada que integrar.
        exists = _git(repo, "ls-remote", "--exit-code", "--heads", "origin", branch, check=False).returncode == 0
        pulled = (_git(repo, "pull", "-q", "--rebase", "--autostash", "origin", branch, check=False)
                  if exists else subprocess.CompletedProcess([], 0))
        if pulled.returncode == 0 and _git(repo, "push", "-q", "origin", f"HEAD:{branch}", check=False).returncode == 0:
            return True
        if pulled.returncode != 0:
            _git(repo, "rebase", "--abort", check=False)
        time.sleep(2 + 3 * attempt)
    print(f"Aviso: no se pudo subir el checkpoint a {branch}; se reintentará en el siguiente.", flush=True)
    return False
