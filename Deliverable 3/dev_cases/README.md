# Casos de desarrollo

Ocho enunciados nuevos para ajustar los prompts antes de congelar la configuración. Los prompts se ajustan solo con estos casos, nunca con los 30 oficiales.

| Archivo | Contenido | Quién lo lee |
|---|---|---|
| `inputs.jsonl` | `id`, `title`, `problem`, con el mismo formato que `data/benchmark_30_generation_only.jsonl`. | El orquestador, como entrada de los agentes. |
| `reference/dev_reference.jsonl` | `reference_model`, `requirements` (`R1..Rn` con `kind`), `distractors` y `notes`. | Solo `eval/` y los tests. Los agentes, las herramientas y los prompts no lo abren. |

| Caso | Tipo | Qué prueba |
|---|---|---|
| dev01 | LP, mezcla | Proporción máxima, rango de grasa y dos números distractores. |
| dev02 | LP | Capacidad ampliable con horas extra y encargos externos. Es distinto de `opt_02`; está declarado en `docs/decisiones.md`. |
| dev03 | MILP binario | Asignación con capacidad, dos revisiones por artículo y conflictos de interés. |
| dev04 | MILP binario | Mochila con dos recursos, precedencia, exclusión y mínimo de proyectos. |
| dev05 | MILP entero | Transporte con viajes enteros que acotan las toneladas. |
| dev06 | MILP | Costo fijo de encendido, capacidad condicionada y lote mínimo. |
| dev07 | MILP binario | Carga en contenedores con incompatibilidad. |
| dev08 | LP multiperíodo | Balance de inventario, silo limitado y dos números distractores. |

`tests/test_dev_cases.py` comprueba el formato, que los distractores estén en el enunciado y que la superposición con los enunciados oficiales sea baja.
