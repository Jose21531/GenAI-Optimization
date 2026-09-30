# Guion de evidencia, máximo 3:00

Este es un guion para la grabación real después de completar las ejecuciones. No reemplaza el video ni contiene resultados inventados.

En el Colab de trabajo quedó al final una celda titulada en el primer comentario **DEMOSTRACIÓN PARA GRABAR**. Una vez completado el juez, **inicia la captura de pantalla antes de pulsar ▶**. La celda ejecuta exactamente `scripts/demo_same_input.py` del repositorio: carga Qwen2.5 y el adapter desde Drive, deshabilita temporalmente el adapter para generar el baseline y luego lo habilita para QLoRA sobre el mismo caso; guarda ambas inferencias nuevas en `live_demo.json`. El script se niega a correr si el juez aún ocupa la GPU. No edites el video para ocultar esperas. Solo se miran los primeros 3:00.

| Tiempo | Pantalla y explicación |
|---|---|
| 0:00-0:20 | Mostrar título y entrada del caso oftalmológico. Explicar: convertir español en formulación paramétrica LP/MILP, sin resolver. |
| 0:20-0:40 | Mostrar la salida histórica: ausencia de apertura, pesos de población y sumas contradictorias. Identificar Qwen2.5-1.5B como el candidato más pequeño del grupo. |
| 0:40-1:10 | Mostrar pipeline y pulsar ▶ en la celda **DEMOSTRACIÓN PARA GRABAR**. Dos inferencias sobre la misma entrada, primero base y luego adapter; mantener el contador y la ejecución visibles. |
| 1:10-1:45 | Mostrar las dos salidas recién obtenidas con sus tiempos. Explicar los cambios que realmente aparezcan en índices, objetivo y restricciones. Si la inferencia tarda más, reducir la introducción para reservar tiempo. |
| 1:45-2:15 | Tabla real de 30 casos, mismo FOM-5 v2 y juez; indicar media base 0.5884, media final y diferencia medidas. Separar caso histórico y agregado extendido 31. Mostrar el nombre del CSV y su provenance. |
| 2:15-2:45 | Mostrar una falla real del adapter identificada en el CSV, su salida intacta y la ecuación omitida/incorrecta. Explicar por qué rompe el modelo. |
| 2:45-3:00 | Mostrar GPU efectiva, enlace del repositorio y comandos/notebooks de reproducción. |

Antes de grabar, medir duración de la demostración en la GPU disponible. El video debe permitir rastrear sus outputs al repositorio. No mostrar el gold como si fuera generado ni sustituir la falla post-ajuste por una falla histórica. Publicar el video con acceso abierto solo cuando el usuario decida el destino.
