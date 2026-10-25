"""LLM de prueba que no necesita GPU: devuelve respuestas guionizadas."""

from __future__ import annotations

from typing import Callable, Union

Responder = Callable[[str, bool], str]


class MockLLM:
    """Implementa generate(prompt, adapter_on) y registra cada llamada."""

    def __init__(self, responses: Union[list[str], Responder]):
        self._responder = responses if callable(responses) else None
        self._queue = [] if callable(responses) else list(responses)
        self.calls: list[tuple[str, bool]] = []

    def generate(self, prompt: str, adapter_on: bool) -> str:
        self.calls.append((prompt, adapter_on))
        if self._responder is not None:
            return self._responder(prompt, adapter_on)
        if not self._queue:
            raise AssertionError("MockLLM no tiene más respuestas")
        return self._queue.pop(0)
