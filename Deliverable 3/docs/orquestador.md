# Orquestador · integración local

`orchestrator.Orchestrator` coordina los tres agentes mediante el mismo objeto
LLM; no carga otro modelo. Su entrada acepta exactamente `id`, `title` y
`problem`. Cada corrida empieza con presupuestos nuevos. No abre datasets.

```python
from orchestrator import Orchestrator, OrchestratorConfig

# run.py entregará el mapping leído de config/development.yaml.
config = OrchestratorConfig.from_mapping(config_mapping)
runner = Orchestrator(llm, config)
result = runner.run(case, variant="full")
```

`case` es el diccionario de un enunciado y `llm` implementa
`generate(prompt, adapter_on)`. Las pruebas usan `MockLLM`. Si la implementación
admite `max_new_tokens`, se aplica el límite por etapa al invocarla.
La integración de carga real en model.py/run.py y el notebook es otro hito;
el orquestador no importa esas dependencias ni inicia una corrida GPU.

## Flujo y límites

1. El Analista entrega el análisis o pide `extract_data_spans`. Si lo pide, se
   ejecuta la herramienta y se le devuelve la observación.
2. El Formulador puede pedir una aclaración. El Analista recibe la pregunta y
   su análisis anterior. Al formular, decisión/plan y candidate son llamadas
   separadas con adapter y límite propios.
3. El Verificador recibe el enunciado, análisis y candidate, sin el plan. Puede
   emitir una decisión o pedir `audit_model`. El informe vuelve al Verificador
   con el mismo mapa. Hay como máximo una auditoría por candidate.
4. `revise` devuelve los issues y el borrador al Formulador una vez; `accept`
   termina; `stop` conserva el texto y detiene la corrida.

Presupuestos iniciales: una aclaración, una revisión, un reintento de formato
global y una relectura. También se limita el total a 20 llamadas de modelo.
Si el modelo sigue pidiendo una acción sin presupuesto, no se fuerza una
aceptación: se conserva el último candidate y se registra el agotamiento.

La variante full exige evidencia literal para cada U. Un candidate incompleto
activa el reintento de formato y se conserva si no puede repararse. El feedback
del reintento cambia el prompt aun con decodificación determinista; los mensajes
de control residen en `prompts/orquestador_v1.md`, no en código Python.

`no_evidence` y `no_plan` seleccionan sus prompts explícitos; `no_audit` impide
ejecutar la herramienta incluso si el modelo la pide. `no_review` mantiene el
diagnóstico y sus issues, pero no devuelve el borrador. Un diagnóstico revise
en esta variante termina como `presupuesto_agotado`, sin ocultar el fallo.

## Trazas y resultado

Por defecto se escribe `traces/<run_id>.jsonl`, con identificador aleatorio.
Se puede pasar un `run_id` simple y `trace_path` explícitos. Los archivos se
crean en modo exclusivo: nunca se sobrescribe una traza anterior.

Las llamadas y respuestas se registran inmediatamente, antes de que otro
generate reemplace las métricas del modelo. Se incluyen prompts, versiones,
estado del adapter, etapa, límites, salidas crudas, decisiones, avisos, errores,
herramientas y observaciones. Los fallos de la segunda llamada del Formulador
no ocultan la primera. El feedback de formato registrado es el enviado al LLM.

Las métricas `tokens_in`, `tokens_out`, `latency_ms` y `reached_limit` se leen
de `last_stats`, compatible con model.py de feat/model. Si no hay métricas de
tokens (por ejemplo, MockLLM), se dejan ausentes en la traza y el total no las
inventa. El resultado suma las métricas disponibles y conserva el texto final.

Los estados son `aceptado`, `detenido`, `presupuesto_agotado` y `fallo_formato`.
Un fallo del LLM o herramienta también cierra la traza y conserva la última
formulación. Errores de entrada o una traza ya existente se rechazan antes de
invocar el modelo.

## Validación y siguientes etapas

Los tests ejecutan todos los recorridos con MockLLM, incluyen las cinco
variantes y comprueban aislamiento de archivos y conservación de métricas.
La configuración de desarrollo usa la recomendación documentada de B:
adapter del Analista y plan apagado, candidate encendido; Verificador encendido
como configuración provisional. Los límites siguen en 1200 por llamada.
El piloto debe decidir especialmente si el Analista requiere más tokens y
qué estado del adapter conviene al Verificador. No se crea frozen.yaml ni el
tag de congelamiento antes del piloto en Colab T4.
