# Bitácora · Rol B (Generación)

Registro de cambios en los módulos de Sebastián: Analista, Formulador, sus prompts, `extract_data_spans` y `dev_cases/`. La entrada más reciente va primero. Cada entrada indica qué se agregó, cambió o quitó, qué deben saber A y C, y qué falta.

Las decisiones que afectan a todo el equipo (versiones de prompt, configuración elegida tras el piloto) se registran además en [decisiones.md](decisiones.md).

---

## 2026-10-25 · Fase 2: Formulador y casos de desarrollo

**Agregado**
- `agents/formulador.py`: `formular(llm, problem, spec, *, candidate_id, adapter_plan, adapter_candidate, prompt_path, observations, previous_draft) -> AgentStep`. Hace dos llamadas al LLM, cada una con su propio adapter:
  1. **decision**: responde `DECISION: formular` seguido de líneas `Uk -> ecuación`, o `DECISION: aclarar` con `PREGUNTA: ...`. Si aclara, no hay segunda llamada y devuelve `FormulatorOutput(action="clarify")`.
  2. **candidate**: la formulación con los cinco encabezados de la Entrega 2. El prompt empieza con el enunciado literal y termina con la frase de cierre de los enunciados de entrenamiento, para acercarse a lo que vio el adapter.
- Funciones reutilizables:
  - `separar_secciones(texto)`: llena `DraftSections` y lista los errores (encabezado faltante, repetido, fuera de orden o vacío). Tolera acentos omitidos y marcas de Markdown. **C puede reutilizarla en `audit_model`.**
  - `limpiar_candidate`: recorta lo anterior a `Conjuntos:` y las vallas de código.
  - `formatear_spec`: resumen del `ProblemSpec` en texto.
- `prompts/formulador_v1.md` (secciones `decision`, `candidate`, `plan`, `previous`, `observations`) y `prompts/formulador_v1_noplan.md`, que no tiene sección `plan` y cuya `decision` pide solo la decisión. El código es el mismo para ambas variantes.
- `dev_cases/inputs.jsonl` (8 casos: `id`, `title`, `problem`), `dev_cases/reference/dev_reference.jsonl` (referencia, requisitos `R1..Rn`, distractores y notas) y `dev_cases/README.md`.
  - Distractores: `dev01` y `dev08` incluyen números que no entran al modelo, y `dev03` describe una escala de puntaje.
  - `dev02` (horas extra) es claramente distinto de `opt_02`; está declarado en `decisiones.md`.
- `tests/test_formulador.py` (15 tests) y `tests/test_dev_cases.py` (5 tests). En total, la suite tiene 47 tests y todos pasan.
- `docs/decisiones.md`: cuatro filas nuevas, con las versiones iniciales de los prompts, el origen de los dev cases, la relación entre `dev02` y `opt_02` (para declararla en el informe) y los distractores.

**Cambiado**
- `agents/analista.py`: nueva función `render`, compartida con el Formulador, que rellena la plantilla y colapsa las líneas en blanco que dejan los bloques vacíos.
- `prompts/analista_v1.md` y `analista_v1_noevidence.md`: se agregaron solo líneas en blanco alrededor de los bloques, sin cambiar el texto. Se mantiene la versión v1, porque todavía no se ha usado en ninguna corrida.

**Comportamiento que deben conocer A y C**
- `FormulatorOutput.plan` guarda solo líneas con IDs que existen en el `ProblemSpec`. Las demás se descartan con aviso, y los requisitos sin línea de plan también quedan como aviso.
- Un candidate incompleto **no lanza error**: se entrega con `parse_ok=False` y `parse_errors`, y el orquestador decide si reintenta. Solo un candidate vacío o una decisión ilegible lanzan `AgentFormatError`.
- Si quedan líneas `Uk ->` dentro del candidate, se registra un `parse_error`; no se borran en silencio.
- `observations` acepta `Issue` del Verificador o texto libre del orquestador. Cuando no hay aclaraciones disponibles, el orquestador debe pedir que se formule mediante una observación.
- Con `no_plan`, la variante cambia solo el archivo de prompt. Si el modelo escribe líneas de plan sin que se le pidan, quedan registradas en `plan`, pero no llegan al candidate.

**Pendiente de coordinar**
- A: `config` necesita un adapter por llamada del Formulador (`adapter_plan`, `adapter_candidate`) y la asignación de cada variante a su archivo de prompt.
- Piloto en Colab con los 8 dev cases:
  - Analista con adapter apagado o encendido.
  - Plan con adapter apagado.
  - Candidate con o sin el bloque del análisis. El adapter se entrenó viendo solo enunciados, y si rinde mejor sin el bloque, eso sería un `formulador_v2`.

