# Verificador · implementación inicial del rol C

`agents/verificador.py` hace una llamada por invocación al mismo protocolo
`LLM.generate(prompt, adapter_on)` usado por B. Devuelve `AgentStep`, con la
llamada para la traza y un `VerifierOutput` local. No cambia `schemas.py`.
El prompt actual es `prompts/verificador_v2.md`; se conserva v1. Todavía no se
ha probado con el modelo real.

## Interfaz para infraestructura

```python
from agents.verificador import verificar

step = verificar(llm, problem, spec, draft, adapter_on=adapter_verificador)
output = step.output
if output.action == "audit":
    # El orquestador comprueba el presupuesto, registra la llamada/observación
    # de herramienta y ejecuta audit_model(spec, draft, output.coverage).
    report = ejecutar_auditoria(spec, draft, output.coverage)
    step = verificar(
        llm, problem, spec, draft,
        adapter_on=adapter_verificador,
        coverage=output.coverage, audit_report=report,
    )
    output = step.output
decision = output.decision
```

`ejecutar_auditoria` representa el punto de integración del orquestador;
`tools/audit_model.py` ya implementa la auditoría determinista y se puede pasar
como función al orquestador. El agente no importa esa herramienta ni inventa
un informe vacío para simularla. Para no_audit, llamar con `audit_allowed=False`.

El contenedor local tiene `action` (`audit` o `review`), `coverage`, `decision`
opcional y `reason` para justificar la solicitud de herramienta. Los artefactos
contenidos siguen siendo `CoverageMap` y `ReviewDecision` de `schemas.py`.
En la continuación, el modelo entrega solo la decisión y el programa conserva
el mapa enviado a la herramienta. Se rechazan mapas sustituidos, IDs de otro
borrador y solicitudes de una segunda auditoría.

El mapa puede describir cobertura incompleta: el agente y la herramienta deben
mostrar las omisiones, sin fabricar ecuaciones o vínculos para llenar huecos.
Eso vale para `revise` y `stop`. Un `accept` se rechaza como `AgentFormatError`
si trae issues, si el mapa no tiene elementos o vínculos, o si algún requisito
del `ProblemSpec` no está vinculado a un elemento existente del mapa. En la
continuación tras auditar se aplica la misma regla al mapa conservado.
La validación de tipos e identificadores del intercambio no sustituye los
chequeos de referencias, cobertura y sintaxis de `audit_model`, ni la revisión
semántica del LLM. El Verificador recibe el enunciado, el análisis y el texto
del borrador; nunca recibe el plan del Formulador.

## Variantes, errores y trazas

- `no_audit`: pasar `audit_allowed=False`, sin mapa ni informe de herramienta.
- `no_review`: conservar `decision`, incluidos sus issues; el orquestador impide
  la devolución al Formulador. El diagnóstico del Verificador no cambia.
- `no_evidence`: se admiten los campos de evidencia opcionales del análisis.
- `no_plan`: no requiere cambios; la interfaz no recibe el plan.
- `AgentFormatError` conserva `raw`, `prompt_version`, `calls` y `warnings`.
  El orquestador decide si queda un reintento y pasa el motivo mediante
  `format_feedback`. No hay reintentos automáticos en el agente.
- Un mapa o informe recibido para otro borrador es `ValueError` antes de llamar
  al LLM; es un error de integración, no un fallo del formato generado.

Cada `AgentStep` conserva el prompt, salida cruda, versión y estado del adapter.
Las trazas JSONL, métricas por llamada, ejecución de herramientas y presupuestos
permanecen a cargo de infraestructura. El estado del adapter y los límites de
tokens del Verificador se deben probar en el piloto de Colab T4 antes de fijarlos.

## Validación y pendientes

Las pruebas con `MockLLM` verifican decisiones, intercambio de mapas e informes,
aislamiento de archivos, conservación de llamadas y errores de formato. No miden
si Qwen identifica errores matemáticos: eso requiere el piloto sobre los ocho
casos de desarrollo. Los agentes solo leen archivos de prompts.

Validación local inicial: 75 tests pasan en Python 3.14, incluidos los 53 previos
y 22 del Verificador. Con las dependencias de `requirements.txt` instaladas,
ejecutar desde la raíz: `python -m unittest discover -s "Deliverable 3/tests"`.

La calibración determinista del auditor se documenta en `docs/audit_model.md`.
Sigue pendiente validar el prompt y los chequeos sobre candidatos de
Qwen2.5-1.5B en Colab T4 y elegir la configuración. Después se congela
la configuración antes de ejecutar el experimento oficial.
