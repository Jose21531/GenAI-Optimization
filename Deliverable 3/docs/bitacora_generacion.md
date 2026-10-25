# Bitácora · Rol B (Generación)

Registro de cambios en los módulos de Sebastián: Analista, Formulador, sus prompts, `extract_data_spans` y `dev_cases/`. La entrada más reciente va primero. Cada entrada indica qué se agregó, cambió o quitó, qué deben saber A y C, y qué falta.

Las decisiones que afectan a todo el equipo (versiones de prompt, configuración elegida tras el piloto) se registran además en [decisiones.md](decisiones.md).

## Pendientes vigentes para otros roles

Esta lista se mantiene al día. Reemplaza las notas sueltas de las entradas antiguas, que se conservan como registro.

**A · José Luis**
1. **Revisar `model.py`** en la rama `feat/model` y abrir su PR. Lo escribió B porque José Luis estaba ocupado. Ya corrió con el modelo real en la prueba temprana.
2. **Config: adapter por llamada.** Analista: apagado. Formulador: plan (`adapter_plan`) apagado y candidate (`adapter_candidate`) encendido. Con el adapter encendido, el Analista copia la plantilla y falla.
3. **Config: prompt por variante.**

   | Variante | Analista | Formulador |
   |---|---|---|
   | `full`, `no_audit`, `no_review` | `analista_v3` | `formulador_v2` |
   | `no_evidence` | `analista_v3_noevidence` | `formulador_v2` |
   | `no_plan` | `analista_v3` | `formulador_v1_noplan` |

4. **Aclaración:** cuando el Formulador devuelve `clarify`, llamar a `analizar(..., question=..., previous_spec=<el ProblemSpec anterior>)`. Sin `previous_spec` se lanza `ValueError`.
5. **Revisión:** pasar a `formular` las `Issue` del Verificador en `observations` y el texto anterior en `previous_draft`.
6. **Reintento por fallo de formato:** con decodificación determinista, el mismo prompt da la misma salida. El reintento tiene que agregar una observación sobre el error. `AgentFormatError` trae `raw` y `prompt_version` para la traza.
7. **`max_new_tokens` del Analista:** 1200 todavía no alcanza en dev01. Hay que decidir en el piloto si se sube. Descarta la propuesta de ~700 de la fase 1.
8. **Trazas:** `model.QwenLLM.last_stats` entrega `tokens_in`, `tokens_out`, `latency_ms` y `reached_limit` de cada llamada, y `AgentStep.calls` y `AgentStep.warnings` traen los prompts, las salidas crudas y los avisos.
9. **Windows (README):** PyTorch con CUDA falla si el entorno virtual está en una ruta larga (`WinError 206`). En Colab no pasa.

**C · Rayén**
1. `formulador.separar_secciones` está disponible para `audit_model`.
2. Las referencias de los dev_cases están en `dev_cases/reference/dev_reference.jsonl`, con el mismo formato del benchmark. Los agentes no las leen.
3. Un candidate incompleto llega con `parse_ok=False` y `parse_errors`; no lanza error.
4. El Formulador nunca eligió aclarar en las pruebas. La revisión del Verificador es la única corrección que funciona de verdad.

---

## 2026-10-25 · Rutas de relectura, aclaración y revisión con el modelo real; `analista_v3`

En la prueba anterior nunca se recorrieron estas rutas, así que se forzaron en la GPU local a partir de los resultados de v2.

| Ruta | v2 | v3 |
|---|---|---|
| Relectura: el Analista recibe los fragmentos (dev02, dev06, dev08) | 0/3 entregas; JSON cortado o `spec` vacío | 2/3 entregas, con más requisitos y sin distractores |
| Aclaración: el Analista responde (dev07) | Rehízo el análisis y perdió el objetivo | Conserva el objetivo; agrega solo parte de lo pedido |
| El Formulador pide aclarar ante un análisis sin decisiones (dev05) | No lo pide | No lo pide |
| Revisión: el Formulador corrige con observaciones (dev04, dev07) | Aplica las correcciones; dev04 agrega restricciones de más | (sin cambios: no depende del Analista) |

