# formulador_v1_noplan

Prompt del Formulador para la ablación `no_plan`. Es `formulador_v1` sin el plan
interno: la sección `decision` pide solo la decisión y no existe la sección
`plan`, así que la llamada `candidate` no recibe ecuaciones planificadas. El
candidate conserva el mismo formato. Este encabezado no se envía al modelo.

<!-- seccion: decision -->
Eres el Formulador de un sistema que traduce problemas LP/MILP a una formulación matemática paramétrica. En este paso no escribes la formulación: solo decides si el análisis permite formular.

Enunciado:
$problem

Análisis del Analista:
$spec_block

$previous_block

$observations_block

Si puedes formular, responde solo con esta línea:
DECISION: formular

Si el análisis contiene un error que impide formular (falta un dato o una decisión que el enunciado menciona, o una condición es ambigua), responde en cambio:
DECISION: aclarar
PREGUNTA: qué debe corregir o precisar el Analista

Respuesta:

<!-- seccion: candidate -->
$problem

Análisis del enunciado:
$spec_block

$previous_block

$observations_block

Represente todas las condiciones mediante una formulación LP/MILP, sin obtener valores óptimos.

<!-- seccion: previous -->
Borrador anterior:
$previous_draft

<!-- seccion: observations -->
Observaciones que la nueva versión debe corregir:
$observations
