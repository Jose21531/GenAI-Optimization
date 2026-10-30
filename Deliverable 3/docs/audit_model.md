# Auditoría determinista · rol C

`audit_model(spec, draft, coverage)` recibe los tres artefactos en memoria y
devuelve `AuditReport`. No lee archivos, no llama al LLM y no resuelve instancias.
Las pruebas comprueban también que no modifica los argumentos.

## Cobertura y referencias

Se comprueban el identificador del borrador, IDs duplicados de elementos,
existencia literal de fragmentos, referencias de cada vínculo y coincidencia
de tipos. Un vínculo inválido no cubre un requisito. Los errores de referencia,
tipo o requisitos sin cubrir tienen gravedad `error`; una restricción sin
requisito es `aviso`, porque puede corresponder a una omisión del Analista.

La herramienta busca además ecuaciones de la sección de restricciones que no
puede emparejar con el inventario. En ese caso registra `no_verificado`: un mapa
vacío o incompleto no constituye una prueba de que no hay restricciones.

## Subconjunto sintáctico

Se admite una declaración por línea, con símbolo y descripción separados por
dos puntos. Los símbolos son letras latinas, con subíndices simples de uno o dos
índices o índices separados por comas. Se reconocen sumatorias `sum_{i in I}` /
`\sum_{i\in I}`, cuantificadores `forall` / `\forall`, relaciones básicas,
dominios habituales y productos, potencias o divisiones simples entre variables.

Los chequeos buscan símbolos no declarados, dominios ausentes, aridad, variables
y parámetros sin uso, datos sin parámetro reconocido, conjuntos de índices,
índices libres y no linealidad detectable. La correspondencia de parámetros
usa el símbolo sugerido por el análisis: un cambio legítimo de nombre necesita
inspección semántica. Una variable auxiliar sin uso reconocido también produce
un aviso, nunca una eliminación automática.

No hay un parser algebraico completo. Fracciones LaTeX, nombres matemáticos
compuestos, texto incrustado, índices desplazados y declaraciones ambiguas se
informan como `no_verificado`. El alcance de una sumatoria termina en el primer
`+`, `-`, relación o paréntesis de cierre a nivel cero; un índice ligado solo por
esa sumatoria que reaparece después produce `indice_libre` (por ejemplo
`\sum_{i\in I} x_{it} = d_i \quad orall t\in T`). Esta regla sigue la
convención habitual y no prueba otros alcances de expresiones compuestas. Una
variable junto a un paréntesis (`x_i (x_i)`, `x_i (1 - y_j)`) se informa como
producto si el otro factor es una variable reconocible y, en todo caso, como
`no_lineal` `no_verificado`. Los chequeos no verificados nunca llevan gravedad.
Un chequeo puede tener simultáneamente un hallazgo comprobable y otras partes
no verificadas. Los hallazgos sintácticos se mantienen como `aviso` durante el
desarrollo; su precisión en salidas reales debe revisarse en el piloto.

## Calibración de desarrollo

`eval/audit_dev_fixtures.py` contiene ocho formulaciones paramétricas escritas
manualmente a partir de los ocho enunciados de desarrollo. No son resultados de
Qwen. Incluyen mezcla, horas extra, asignación, lógica binaria, viajes enteros,
costos fijos, contenedores e inventario. Los controles usan un formato explícito;
el inventario con índice desplazado comprueba la degradación a no verificado.

Ejecutar desde la raíz, con las dependencias del proyecto instaladas:

```powershell
python "Deliverable 3/eval/calibrate_audit.py" --output "Deliverable 3/eval/audit_calibration.json"
python -m unittest discover -s "Deliverable 3/tests"
```

Los tests incluyen mutaciones que introducen los errores deterministas y ocho
controles sin hallazgos falsos. El informe conserva explícitamente las partes no
verificadas; su ausencia de errores no prueba corrección matemática ni reemplaza
la calibración sobre candidatos del piloto en Colab T4.
