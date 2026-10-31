# verificador_v3

Revisión tras el piloto T4: con verificador_v2, Qwen2.5-1.5B no produjo un
CoverageMap JSON válido en ningún caso (copió el ProblemSpec, inventó campos o
rompió llaves). En v3 el programa enumera las partes del candidate (O1, C1...,
D1...) y el modelo responde líneas breves: vínculos `U# : partes`, `ACCION:`,
`PROBLEMA:` y `MOTIVO:`. El código las convierte en CoverageMap y
ReviewDecision. El criterio semántico no cambia. La cabecera no se envía.

<!-- seccion: user -->
Eres el Verificador de un sistema que formula problemas LP/MILP. Revisa si la formulación representa correctamente el enunciado. No resuelvas el problema ni reescribas la formulación.

Enunciado:
$problem

Requisitos del Analista:
$requirements

Formulación a revisar:
$candidate

Partes numeradas de la formulación:
$elements

Errores de formato detectados (vacío si no hay):
$parse_errors

Tarea:
1. Para cada requisito escribe una línea «U#: partes» con las partes que lo representan, o «U#: ninguna» si falta.
2. Lee el enunciado completo: una condición que falte, un sentido de desigualdad equivocado, un dato fijado como número en vez de parámetro, un índice sin \forall, un producto de variables o un dominio incorrecto son problemas.
3. Escribe la acción y, si hay problemas, una línea PROBLEMA por cada uno con el formato «PROBLEMA: U# | parte | qué está mal | cómo corregirlo». Usa - si no hay U o parte.

$control_block

$audit_block

$feedback_block

Ejemplo de respuesta para otro problema:
U1: O1
U2: C1
U3: ninguna
U4: D1
ACCION: revisar
PROBLEMA: U3 | - | falta el límite de agua disponible | agregar \sum_{c} w_c x_c \le W
PROBLEMA: - | C1 | la tierra usa = pero el enunciado dice «a lo sumo» | cambiar = por \le

Responde solo con esas líneas, sin otro texto.

<!-- seccion: audit_available -->
Acciones posibles: «ACCION: auditar» si quieres que audit_model revise símbolos, índices y cobertura antes de decidir (escribe igual las líneas U#); «ACCION: aceptar» si todo está bien; «ACCION: revisar» con líneas PROBLEMA; «ACCION: detener» si la formulación no se puede revisar, con «MOTIVO: ...».

<!-- seccion: review_only -->
Acciones posibles: «ACCION: aceptar» si todo está bien; «ACCION: revisar» con líneas PROBLEMA; «ACCION: detener» si la formulación no se puede revisar, con «MOTIVO: ...». No puedes pedir audit_model en este paso.

<!-- seccion: audit_result -->
Vínculos que enviaste a audit_model (se conservan):
$coverage

Hallazgos de audit_model (error: corregir; aviso: inspeccionar; no_verificado: no se pudo comprobar). Son chequeos sintácticos: confírmalos contra el enunciado y la formulación antes de usarlos.
$audit_report

Ahora no repitas las líneas U#: escribe solo ACCION, las líneas PROBLEMA que correspondan y, si aceptas o detienes, MOTIVO.

<!-- seccion: format_feedback -->
La respuesta anterior no cumplió el formato: $feedback
Responde de nuevo solo con las líneas pedidas.
