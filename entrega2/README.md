# Entrega 2: formulación LP/MILP con Qwen2.5-1.5B + QLoRA

La tarea es formular modelos matemáticos paramétricos desde español, sin resolverlos. El modelo elegido sigue siendo Qwen2.5-1.5B-Instruct; Qwen3-14B se usa exclusivamente como juez offline.

## Estado comprobado

- Baseline recuperado del CSV original: **0.5884/5**, n=30; cobertura 0.164444; 21 casos con score cero.
- Caso oftalmológico: **0.369/5** para la respuesta histórica de Entrega 1 y **0.650/5** para prompting directo determinista. No mezclar las dos variantes.
- Dataset: 1050 entradas únicas, 50 targets canónicos, 50 familias; separación 840/210 correcta.
- Tokenización y assistant-only verificados sobre los 1050 ejemplos: máximo 930 tokens; 1024 basta; cero truncamientos.
- Reagregación exacta de los 32 juicios históricos usando el código original FOM-5 v2: todos los campos coinciden.
- MCP y Google Drive conectados; Tesla T4 de 15 GB comprobada. Dos pilotos de 160/40 y entrenamiento completo de 1050 finalizados (131 pasos, 982 s). Las 31 respuestas de prueba están guardadas y verificadas por ID y hash de entrada. **FOM-5 v2 oficial: 0.5884 → 0.8024/5 en 30 casos**, diferencia media pareada +0.2140; 14 mejoran, 8 empatan y 8 empeoran. Los puntajes cero bajan de 21 a 12. El IC bootstrap del cambio (-0.2136, +0.7007) incluye cero, por lo que no demuestra una mejora robusta.

## Archivos principales

- `notebooks/01_qlora_experimento_controlado.ipynb`: revisión derivada del notebook `fixed`; pilot, development y final, persistencia en Drive y controles de transición.
- `notebooks/02_generacion_final_31.ipynb`: inferencia FP16, user-only, 1200 tokens, igual que el baseline. Usa únicamente entradas sin gold.
- `notebooks/03_evaluacion_fom5_v2_final.ipynb`: mismo prompt, parser, calibración y agregación del evaluador autoritativo; 31 evaluaciones nuevas, sin sobrescribir el baseline.
- `results/baseline/`: 30 resultados originales filtrados, resumen, dos respuestas diagnósticas originales y texto exacto del caso 31.
- `results/audit/`: checksums, diversidad, longitudes y regresión del evaluador.
- `docs/experimental_protocol.md`: protocolo y límites metodológicos.
- `docs/dataset_review.md`: revisión del dataset, incluyendo sus limitaciones.
- `codex_missing_assets/`: evidencia autoritativa recibida; conservar intacta.

## Ejecución en Colab

1. Guardar esta carpeta (sin `.tools`, `.venv`, `tmp`) en `MyDrive/IA/entrega2_qlora`. Guardar el ZIP de datos en `MyDrive/IA/or_sft_dataset_v1_2_final.zip`.
2. Abrir el notebook 01 en Colab y seleccionar GPU T4. Los artefactos se guardan en `MyDrive/IA/qwen25_qlora_or_v2`; así no se sobrescribe una corrida previa del notebook original.
3. Se ejecutó `RUN_MODE='pilot'`, `RUN_TAG='run01'`: 160/40, una época. La pérdida bajó, pero las respuestas no pasaron la revisión matemática. Sus salidas intactas están en Drive.
4. Se ejecutó `04_qlora_user_only_controlado.ipynb` con `RUN_MODE='pilot'`, `RUN_TAG='user_only_run01'`: mismos 160/40 y parámetros, con entrada de entrenamiento igual a la inferencia user-only. Redujo truncamientos 5/10 → 1/10, aunque persistieron errores matemáticos.
5. La corrida exploratoria real congeló **una época y el formato user-only** antes del benchmark y usa los 1050 ejemplos desde el modelo base. Se omitió el desarrollo 840/210 que aparecía en el plan inicial; no atribuirle una selección por pérdida de esa fase. Artefactos en `final/user_only_run01`.
6. Tras completar final, ejecutar notebook 02. Guarda `final/user_only_run01/benchmark/final_generations_31.jsonl`. No mostrar gold/requirements al modelo ni reparar respuestas.
7. Liberar la GPU o abrir un entorno limpio; ejecutar notebook 03. Se exige calibración y se guardan resultados caso a caso. Un fallo del juez se reintenta al reanudar; nunca se elimina para reducir n.
8. Conservar el CSV final, comparación pareada, manifests, adapter, logs y versiones. Elaborar informe y video solo con resultados realmente obtenidos.

