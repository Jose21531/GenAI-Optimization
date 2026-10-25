# Registro de decisiones · Entrega 3

| Estado | Decisión |
|---|---|
| Acordada | La respuesta evaluable del Formulador conserva el formato textual de `candidate` de la Entrega 2. Los mensajes de decisión, plan y cobertura son artefactos separados. |
| Acordada | Los agentes no leen gold ni requisitos oficiales durante la generación; el juez FOM-5 v2 es externo y posterior. |
| Acordada | Sin RAG. `audit_model` realiza comprobaciones estructurales por tipo de requisito y no sustituye al juicio matemático. |
| Acordada | Los prompts y la configuración se prueban solo en ocho casos nuevos y se congelan antes de evaluar los 30 casos oficiales. |
| Acordada | José Luis Erices asume A (infraestructura), Sebastián asume B (generación) y Rayén asume C (verificación/evaluación). |
| Acordada | `audit_model` comprueba símbolos, dominios, índices, uso de variables y parámetros, linealidad detectable y cobertura estructural. La notación no analizable se informa como `no_verificado`; la semántica queda a cargo del Verificador. Se conservan los IDs `U` y el `candidate` textual sin anteponer el plan. |
| Acordada | `schemas.py` fija los mensajes entre roles con Pydantic v2. Usa acciones en inglés para coincidir con los contratos documentados, IDs internos `U`, `CoverageMap` independiente y `candidate_id` común. El texto `candidate` permanece en `DraftModel.raw_text`; el plan se registra aparte. |
| Pendiente del piloto | Estado del adapter por agente y necesidad de decodificación restringida para los mensajes JSON breves. Se documentarán la prueba y la configuración elegida. |

Toda versión nueva de prompt debe registrar aquí su cambio, motivo y evidencia de desarrollo. No se sobrescriben versiones anteriores.
