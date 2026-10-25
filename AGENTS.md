# AGENTS.md · Reglas del repositorio (Entrega 3)

Codex y Claude Code (mediante `CLAUDE.md`) leen este archivo. Define el trabajo de la Entrega 3 de GenAI-Optimization, Universidad de Concepción, curso 580694. Los archivos de gobierno y el índice raíz son la única excepción a la regla de mantener la implementación nueva dentro de `Deliverable 3/`.

## Objetivo y límites

- La tarea sigue siendo traducir un enunciado LP/MILP en español a una formulación paramétrica: conjuntos, parámetros, variables y dominios, objetivo y restricciones. No se resuelve la instancia.
- La Entrega 1 diagnosticó el prompting directo. La Entrega 2 entrenó un adapter QLoRA; en FOM-5 v2 sobre 30 problemas, las medias archivadas fueron 0,5884 (baseline) y 0,8024 (QLoRA). La Entrega 3 construye un sistema de agentes sobre esa formulación.
- Los agentes usan Qwen2.5-1.5B-Instruct y el adapter QLoRA publicado en la Entrega 2. Durante el desarrollo puede probarse el adapter encendido o apagado por rol; la configuración elegida se fija antes del benchmark y se declara. No se usa otro LLM dentro del sistema.
- Qwen3-14B con FOM-5 v2 es un evaluador externo posterior a la generación. No pertenece al sistema de agentes.
- `agents/`, `tools/` y `orchestrator.py` no abren referencias ni requisitos oficiales del benchmark. La generación recibe solo `id`, `title` y `problem`; el gold queda reservado a `eval/`.
- No se modifican el benchmark oficial, el prompt del juez, su agregación ni su calibración. No se usa RAG.

## Agentes y contratos

- **Analista:** recibe el enunciado y produce `ProblemSpec` JSON con datos, unidades, decisiones y requisitos propios `U1..Un`, cada uno apoyado en una cita literal del enunciado. Puede pedir `extract_data_spans` o entregar el análisis. Los IDs `U` evitan confundir estos requisitos inferidos con los `R` oficiales del benchmark.
- **Formulador:** recibe enunciado, `ProblemSpec` y, si corresponde, observaciones. Primero comunica una decisión de formular o pedir aclaración. Su artefacto `candidate` es **solo** la formulación en el formato textual de la Entrega 2: Conjuntos, Parámetros, Variables de decisión, Función objetivo y Restricciones. El plan requisito → ecuación es un mensaje interno separado; no se antepone a `candidate`.
- **Verificador:** recibe el enunciado, `ProblemSpec` y `candidate`. Produce un `CoverageMap` independiente y un `ReviewDecision` JSON para aceptar, devolver observaciones concretas o detener. Puede usar `audit_model` y leer el enunciado para identificar requisitos omitidos por el Analista.
- `audit_model` realiza los chequeos deterministas descritos abajo. Sus hallazgos ayudan al Verificador, pero no prueban equivalencia matemática; el Verificador inspecciona el significado de las ecuaciones frente al enunciado.
- El orquestador valida formatos, ejecuta herramientas, registra trazas y hace cumplir presupuestos. Cada agente decide su siguiente acción a partir de las observaciones. Presupuestos iniciales: una aclaración, una revisión y un reintento por fallo de formato. Al agotarse, se conserva la última salida y se registra el fallo.

## Chequeos de `audit_model`

La herramienta cruza el `ProblemSpec`, el texto `candidate` y el `CoverageMap` independiente del Verificador. Cada hallazgo lleva un fragmento o ID comprobable y una gravedad: `error` permite devolver el borrador; `aviso` pide inspección. Si la notación del borrador impide un análisis sintáctico fiable, se informa `no_verificado`: la herramienta no declara que el chequeo pasó. Los chequeos se calibran con los ocho casos de desarrollo; los que produzcan falsos positivos frecuentes quedan como `aviso`.

| Grupo | Chequeo |
|---|---|
| Símbolos | Cada símbolo usado en objetivo o restricciones está declarado como conjunto, parámetro, variable o índice. |
| Variables | Cada variable declara un dominio; su número de índices es consistente entre declaración y uso. |
| Variables | Cada variable declarada aparece en el objetivo o en alguna restricción; las auxiliares legítimas se justifican. |
| Parámetros | Cada dato paramétrico del `ProblemSpec` tiene una representación declarada; cada parámetro declarado se usa. |
| Parámetros | Los índices de cada parámetro corresponden a conjuntos declarados. |
| Índices | Cada índice libre de una restricción está ligado por un cuantificador; los índices de sumación están ligados por su suma. |
| Linealidad | Se señalan productos entre variables y otras expresiones no lineales detectables. |
| Cobertura | Cada requisito `U1..Un` tiene al menos un vínculo del tipo correcto (`objective`, `constraint` o `domain`) a una parte existente del borrador. |
| Cobertura | Cada restricción identificada tiene al menos un requisito vinculado; la ausencia se señala como posible adición injustificada. |

Estos chequeos verifican presencia y consistencia sintáctica. Que un parámetro aparezca no demuestra que esté en la ecuación correcta; tampoco se infiere de la sintaxis si un dominio elegido es semánticamente correcto. El Verificador decide esos puntos. No se comprueban valores numéricos de una instancia, porque la salida es paramétrica.

## Experimento y archivos

- Cada prompt vive en `Deliverable 3/prompts/<agente>_vN.md`. No se incrustan prompts de agente en código. Una revisión crea una nueva versión y queda registrada en `docs/decisiones.md`.
- Las variantes son `full`, `no_evidence`, `no_plan`, `no_audit` y `no_review`. Se ejecutan sobre los mismos 30 enunciados, con decodificación determinista y límites fijados. Baseline y QLoRA usan las respuestas archivadas de la Entrega 2.
- Se ajustan los prompts únicamente con ocho casos nuevos en `dev_cases/`. La configuración de desarrollo está en `config/development.yaml`; tras el piloto se copia la elegida a `config/frozen.yaml` y se crea el tag `v3-freeze`. No se afinan prompts con los resultados oficiales.
- Cada mensaje, decisión, llamada y observación de herramienta se registra en JSONL bajo `traces/`. Las salidas finales y juicios se guardan por variante en `results/`.
- La lógica reside en `.py`. El notebook de Colab solo prepara el entorno y llama a `run.py`; se publica sin salidas. No se duplican archivos pesados de la Entrega 2.

## Responsables y flujo de trabajo

| Rol | Persona | Módulos |
|---|---|---|
| A · Infraestructura | José Luis Erices | `orchestrator.py`, `schemas.py`, `model.py`, `run.py`, trazas, notebook y README |
| B · Generación | Sebastián | `agents/analista.py`, `agents/formulador.py`, sus prompts, `tools/extract_data_spans.py` y `dev_cases/` |
| C · Verificación y evaluación | Rayén | `agents/verificador.py`, su prompt, `tools/audit_model.py` y `eval/` |

Una IA que trabaja para un integrante edita solo los módulos de ese integrante. Los contratos comunes se revisan con el equipo antes de cambiar `schemas.py`. El trabajo se desarrolla en ramas de cada responsable (`feat/infra`, `feat/generacion`, `feat/verificacion`) y se integra mediante PR revisado por otra persona. Antes de cada commit se revisan el diff y los tests del módulo. Para el desarrollo local se usa `MockLLM`; las corridas reales se realizan en Colab T4.
