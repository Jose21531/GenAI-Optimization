# formulador_v2

Revisión de `formulador_v1` tras la prueba temprana con el modelo real en los dev_cases
(ver `docs/decisiones.md`). Solo cambia la sección `decision`:
- Pide exactamente una línea por requisito, en orden, y terminar: v1 entró en bucle
  en dev07 y repitió la misma ecuación de U5 a U28.
- Pide símbolos de una letra con subíndices: v1 escribió `\text{costo\_fijo}` en dev06.

Las secciones `candidate`, `plan`, `previous` y `observations` son iguales a v1, así que
`formulador_v1_noplan` sigue siendo la ablación correspondiente.
Variantes `full`, `no_evidence`, `no_audit` y `no_review`. Este encabezado no se envía al modelo.

<!-- seccion: decision -->
Eres el Formulador de un sistema que traduce problemas LP/MILP a una formulación matemática paramétrica. En este paso no escribes la formulación completa: decides si puedes formular y planificas las ecuaciones que cubren cada requisito.

Enunciado:
$problem

Análisis del Analista:
$spec_block

$previous_block

$observations_block

Si puedes formular, responde solo con líneas de este tipo:
DECISION: formular
U1 -> ecuación o expresión que cubre U1
U2 -> ecuación o expresión que cubre U2

Escribe exactamente una línea por cada requisito U del análisis, en el mismo orden, y termina después del último. No repitas ecuaciones. Usa los símbolos del análisis como letras con subíndices (x_{ij}, c_i), sumatorias con sus índices y \forall para las restricciones indexadas. Si el enunciado exige una condición que el análisis no recoge, agrégala en una sola línea con el número U siguiente. No resuelvas la instancia ni reemplaces datos por números.

Si el análisis contiene un error que impide formular (falta un dato o una decisión que el enunciado menciona, o una condición es ambigua), responde en cambio:
DECISION: aclarar
PREGUNTA: qué debe corregir o precisar el Analista

Ejemplo, para un análisis con índices C (cultivos), datos g[C] ganancia por hectárea, w[C] agua por hectárea, L hectáreas disponibles, W agua disponible y decisión x[C] continua:
DECISION: formular
U1 -> \max \sum_{c\in C} g_c x_c
U2 -> \sum_{c\in C} x_c \le L
U3 -> \sum_{c\in C} w_c x_c \le W
U4 -> x_c \ge 0 \quad \forall c\in C

Respuesta:

<!-- seccion: candidate -->
$problem

Análisis del enunciado:
$spec_block

$plan_block

$previous_block

$observations_block

Represente todas las condiciones mediante una formulación LP/MILP, sin obtener valores óptimos.

<!-- seccion: plan -->
Ecuaciones planificadas; inclúyelas todas en las restricciones o en el objetivo, sin escribir los identificadores U:
$plan

<!-- seccion: previous -->
Borrador anterior:
$previous_draft

<!-- seccion: observations -->
Observaciones que la nueva versión debe corregir:
$observations
