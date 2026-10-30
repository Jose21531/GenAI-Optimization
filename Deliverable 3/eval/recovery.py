"""Recuperación explícita y respaldada de una última línea JSONL truncada."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from eval.artifacts import parse_jsonl


def _incomplete(tail: bytes) -> bool:
    try:
        text = tail.decode("utf-8")
    except UnicodeDecodeError as error:
        if error.reason != "unexpected end of data" or error.end != len(tail):
            return False
        text = tail[:error.start].decode("utf-8")
    text = text.rstrip()
    if not text.startswith("{"):
        return False
    try:
        json.loads(text)
    except json.JSONDecodeError as error:
        suffix = text[error.pos:]
        return (error.pos >= len(text) or error.msg.startswith("Unterminated string")
                or (error.msg.startswith("Invalid \\uXXXX escape") and bool(re.search(r"\\u[0-9a-fA-F]{0,3}$", text)))
                or (error.msg == "Expecting value" and suffix in {"n", "nu", "nul", "t", "tr", "tru", "f", "fa", "fal", "fals", "-"})
                or (error.msg == "Expecting ',' delimiter" and bool(re.fullmatch(r"(?:[eE][+-]?|\.)", suffix))))
    return False


def recover_jsonl_tail(path: Path):
    """No cambia la lectura normal. Valida todo el prefijo antes de escribir.

    Recupera sintaxis, no valida puntajes ni identidad del experimento: esas
    comprobaciones siguen siendo obligatorias al reanudar la evaluación.
    """
    path = Path(path)
    original = path.read_bytes()
    if not original or original.endswith(b"\n"):
        raise ValueError("Solo se recupera una última línea incompleta sin salto de línea final")
    boundary = original.rfind(b"\n") + 1
    prefix, tail = original[:boundary], original[boundary:]
    if not _incomplete(tail):
        raise ValueError("La última línea es válida o no se reconoce como JSON truncado; no se modificó el archivo")
    rows = parse_jsonl(prefix.decode("utf-8"), str(path))
    token = uuid4().hex
    backup = path.with_name(path.name + f".before-recovery-{token}.bak")
    temporary = path.with_name(path.name + f".recovery-{token}.tmp")
    audit = path.with_name(path.name + f".recovery-{token}.json")
    event = {"action": "recover_incomplete_jsonl_tail", "source": path.name, "backup": backup.name,
             "utc": datetime.now(timezone.utc).isoformat(), "retained_records": len(rows),
             "discarded_bytes": len(tail), "original_sha256": hashlib.sha256(original).hexdigest(),
             "recovered_sha256": hashlib.sha256(prefix).hexdigest(), "status": "prepared"}
    if path.read_bytes() != original:
        raise ValueError("El archivo cambió durante la validación; detener la recuperación")
    with backup.open("xb") as stream:
        stream.write(original)
        stream.flush()
        os.fsync(stream.fileno())
    with audit.open("x", encoding="utf-8") as stream:
        json.dump(event, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    with temporary.open("xb") as stream:
        stream.write(prefix)
        stream.flush()
        os.fsync(stream.fileno())
    if path.read_bytes() != original:
        raise ValueError("El archivo cambió antes de reemplazarlo; el original no fue modificado")
    temporary.replace(path)
    event["status"] = "recovered"
    audit_completed = audit.with_name(audit.name + ".tmp")
    with audit_completed.open("x", encoding="utf-8") as stream:
        json.dump(event, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    audit_completed.replace(audit)
    return dict(event, recovery_log=str(audit))
