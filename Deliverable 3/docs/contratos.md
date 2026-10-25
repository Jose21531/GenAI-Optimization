# Contratos de intercambio · Entrega 3

Las clases compartidas están en [`schemas.py`](../schemas.py). El orquestador transmite al sistema solo `id`, `title` y `problem`. Mantiene el identificador de corrida y la versión de cada prompt en la traza. Ningún mensaje de generación contiene `reference_model` ni los `requirements` oficiales del benchmark. Las acciones de control usan `deliver`/`reread`, `formulate`/`clarify` y `accept`/`revise`/`stop` en el código.

## Analista → Formulador: `ProblemSpec`

`AnalystOutput` contiene una decisión y, al entregar, un `ProblemSpec` JSON con `case_id`, `sets`, `data`, `decisions`, `objective`, `requirements` y posibles `uncertainties`. Cada requisito tiene `id` propio (`U1..Un`), `kind` (`objective`, `constraint` o `domain`), `text` y `evidence`, donde `evidence` es un fragmento literal comprobable del enunciado. El campo es opcional en el esquema para permitir `no_evidence`; la variante `full` exige evidencia mediante validación del orquestador. `extract_data_spans` devuelve fragmentos y unidades del enunciado, no interpreta ecuaciones.

## Formulador → Verificador: `candidate`

El Formulador comunica primero una decisión de control (`formulate` o `clarify`) y, al formular, devuelve **solo texto** con los cinco encabezados usados en la Entrega 2. El programa asigna `candidate_id` y guarda ese texto en `DraftModel.raw_text` sin anteponer JSON, plan ni marcas de cobertura. El plan requisito → ecuación es un mensaje interno separado, que el orquestador reúne en `FormulatorOutput.plan`. `DraftSections` y `parse_ok` son metadatos del parser. En la revisión, la entrada incluye el mismo enunciado, el `ProblemSpec`, el borrador y los problemas concretos señalados por el Verificador.

## Verificador ↔ herramienta: `CoverageMap` y `audit_model`

El Verificador lee independientemente el enunciado y asigna IDs a las partes efectivamente presentes en `candidate`. Su `CoverageMap` contiene `elements` (ID, tipo y fragmento) y `links` (requisito `U` → ID de parte); puede vincular varios requisitos con una ecuación y viceversa. El mismo `candidate_id` identifica el borrador, el mapa, el informe de auditoría y la decisión. `audit_model` valida que:

1. Todo requisito del `ProblemSpec` tenga al menos un vínculo del tipo correcto a una parte existente del borrador.
2. Toda restricción identificada tenga al menos un requisito vinculado; una ausencia se marca como posible adición no justificada.
3. Todos los IDs y fragmentos de ecuación citados existan en los artefactos recibidos.
4. Los símbolos usados estén declarados; las variables tengan dominio y aridad de índices consistente; las variables y los parámetros declarados se usen.
5. Cada dato paramétrico del `ProblemSpec` tenga representación declarada; los índices de parámetros correspondan a conjuntos declarados y los índices de ecuaciones estén ligados.
6. No haya productos entre variables ni otra no linealidad que el análisis sintáctico pueda detectar.

`AuditReport` registra los chequeos ejecutados y los hallazgos con evidencia y gravedad (`error` o `aviso`). Si el parser no puede comprobar una expresión, registra un hallazgo `no_verificado` sin gravedad; no supone aprobación. La precisión de cada chequeo se prueba con los ocho casos de desarrollo y los de falsos positivos frecuentes bajan a `aviso`. Estas reglas no afirman equivalencia matemática. La presencia de un parámetro o un vínculo declarado tampoco demuestra que esté en la ecuación correcta. El Verificador revisa esa semántica frente al enunciado y señala requisitos que falten en el propio `ProblemSpec`.

En la ablación `no_evidence`, el campo `evidence` puede quedar vacío; los demás campos e IDs de `ProblemSpec` se mantienen para conservar la interfaz. `no_plan` elimina solo el mensaje interno de planificación; `candidate` conserva el mismo formato. `no_audit` omite la herramienta y deja la decisión al Verificador. `no_review` conserva su diagnóstico, pero impide devolver el borrador al Formulador.

## Verificador → orquestador: `ReviewDecision`

JSON con `action` (`accept`, `revise`, `stop`), `candidate_id` y `issues`, cada una con requisito, fragmento, problema y corrección solicitada. `revise` exige al menos un problema y devuelve el borrador al Formulador una sola vez. Si quedan fallas al terminar el presupuesto, `RunResult.status` registra `presupuesto_agotado` y la última formulación se conserva para el juicio posterior, sin ocultar el fallo. `TraceEvent` guarda cada mensaje, llamada y observación como una línea JSONL.
