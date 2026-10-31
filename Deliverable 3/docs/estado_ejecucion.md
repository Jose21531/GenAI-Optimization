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

El piloto usa `analista_v5` (ver `docs/decisiones.md`). El trabajo GPU se reparte entre sesiones de Colab; el repositorio es el checkpoint común. Con `SYNC=True`, `run.py --git-sync` sube cada caso terminado a la rama de resultados (`resultados-piloto` o `resultados-oficiales`) y los juicios se suben cada 5 minutos. Cada cuenta necesita el secreto de Colab `GITHUB_TOKEN` con permiso de escritura en el repositorio. Si una sesión se corta, otra cuenta ejecuta la sección 1 con la misma `STAGE` y la misma celda; continúa por ID.

1. Piloto: `STAGE='piloto'`, `RUN_PILOT=True`; `PILOT_RUNS=['verifier_on']` y `['verifier_off']` pueden ir en dos sesiones. Resultados en `results/pilot/<rótulo>` de `resultados-piloto`; revisar resúmenes, estados (`fallo_formato`) y hallazgos del auditor.
2. Elegir el estado del adapter del Verificador (y v5 o v4 del Analista), registrar la justificación en `docs/decisiones.md`, copiar la configuración a `config/frozen.yaml` con `status: frozen`, hacer commit, crear y publicar el tag `v3-freeze` antes de leer resultados oficiales.
3. Generación oficial: `STAGE='oficial'`, `RUN_GENERATE_30=True`. José ejecuta `MY_VARIANTS=['full','no_evidence','no_plan']` y la compañera `['no_audit','no_review']`. Todas las sesiones deben mostrar el mismo SHA de `v3-freeze`.
4. La celda de estado (sección 6) debe mostrar 30/30 y manifiesto en las cinco variantes; después una sola sesión ejecuta `RUN_EVALUATE_30=True`. El juez es secuencial y reanudable desde `results/evaluation-official`.
5. Ejecutar el caso oftalmológico de la sección 2 y su juicio de la sección 4, analizar el contraste con las dos respuestas archivadas y publicar respuestas/trazas/juicios relevantes.
6. Redactar y compilar el informe de una página con métricas **medidas**, verificarlo visualmente y publicar el enlace del video grabado por el equipo.

Los resultados oficiales deben contener exactamente 30 IDs por cada una de `full`, `no_evidence`, `no_plan`, `no_audit` y `no_review`. El diagnóstico permanece fuera de esas medias.
