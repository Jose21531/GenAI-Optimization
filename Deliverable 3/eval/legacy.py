"""Carga del FOM-5 v2 publicado, sin ejecutar celdas del notebook ni alterarlo."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from types import SimpleNamespace

VENDOR = Path(__file__).resolve().parent / "vendor"
KERNEL_SHA256 = "63b4008353cebd4a933c3083bf89eab820046b0b78e08f4c86a04e592f7869a9"
CALIBRATION_SHA256 = "4e6cf372912e15bfefaee8f2804a69002e9d354ff530877fb1b097d67e06f2fc"
JUDGE_MODEL = "Qwen/Qwen3-14B"
JUDGE_REVISION = "40c069824f4251a91eefaf281ebe4c544efd3e18"


def text_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def kernel_source() -> str:
    source = text_bytes(VENDOR / "fom5_v2.py")
    if hashlib.sha256(source).hexdigest() != KERNEL_SHA256:
        raise ValueError("El juez FOM-5 v2 publicado fue modificado")
    return source.decode("utf-8")


def calibration_spec() -> list:
    source = text_bytes(VENDOR / "calibration.json")
    if hashlib.sha256(source).hexdigest() != CALIBRATION_SHA256:
        raise ValueError("La calibración FOM-5 v2 publicada fue modificada")
    return json.loads(source)


def load_kernel() -> SimpleNamespace:
    # La celda original define funciones, constantes y un decorador torch.
    # La parte pura no necesita cargar torch ni pesos del juez.
    import numpy as np

    tree = ast.parse(kernel_source())
    nodes = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == "judge_local")]
    namespace = {"np": np, "re": re, "json": json}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(VENDOR / "fom5_v2.py"), "exec"), namespace)
    return SimpleNamespace(**{k: v for k, v in namespace.items() if not k.startswith("__")})


def bind_judge(model, tokenizer, torch):
    """La función original, incluidos decorador, límites y dos intentos."""
    namespace = vars(load_kernel()).copy()
    namespace.update(model=model, tokenizer=tokenizer, torch=torch)
    tree = ast.parse(kernel_source())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {"_chat_text", "judge_local"}]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(VENDOR / "fom5_v2.py"), "exec"), namespace)
    return namespace["judge_local"]
