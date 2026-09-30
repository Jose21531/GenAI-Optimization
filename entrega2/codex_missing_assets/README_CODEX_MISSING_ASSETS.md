# Archivos faltantes para Codex

Este paquete complementa `contexto_codex_proyecto_IA_QLoRA_v2_31_casos.md`.

## Archivos autoritativos

### Generación / benchmark
- `benchmark_30_generation_only.jsonl`: 30 problemas oficiales sin gold ni requirements. Archivo seguro para el generador final.
- `benchmark_30_v2.jsonl`: mismos 30 casos con `reference_model` y `requirements`. Usar SOLO para evaluación post-hoc.
- `30_problemas_con_referencias.jsonl`: versión histórica con referencias, conservada por trazabilidad.

### Baseline
- `resultados_fom5_local.csv`: salidas originales del baseline directo y reevaluación FOM-5 v2.
  - filtro oficial: `split == "benchmark"` y `variant == "baseline_direct_deterministic"`
  - n=30
  - media FOM-5 v2=0.5884
  - mediana=0.0000
  - requirement coverage media=0.1644
- `resultados_fom5.csv`: archivo histórico de resultados de evaluación.
- `qwen_baseline_30_pipeline.ipynb`: pipeline que genera el baseline directo.

### Evaluador
- `evaluador_fom5_local.ipynb`: evaluador FOM-5 v2 autoritativo; usa `Qwen/Qwen3-14B` cuantizado en 4 bits.
- `calibracion_manual_judge.csv`: controles de calibración manual.
- `reevaluar_fom5_v2.ipynb`: notebook histórico de reevaluación; conservar por trazabilidad.

## Caso 31
El caso oftalmológico original se reporta por separado como continuidad histórica. El resultado principal sigue siendo la media de los 30 casos held-out.

## Enlace de Colab
La URL exacta del Colab no aparece en los `.ipynb` y no puede inferirse de ellos. El usuario debe proporcionar a Codex el enlace real del notebook de trabajo, normalmente con formato:

`https://colab.research.google.com/drive/<ID_DEL_NOTEBOOK>`

Codex debe usar esa URL mediante el MCP de Colab y continuar desde `qlora_qwen25_or_sft_v1_2_fixed.ipynb`.
