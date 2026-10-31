# formulador_v3_noplan

Ablación de `formulador_v3`: la decisión no produce plan y la primera llamada
QLoRA de candidate recibe exactamente el enunciado, como en la Entrega 2.
En una revisión recibe además el borrador anterior y observaciones.

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
$previous_block

$observations_block

$problem

<!-- seccion: previous -->
Borrador anterior:
$previous_draft

<!-- seccion: observations -->
Observaciones que la nueva versión debe corregir:
$observations
