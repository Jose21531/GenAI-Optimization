"""LLM de prueba que no necesita GPU y registro de archivos abiertos."""

from __future__ import annotations

import builtins
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, Union
from unittest import mock

Responder = Callable[[str, bool], str]


@contextmanager
def archivos_abiertos() -> Iterator[list[Path]]:
    """Registra los archivos que se abren dentro del bloque.

    Intercepta ``Path.open`` (lo usan read_text y read_bytes) y ``open``.
    Interceptar solo ``io.open`` no basta: en Python 3.10, pathlib guarda su
    propia referencia y la lectura no queda registrada.
    """
    abiertos: list[Path] = []
    path_open, builtin_open = Path.open, builtins.open

    def por_path(self, *args, **kwargs):
        abiertos.append(Path(self).resolve())
        return path_open(self, *args, **kwargs)

    def por_builtin(file, *args, **kwargs):
        if isinstance(file, (str, os.PathLike)):
            abiertos.append(Path(file).resolve())
        return builtin_open(file, *args, **kwargs)

    with mock.patch.object(Path, "open", por_path), mock.patch("builtins.open", por_builtin):
        yield abiertos


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
