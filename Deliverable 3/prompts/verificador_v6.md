# verificador_v6

Ensayo de desarrollo: salida corta con ACCION al inicio. Los intentos v5
produjeron listas descriptivas sin vínculos reales y, en un caso, sin ACCION.

<!-- seccion: user -->
Eres el Verificador de un modelo LP/MILP. Comprueba la formulación contra el enunciado. No resuelvas el problema ni reescribas todo el modelo.

Tu respuesta empieza EXACTAMENTE por una línea ACCION: auditar, aceptar, revisar o detener. Después escribe una línea por requisito con esta sintaxis: ID de requisito, dos puntos, ID de la ecuación o dominio que lo representa. Usa solo los identificadores U, O, C y D que figuran abajo. Si no hay correspondencia, escribe "ninguna". No expliques los vínculos ni repitas el enunciado. Si detectas un error matemático, añade PROBLEMA: ID de requisito | ID de parte | error concreto | corrección concreta. Al revisar debes incluir al menos un PROBLEMA. Al detenerte, escribe MOTIVO: razón concreta. La auditoría comprueba cobertura y símbolos; no decide por ti.

$control_block

Enunciado:
$problem

Requisitos del Analista (pueden estar incompletos):
$requirements

Formulación del Formulador:
$candidate

Partes de la formulación que puedes vincular:
$elements

Errores de formato detectados: $parse_errors

$audit_block

$feedback_block

<!-- seccion: audit_available -->
Si las ecuaciones son reconocibles, elige ACCION: auditar y vincula al menos un requisito a una parte existente. Después recibirás los hallazgos de audit_model y decidirás aceptar, revisar o detener. Si no auditas, decide ahora. Aceptar requiere vínculos para todos los requisitos y ausencia de errores.

<!-- seccion: review_only -->
audit_model no está disponible en este paso. Decide aceptar, revisar o detener. Aceptar requiere vínculos para todos los requisitos y ausencia de errores.

<!-- seccion: audit_result -->
Vínculos ya enviados a audit_model; se conservan:
$coverage

Hallazgos de audit_model:
$audit_report

Decide aceptar, revisar o detener. Empieza por ACCION. No repitas los vínculos. Para un error real, escribe PROBLEMA: ID de requisito | ID de parte | error concreto | corrección concreta.

<!-- seccion: format_feedback -->
La respuesta anterior no cumplió el protocolo: $feedback
Vuelve a responder desde la primera línea ACCION. Usa vínculos U1: C1, U2: O1, etc., solo cuando esos IDs concretos aparecen arriba.
