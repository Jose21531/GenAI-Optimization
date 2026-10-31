# Estado de continuidad · Entrega 3

Este archivo distingue trabajo terminado de resultados pendientes. La rama de integración es `feat/entrega3-integracion`; para el SHA exacto del código ejecutado, usar `git rev-parse HEAD` y conservarlo con cada corrida.

## Implementado y verificado localmente

- Integrados modelo Qwen2.5-1.5B + adapter público, tres agentes, orquestador y evaluación FOM-5 v2.
- `run.py` carga solo entradas de generación, escribe un `RunResult` y una traza por caso, reanuda por ID y crea manifiestos al completar una variante.
- `Deliverable_3.ipynb` separa el caso diagnóstico, su juicio opcional, el piloto de ocho casos y la reproducción de cinco variantes × 30 casos.
- El gold diagnóstico proviene del evaluador original de Entrega 2 y coincide con su enunciado archivado; queda separado del archivo que reciben los agentes.
- Pruebas CPU: 138 del sistema y 38 de evaluación. `verify-archives` reprodujo los 60 puntajes archivados: baseline 0,5884/5 y QLoRA 0,8023667/5.

## Pendiente de medición

No hay aún piloto GPU completo, configuración congelada, resultados oficiales nuevos, puntuación nueva del caso diagnóstico, informe final ni video. El puente MCP de Colab no respondió durante la última conexión; no se interpreta como una corrida iniciada.

## Reanudación

1. Abrir `Deliverable_3.ipynb` desde GitHub en una cuenta con T4. Ejecutar la sección 1 y después `RUN_PILOT=True` en la sección 5. Guardar los dos resúmenes de desarrollo y revisar trazas y hallazgos del auditor.
2. Elegir el estado del adapter del Verificador con los ocho casos, registrar la justificación en `docs/decisiones.md`, copiar la configuración final a `config/frozen.yaml`, hacer commit y crear el tag `v3-freeze` antes de leer resultados oficiales.
3. Ejecutar `RUN_GENERATE_30=True` y después `RUN_EVALUATE_30=True` en la sección 6, usando una ruta persistente en `ARTIFACT_ROOT` si la sesión puede cortarse. Repetir el mismo comando para reanudar; no mezclar identidades.
4. Ejecutar el caso oftalmológico de la sección 2 y su juicio de la sección 4, analizar el contraste con las dos respuestas archivadas y publicar respuestas/trazas/juicios relevantes.
5. Redactar y compilar el informe de una página con métricas **medidas**, verificarlo visualmente y publicar el enlace del video grabado por el equipo.

Los resultados oficiales deben contener exactamente 30 IDs por cada una de `full`, `no_evidence`, `no_plan`, `no_audit` y `no_review`. El diagnóstico permanece fuera de esas medias.
