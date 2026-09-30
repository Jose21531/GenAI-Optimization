"""Reconstruye los dos conjuntos publicados desde los archivos fuente congelados.

No es el generador sintético original: ese código de autoría no fue entregado.
Se preservan exactamente los 30 problemas oficiales y los 1050 ejemplos del ZIP.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"


def read_jsonl_bytes(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    with ZipFile(SOURCE / "or_sft_dataset_v1_2_final.zip") as archive:
        rich = read_jsonl_bytes(archive.read("or_sft_1050_rich_v1_2.jsonl"))
        messages = read_jsonl_bytes(archive.read("or_sft_1050_messages_v1_2.jsonl"))
    assert len(rich) == len(messages) == 1050
    by_id = {row["id"]: row for row in messages}
    assert len(by_id) == 1050
    assert len({row["problem"] for row in rich}) == 1050
    assert len({row["family_id"] for row in rich}) == 50
    assert {row["model_type"] for row in rich} == {"LP", "MILP"}
    train = []
    for row in rich:
        msg = by_id[row["id"]]["messages"]
        assert [part["role"] for part in msg] == ["system", "user", "assistant"]
        assert msg[1]["content"] == row["problem"]
        assert msg[2]["content"] == row["answer"]
        train.append({
            "id": row["id"], "family_id": row["family_id"],
            "family": row["family"], "model_type": row["model_type"],
            "difficulty": row["difficulty"],
            "messages": msg[1:],  # Formato user-only congelado para el ajuste final.
        })

    official = read_jsonl_bytes((SOURCE / "benchmark_30_v2.jsonl").read_bytes())
    generation = read_jsonl_bytes((SOURCE / "benchmark_30_generation_only.jsonl").read_bytes())
    assert len(official) == len(generation) == 30
    assert len({row["id"] for row in official}) == 30
    stripped = [
        {key: row[key] for key in ("id", "title", "problem", "model_class", "difficulty")}
        for row in official
    ]
    assert stripped == generation, "El benchmark de generación difiere del archivo oficial."
    assert all("reference_model" not in row and "requirements" not in row for row in generation)

    diagnostic = read_jsonl_bytes((SOURCE / "caso_entrega1_generation_only.jsonl").read_bytes())
    assert len(diagnostic) == 1 and diagnostic[0]["id"] == "diagnostic_oftalmo"
    write_jsonl(HERE / "train_1050_user_only.jsonl", train)
    write_jsonl(HERE / "benchmark_30_generation_only.jsonl", generation)
    write_jsonl(HERE / "caso_entrega1_generation_only.jsonl", diagnostic)
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.glob("*.jsonl"))
    }
    (HERE / "SHA256SUMS.generated.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Reconstruidos: {len(generation)} benchmark, {len(train)} entrenamiento, 1 diagnóstico")
    print("Familias:", len({row["family_id"] for row in train}))
    print("Tipos:", {kind: sum(row["model_type"] == kind for row in train) for kind in ("LP", "MILP")})


if __name__ == "__main__":
    main()
