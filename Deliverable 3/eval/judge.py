"""Backend externo Qwen3-14B: carga diferida y protocolo del juez original."""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field

from eval.legacy import JUDGE_MODEL, JUDGE_REVISION, bind_judge


@dataclass
class JudgeReply:
    parsed: dict
    raw: str
    input_tokens: int
    output_tokens: int
    latency_sec: float = 0.0
    attempts: list[dict] = field(default_factory=list)


class JudgeFailure(RuntimeError):
    def __init__(self, message, attempts):
        super().__init__(message)
        self.attempts = copy.deepcopy(attempts)


class _ObservedTokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.attempts = []

    def __getattr__(self, name):
        return getattr(self.tokenizer, name)

    def apply_chat_template(self, messages, **kwargs):
        result = self.tokenizer.apply_chat_template(messages, **kwargs)
        self.attempts.append({"messages": copy.deepcopy(messages)})
        return result

    def __call__(self, *args, **kwargs):
        result = self.tokenizer(*args, **kwargs)
        self.attempts[-1]["input_tokens"] = int(result["input_ids"].shape[1])
        return result

    def decode(self, generated, **kwargs):
        raw = self.tokenizer.decode(generated, **kwargs)
        self.attempts[-1].update(raw=raw.strip(), output_tokens=int(generated.shape[0]))
        return raw


class _ObservedModel:
    def __init__(self, model, observed):
        self.model, self.observed = model, observed

    def __getattr__(self, name):
        return getattr(self.model, name)

    def generate(self, **kwargs):
        self.observed.attempts[-1]["generation"] = {
            key: kwargs[key] for key in ("max_new_tokens", "do_sample", "use_cache", "pad_token_id", "eos_token_id")}
        try:
            return self.model.generate(**kwargs)
        except Exception as error:
            self.observed.attempts[-1]["error"] = str(error)
            raise


class QwenFOM5Judge:
    kind = "real"
    model_id = JUDGE_MODEL
    revision = JUDGE_REVISION

    def __init__(self, model, tokenizer, torch):
        self.observed = _ObservedTokenizer(tokenizer)
        self.function = bind_judge(_ObservedModel(model, self.observed), self.observed, torch)

    def judge(self, item, candidate) -> JudgeReply:
        self.observed.attempts = []
        started = time.perf_counter()
        try:
            parsed, raw, incoming, outgoing = self.function(item, candidate)
        except Exception as error:
            raise JudgeFailure(str(error), self.observed.attempts) from error
        return JudgeReply(parsed, raw, incoming, outgoing, time.perf_counter() - started,
                          copy.deepcopy(self.observed.attempts))


def load_qwen3() -> QwenFOM5Judge:
    """Misma revisión, NF4, dtype y device_map de la celda 14 de Entrega 2."""
    import importlib.util
    import torch

    if not torch.cuda.is_available() or "T4" not in torch.cuda.get_device_name(0):
        raise RuntimeError("La evaluación real se ejecuta en una GPU T4 de Colab")
    try:
        in_colab = importlib.util.find_spec("google.colab") is not None
    except ModuleNotFoundError:
        in_colab = False
    if not in_colab:
        raise RuntimeError("La evaluación real debe ejecutarse en Colab")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                              bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(JUDGE_MODEL, revision=JUDGE_REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        JUDGE_MODEL, revision=JUDGE_REVISION, quantization_config=quant,
        device_map={"": 0}, torch_dtype=torch.float16, low_cpu_mem_usage=True)
    model.eval()
    judge = QwenFOM5Judge(model, tokenizer, torch)
    from importlib.metadata import version
    judge.runtime = {name: version(name) for name in ("torch", "transformers", "accelerate", "bitsandbytes")}
    judge.runtime["device"] = torch.cuda.get_device_name(0)
    return judge


class MockJudge:
    """Prueba de intercambio; sus puntajes nunca son resultados del experimento."""
    kind = "mock"
    model_id = "MockJudge"
    revision = "test-only"

    def judge(self, item, candidate):
        import json

        parsed = {"has_formulation": False,
                  "requirements": {r["id"]: "missing" for r in item["requirements"]},
                  "scores": {d: 0 for d in ("decision_domains", "objective", "constraints_logic", "algebra_validity", "generalization")},
                  "fatal_errors": ["Salida sintética para probar infraestructura de evaluación"]}
        return JudgeReply(parsed, json.dumps(parsed, ensure_ascii=False), 0, 0)
