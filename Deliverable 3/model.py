"""Qwen2.5-1.5B-Instruct con el adapter QLoRA de la Entrega 2.

Reproduce la inferencia de la Entrega 2 (celdas 8 y 12 del notebook): plantilla
de chat con un único mensaje user, fp16 en GPU, ``do_sample=False`` con la
``generation_config`` publicada del modelo y el adapter apagado mediante
``disable_adapter()``. Los agentes solo ven ``generate(prompt, adapter_on)``.

torch, transformers y peft se importan al cargar el modelo, de modo que los
tests con MockLLM no los necesitan.
"""

from __future__ import annotations

import hashlib
import time
import zipfile
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
ADAPTER_SHA256 = "68583e9dffa6647a5c0b89a74168363264daf246e4337ef1ae0c644243391151"
ADAPTER_FILES = {"adapter_config.json", "adapter_model.safetensors"}
DEFAULT_MAX_NEW_TOKENS = 1200


@dataclass
class GenerationStats:
    """Datos de la última llamada, para TraceEvent."""

    tokens_in: int
    tokens_out: int
    latency_ms: float
    reached_limit: bool


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_adapter(zip_path: Path, dest: Path, expected_sha256: str = ADAPTER_SHA256) -> Path:
    """Verifica el zip publicado en la Entrega 2 y lo extrae en ``dest``."""
    actual = sha256_file(zip_path)
    if actual != expected_sha256:
        raise ValueError(f"SHA-256 del adapter no coincide: {actual}")
    with zipfile.ZipFile(zip_path) as archive:
        if set(archive.namelist()) != ADAPTER_FILES:
            raise ValueError(f"contenido inesperado en el zip: {archive.namelist()}")
        dest = Path(dest)
        dest.mkdir(parents=True, exist_ok=True)
        archive.extractall(dest)
    return dest


class QwenLLM:
    """Implementa el protocolo LLM de los agentes sobre un modelo ya cargado."""

    def __init__(self, model: Any, tokenizer: Any, *, has_adapter: bool,
                 max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS):
        self.model = model
        self.tokenizer = tokenizer
        self.has_adapter = has_adapter
        self.max_new_tokens = max_new_tokens
        self.last_stats: Optional[GenerationStats] = None

    def generate(self, prompt: str, adapter_on: bool, max_new_tokens: Optional[int] = None) -> str:
        if adapter_on and not self.has_adapter:
            raise ValueError("adapter_on=True, pero el modelo se cargó sin adapter")
        import torch

        limit = max_new_tokens or self.max_new_tokens
        text = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt", add_special_tokens=False).to(self.model.device)
        adapter = nullcontext() if adapter_on or not self.has_adapter else self.model.disable_adapter()
        cuda = torch.cuda.is_available()
        if cuda:
            torch.cuda.synchronize()
        started = time.perf_counter()
        with adapter, torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=limit, do_sample=False,
                                         pad_token_id=self.tokenizer.eos_token_id)
        if cuda:
            torch.cuda.synchronize()
        new = output[0, inputs["input_ids"].shape[1]:]
        self.last_stats = GenerationStats(
            tokens_in=int(inputs["input_ids"].shape[1]), tokens_out=int(new.numel()),
            latency_ms=round((time.perf_counter() - started) * 1000, 1),
            reached_limit=bool(new.numel() >= limit),
        )
        return self.tokenizer.decode(new, skip_special_tokens=True).strip()


def load_qwen(adapter_dir: Optional[Path] = None, *, device_map: Any = None, dtype: Any = None,
              max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS) -> QwenLLM:
    """Carga el modelo base y, si se indica, el adapter extraído con extract_adapter."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    set_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=REVISION, torch_dtype=dtype or torch.float16,
        device_map=device_map or {"": 0})
    if adapter_dir is not None:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter_dir, is_trainable=False)
    model.eval()
    return QwenLLM(model, tokenizer, has_adapter=adapter_dir is not None,
                   max_new_tokens=max_new_tokens)
