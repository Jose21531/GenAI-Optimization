# Estado de continuidad · Entrega 3

Este archivo distingue trabajo terminado de resultados pendientes. La rama de integración es `feat/entrega3-integracion`; para el SHA exacto del código ejecutado, usar `git rev-parse HEAD` y conservarlo con cada corrida.

## Implementado y verificado localmente

- Integrados modelo Qwen2.5-1.5B + adapter público, tres agentes, orquestador y evaluación FOM-5 v2.
- `run.py` carga solo entradas de generación, escribe un `RunResult` y una traza por caso, reanuda por ID y crea manifiestos al completar una variante.
- `Deliverable_3.ipynb` separa el caso diagnóstico, su juicio opcional, el piloto de ocho casos y la reproducción de cinco variantes × 30 casos.
- El gold diagnóstico proviene del evaluador original de Entrega 2 y coincide con su enunciado archivado; queda separado del archivo que reciben los agentes.
- Pruebas CPU: 151 del sistema y 38 de evaluación. `verify-archives` reprodujo los 60 puntajes archivados: baseline 0,5884/5 y QLoRA 0,8023667/5.

## Pendiente de medición

No hay aún piloto GPU completo, configuración congelada, resultados oficiales nuevos, puntuación nueva del caso diagnóstico, informe final ni video. Los ensayos anteriores están separados por SHA y no forman una sola muestra. El piloto actual comenzó en T4 con el SHA `0e2822d`, `analista_v6`, `formulador_v3`, `verificador_v10` y el adapter del Verificador apagado. Su directorio es `/content/d3_artifacts/pilot_0e2822d/verifier_off`; el proceso en Colab comenzó con PID 65025. La corrección de este SHA descarta requisitos del Analista repetidos literalmente y los renumera antes de la verificación. Al continuar, revisar `runner.log` y `results/full/outputs.jsonl` antes de iniciar otro proceso.

## Reanudación

El piloto usa los ocho casos de desarrollo. Esta cuenta de Colab no tiene `GITHUB_TOKEN`; los artefactos de la sesión deben copiarse al repositorio antes de que termine la T4. `run.py --git-sync` sirve como alternativa cuando se dispone de ese secreto. Cada directorio de corrida tiene una identidad de código y configuración, y `run.py` reanuda por ID sin repetir los completos.

1. Piloto: terminar `verifier_off` bajo `0e2822d`; luego correr `verifier_on` con el mismo SHA y solo el cambio de `model.adapter_enabled.verificador`. Revisar los ocho estados, errores matemáticos y hallazgos de `audit_model`; transferir resultados y trazas al repositorio.
2. Elegir el estado del adapter del Verificador y las versiones de prompt con los ocho casos de desarrollo, registrar la justificación en `docs/decisiones.md`, copiar la configuración a `config/frozen.yaml` con `status: frozen`, hacer commit, crear y publicar el tag `v3-freeze` antes de leer resultados oficiales.
3. Generación oficial: ejecutar `run.py --mode official --variants full no_evidence no_plan no_audit no_review` desde `v3-freeze`, con checkpoints por ID. Si se usan varias T4, cada variante mantiene el mismo SHA y directorio propio.
4. La celda de estado (sección 6) debe mostrar 30/30 y manifiesto en las cinco variantes; después una sola sesión ejecuta `RUN_EVALUATE_30=True`. El juez es secuencial y reanudable desde `results/evaluation-official`.
5. Ejecutar el caso oftalmológico de la sección 2 y su juicio de la sección 4, analizar el contraste con las dos respuestas archivadas y publicar respuestas/trazas/juicios relevantes.
6. Redactar y compilar el informe de una página con métricas **medidas**, verificarlo visualmente y publicar el enlace del video grabado por el equipo.

Los resultados oficiales deben contener exactamente 30 IDs por cada una de `full`, `no_evidence`, `no_plan`, `no_audit` y `no_review`. El diagnóstico permanece fuera de esas medias.
