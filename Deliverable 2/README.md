# Deliverable 2 · QLoRA sobre Qwen2.5-1.5B-Instruct

**[Abrir notebook principal en Colab](https://colab.research.google.com/github/Jose21531/GenAI-Optimization/blob/main/Deliverable%202/Deliverable_2.ipynb)** · [Informe PDF](report/informe.pdf) · [Fuente LaTeX](report/informe.tex)

El notebook principal ofrece, en orden, instalación, descarga de datos por URL con verificación de hashes, comparación caso a caso, demostración de baseline y QLoRA sobre una entrada idéntica, reproducción opcional del entrenamiento y referencias de auditoría. Requiere una T4 para las celdas de generación o entrenamiento. La demostración descarga el [adapter final público](model/adapter_qlora_qwen25_final.zip) desde este repositorio; **no requiere acceso al Gmail ni al Drive del equipo**. La sección 4 permite crear un adapter nuevo (una época, aproximadamente 16 min en la T4 observada). Un adapter nuevo debe ser evaluado de nuevo; no hereda los puntajes publicados.

## Datos y procedencia

- [`data/benchmark_30_generation_only.jsonl`](data/benchmark_30_generation_only.jsonl): 30 enunciados oficiales, **sin referencias ni requisitos**. Única entrada de generación del benchmark.
- [`data/train_1050_user_only.jsonl`](data/train_1050_user_only.jsonl): 1050 pares user/assistant, 50 familias de 21 variantes, 315 LP y 735 MILP. Hay 50 formulaciones canónicas, no 1050 estructuras independientes.
- [`data/caso_entrega1_generation_only.jsonl`](data/caso_entrega1_generation_only.jsonl): diagnóstico oftalmológico separado del promedio principal.
- [`data/source/`](data/source/) conserva el ZIP sintético original, los 30 problemas con referencias y los archivos de entrada sin referencias. El gold del benchmark **solo** se utiliza en el juicio posterior.
- [`data/build_datasets.py`](data/build_datasets.py) vuelve a producir los tres JSONL publicados, verifica IDs, roles, diversidad básica y que el archivo de generación coincide con las columnas públicas del benchmark oficial. El código original que *creó* desde cero los 30 problemas y las 50 familias sintéticas no fue entregado: este script **reconstruye** los datasets desde las fuentes congeladas, sin fingir una nueva autoría. Los SHA-256 resultantes están en `data/SHA256SUMS.generated.json`.

## Salidas y evaluación

Los dos archivos principales usan el mismo esquema: ID, respuesta textual completa (`candidate`), FOM-5 v2 y dimensiones, juicio bruto, tokens y tiempos.

| Archivo | Procedencia | Filas |
|---|---|---:|
| [`outputs/baseline_31_respuestas_y_fom5.csv`](outputs/baseline_31_respuestas_y_fom5.csv) | 30 respuestas originales filtradas de `evidence/resultados_fom5_local_original.csv` y baseline determinista del diagnóstico; **no se regeneraron** | 31 |
| [`outputs/qlora_31_respuestas_y_fom5.csv`](outputs/qlora_31_respuestas_y_fom5.csv) | Corrida final QLoRA y juez FOM-5 v2 | 31 |

[`src/build_outputs.py`](src/build_outputs.py) reconstruye ambos CSV desde la evidencia original, conserva cada respuesta y juicio e impide mezclar el diagnóstico con la media principal. `outputs/paired_comparison_30.csv` y `outputs/comparison_summary_original.json` registran los cambios y el bootstrap. El benchmark oficial de 30 casos subió de **0.5884 a 0.8024/5**: 14 mejoraron, 8 empataron y 8 empeoraron. El cambio medio fue +0.2140/5; IC bootstrap pareado de 95 % **[-0.2136, +0.7007]**, que incluye cero. Los casos con score cero bajaron de 21 a 12.

El juez autoritativo está archivado en `evidence/evaluador_fom5_local.ipynb`; la ejecución final en `src/evaluacion_final_original.ipynb`. **El juez calcula los scores por respuesta.** Después, un script y la sección 2 del notebook hacen 10 000 remuestreos de las 30 diferencias pareadas con semilla 42. El intervalo no evalúa variación entre semillas de entrenamiento ni entre jueces.

El caso de Entrega 1 se informa aparte: histórico muestreado **0.369**, baseline determinista **0.650**, QLoRA **3.850**. Aun con esta mejora, QLoRA omite $p_j$ en el objetivo; véase [`docs/failure_case_diagnostic.md`](docs/failure_case_diagnostic.md). En el benchmark, [`opt_02`](docs/failure_case_opt02.md) empeoró de **1.300 a 0.000** por inventar variables y omitir una entrega mínima. El ajuste no corrige todos los problemas.

## Reproducir los archivos locales

Desde esta carpeta, con Python 3.10+:

```bash
python data/build_datasets.py
python src/build_outputs.py
```

Para reproducir la demo, ejecutar las celdas 1–3 de [`Deliverable_2.ipynb`](Deliverable_2.ipynb) en Colab. El archivo `/content/deliverable_2/outputs/live_demo.json` escrito por la sección 3 contiene **nuevas respuestas** y tiempos bajo un mismo hash de entrada, separado de los CSV evaluados. La sección 4 puede repetir el ajuste completo sobre una T4. Los notebooks `src/qlora_user_only_original.ipynb`, `src/generacion_final_original.ipynb` y `src/evaluacion_final_original.ipynb` conservan el pipeline de investigación completo y sus controles originales.

## Límites metodológicos

El ajuste final se ejecutó con los 1050 después de dos pilotos 160/40, sin la fase de desarrollo 840/210 prevista por límite de GPU. Las familias comparten estructuras; un split por familia no garantiza independencia algebraica. El diagnóstico se usó durante el diseño y `opt_01`, `opt_16` y `opt_30` tenían exposición histórica previa. Al excluir esos tres, el cambio medio de los otros 27 fue +0.2464. Hay una sola semilla final y un juez automático: el aumento observado es exploratorio. Los detalles de datos y protocolo están en [`docs/dataset_review.md`](docs/dataset_review.md) y [`docs/experimental_protocol.md`](docs/experimental_protocol.md).

La grabación real de pantalla (máximo tres minutos) se añadirá en `video/` y se enlazará desde el README raíz. Debe mostrar la celda de generación ejecutándose, con ambos modelos sobre el mismo enunciado; no se debe cortar la ejecución de forma que la oculte.