**Cambiado**
- `agents/analista.py`: `analizar(..., question=..., previous_spec=...)`. Una aclaración **exige** el análisis anterior, que se envía como JSON compacto sin `case_id` ni offsets (`compact_spec`). Antes el Analista no lo veía y rehacía el análisis desde cero. **A debe pasar `previous_spec`** cuando el Formulador pide aclarar.
- Prompts nuevos: `analista_v3.md` y `analista_v3_noevidence.md`, que ahora son los valores por defecto. v1 y v2 se conservan.
- Tests: 50 en total.

**Conclusión para el piloto:** con este modelo, la aclaración del Formulador casi no se va a activar. La revisión sí funciona, así que la calidad final depende sobre todo de lo que observe el Verificador.

---

## 2026-10-25 · Prueba temprana con el modelo real, prompts v2 y `model.py`

**Qué se probó.** Analista y Formulador con Qwen2.5-1.5B-Instruct en fp16 y el adapter de la Entrega 2, sobre los 8 dev_cases. Corrió en una RTX 3050 local de 4 GB, con las mismas versiones de transformers y peft que la Entrega 2. No hubo Verificador ni orquestador: esto **no reemplaza el piloto**. Las salidas crudas quedaron fuera del repositorio.

**Resultados**

| Medida (8 casos) | v1 | v2 |
|---|---:|---:|
| El Analista entrega un `ProblemSpec` válido | 5 | 7 |
| Salidas del Analista cortadas en 1200 tokens | 3 | 1 |
| Casos con un distractor dentro del `ProblemSpec` | 1 | 0 |
| Casos con candidate y `parse_ok=True` | 5 | 7 |

- Con el adapter encendido, el Analista no sirve: copia la plantilla de `reread` y luego falla (dev02, dev06). **Analista y plan van con el adapter apagado.**
- El candidate, generado con adapter, siempre respetó los 5 encabezados. Su calidad matemática es parecida a la de la Entrega 2: hay errores de modelación, como un producto entre variables en dev07 y restricciones lógicas mal escritas en dev04. Eso lo debe medir el juez en el piloto.

**Errores corregidos en el código**
- `extraer_json`: con una salida truncada, devolvía un objeto interno y el error salía como "falta action". Ahora informa "JSON incompleto".
- `extraer_json`: repara strings partidos en dos líneas sin coma (`"a"` `"b"`), como apareció en dev01.
- `formulador._parse_plan`: el modelo base entra en bucle y repite la misma ecuación con IDs crecientes. Ahora se descartan las repeticiones, se conservan con aviso las ecuaciones nuevas con un ID fuera del `ProblemSpec` (pueden cubrir lo que el Analista omitió) y el plan se limita al doble de los requisitos.

**Agregado**
- `prompts/analista_v2.md`, `analista_v2_noevidence.md` y `formulador_v2.md`. Los v1 se conservan. Los valores por defecto de `analizar` y `formular` ahora apuntan a v2. Los cambios y la evidencia están en `decisiones.md`.
- Tests: 49 en total, entre ellos los casos de bucle y de string partido observados en la prueba.
- `model.py` (módulo de A), adelantado porque José Luis estaba ocupado. Está en una **rama aparte, `feat/model`**, con sus tests, para que él lo revise en su propio PR. Reproduce las celdas 8 y 12 de la Entrega 2, verifica el SHA-256 del adapter y registra tokens y latencia de cada llamada.

**Para A**
- En Windows, PyTorch con CUDA falla si el entorno virtual está en una ruta larga (`WinError 206`). En Colab no ocurre.
- Hay que decidir si el Analista necesita un `max_new_tokens` mayor que 1200 (dev01).
- Con decodificación determinista, reintentar con el mismo prompt da la misma salida. El reintento por fallo de formato tiene que agregar al prompt una observación sobre el error.

**Siguiente:** revisión de `model.py` por José Luis, orquestador y piloto completo cuando estén el Verificador y `audit_model`.

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
