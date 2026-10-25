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
| Registrada (B) | Versiones iniciales de prompt: `analista_v1`, `analista_v1_noevidence`, `formulador_v1` y `formulador_v1_noplan`. Las ablaciones cambian solo el archivo de prompt, no el código. Evidencia actual: tests con MockLLM; falta el piloto en los ocho casos de desarrollo. |
| Registrada (B) | Los ocho casos de `dev_cases/` se escribieron desde cero. La mayor superposición de trigramas de palabras con un enunciado oficial es 1,6 %. Las referencias están en `dev_cases/reference/` y los agentes, herramientas y prompts no las leen (lo comprueba un test). |
| Registrada (B), declarar en el informe | `dev02` (laboratorio de suelos) comparte con `opt_02` la idea de una capacidad ampliable con horas extra, para probar la falla de plantilla observada en la Entrega 2. Cambia el contexto, todos los datos y el sentido del objetivo (minimizar costos), y agrega encargos externos con mínimos comprometidos. Superposición de trigramas con `opt_02`: 0,5 %. |
| Registrada (B) | `dev01` y `dev08` incluyen números distractores (distancia, años, dotación) y `dev03` describe una escala de puntaje. Sirven para comprobar que el Analista trata la salida de `extract_data_spans` como candidatos y no lleva esos números al `ProblemSpec`. |

Toda versión nueva de prompt debe registrar aquí su cambio, motivo y evidencia de desarrollo. No se sobrescriben versiones anteriores.
