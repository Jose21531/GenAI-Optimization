# Contratos de intercambio · borrador para revisión del equipo

El orquestador transmite al sistema solo `id`, `title` y `problem`. Mantiene el identificador de corrida y la versión de cada prompt en la traza. Ningún mensaje de generación contiene `reference_model` ni los `requirements` oficiales del benchmark.

## Analista → Formulador: `ProblemSpec`

JSON con `case_id`, `decisions`, `data` y `requirements`. Cada requisito tiene `id` propio (`U1..Un`), `kind` (`objective`, `constraint` o `domain`), `text` y `evidence`, donde `evidence` es un fragmento literal comprobable del enunciado. El Analista puede comunicar `uncertainties` sin inventar datos. `extract_data_spans` devuelve fragmentos y unidades del enunciado, no interpreta ecuaciones.

## Formulador → Verificador: `candidate`

El Formulador comunica primero una decisión de control (`formulate` o `clarify`) y, al formular, devuelve **solo texto** con los cinco encabezados usados en la Entrega 2. El programa asigna `candidate_id` y guarda el texto sin anteponer JSON, plan ni marcas de cobertura. El plan requisito → ecuación es un mensaje interno separado. En la revisión, la entrada incluye el mismo enunciado, el `ProblemSpec`, el borrador y los problemas concretos señalados por el Verificador.

## Verificador ↔ herramienta: `CoverageMap` y `audit_model`

El Verificador lee independientemente el enunciado y asigna IDs a las ecuaciones efectivamente presentes en `candidate`. Su `CoverageMap` vincula requisitos `U` con el objetivo, los dominios o las restricciones correspondientes; puede vincular varios requisitos con una ecuación y viceversa. `audit_model` valida que:

1. Todo requisito del `ProblemSpec` tenga al menos un vínculo del tipo correcto.
2. Toda restricción identificada tenga al menos un requisito vinculado; una ausencia se marca como posible adición no justificada.
3. Todos los IDs y fragmentos de ecuación citados existan en los artefactos recibidos.

La herramienta puede añadir verificaciones sintácticas conservadoras de símbolos y contradicciones, pero no afirma equivalencia matemática. Un vínculo declarado tampoco demuestra que la ecuación sea correcta. El Verificador debe revisar esa semántica frente al enunciado y señalar requisitos que falten en el propio `ProblemSpec`.

En la ablación `no_evidence`, el campo `evidence` puede quedar vacío; los demás campos e IDs de `ProblemSpec` se mantienen para conservar la interfaz. `no_plan` elimina solo el mensaje interno de planificación; `candidate` conserva el mismo formato. `no_audit` omite la herramienta y deja la decisión al Verificador. `no_review` conserva su diagnóstico, pero impide devolver el borrador al Formulador.

## Verificador → orquestador: `ReviewDecision`

JSON con `action` (`accept`, `revise`, `stop`), `candidate_id` y `issues`, cada una con requisito, fragmento, problema y corrección solicitada. `revise` devuelve el borrador al Formulador una sola vez. Si quedan fallas al terminar el presupuesto, la traza registra `unresolved` y la última formulación se conserva para el juicio posterior, sin ocultar el fallo.
