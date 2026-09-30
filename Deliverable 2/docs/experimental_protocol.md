# Protocolo experimental - Entrega 2

## Pregunta y evidencia

¿El ajuste QLoRA de Qwen2.5-1.5B-Instruct mejora la formulación paramétrica LP/MILP respecto de prompting directo en las mismas entradas?
El criterio es equivalencia matemática con símbolos definidos, índices y dominios coherentes, objetivo y restricciones completos, sin resolver el óptimo. Un indicador de formato no mide este criterio.

El baseline **histórico recuperado y verificado** es FOM-5 v2 = 0.5884/5 en 30 casos. Su mediana es 0, desviación muestral 1.159973 y cobertura 0.164444. Se recuperaron problemas, respuestas, prompt, configuración y evaluador desde `codex_missing_assets`. La reagregación del JSON del juez reproduce los 32 registros (30 oficiales y dos variantes diagnósticas). No se volvió a ejecutar el modelo ni el juez. No reemplazar esta cifra ni fabricar resultados faltantes.

La documentación revela exposición previa de `opt_01`, `opt_16` y `opt_30` durante ensayos de prompting. Se mantiene el conjunto oficial de 30 para comparabilidad, pero debe declararse esa exposición; no llamarlo test completamente independiente. Un análisis secundario de los otros 27 requiere recuperar las filas originales y comprobar la historia de exposición. El promedio 0.5884 no es el baseline de esos 27.

## Diseño y orden obligatorio

1. **Auditoría previa:** checksums, integridad de roles y etiquetas, 50 familias, 1050 entradas únicas, separación 840/210, 200 ejemplos piloto. Longitudes con tokenizer real de Qwen y cero truncamientos. Revisar explícitamente tokens supervisados y delimitadores de fin de respuesta.
2. **Pilot:** inicializar desde el modelo base; 160 train (4 por cada una de 40 familias) y 40 validación (4 por cada una de 10 familias). Una época. Medir loss de validación antes/después y generar en las mismas 10 entradas, una por familia, antes/después del ajuste.
3. **Decisión pilot:** loss finito, gradientes finitos, descenso de loss de entrenamiento, ausencia de colapso del formato; contrastar truncamiento/repetición antes/después. Revisar manualmente coherencia matemática y transferencia en las diez familias. Un loss menor por sí solo no basta. Guardar decisión y justificación. No acceder al test para tomarla.
4. **Development:** nuevo adapter desde base; 840 train y 210 validación; configuración inicial de 2 épocas. Elegir entre checkpoints de 1 y 2 épocas por loss de validación, comprobar generaciones y congelar la configuración completa. Cualquier cambio adicional queda documentado y se decide solo con validación. No continuar el adapter pilot: produce un número distinto de exposiciones a esos 160 ejemplos.
5. **Final:** nuevo adapter desde base y entrenamiento con las 1050 instancias y los hiperparámetros congelados. La antigua validación ya pertenece al entrenamiento: no sirve como resultado independiente en esta fase. Guardar adapter, tokenizer, hashes, versión de paquetes, revisión del modelo, tiempos y VRAM.
6. **Test:** congelar adapter y configuración de generación; usar los 30 problemas oficiales y el caso histórico por separado. Se recuperó el protocolo exacto: Qwen2.5 FP16, mensaje user-only, `do_sample=False`, máximo 1200 tokens. El adapter se carga sobre la base FP16 para comparar bajo la misma precisión de inferencia. El entrenamiento sigue usando NF4. No se sustituye por el prompt de sistema del SFT. La revisión de pesos original no estaba fijada: conservar esta limitación y registrar el commit de las nuevas ejecuciones.
7. **Juez post-hoc:** Qwen3-14B, NF4, determinista, sin thinking, separado del generador. Descargar/liberar el generador antes. Se recuperaron las celdas originales de prompt, parser, retries, calibración y agregación de FOM-5 v2 y se preservaron en el notebook 03. Se guardan hashes para comprobarlo. No sustituirlo por otro que solo use los mismos pesos.

