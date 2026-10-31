# Entrega 3 · Sistema de agentes para formulación LP/MILP

El sistema transforma un enunciado en español en un **borrador paramétrico** con conjuntos, parámetros, variables y dominios, objetivo y restricciones. No resuelve la instancia. Usa Qwen2.5-1.5B-Instruct (revisión `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`) y el [adapter QLoRA público de Entrega 2](../Deliverable%202/adapter_qlora_qwen25_final.zip). El texto evaluable conserva el formato de la columna `candidate` de aquella entrega.

**Estado:** el piloto con ocho casos está archivado y la configuración oficial quedó fijada en [`v3-freeze`](https://github.com/Jose21531/GenAI-Optimization/tree/v3-freeze). La medición de los 30 problemas está pendiente; las medias oficiales se publicarán al completar sus cinco variantes y el juez externo.

## Recorrido de los agentes

```mermaid
flowchart LR
    E[Enunciado] --> A[Analista]
    A -->|opcional| X[extract_data_spans]
    X -->|fragmentos literales| A
    A -->|ProblemSpec + requisitos U| F[Formulador]
    F -->|plan separado + candidate textual| V[Verificador]
    V -->|opcional: CoverageMap| T[audit_model]
    T -->|AuditReport| V
    F -->|aclaración: máx. una| A
    V -->|revisión: máx. una| F
    V -->|aceptar o detener| S[Respuesta final + traza]
    S --> J[FOM-5 v2 externo]
```

| Agente | Entrada | Decisión y herramienta | Salida |
|---|---|---|---|
| Analista | `id`, título y enunciado | Entregar o releer; puede consultar `extract_data_spans` | `ProblemSpec` JSON con requisitos propios `U1…Un` y evidencia literal. |
| Formulador | Enunciado, `ProblemSpec` y observaciones si las hay | Formular o pedir aclaración; no usa herramienta externa | Plan requisito→ecuación separado y `candidate` textual con cinco secciones. |
| Verificador | Enunciado, `ProblemSpec` y borrador | Aceptar, devolver o detener; puede consultar `audit_model` | `CoverageMap`, `ReviewDecision` y observaciones comprobables. |

El orquestador valida los mensajes, aplica los presupuestos y escribe una traza JSONL de cada corrida. `audit_model` detecta inconsistencias estructurales; la revisión semántica corresponde al Verificador. [Contratos](docs/contratos.md) · [Orquestación](docs/orquestador.md) · [Decisiones](docs/decisiones.md).

## Abrir y ejecutar

[**Abrir Deliverable_3.ipynb en Colab**](https://colab.research.google.com/github/Jose21531/GenAI-Optimization/blob/main/Deliverable%203/Deliverable_3.ipynb) · [Ver el cuaderno en GitHub](Deliverable_3.ipynb)

1. Selecciona **Entorno de ejecución → Cambiar tipo de entorno → T4 GPU**. Ejecuta la sección 1 para descargar el repositorio, instalar dependencias y cargar el modelo y el adapter. Si Colab pide reiniciar después de instalar PyTorch, reinicia y repite la sección.
2. Ejecuta la sección 2: procesa **solo** el caso de centros oftalmológicos y muestra el análisis, el plan, los borradores, la revisión y la respuesta final. La sección 3 compara esa respuesta con las respuestas exactas archivadas del baseline y de Entrega 2, además de la formulación de referencia.
3. Para puntuar una respuesta nueva, activa `RUN_DIAGNOSTIC_JUDGE` en la sección 4. La celda libera el modelo generador, calibra Qwen3-14B y guarda el juicio FOM-5 v2 asociado al hash de esa respuesta. La [corrida diagnóstica archivada](results/diagnostic/initial/fom5_v2_diagnostic.json) obtuvo 2,600/5 con los tres agentes, frente a 0,650/5 del baseline y 3,850/5 de QLoRA. Ilustra los mensajes y errores del sistema; queda fuera de la media oficial.
4. La sección 5 permite repetir el [piloto archivado](results/pilot/) de ocho casos con el adaptador del Verificador encendido y apagado. Con el adaptador apagado hubo un fallo de formato; encendido, seis. Esa comparación determinó la configuración congelada. La sección 6 reproduce los 30 problemas al activar `RUN_GENERATE_30` con `STAGE='oficial'`. Después de obtener 30/30 y manifiesto en las cinco variantes, activa `RUN_EVALUATE_30`. Las opciones comienzan en `False`.

Para conservar checkpoints en Colab, activa `SAVE_TO_DRIVE` en la sección 6. El cuaderno escribe cada resultado y traza en `MyDrive/GenAI_Entrega3_oficial_v3freeze` y puede reanudar por ID. El valor predeterminado escribe en la carpeta temporal del repositorio. El código, las entradas y el adaptador se descargan públicamente; Drive se usa solo como respaldo opcional durante una sesión larga.

La grabación de hasta tres minutos puede partir desde GitHub y seguir el enlace al cuaderno. Prepara el modelo antes de grabar; muestra la ejecución del caso diagnóstico, sus mensajes intermedios y la comparación final. La sección de 30 casos queda para reproducción, fuera del recorrido breve.

## Ablaciones y archivos

Las cinco variantes usan el mismo modelo, enunciados y criterio de evaluación. `full` emplea todo el sistema; `no_evidence` retira las citas del Analista; `no_plan` retira el plan del Formulador; `no_audit` omite la herramienta del Verificador; `no_review` impide devolver el borrador para corregirlo. Baseline y QLoRA son las respuestas **archivadas** de Entrega 2, no variantes nuevas de generación.

`data/benchmark_30_generation_only.jsonl` contiene únicamente `id`, `title` y `problem`. El gold de los 30 casos se abre solo en `eval/`. Para el caso diagnóstico, `data/diagnostic_oftalmo_input.jsonl` es la entrada de los agentes y `data/diagnostic_oftalmo_gold.json` es la referencia del evaluador, extraída del evaluador original de Entrega 2. Ningún prompt ni herramienta de generación recibe el gold.

`run.py` genera un `RunResult` por ID y variante en `results/<modo>/<variante>/outputs.jsonl`, más una traza por ID bajo `traces/`. Guarda cada resultado al terminar y omite IDs completos al reanudar con la misma identidad de código y configuración. Para los ocho casos de desarrollo:

```bash
python "Deliverable 3/run.py" --mode development --variants full
```

La configuración oficial está en `config/frozen.yaml`, identificada por `v3-freeze`. El comando de generación es:

```bash
python "Deliverable 3/run.py" --mode official --variants full no_evidence no_plan no_audit no_review
```

`eval/run_eval.py` verifica los manifiestos, ejecuta FOM-5 v2 con un juez externo Qwen3-14B y conserva juicios y métricas por caso. El [protocolo de evaluación](eval/README.md) explica la calibración y la reanudación. Las salidas fallidas de generación permanecen en los 30 IDs; un fallo del juez detiene la evaluación sin inventar puntajes.

## Comprobación local

Con Python 3.10 o superior, desde la raíz del repositorio:

```bash
python -m pip install -r "Deliverable 3/eval/requirements.txt"
python -m unittest discover -s "Deliverable 3/tests"
python -m unittest discover -s "Deliverable 3/eval/tests"
python "Deliverable 3/eval/run_eval.py" verify-archives
```

Las pruebas CPU comprueban contratos, herramientas, rutas del orquestador, checkpoints y la reproducción de los 60 puntajes archivados; **no sustituyen** el piloto GPU ni el juicio real de resultados nuevos.
