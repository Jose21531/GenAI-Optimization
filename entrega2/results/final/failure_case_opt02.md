# Degradación post-ajuste en el benchmark: opt_02

Baseline directo determinista: 1.300/5. QLoRA: 0.0/5 (FOM-5 v2).

## Enunciado exacto

Una fábrica produce tres artículos A, B y C en una semana. Debe decidir las cantidades fabricadas y si utiliza horas extraordinarias de mano de obra. Los artículos consumen simultáneamente horas de trabajo, horas de máquina y materia prima; una hora extraordinaria aumenta exclusivamente la disponibilidad de trabajo. Las ganancias unitarias indicadas ya descuentan los costos ordinarios de fabricación, mientras que las horas extraordinarias se pagan por separado.

Por unidad, A deja una contribución de 35 y requiere 2 horas de trabajo, 1 de máquina y 3 unidades de materia prima. B deja 50 y consume 3, 2 y 2 unidades de esos recursos, respectivamente. C deja 42 y consume 1, 3 y 4. Existen 140 horas ordinarias de trabajo, 120 horas de máquina y 210 unidades de materia prima. Pueden contratarse hasta 20 horas extraordinarias, a 10 unidades monetarias cada una. La demanda permite vender como máximo 30 unidades de A, 28 de B y 32 de C. Además, la fábrica tiene comprometida la entrega de al menos 10 unidades de C.

Se busca maximizar la ganancia semanal neta, después de pagar las horas extraordinarias, sin exceder ninguna capacidad ni los topes de ventas. Las cantidades de artículos se pueden planificar de manera continua para efectos de este modelo; las horas extraordinarias también pueden fraccionarse.

## Respuesta QLoRA exacta

Conjuntos:
\(I\): tipos de artículo.
\(M\): recursos: trabajo, máquina, materia prima.
\(K\): disponibilidad extra de mano de obra.

Parámetros:
\(p_i\): precio unitario del artículo \(i\).
\(c_{mi}\): costo unitario del recurso \(m\) proporcionado por un horizonte extra de mano de obra.
\(a_{ik}\): requerimiento del recurso \(m\) por unidad del artículo \(i\).
\(b_k\): disponibilidad extra de mano de obra disponible para uso con el artículo \(i\).

Variables de decisión:
\(x_i\ge0\): cantidad del artículo \(i\) producida.
\(y_k\in[0,1]\): vale 1 si se utilizan \(k\) horas extras de mano de obra.

Función objetivo:
\[
\max \sum_{i\in I} p_i x_i - \sum_{i\in I}\sum_{k=0}^{K} c_{mk}y_k
\]

Restricciones:
\[
\sum_{i\in I} a_{im}x_i\le b_m \qquad \forall m\in M
\]
\[
\sum_{i\in I}a_{ik}x_i\le b_k+y_k \qquad \forall i\in I,\ \forall k\in K
\]
\[
x_i\le b_k y_k \qquad \forall i\in I,\ \forall k\in K
\]
\[
\sum_{i\in I}x_i\le s
\]

## Error matemático

La hora extraordinaria debe ser una variable continua $h\in[0,20]$ que amplía solo la disponibilidad laboral: $2x_A+3x_B+x_C\le140+h$, con costo $10h$ en la ganancia neta. La respuesta usa $y_k\in[0,1]$ como supuesto indicador de horas extras y le impone vínculos artificiales con cada producto. Además omite $x_C\ge10$ y no representa correctamente las capacidades de máquina y materia prima. El juez le asignó 0.000/5, frente a 1.300/5 del baseline; el caso muestra una degradación real, no solo una mejora incompleta.

## Juicio bruto

```json
{
  "has_formulation": true,
  "requirements": {
    "R1": "wrong",
    "R2": "wrong",
    "R3": "wrong",
    "R4": "wrong",
    "R5": "wrong",
    "R6": "wrong"
  },
  "scores": {
    "decision_domains": 2,
    "objective": 2,
    "constraints_logic": 0,
    "algebra_validity": 0,
    "generalization": 0
  },
  "fatal_errors": ["La formulación presenta múltiples errores esenciales en la lógica de las restricciones, en la definición de variables y en la relación entre horas extraordinarias y recursos. La función objetivo no representa correctamente la ganancia neta, y las restricciones no reflejan las condiciones del problema original."]
}
```
