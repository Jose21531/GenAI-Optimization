# Registro técnico de ejecución

## 2026-09-30: conexión y piloto

- Conexión real mediante el servidor MCP oficial de Google Colab; acceso a Drive autorizado por el usuario.
- Hardware observado: Tesla T4, 15360 MiB; runtime Python 3.13.15, PyTorch 2.11.0+cu128. Las dependencias específicas se instalaron desde el notebook y se registran en el manifest.
- Las verificaciones en Colab reprodujeron las longitudes locales: máximo 930 tokens en 1050 ejemplos, sin truncamiento a 1024. Piloto 160/40, 40 familias de entrenamiento y 10 de validación, sin intersección.
- Antes del primer paso de optimización, se hizo explícito `label_names=['labels']` en `TrainingArguments` para evitar la inferencia automática de etiquetas de PEFT. La primera evaluación **sí había registrado** `base_eval_loss=0.8176520466804504`; el aviso no implicaba que esa medición estuviera ausente. Se conservaron los archivos previos con sufijo `before_label_fix` y se reinició el piloto desde el modelo base.
- El notebook fuente, su hash, el proceso, la celda activa y los errores quedan registrados. Los procesos de cada fase son independientes; la desconexión de una llamada MCP no debe confundirse con la terminación del trabajo remoto.
- Última lectura confirmada del piloto: 10 respuestas previas al ajuste guardadas, 5 truncadas a 1200 tokens; entrenamiento en paso 19/20, T4 activa. Desde el guardado del checkpoint, las llamadas del MCP a `run_code_cell` y `get_cells` han agotado 180 s aun después de reiniciar únicamente el puente MCP. **No se ha verificado si el proceso remoto terminó.** Antes de reanudar, inspeccionar `worker_pilot.json`, `worker_pilot.log` y `pilot/run01/completed.json` en Drive; no lanzar una segunda corrida a ciegas.

Este registro no acredita resultados finales ni una mejora matemática; esas conclusiones requieren las salidas y la evaluación posteriores.

## Recuperación y decisión del primer piloto

Tras recargar la pestaña, el MCP pudo leer el cierre real del piloto: estado `completed`, pérdida de validación 0.817652 → 0.414046, 10 pares de respuestas guardados. Las salidas ajustadas llegaron al límite de 1200 tokens en 5/10 casos, igual que el modelo base; las líneas largas repetidas subieron de 36 a 216. La disminución de pérdida **no** se acepta como prueba de formulación correcta. En F21 el adapter impone `sum_i x_i=6` y `x_i<=x_j` para rutas, restricciones ajenas a la cobertura exacta pedida; en F49 reproduce el enunciado sin formular decisiones ni restricciones. No se aprobó este piloto para desarrollo ni final.

Se detectó un desajuste controlable: el SFT original incluye una instrucción de sistema en el input, pero la inferencia comparable con el baseline oficial recibe solo el mensaje del usuario. Se creó `04_qlora_user_only_controlado.ipynb` con el mismo conjunto, split, targets y parámetros, cambiando exclusivamente el contexto de entrenamiento a user-only. La auditoría con tokenizer real verificó 1050/1050 fronteras de respuesta, targets exactos y tokens finales, máximo 887 tokens, cero truncamientos con 1024. Se inició un segundo piloto aislado en `pilot/user_only_run01`. Las diez salidas del modelo base se reutilizan porque revisión, pesos de base, prompt de inferencia, entradas y configuración de generación son idénticos; se registró su hash. Esta reutilización no afecta la evaluación oficial posterior.

## Segundo piloto y entrenamiento completo

El piloto user-only terminó en Drive: pérdida de validación 0.917530 → 0.423407, truncamientos 5/10 → 1/10 y 36 líneas largas repetidas antes y después. La revisión algebraica halló errores concretos en F05, F11, F17, F38 y F43; no se declaró éxito de formulación. Se congeló entonces una corrida exploratoria de una época con las 1050 instancias para medir el benchmark solicitado, omitiendo la etapa development 840/210 por la cuota de T4. La decisión fue anterior a leer cualquier salida del test.

La corrida final `final/user_only_run01` completó 131/131 pasos en una Tesla T4, con `train_runtime=981.9066` s, `train_loss=0.1054399661`, pico de memoria reservada de 9.037 GiB y sin checkpoint seleccionado por validación. El `manifest.json` y `completed.json` se copiaron localmente; sus hashes coinciden, y el cierre enumera hashes del adapter, tokenizer y argumentos de entrenamiento. Este loss de entrenamiento no se usa como medida de equivalencia matemática. La inferencia FP16 en 31 casos comenzó después del cierre y escribe cada salida en Drive por ID; la evaluación FOM-5 v2 se ejecutará solo cuando terminen las 31.

## Comparación oficial cerrada

La generación final produjo 31 salidas con 31 IDs únicos, hashes de entrada concordantes y ningún agotamiento del límite de 1200 tokens. El juez Qwen3-14B se cargó en NF4 después de liberar el generador. Su manifiesto conserva la revisión de pesos, la Tesla T4 y los hashes exactos de generaciones, gold y notebook evaluador. La calibración original superó 5/5 umbrales, incluido el 0.369 histórico del diagnóstico. Las 31 respuestas se juzgaron sin errores y sus JSON brutos se reagregaron localmente, reproduciendo 31/31 puntajes y dimensiones.

En los 30 casos oficiales la media FOM-5 v2 pasó de 0.5884 a 0.802367/5: diferencia media pareada +0.213967. Mejoran 14, empatan 8 y empeoran 8. El IC bootstrap pareado 95% del cambio es [-0.21357, +0.70073], por lo que la media positiva no constituye evidencia sólida de mejora general con una sola semilla. Excluyendo solo `opt_01`, `opt_16`, `opt_30`, previamente expuestos según la bitácora, el cambio medio de los otros 27 es +0.24637; tampoco se garantiza independencia algebraica entre esos casos y las familias sintéticas. El diagnóstico oftalmológico mejora 0.650 → 3.850 en la variante determinista, pero la salida QLoRA omite $p_j$ del objetivo y sigue siendo matemáticamente distinta al gold. Los CSV, juicios brutos y comparaciones quedan en `results/colab/final/user_only_run01` y `results/final`.
