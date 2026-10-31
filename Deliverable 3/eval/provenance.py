"""Identidad de entradas, configuración y código usados al generar resultados."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

from eval.artifacts import ROOT, input_hash, load_predictions, sha256
from eval.legacy import text_bytes


def _text_hash(path):
    return hashlib.sha256(text_bytes(path)).hexdigest()


def generation_context(mode: str, root: Path = ROOT):
    root = Path(root).resolve()
    if mode not in {"official", "development"}:
        raise ValueError("Modo de evaluación desconocido")
    config_path = root / "config" / ("frozen.yaml" if mode == "official" else "development.yaml")
    if not config_path.is_file():
        raise ValueError(f"Falta {config_path}; no se puede evaluar la corrida como {mode}")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    model = config.get("model", {})
    if model.get("id") != "Qwen/Qwen2.5-1.5B-Instruct" or config.get("generation", {}).get("do_sample") is not False:
        raise ValueError("Configuración de generación incompatible con el experimento")
    paths = [config_path, root / "schemas.py"]
    paths += sorted((root / "agents").glob("*.py")) + sorted((root / "tools").glob("*.py"))
    paths += [root / name for name in ("model.py", "orchestrator.py", "run.py") if (root / name).exists()]
    for relative in config.get("prompts", {}).values():
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Un prompt de configuración sale de Deliverable 3")
        paths.append(path)
    # Antes de que A explicite el mapping, el desarrollo conserva todas las versiones.
    if not config.get("prompts"):
        if mode == "official":
            raise ValueError("La configuración congelada debe declarar los prompts")
        paths += sorted((root / "prompts").glob("*.md"))
    freeze_commit = None
    if mode == "official":
        required = ("model.py", "orchestrator.py", "run.py")
        if any(not (root / filename).is_file() for filename in required):
            raise ValueError("Faltan módulos de infraestructura para una corrida oficial")
        if model.get("revision") != "989aa7980e4cf806f80c7fef2b1adb7bc71aa306" or model.get("adapter_sha256") != "68583e9dffa6647a5c0b89a74168363264daf246e4337ef1ae0c644243391151":
            raise ValueError("Modelo o adapter congelado incompatible con Entrega 2")
        try:
            freeze_commit = subprocess.check_output(
                ["git", "-C", str(root.parent), "rev-parse", "v3-freeze^{commit}"], text=True, stderr=subprocess.PIPE).strip()
            subprocess.run(["git", "-C", str(root.parent), "merge-base", "--is-ancestor", freeze_commit, "HEAD"], check=True, capture_output=True)
            for path in paths:
                original = subprocess.check_output(["git", "-C", str(root.parent), "show",
                    f"{freeze_commit}:{path.relative_to(root.parent).as_posix()}"], stderr=subprocess.PIPE)
                if original.replace(b"\r\n", b"\n") != text_bytes(path):
                    raise ValueError(f"El código o configuración cambió después de v3-freeze: {path.name}")
        except subprocess.CalledProcessError as error:
            raise ValueError("Falta un tag v3-freeze válido con el código y la configuración congelados") from error
    return {"mode": mode, "freeze_commit": freeze_commit,
            "config_sha256": _text_hash(config_path),
            "sources": {p.relative_to(root).as_posix(): _text_hash(p) for p in sorted(set(paths))}}


def manifest_path(predictions: Path):
    return Path(str(predictions) + ".manifest.json")


def generation_manifest(predictions: Path, variant: str, items, *, mode: str, root: Path = ROOT):
    load_predictions(predictions, variant, items)
    return {"schema_version": 1, "variant": variant, "mode": mode,
            "predictions_sha256": sha256(predictions), "inputs_sha256": input_hash(items),
            "generation": generation_context(mode, root)}


def write_generation_manifest(predictions: Path, variant: str, items, *, mode: str, root: Path = ROOT):
    payload = generation_manifest(predictions, variant, items, mode=mode, root=root)
    path = manifest_path(predictions)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return path


def verify_generation_manifest(predictions: Path, variant: str, items, *, mode: str, root: Path = ROOT):
    expected = generation_manifest(predictions, variant, items, mode=mode, root=root)
    actual = json.loads(manifest_path(predictions).read_text(encoding="utf-8"))
    if actual != expected:
        raise ValueError(f"El manifiesto no corresponde a estas salidas/entradas/configuración: {predictions}")
    return expected
