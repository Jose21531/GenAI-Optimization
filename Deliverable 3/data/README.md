# Entradas de generación

`benchmark_30_generation_only.jsonl` contiene los mismos `id`, `title` y `problem` de los 30 registros oficiales de la Entrega 2. Se eliminan `reference_model`, `requirements`, `model_class` y `difficulty` antes de la ejecución de agentes. El archivo permite que `run.py` lea únicamente los enunciados. Las referencias oficiales permanecen en la Entrega 2 y se usan solo después de generar, dentro de `eval/`.
