# Estado de continuidad · Entrega 3

Actualizado el 31-10-2026. La generación está congelada en el tag `v3-freeze` (`a5c9c82`): Qwen2.5-1.5B-Instruct, adapter QLoRA en el Formulador, Verificador sin adapter, prompts `analista_v6`, `formulador_v3`, `verificador_v10`. `eval/provenance.py` verifica los bytes de código, prompts y configuración de ese tag.

- **Piloto:** ocho casos de desarrollo por configuración, resultados y trazas en `results/pilot/` y `traces/pilot/`. Verificador sin adapter: un fallo de formato; con adapter: seis. Se eligió la primera configuración antes de la medición.
- **Diagnóstico:** centros oftalmológicos, fuera de la muestra principal. FOM-5 v2: baseline archivado 0,65/5; QLoRA archivado 3,85/5; tres agentes 2,60/5. Respuesta, juicio y traza en `results/diagnostic/initial/` y `traces/diagnostic/initial/`.
- **Pruebas CPU:** 187 aprobadas, 2 omitidas y 77 subpruebas en la última ejecución. Comando: `python -m pytest -q "Deliverable 3/tests" "Deliverable 3/eval/tests"` con las dependencias de `eval/requirements.txt`.
- **Experimento pendiente:** cinco variantes × 15 IDs (`opt_01`–`opt_15`). Las respuestas archivadas de baseline y QLoRA se comparan sobre esos mismos IDs. El benchmark completo de Entrega 2 contiene 30 casos y se cita como antecedente, sin atribuir 30 casos a la nueva medición. No se afirma mejora de Entrega 3 antes de completar el juez.

Para continuar: abrir el [cuaderno](../Deliverable_3.ipynb) desde `main`, conectar T4, ejecutar la sección 1 y en la sección 6 fijar `CONFIGURATION=1…5`, `FIRST_CASE=1`, `LAST_CASE=15`, `RUN_VARIANT=True`. Se guarda cada caso en `MyDrive/GenAI_Entrega3_v3freeze/`; repetir la misma celda con la misma carpeta omite los IDs terminados. Exportar cada variante como ZIP, reunir las cinco en una cuenta y activar `RUN_EVALUATE_15=True`. El juez se reanuda desde `evaluation-15/`. Después, `RUN_COMPARE_15=True` calcula las diferencias pareadas sin GPU.

Pendiente de cierre: incorporar las 75 salidas y trazas, los cinco manifiestos, los 75 juicios FOM-5 v2, la comparación pareada, cifras medidas en el informe y video del equipo. No ajustar prompts con estos 15 casos.