Al reanudar, usar el mismo `RUN_TAG` y configuración; el notebook detecta checkpoint. Si cambia cualquier configuración, usar un tag nuevo. No volver a entrenar una corrida con `completed.json`. Si una sesión se interrumpe después de guardar adapter pero antes de completar la evidencia, revisar el checkpoint y los archivos parciales antes de relanzar.

La comparación principal usa los 30 casos y el baseline 0.5884. Una degradación concreta aparece en `opt_02`: 1.300 → 0.000, pues el adapter modela incorrectamente las horas extraordinarias y omite la entrega mínima de C; véase `results/final/failure_case_opt02.md`. El caso 31 se informa aparte: baseline determinista 0.650, QLoRA 3.850, pero el adapter aún omite la ponderación poblacional del objetivo. El promedio extendido de 31 es 0.9007 para QLoRA. El caso histórico muestreado (0.369) se usa solo para continuidad de Entrega 1. Al menos `opt_01`, `opt_16`, `opt_30` tuvieron exposición previa durante desarrollo histórico; el benchmark no es completamente virgen. Al excluir solo esos tres, el cambio medio en 27 casos es +0.2464. El cambio a user-only y la época única quedaron congelados antes de generar sobre el conjunto oficial.

## Auditorías locales

Python 3.12 o 3.13:

```powershell
python -m pip install transformers==4.51.3 numpy jinja2
python scripts/audit_dataset.py
python scripts/recover_baseline.py
python scripts/build_notebook.py
python scripts/build_evaluation_notebooks.py
python scripts/verify_tokenizer_and_metric.py
```

Estas auditorías no necesitan pesos del modelo ni GPU. Las dependencias de entrenamiento están fijadas en el notebook; además se guarda `pip freeze` del runtime efectivo. La revisión del modelo queda registrada por hash.

## MCP oficial de Colab

Se instaló `googlecolab/colab-mcp` 1.0.1, commit `b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1`, en `.tools/colab-mcp` y se registró como `colab` en la configuración local de Codex. `codex mcp get colab` comprueba el registro. Requiere enlazar una pestaña de Colab en el mismo equipo; registrar el servidor no acredita una sesión GPU conectada.

El cliente local `scripts/colab_mcp_client.py` usa el SDK MCP oficial y mantiene una sesión stdio; no expone un servidor HTTP. Su estado temporal queda en `tmp/colab_mcp/`. Ejecutarlo con el Python del entorno del MCP. No publicar esos archivos temporales.

Para las ejecuciones largas se usa `scripts/run_training_notebook.py`: ejecuta las celdas 2–12 del notebook revisado en un proceso Python nuevo por fase. El montaje de Drive y la instalación se hacen primero en Colab. Se sustituye únicamente `RUN_MODE` y la llamada de montaje por una comprobación de Drive ya montado. El hash del notebook, la celda activa, los errores y el progreso se guardan en `worker_<fase>.json` y `worker_<fase>.log`. Esto permite consultar el progreso sin depender de que una llamada MCP permanezca abierta durante todo el entrenamiento.

## Demostración y repositorio público

Repositorio del grupo: [GenAI-Optimization](https://github.com/Jose21531/GenAI-Optimization). La versión controlada de esta entrega contiene código, datos, salidas y juicios verificables; el PDF y video se agregan al cerrarlos. La celda **DEMOSTRACIÓN PARA GRABAR** al final del Colab de trabajo ejecuta `scripts/demo_same_input.py` sobre el caso oftalmológico: genera un baseline directo nuevo y una salida QLoRA nueva bajo el mismo prompt y guarda `live_demo.json`. Se ejecuta con la captura de pantalla ya iniciada. La respuesta histórica recuperada permanece intacta.

## Entrega del profesor

PDF vertical de una página compilado desde LaTeX, video real <=3 minutos con baseline y solución en la misma entrada, y enlace de repositorio reproducible. La falla real post-ajuste se documenta en `results/final/failure_case_diagnostic.md`. El video de pantalla se grabará con la celda preparada y se añadirá al repositorio. La mejora de la media observada es exploratoria y su intervalo bootstrap incluye cero.