## Hiperparámetros iniciales

NF4 de 4 bits, doble cuantización, cómputo FP16; LoRA r=16, alpha=32, dropout=0.05 en q/k/v/o_proj y gate/up/down_proj. Batch 1, acumulación 8, LR=2e-4, warmup 0.05, scheduler cosine, paged_adamw_8bit, semilla 42. Longitud 1024: máximo medido sobre todo el conjunto 930. Prohibido cortar etiquetas para hacerlas caber. La auditoría CPU verificó assistant-only, correspondencia exacta del target y EOS en 1050/1050 ejemplos.

Colab Free/T4 es el hardware objetivo. Se debe registrar el hardware realmente asignado y cualquier diferencia. La disponibilidad de GPU y la duración de sesión no están garantizadas. No descargar ambos modelos simultáneamente en GPU.

## Evaluación y reporte

FOM-5 v2: dominios 15%, objetivo 20%, restricciones 35%, álgebra 15%, generalización 15%, dimensiones en escala 0-5. Cobertura: met=1, partial=0.5, missing/wrong=0. Las reglas y cualquier gate final son las del evaluador original, no se infieren del resumen.

Reportar tres agregaciones distintas: media principal de 30, score del caso original y media extendida de 31. Conservar scores y salidas por ID; incluir cinco dimensiones, cobertura, truncamiento, tiempo y tokens. Para una comparación pareada: delta medio, bootstrap pareado con semilla fija y proporción mejora/empate/empeora, solo con las 30 parejas auténticas. Con n=30, una sola semilla de entrenamiento y un juez automático, la incertidumbre sigue siendo importante.

Seleccionar un caso ilustrativo de éxito y **una falla real del modelo adaptado**, con salida intacta, ID y explicación algebraica concreta. No usar fallas del baseline para fingir una falla post-ajuste. El caso oftalmológico es continuidad histórica, no evidencia independiente. La formulación de referencia nunca se muestra al generador.

## Entrega requerida por el profesor

- PDF vertical de una página, compilado desde LaTeX: modelo y versión, selección frente a Gemma-2-2B-IT y Phi-3-mini (3.8B), pipeline, intervención vinculada a la falla, alternativas evaluadas, resultados medidos y tamaño del conjunto, límites concretos.
- Video <=3:00 mostrando ejecución real y baseline visible sobre la misma entrada; enlace accesible.
- Repositorio con enlace funcional y README que reproduce lo mostrado.

El informe solo puede considerarse final cuando haya resultados reales. No se presupone que el ajuste mejorará: una degradación también se debe informar.

## Ejecución real y desviación del plan

El piloto original con system+user bajó la pérdida de validación de 0.817652 a 0.414046, pero conservó 5/10 truncamientos y elevó las líneas largas repetidas de 36 a 216. Ejemplos revisados F21 y F49 muestran restricciones ajenas y eco del enunciado. No se aprobó como éxito matemático.

Un segundo piloto alineó la entrada de SFT con el protocolo user-only del benchmark, sin cambiar targets, familia, split ni hiperparámetros. La auditoría verificó 1050/1050 fronteras assistant, targets y tokens de fin, con máximo 887 tokens. La pérdida de validación bajó de 0.917530 a 0.423407, los truncamientos pasaron de 5/10 a 1/10 y las líneas repetidas permanecieron en 36. Persisten errores en F05, F11, F17, F38 y F43, entre otros; tampoco certifica formulación correcta.

Para obtener la comparación con los 30 casos solicitada, se congeló antes del test una corrida **exploratoria** con user-only, una época y los hiperparámetros del piloto, entrenando desde la base con 1050 instancias. La fase development 840/210 del plan anterior se omitió para priorizar la ejecución completa con la cuota de T4 disponible. No se seleccionó un checkpoint ni épocas según la pérdida de 210 casos y no debe afirmarse tal ablación. Se preservan los dos pilotos, la decisión y los hashes. El test oficial solo se abrirá tras concluir el entrenamiento final.