**Siguiente:** integración con el orquestador de A y piloto en Colab.

---

## 2026-10-25 · Fase 1: Analista y `extract_data_spans`

**Agregado**
- `agents/analista.py`: `analizar(llm, case_id, problem, *, adapter_on, prompt_path, spans, question) -> AgentStep`. Hace una sola llamada al LLM por invocación y devuelve un `AnalystOutput` (`deliver` con `ProblemSpec` o `reread` con motivo).
- Piezas compartidas, definidas en el mismo archivo para que el Formulador las reutilice:
  - `LLM`: protocolo `generate(prompt, adapter_on) -> str`, donde `prompt` es el mensaje user.
  - `LLMCall` y `AgentStep`: la salida validada, las llamadas hechas (versión del prompt, prompt, adapter, texto crudo) y los avisos.
  - `AgentFormatError`: incluye `raw` y `prompt_version`. Los reintentos los cuenta el orquestador.
  - `load_prompt`: lee `prompts/*.md` dividido en secciones `<!-- seccion: nombre -->`, que se usan como plantillas de `string.Template` (`$variable`).
- `tools/extract_data_spans.py`:
  - `extract_data_spans(problem) -> list[Span]` reconoce números en notación española (`1,3`, `1.200`, `30 mil`, `15%`, `$ 10`, `dos`) y la unidad que les sigue. Ignora identificadores como `P1` o `m3`.
  - `localizar_cita(problem, quote)` ubica una cita literal; tolera diferencias de espacios, mayúsculas y comillas.
- `prompts/analista_v1.md` (variantes `full`, `no_plan`, `no_audit`, `no_review`) y `prompts/analista_v1_noevidence.md` (ablación `no_evidence`). Los dos dicen explícitamente que los fragmentos de la herramienta son **candidatos**: un número que no afecta decisiones, objetivo ni restricciones no entra al `ProblemSpec`. El ejemplo del prompt incluye un año distractor para ilustrarlo.
- `tests/mock_llm.py` (LLM guionizado, sin GPU) y `tests/test_analista.py` (22 tests).

**Comportamiento que deben conocer A y C**
- **Releer o entregar:** decide el modelo con el campo `"action"`. Si responde `reread` después de haber recibido los fragmentos, se lanza `AgentFormatError`. Así hay como máximo una relectura.
- **JSON:** se toma el primer objeto balanceado y se reparan errores menores (vallas, comas finales, comillas tipográficas, barras de LaTeX). Si no se puede reparar, `AgentFormatError`.
- **Normalizaciones**, cada una registrada en `AgentStep.warnings`:
  - `case_id` siempre se sobrescribe con el del orquestador.
  - Las claves desconocidas se eliminan (por ejemplo `reference_model`).
  - Los IDs `R1` o `2` pasan a `U1` o `U2`.
  - Los valores escritos en español (`entregar`, `objetivo`, `maximizar`) se traducen a los del contrato.
- **Evidencia:** el modelo solo escribe la cita y el código calcula `start/end`. Una cita que no aparece en el enunciado queda sin offsets y con aviso. Rechazarla en `full` le corresponde al orquestador (ver `contratos.md`).
- **Aislamiento:** un test revisa que `agents/`, `tools/` y `prompts/` no mencionen el gold de la Entrega 2, `benchmark_30`, `reference_model` ni `dev_cases/reference`. Otro test comprueba que `analizar` solo abre archivos de `prompts/`.

**Pendiente de coordinar con A**
- `model.py` debe aplicar la plantilla de chat con **un único mensaje user**, como en la Entrega 2 (sin system propio; Qwen agrega el suyo por defecto), y decodificar con `do_sample=False`.
- Definir `max_new_tokens` por llamada (propuesta: Analista ~700, candidate 1200).
- Piloto: probar el Analista con el adapter **apagado**. Con el adapter encendido, el modelo tiende a responder en el formato "Conjuntos:…" en lugar de JSON, y esa salida termina en `AgentFormatError`.

**Siguiente (fase 2):** Formulador (dos llamadas: decisión + plan, y candidate), `formulador_v1.md` y `formulador_v1_noplan.md`, los 8 `dev_cases/` (uno de horas extra claramente distinto de `opt_02` y al menos uno con número distractor), una nota en `decisiones.md` y los tests del Formulador.
