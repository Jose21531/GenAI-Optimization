# Casos del benchmark: enunciado, respuestas y puntaje

Este archivo permite revisar, problema por problema, qué recibió el modelo, qué respondió con y sin QLoRA y cómo lo evaluó el juez FOM-5 v2. Se genera a partir de [`data/benchmark_30.jsonl`](data/benchmark_30.jsonl) y de los CSV de [`output/`](output/), sin editar las respuestas.

- **Baseline:** Qwen2.5-1.5B-Instruct con prompting directo (adapter apagado).
- **QLoRA:** el mismo modelo con el adapter entrenado.
- **Puntaje:** FOM-5 v2, de 0 a 5. Ambos generadores recibieron solo el enunciado; la referencia y los requisitos se usaron únicamente en la evaluación.
- Las respuestas completas están en los CSV; aquí se normalizan espacios finales y delimitadores de código para mantener legible el Markdown.

**Resumen de los 30 casos:** media 0.59 → 0.80 · 14 mejoran, 8 quedan igual, 8 empeoran. El caso de la Entrega 1 aparece al final, fuera de la media.

## Índice

| ID | Problema | Tipo | Baseline | QLoRA | Cambio |
|---|---|:---:|---:|---:|---|
| [opt_01](#opt_01) | Plan de publicidad con cobertura de públicos | IP | 4.85 | 3.67 | empeora (-1.18) |
| [opt_02](#opt_02) | Producción con horas extraordinarias | LP | 1.30 | 0.00 | empeora (-1.30) |
| [opt_03](#opt_03) | Paquetes escolares con tres composiciones | IP | 1.95 | 0.00 | empeora (-1.95) |
| [opt_04](#opt_04) | Distribución de fruta según calidad promedio | LP | 0.00 | 0.00 | igual (+0.00) |
| [opt_05](#opt_05) | Dotación semanal con descansos consecutivos | IP | 0.00 | 5.00 | mejora (+5.00) |
| [opt_06](#opt_06) | Dos alimentos y existencias compartidas | LP | 2.60 | 1.45 | empeora (-1.15) |
| [opt_07](#opt_07) | Portafolio con desembolsos por año | BIP | 0.00 | 0.80 | mejora (+0.80) |
| [opt_08](#opt_08) | Asignación de jugadores a posiciones | BIP | 0.00 | 0.00 | igual (+0.00) |
| [opt_09](#opt_09) | Desarrollo habitacional con cuota social | IP | 0.00 | 0.00 | igual (+0.00) |
| [opt_10](#opt_10) | Selección de exploraciones con conflictos | BIP | 0.00 | 1.60 | mejora (+1.60) |
| [opt_11](#opt_11) | Programa académico con matrículas fijas | MILP/BIP | 0.00 | 1.98 | mejora (+1.98) |
| [opt_12](#opt_12) | Reducción de vertimientos en un río | MILP | 0.00 | 0.00 | igual (+0.00) |
| [opt_13](#opt_13) | Camino de inspección obligatoria | BIP/red | 2.93 | 1.80 | empeora (-1.13) |
| [opt_14](#opt_14) | Flujo máximo en una red de abastecimiento | LP/red | 0.00 | 0.30 | mejora (+0.30) |
| [opt_15](#opt_15) | Envíos con dos plantas y centros de transbordo | LP/red | 0.00 | 0.35 | mejora (+0.35) |
| [opt_16](#opt_16) | Dos productos sobre arcos compartidos | LP/red | 0.00 | 0.55 | mejora (+0.55) |
| [opt_17](#opt_17) | Red de fibra con conexión de todas las estaciones | BIP/red | 0.00 | 1.60 | mejora (+1.60) |
| [opt_18](#opt_18) | Recorrido circular de visitas técnicas | MILP/TSP | 0.00 | 0.45 | mejora (+0.45) |
| [opt_19](#opt_19) | Rutas de dos vehículos con carga limitada | MILP/CVRP | 0.00 | 0.00 | igual (+0.00) |
| [opt_20](#opt_20) | Secuenciación de trabajos con preparación | MILP/secuenciación | 0.00 | 0.00 | igual (+0.00) |
| [opt_21](#opt_21) | Corte de barras con patrones y merma | IP | 1.00 | 0.00 | empeora (-1.00) |
| [opt_22](#opt_22) | Producción por lotes e inventario limitado | MILP | 0.92 | 0.00 | empeora (-0.92) |
| [opt_23](#opt_23) | Contratación con un mes de capacitación | IP | 0.00 | 0.00 | igual (+0.00) |
| [opt_24](#opt_24) | Despacho eléctrico con batería | LP | 0.00 | 0.00 | igual (+0.00) |
| [opt_25](#opt_25) | Localización con peor distancia de servicio | MILP/localización | 0.00 | 0.74 | mejora (+0.74) |
| [opt_26](#opt_26) | Cobertura de barrios bajo un presupuesto | BIP/cobertura | 0.35 | 1.18 | mejora (+0.83) |
| [opt_27](#opt_27) | Bodegas con apertura, capacidad y reparto | MILP/localización | 0.00 | 0.95 | mejora (+0.95) |
| [opt_28](#opt_28) | Trabajos indivisibles en impresoras con horas limitadas | MILP/asignación | 0.00 | 0.45 | mejora (+0.45) |
| [opt_29](#opt_29) | Selección de rutas de cuadrillas ya diseñadas | BIP/partición | 1.75 | 0.80 | empeora (-0.95) |
| [opt_30](#opt_30) | Proyecto con precedencias y recurso compartido | MILP/proyecto | 0.00 | 0.40 | mejora (+0.40) |
| [diagnóstico](#diagnostico-oftalmo) | Centros oftalmológicos (Entrega 1) | MILP | 0.65 | 3.85 | fuera de la media |

---

## opt_01

### Plan de publicidad con cobertura de públicos

Tipo: IP · Dificultad: baja · Baseline **4.85** → QLoRA **3.67** (empeora)

**Enunciado**

> Una organización regional lanzará una campaña de prevención y debe contratar espacios publicitarios en radio, plataformas digitales y pantallas de transporte. Puede comprar una cantidad entera de inserciones de cada medio. Una misma persona podría ver más de una inserción; por ello las cifras siguientes representan contactos publicitarios acumulados y no personas únicas. La meta es asegurar un mínimo de contactos tanto entre jóvenes como entre adultos, sin exceder el presupuesto disponible.
>
> Una inserción de radio cuesta 8 unidades presupuestarias y produce 4 unidades de contactos jóvenes y 8 de contactos adultos. Una inserción digital cuesta 5 y produce 7 unidades de contactos jóvenes y 2 de adultos. Una pantalla de transporte cuesta 6 y genera 5 unidades de contactos jóvenes y 4 de adultos. Se requieren al menos 60 unidades de contactos jóvenes y 50 de contactos adultos. El presupuesto máximo es 110 unidades; además, por disponibilidad comercial, pueden contratarse a lo sumo 10 inserciones de radio, 12 digitales y 9 de pantallas. Cada compra se realiza por inserción completa.
>
> La dirección desea determinar cuántas inserciones contratar de cada medio para cumplir simultáneamente ambas metas de cobertura y las condiciones comerciales. Entre los planes que satisfacen esas condiciones, prefiere el que tenga el menor gasto total. Plantee el modelo en términos de las decisiones enteras, las unidades de contactos y los costos indicados.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar el costo total de inserciones. | cumple | cumple |
| R2 | constraint | Cumplir al menos el mínimo de contactos de cada grupo. | cumple | cumple |
| R3 | constraint | No exceder el presupuesto total. | cumple | cumple |
| R4 | constraint | Respetar máximos por medio. | cumple | ausente |
| R5 | domain | Variables de inserciones enteras no negativas. | cumple | parcial |

<details><summary>Formulación de referencia</summary>

Sean $M=\{R,D,P\}$ los medios radio, digital y pantallas, y $G=\{J,A\}$ los públicos jóvenes y adultos. $c_m$ es costo por inserción, $a_{gm}$ contactos del grupo $g$ por inserción, $b_g$ mínimo de contactos, $u_m$ límite de inserciones y $B=110$ presupuesto. $x_m\in\mathbb Z_{\geq0}$ indica inserciones contratadas.

$$
\min\sum_{m\in M}c_mx_m\quad\text{s.a.}\quad
\sum_{m\in M}a_{gm}x_m\geq b_g\ (g\in G),\quad
\sum_{m\in M}c_mx_m\leq B,\quad
0\leq x_m\leq u_m,\ x_m\in\mathbb Z\ (m\in M).
$$

</details>

**Baseline — 4.85/5** (decisiones 5.0, objetivo 5.0, restricciones 5.0, álgebra 5.0, generalización 4.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un método llamado "modelización matemática" o "programación lineal". Esta técnica nos permitirá encontrar la solución óptima que cumpla con todas las restricciones dadas (como el número de inserciones y el presupuesto) y minimice el costo total.

### Variables:
- \( x_1 \): Inserciones de radio.
- \( x_2 \): Inserciones digitales.
- \( x_3 \): Inserciones de transportes.

### Restricciones:

1. **Contactos Jóvenes**:
   - \( 4x_1 + 7x_2 + 5x_3 \geq 60 \)

2. **Contactos Adultos**:
   - \( 8x_1 + 2x_2 + 4x_3 \geq 50 \)

3. **Presupuesto**:
   - \( 8x_1 + 5x_2 + 6x_3 \leq 110 \)

4. **Número de Inserciones**:
   - \( x_1 \leq 10 \)
   - \( x_2 \leq 12 \)
   - \( x_3 \leq 9 \)

5. **Restricciones de Posición**:
   - No hay restricción específica mencionada sobre la posición de las inserciones, pero deben ser completas.

### Objetivo:
Minimizar el costo total:
\[ \text{Costo} = 8x_1 + 5x_2 + 6x_3 \]

### Modelo Matemático

Vamos a construir un sistema de ecuaciones lineales que representa nuestra situación:

\[
\begin{align*}
4x_1 + 7x_2 + 5x_3 &\geq 60 \\
8x_1 + 2x_2 + 4x_3 &\geq 50 \\
8x_1 + 5x_2 + 6x_3 &\leq 110 \\
x_1 &\leq 10 \\
x_2 &\leq 12 \\
x_3 &\leq 9 \\
x_1, x_2, x_3 &\in \mathbb{Z}^+
\end{align*}
\]

### Solución del Sistema

Primero, resolvemos la primera restricción para obtener una relación entre \(x_1\) y \(x_2\):

\[
4x_1 + 7x_2 + 5x_3 \geq 60
\]

Ahora, resolvemos la segunda restricción para obtener otra relación:

\[
8x_1 + 2x_2 + 4x_3 \geq 50
\]

Finalmente, resolvemos la tercera restricción para obtener la última relación:

\[
8x_1 + 5x_2 + 6x_3 \leq 110
\]

### Paso 1: Resolución de Ecuaciones Simultáneas

Resolver estas ecuaciones simultáneamente puede ser complejo manualmente, así que usaremos software de programación lineal o herramientas de optimización para encontrar la solución óptima. Aquí te proporciono una guía general:

1. **Incorporar las restricciones** en un programa de optimización.
2. **Definir variables** y **objetivos**.
3. **Resolver el sistema** utilizando el algoritmo de optimización.

### Resultado Final

Después de resolver el sistema usando un programa de optimización, obtenemos las siguientes soluciones:

- \( x_1 = 5 \)
- \( x_2 = 4 \)
- \( x_3 = 5 \)

### Costo Total

Con estos valores, el costo total será:

\[
\text{Costo} = 8(5) + 5(4) + 6(5) = 40 + 20 + 30 = 90
\]

### Conclusión

El plan que minimiza el costo total mientras cumple con todas las restricciones es:

- 5 inserciones de radio,
- 4 inserciones digitales,
- 5 inserciones de transportes.

Este plan garantiza al menos 60 contactos jóvenes y 50 contactos adultos, dentro del presupuesto de 110 unidades y con un máximo de 10 inserciones de radio, 12 digitales y 9 de transportes.
```

</details>

**QLoRA — 3.67/5** (decisiones 2.0, objetivo 5.0, restricciones 3.333333333333333, álgebra 5.0, generalización 3.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): medios de comunicación.
\(J\): grupos demográficos o contactos.

Parámetros:
\(c_i\): costo de una inserción en el medio \(i\).
\(a_{ij}\): contactos del grupo \(j\) generados por una inserción en \(i\).
\(b_j\): contactos mínimos requeridos en el grupo \(j\).
\(B\): presupuesto máximo.

Variables de decisión:
\(x_i\in\mathbb Z^{+}\): número de inserciones contratadas en el medio \(i\).

Función objetivo:
\[
\min \sum_{i\in I}c_ix_i
\]

Restricciones:
\[
\sum_{i\in I}a_{ij}x_i\ge b_j \qquad \forall j\in J
\]
\[
\sum_{i\in I}cix_i\le B
\]
\[
x_i\in\mathbb Z^{+}\qquad \forall i\in I
\]
```

</details>

Observación del juez sobre QLoRA: No se incluyeron las restricciones de límite por medio (máximo de inserciones por tipo)

---

## opt_02

### Producción con horas extraordinarias

Tipo: LP · Dificultad: baja · Baseline **1.30** → QLoRA **0.00** (empeora)

**Enunciado**

> Una fábrica produce tres artículos A, B y C en una semana. Debe decidir las cantidades fabricadas y si utiliza horas extraordinarias de mano de obra. Los artículos consumen simultáneamente horas de trabajo, horas de máquina y materia prima; una hora extraordinaria aumenta exclusivamente la disponibilidad de trabajo. Las ganancias unitarias indicadas ya descuentan los costos ordinarios de fabricación, mientras que las horas extraordinarias se pagan por separado.
>
> Por unidad, A deja una contribución de 35 y requiere 2 horas de trabajo, 1 de máquina y 3 unidades de materia prima. B deja 50 y consume 3, 2 y 2 unidades de esos recursos, respectivamente. C deja 42 y consume 1, 3 y 4. Existen 140 horas ordinarias de trabajo, 120 horas de máquina y 210 unidades de materia prima. Pueden contratarse hasta 20 horas extraordinarias, a 10 unidades monetarias cada una. La demanda permite vender como máximo 30 unidades de A, 28 de B y 32 de C. Además, la fábrica tiene comprometida la entrega de al menos 10 unidades de C.
>
> Se busca maximizar la ganancia semanal neta, después de pagar las horas extraordinarias, sin exceder ninguna capacidad ni los topes de ventas. Las cantidades de artículos se pueden planificar de manera continua para efectos de este modelo; las horas extraordinarias también pueden fraccionarse.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar contribución de producción menos costo de horas extra. | incorrecto | incorrecto |
| R2 | constraint | Capacidad de trabajo ordinaria ampliable únicamente por horas extra. | incorrecto | incorrecto |
| R3 | constraint | Capacidades de máquina y materia prima. | incorrecto | incorrecto |
| R4 | constraint | 0 <= horas extra <= máximo permitido. | cumple | incorrecto |
| R5 | constraint | Topes de venta por producto y mínimo comprometido de C. | cumple | incorrecto |
| R6 | domain | Producción y horas extra continuas no negativas. | cumple | incorrecto |

<details><summary>Formulación de referencia</summary>

Sean $I=\{A,B,C\}$ los productos y $R=\{L,M,P\}$ los recursos trabajo, máquina y materia prima. $p_i$ es contribución, $a_{ri}$ consumo unitario, $b_r$ disponibilidad ordinaria, $d_i$ máximo de ventas, $O=20$ máximo de horas extra y $q=10$ costo por hora extra. $x_i\geq0$ es producción y $h\geq0$ son horas extraordinarias.

$$
\max\sum_{i\in I}p_ix_i-qh\quad\text{s.a.}\quad
\sum_i a_{Li}x_i\leq b_L+h,\quad
\sum_i a_{Mi}x_i\leq b_M,\quad
\sum_i a_{Pi}x_i\leq b_P,\quad
0\leq h\leq O,\quad x_C\geq10,\quad
0\leq x_i\leq d_i\ (i\in I).
$$

</details>

**Baseline — 1.30/5** (decisiones 2.0, objetivo 0.0, restricciones 2.0, álgebra 2.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, vamos a seguir estos pasos:

1) **Definición de Variables:**
   - X_A = cantidad de artículo A producida (en unidades)
   - X_B = cantidad de artículo B producida (en unidades)
   - X_C = cantidad de artículo C producida (en unidades)
   - Y = número de horas extraordinarias utilizadas

2) **Restricciones:**

   - Horas de trabajo:
     \[ 2X_A + 3X_B + Y \leq 140 \]

   - Horas de máquina:
     \[ X_A + 2X_B + 3Y \leq 120 \]

   - Unidades de materia prima:
     \[ 3X_A + 2X_B + 4Y \leq 210 \]

   - Demanda máxima de A:
     \[ X_A \leq 30 \]

   - Demanda máxima de B:
     \[ X_B \leq 28 \]

   - Demanda máxima de C:
     \[ X_C \leq 32 \]

   - Firma obligatoria de C:
     \[ X_C \geq 10 \]

   - Horas extraordinarias:
     \[ 0 \leq Y \leq 20 \]

3) **Ganancias Unitarias:**
   - Ganancia de A: $35
   - Ganancia de B: $50
   - Ganancia de C: $42

4) **Costo de horas extraordinarias:**
   - Costo de una hora extraordinaria: $10

5) **Maximización de Gananza Semanal Neta:**
   \[ \text{Maximize} \quad Z = 35X_A + 50X_B + 42X_C \]

6) **Formulación del Modelo:**
   Usando el método de optimización lineal, podemos escribir la función objetivo y las restricciones como sigue:

   \[
   \begin{align*}
   &\text{Maximize} \quad Z = 35X_A + 50X_B + 42X_C \\
   &\text{s.t.} \\
   &2X_A + 3X_B + Y \leq 140 \\
   &X_A + 2X_B + 3Y \leq 120 \\
   &3X_A + 2X_B + 4Y \leq 210 \\
   &X_A \leq 30 \\
   &X_B \leq 28 \\
   &X_C \leq 32 \\
   &X_C \geq 10 \\
   &0 \leq Y \leq 20 \\
   &X_A, X_B, X_C, Y \geq 0
   \end{align*}
   \]

7) **Resolución del Modelo:**
   Este es un problema de programación lineal con múltiples variables y restricciones. Para su resolución, podríamos utilizar software de programación lineal o procedimientos numéricos como simplex.

8) **Interpretación del Resultado:**
   Una vez obtenido el valor óptimo de Z, interpretaremos cómo deben ser las cantidades de A, B y C para maximizar la ganancia semanal neta, considerando además las horas extraordinarias y sus costos.

Este proceso debe realizarse utilizando un programa de optimización lineal o un sistema de cálculo avanzado para obtener resultados precisos.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
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
```

</details>

Observación del juez sobre QLoRA: La formulación presenta múltiples errores esenciales en la lógica de las restricciones, en la definición de variables y en la relación entre horas extraordinarias y recursos. La función objetivo no representa correctamente la ganancia neta, y las restricciones no reflejan las condiciones del problema original.

---

## opt_03

### Paquetes escolares con tres composiciones

Tipo: IP · Dificultad: baja · Baseline **1.95** → QLoRA **0.00** (empeora)

**Enunciado**

> Una cooperativa dispone de cuadernos, carpetas y lápices para armar tres tipos de paquetes escolares. Cada paquete debe ensamblarse completo; no se venden fracciones ni se reemplazan insumos faltantes. La cooperativa puede dejar artículos sin usar, pero no comprar más antes de la campaña. Sus acuerdos comerciales fijan una demanda máxima para cada tipo de paquete y un compromiso mínimo para el paquete básico.
>
> Hay 180 cuadernos, 120 carpetas y 170 lápices. El paquete básico requiere 2 cuadernos, 1 carpeta y 2 lápices y deja un margen de 25 unidades monetarias. El paquete de actividades utiliza 1 cuaderno, 2 carpetas y 2 lápices y deja un margen de 30. El paquete avanzado consume 3 cuadernos, 1 carpeta y 1 lápiz y deja un margen de 35. Se pueden vender como máximo 40 paquetes básicos, 35 de actividades y 45 avanzados. Una escuela ya encargó al menos 20 paquetes básicos, incluidos dentro del límite de venta de ese producto.
>
> La cooperativa quiere elegir cuántos paquetes de cada clase armar para maximizar el margen total. Debe respetar las tres existencias, el pedido mínimo y los máximos de venta. Formule las variables como cantidades enteras y refleje la distinta composición de cada paquete en cada restricción de inventario.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar margen total de paquetes. | cumple | incorrecto |
| R2 | constraint | Restricciones de inventario separadas por cada insumo. | incorrecto | incorrecto |
| R3 | constraint | Máximos de demanda por paquete. | parcial | incorrecto |
| R4 | constraint | Mínimo de paquetes básicos. | cumple | incorrecto |
| R5 | domain | Variables enteras no negativas. | parcial | incorrecto |

<details><summary>Formulación de referencia</summary>

$I=\{C,F,L\}$ representa cuadernos, carpetas y lápices; $K=\{B,A,V\}$ representa paquetes básico, actividades y avanzado. $a_{ik}$ es la cantidad del insumo $i$ en el paquete $k$, $s_i$ la existencia, $p_k$ el margen unitario y $u_k$ la demanda máxima. $x_k\in\mathbb Z_{\geq0}$ es el número de paquetes.

$$
\max\sum_{k\in K}p_kx_k\quad\text{s.a.}\quad
\sum_{k\in K}a_{ik}x_k\leq s_i\ (i\in I),\quad
x_B\geq20,\quad 0\leq x_k\leq u_k,\ x_k\in\mathbb Z\ (k\in K).
$$

</details>

**Baseline — 1.95/5** (decisiones 2.0, objetivo 5.0, restricciones 1.0, álgebra 1.0, generalización 1.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, primero definiremos las variables:

- \( x_1 \): número de paquetes básicos que se van a producir.
- \( x_2 \): número de paquetes de actividades que se van a producir.
- \( x_3 \): número de paquetes avanzados que se van a producir.

Luego, estableceremos las restricciones basadas en las necesidades mínimas y máximas de cada tipo de paquete, así como las limitaciones de inventarios:

1. **Paquetes Básicos:**
   - Necesidad mínima: 20 paquetes básicos (incluido el pedido)
   - Máximo permitido: 40 paquetes básicos

2. **Paquetes de Actividades:**
   - Necesidad mínima: Ninguna (no hay restricción específica mencionada)
   - Máximo permitido: 35 paquetes de actividades

3. **Paquetes Avanzados:**
   - Necesidad mínima: Ninguna (no hay restricción específica mencionada)
   - Máximo permitido: 45 paquetes avanzados

4. **Inventario de Cuadernos:**
   - Necesidad mínima: 180 cuadernos
   - Máximo permitido: 180 cuadernos

5. **Inventario de Carpetas:**
   - Necesidad mínima: 120 carpetas
   - Máximo permitido: 120 carpetas

6. **Inventario de Lápices:**
   - Necesidad mínima: 170 lápices
   - Máximo permitido: 170 lápices

Ahora, formulemos las ecuaciones de restricción utilizando estas variables y las condiciones proporcionadas:

### Inventario de Cuadernos:
\[ 2x_1 + x_2 + 3x_3 \geq 180 \]

### Inventario de Carpetas:
\[ x_1 + 2x_2 + x_3 \geq 120 \]

### Inventario de Lápices:
\[ 2x_1 + 2x_2 + x_3 \geq 170 \]

### Paquetes Básicos:
\[ x_1 \geq 20 \]

### Paquetes de Actividades:
\[ x_2 \geq 0 \]

### Paquetes Avanzados:
\[ x_3 \geq 0 \]

### Margen Total:
\[ 25x_1 + 30x_2 + 35x_3 \]

### Maximización del Margen Total:
\[ \text{Maximize} \quad 25x_1 + 30x_2 + 35x_3 \]

### Restricciones:
1. \( 2x_1 + x_2 + 3x_3 \geq 180 \)
2. \( x_1 + 2x_2 + x_3 \geq 120 \)
3. \( 2x_1 + 2x_2 + x_3 \geq 170 \)
4. \( x_1 \geq 20 \)
5. \( x_2 \geq 0 \)
6. \( x_3 \geq 0 \)

### Solución:
Primero, resolvamos las primeras dos restricciones para obtener una solución inicial:

1. \( 2x_1 + x_2 + 3x_3 = 180 \)
2. \( x_1 + 2x_2 + x_3 = 120 \)

Resolviendo estos sistemas de ecuaciones simultáneamente es complicado directamente, por lo que usaremos un método iterativo o programación lineal para encontrar una solución óptima.

Finalmente, verificaremos si esta solución cumple con todas las restricciones y maximiza el margen total. Si no, ajustaremos las variables para cumplir con todas las restricciones y maximizar el margen total.

Este proceso generalmente requiere software de optimización lineal para resolverlo exhaustivamente. Sin embargo, puedes utilizar herramientas como Excel Solver, Python con SciPy, o cualquier otro programa de optimización para realizarlo.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): tipos de paquetes.
\(K\): existencias disponibles.
\(M\): margen monetario disponible.

Parámetros:
\(s_i\): cantidad requerida del tipo \(i\) de paquete.
\(u_{ik}\): disponibilidad del tipo \(i\) en la existencia \(k\).
\(c_{ijk}\): costo unitario del tipo \(i\), cantidad \(k\) del tipo \(j\).
\(b_i\): pedido mínimo del tipo \(i\).
\(B_i\): límite de venta del tipo \(i\).

Variables de decisión:
\(x_{ik}\in\mathbb Z_{\ge0}\): número del tipo \(i\) del paquete \(k\).

Función objetivo:
\[
\max \sum_{i\in I}\sum_{k\in K}c_{ijk}x_{ik}
\]

Restricciones:
\[
\sum_{i\in I}x_{ik}\le B_k \qquad \forall k\in K
\]
\[
\sum_{k\in K}s_ix_{ik}\le M(b_i-x_{ik})+b_i \qquad \forall i\in I,\ x_{ik}\ge b_i
\]
\[
\sum_{k\in K}u_{ik}x_{ik}\le M(B_i-x_{ik})+B_i \qquad \forall i\in I,\ x_{ik}\ge B_i
\]
```

</details>

Observación del juez sobre QLoRA: La formulación presenta múltiples errores en la definición de conjuntos, parámetros, variables y restricciones. La función objetivo no refleja el margen de los paquetes, las restricciones de inventario están mal definidas, y no se respetan los requisitos de mínimos y máximos por paquete. La notación y la estructura son inconsistentes con el enunciado.

---

## opt_04

### Distribución de fruta según calidad promedio

Tipo: LP · Dificultad: media · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Una procesadora dispone de naranjas de grado 9 y de grado 6, medidos en una escala donde un valor mayor representa mejor calidad. Puede destinarlas a bolsas de fruta fresca o a la elaboración de jugo. Las naranjas de cada grado pueden dividirse entre ambos destinos y una parte de la cosecha puede quedar sin utilizar. Las exigencias de calidad se aplican al promedio ponderado de las naranjas efectivamente destinadas a cada producto.
>
> Se dispone de hasta 100 toneladas de grado 9 y 120 toneladas de grado 6. Las bolsas de fruta fresca requieren calidad promedio de al menos 8 y dejan una contribución de 80 unidades monetarias por tonelada utilizada. El jugo requiere promedio de al menos 7,5 y deja 50 por tonelada. Por compromisos comerciales deben prepararse al menos 40 toneladas de fruta fresca y 50 de jugo; el equipamiento permite como máximo 130 toneladas de fruta fresca y 120 de jugo. Las contribuciones son independientes del grado de origen una vez cumplida la calidad del producto final.
>
> Se debe decidir cuántas toneladas de cada grado enviar a cada destino para maximizar la contribución total. El modelo debe conservar por separado las disponibilidades de cada grado, las cantidades mínima y máxima de cada producto y las dos condiciones de promedio de calidad, sin imponer que toda la cosecha sea procesada.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar contribución total de toneladas destinadas a productos. | incorrecto | incorrecto |
| R2 | constraint | Disponibilidad separada por grado. | incorrecto | incorrecto |
| R3 | constraint | Mínimo y máximo de toneladas por producto. | incorrecto | incorrecto |
| R4 | constraint | Calidad promedio mínima de cada producto correctamente linealizada. | incorrecto | incorrecto |
| R5 | domain | Variables continuas no negativas; no obligar a usar toda la cosecha. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$G=\{9,6\}$ son grados y $P=\{F,J\}$ productos fruta fresca y jugo. $s_g$ es disponibilidad de grado $g$, $q_g=g$ calidad, $Q_p$ calidad mínima, $l_p,u_p$ producción mínima y máxima y $v_p$ contribución por tonelada. $x_{gp}\geq0$ son toneladas de grado $g$ destinadas a $p$.

$$
\max\sum_{p\in P}v_p\sum_{g\in G}x_{gp}\quad\text{s.a.}\quad
\sum_p x_{gp}\leq s_g\ (g\in G),\quad
l_p\leq\sum_gx_{gp}\leq u_p\ (p\in P),\quad
\sum_g(q_g-Q_p)x_{gp}\geq0\ (p\in P),\quad x_{gp}\geq0.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos usar un método matemático llamado "Programación Lineal". Esta técnica nos permitirá optimizar nuestra decisión de cómo distribuir las naranjas según los requisitos de calidad y las limitaciones de capacidad.

### Variables:
- \( x_1 \): Toneladas de grado 9 destinadas a frutas frescas.
- \( x_2 \): Toneladas de grado 9 destinadas a jugo.
- \( x_3 \): Toneladas de grado 6 destinadas a frutas frescas.
- \( x_4 \): Toneladas de grado 6 destinadas a jugo.

### Ecuaciones:

1. **Suma de toneladas**: La suma total de las toneladas de naranjas destinadas a frutas frescas y jugo debe ser igual a la cantidad disponible (100 + 120 = 220 toneladas).
   - \( x_1 + x_2 + x_3 + x_4 = 220 \)

2. **Promedio de calidad**: Para frutas frescas, la contribución promedio es 80 unidades monetarias por tonelada. Para jugo, es 50 unidades monetarias por tonelada.
   - \( 8x_1 + 7.5x_3 = 40 \) (para frutas frescas)
   - \( 5x_2 + 50x_4 = 50 \) (para jugo)

3. **Capacidad de producción**: No se pueden producir más de 130 toneladas de frutas frescas ni 120 toneladas de jugo.
   - \( x_1 + x_2 \leq 130 \)
   - \( x_3 + x_4 \leq 120 \)

4. **Restricciones de grado de origen**:
   - \( 9x_1 + 6x_3 \geq 100 \) (grado 9)
   - \( 9x_2 + 6x_4 \geq 120 \) (grado 6)

### Modelo Matemático

La función objetivo es maximizar la contribución total:
\[ \text{Maximize} \quad 80x_1 + 50x_3 + 5x_2 + 50x_4 \]

Con las siguientes restricciones:
1. \( x_1 + x_2 + x_3 + x_4 = 220 \)
2. \( 8x_1 + 7.5x_3 = 40 \)
3. \( 5x_2 + 50x_4 = 50 \)
4. \( x_1 + x_2 \leq 130 \)
5. \( x_3 + x_4 \leq 120 \)
6. \( 9x_1 + 6x_3 \geq 100 \)
7. \( 9x_2 + 6x_4 \geq 120 \)

### Solución

Primero resolvemos las ecuaciones lineales para encontrar valores aproximados para \( x_1, x_2, x_3, x_4 \).

1. Resolvamos \( 8x_1 + 7.5x_3 = 40 \):
   - \( x_1 = \frac{40 - 7.5x_3}{8} \)

2. Resolvamos \( 5x_2 + 50x_4 = 50 \):
   - \( x_2 = \frac{50 - 50x_4}{5} \)

3. Resolvamos \( 9x_1 + 6x_3 \geq 100 \):
   - \( x_3 \geq \frac{100 - 9x_1}{6} \)

4. Resolvamos \( 9x_2 + 6x_4 \geq 120 \):
   - \( x_4 \geq \frac{120 - 9x_2}{6} \)

Ahora, combinamos estas ecuaciones con las restricciones de capacidad y grado de origen para obtener los valores óptimos.

Finalmente, calcularemos los valores de \( x_1, x_2, x_3, x_4 \) utilizando estos cálculos y verificaremos si cumple todas las restricciones.

Este proceso requerirá un programa de programación lineal o software de optimización para realizarlo exactamente. Sin embargo, esta descripción te da una idea general de cómo resolver este tipo de problema.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): grados de naranja.
\(P\): tipos de producto (fruta fresca, jugo).

Parámetros:
\(b_i\): capacidad disponible del grado \(i\).
\(c_p\): costo unitario del producto \(p\).
\(u_p\): requerimiento mínimo de calidad del producto \(p\).
\(L_{ip},U_{ip}\): límites inferior y superior de disponibilidad del grado \(i\) del producto \(p\).
\(u_{fp},u_{gp}\): límites inferior y superior de producción del producto \(p\).

Variables de decisión:
\(x_{ip}\in\mathbb Z^{+}:\) cantidad del grado \(i\) enviada al producto \(p\).

Función objetivo:
\[
\max \sum_{i\in I}\sum_{p\in P}c_px_{ip}
\]

Restricciones:
\[
\sum_{i\in I}x_{ip}\le b_i \qquad \forall p\in P
\]
\[
\frac{\sum_{i\in I}cx_{ip}}{u_p}\ge u_{fp} \qquad \forall p\in P
\]
\[
\frac{\sum_{i\in I}cx_{ip}}{g_p}\ge u_{gp} \qquad \forall p\in P
\]
\[
L_{ip}x_{ip}\le u_{ip}x_{ip}\le U_{ip}x_{ip}\qquad \forall i\in I,\ \forall p\in P
\]
```

</details>

Observación del juez sobre QLoRA: La formulación presenta múltiples errores esenciales: objetivo incorrecto, restricciones mal formuladas, dominios de variables incorrectos, y condiciones de calidad no linealizadas correctamente.

---

## opt_05

### Dotación semanal con descansos consecutivos

Tipo: IP · Dificultad: baja · Baseline **0.00** → QLoRA **5.00** (mejora)

**Enunciado**

> Una tienda opera de lunes a domingo y necesita decidir cuántos vendedores comienzan su jornada semanal cada día. Quien inicia un día trabaja cinco días consecutivos y luego descansa los dos siguientes; el ciclo continúa de una semana a otra. Por ejemplo, una persona que empieza el sábado atiende sábado, domingo, lunes, martes y miércoles. Cada vendedor sigue exactamente uno de los siete patrones posibles, identificado por su día de inicio.
>
> Los mínimos de vendedores presentes de lunes a domingo son 14, 18, 20, 25, 30, 28 y 22. El costo semanal por vendedor es de 500 unidades monetarias si inicia de lunes a viernes y de 550 si inicia sábado o domingo, considerando el suplemento correspondiente. La tienda puede contratar hasta 45 vendedores en total; cualquier exceso de cobertura en un día está permitido. No existen empleados compartidos con otras sucursales y las cantidades contratadas deben ser enteras.
>
> La gerencia busca determinar cuántas personas asignar a cada patrón de inicio para cumplir los siete mínimos diarios con el menor costo semanal. La cobertura de un día debe sumar solamente a quienes efectivamente trabajan ese día, incluidos los turnos que comenzaron durante la semana anterior y cruzan el límite entre domingo y lunes.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo semanal de vendedores por patrón de inicio. | incorrecto | cumple |
| R2 | constraint | Cobertura mínima cada día considerando patrón cíclico de 5 días trabajados y 2 libres. | incorrecto | cumple |
| R3 | constraint | Máximo total de vendedores. | incorrecto | cumple |
| R4 | domain | Variables enteras no negativas por patrón. | incorrecto | cumple |

<details><summary>Formulación de referencia</summary>

$D=\{1,\ldots,7\}$ enumera lunes a domingo. $a_{ds}=1$ si el patrón que empieza el día $s$ trabaja el día $d$ dentro de un ciclo de siete días (cinco días consecutivos), y 0 en otro caso. $r_d$ es el mínimo diario, $c_s$ el costo por empleado y $H=45$ el máximo contratado. $x_s\in\mathbb Z_{\geq0}$ indica personas que inician en $s$.

$$
\min\sum_{s\in D}c_sx_s\quad\text{s.a.}\quad
\sum_{s\in D}a_{ds}x_s\geq r_d\ (d\in D),\quad
\sum_{s\in D}x_s\leq H,\quad x_s\in\mathbb Z_{\geq0}\ (s\in D).
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, necesitamos seguir estos pasos:

1) **Definición del Problema**:
   - Hay 7 patrones de inicio (lunes a viernes vs sábado/domingo).
   - Se requiere cubrir al menos 7 días laborables.
   - Coste por vendedor:
     - $500 por día de lunes a viernes.
     - $550 por día de sábado/domingo.
   - Máximo número de vendedores: 45.

2) **Análisis de Datos**:
   - Mínimos de vendedores por día: 14, 18, 20, 25, 30, 28, 22.
   - Costo por vendedor: $500 (lunes a viernes), $550 (sábado/domingo).

3) **Modelo Matemático**:
   - Definiremos variables como `x` para el número de vendedores que inician el día lunes a viernes y `y` para los que iniciaran el día sábado/domingo.
   - La ecuación general sería: `500(x + y) = 45`.

4) **Restricciones**:
   - Total de vendedores: `x + y <= 45`.
   - Algunos mínimos de vendedores: `min(x) >= 14`, `min(y) >= 18`, `min(x + y) >= 20`, `min(2 * x) >= 25`, `min(2 * y) >= 30`, `min(3 * x) >= 28`, `min(3 * y) >= 22`.

5) **Solución**:
   - Primero resolvemos la ecuación matemática básica: `x + y = 9`.
   - Luego aplicamos las restricciones de mínimos de vendedores.

6) **Implementación**:
   - Utilizaremos un programa de optimización lineal para resolver esta situación.

### Ejemplo de Implementación

ˋˋˋpython
from scipy.optimize import linprog

# Coeficientes de la función objetivo
c = [-500, -550]

# Restricciones
A_eq = [[1, 1], [1, 0], [0, 1]]  # x + y = 9
b_eq = [45]  # Máximo 45 vendedores

# Mínimos de vendedores
A_ineq = [[-1, 1], [-1, 0], [0, -1], [-1, 0], [0, -1], [0, -1], [-1, 0]]
b_ineq = [14, 18, 20, 25, 30, 28, 22]

# Resolver el problema
res = linprog(c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ineq, b_ub=b_ineq)

print("Número de vendedores:", int(res.x[0]), "vendedores lunes a viernes")
print("Número de vendedores:", int(res.x[1]), "vendedores sábado/domingo")
ˋˋˋ

Este código utiliza `scipy.optimize.linprog` para resolver el problema de optimización lineal. Los parámetros `c`, `A_eq`, `b_eq`, `A_ineq`, y `b_ineq` se utilizan para definir la función objetivo y las restricciones del problema.

El resultado proporcionará el número mínimo de vendedores necesarios para cumplir con todos los requisitos y minimizar el costo semanal.
```

</details>

**QLoRA — 5.00/5** (decisiones 5.0, objetivo 5.0, restricciones 5.0, álgebra 5.0, generalización 5.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(D\): días de la semana.
\(K\): patrones de inicio.

Parámetros:
\(m_d\): mínimo de vendedores requeridos el día \(d\).
\(c_k\): costo de un vendedor con patrón \(k\).
\(a_{dk}\in\{0,1\}\): vale 1 si el patrón \(k\) trabaja el día \(d\).

Variables de decisión:
\(x_k\in\mathbb Z_{\ge0}\): número de vendedores asignados al patrón \(k\).

Función objetivo:
\[
\min \sum_{k\in K}c_kx_k
\]

Restricciones:
\[
\sum_{k\in K}a_{dk}x_k\ge m_d \qquad \forall d\in D
\]
```

</details>

---

## opt_06

### Dos alimentos y existencias compartidas

Tipo: LP · Dificultad: media · Baseline **2.60** → QLoRA **1.45** (empeora)

**Enunciado**

> Un molino prepara dos fórmulas de alimento, una para ganado y otra para aves, usando maíz, soya y harina mineral. La producción se mezcla en kilogramos y puede fraccionarse. Las dos fórmulas compiten por las mismas existencias de ingredientes, por lo que no basta con optimizar cada receta por separado. Los requisitos de proteína y fibra se evalúan como proporciones del peso final de cada fórmula.
>
> El molino debe entregar exactamente 80 kg de alimento para ganado y 60 kg de alimento para aves. Hay disponibles 70 kg de maíz, 90 de soya y 100 de harina mineral. Sus costos por kilogramo son 4, 3 y 2, respectivamente. El maíz aporta 30 % de proteína y 5 % de fibra; la soya, 20 % de proteína y 10 % de fibra; y la harina mineral, 10 % de proteína y 2 % de fibra. El alimento para ganado requiere al menos 20 % de proteína y como máximo 8 % de fibra. El alimento para aves requiere al menos 16 % de proteína y como máximo 7 % de fibra.
>
> Se solicita decidir cuánto de cada ingrediente incorporar a cada alimento para minimizar el costo total de los 140 kg entregados. El modelo debe controlar por separado la calidad de las dos fórmulas y, a la vez, limitar el consumo agregado de cada ingrediente.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo total de ingredientes. | cumple | cumple |
| R2 | constraint | Cantidad exacta requerida de cada alimento. | incorrecto | incorrecto |
| R3 | constraint | Inventario agregado de cada ingrediente compartido entre alimentos. | incorrecto | incorrecto |
| R4 | constraint | Proteína mínima por alimento. | cumple | incorrecto |
| R5 | constraint | Fibra máxima por alimento. | cumple | incorrecto |
| R6 | domain | Variables continuas no negativas por ingrediente y alimento. | cumple | cumple |

<details><summary>Formulación de referencia</summary>

$I=\{M,S,H\}$ son maíz, soya y harina mineral; $P=\{G,A\}$ son alimentos para ganado y aves. $c_i$ es costo, $s_i$ inventario, $D_p$ pedido, $v_i$ proporción de proteína, $f_i$ de fibra, $V_p$ proteína mínima y $F_p$ fibra máxima. $x_{ip}\geq0$ es masa del ingrediente $i$ destinada al alimento $p$.

$$
\min\sum_{i\in I}\sum_{p\in P}c_ix_{ip}\quad\text{s.a.}\quad
\sum_i x_{ip}=D_p\ (p\in P),\quad
\sum_p x_{ip}\leq s_i\ (i\in I),\quad
\sum_i v_ix_{ip}\geq V_pD_p\ (p\in P),\quad
\sum_i f_ix_{ip}\leq F_pD_p\ (p\in P),\quad x_{ip}\geq0.
$$

</details>

**Baseline — 2.60/5** (decisiones 2.0, objetivo 5.0, restricciones 2.0, álgebra 2.0, generalización 2.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un método matemático llamado "modelización de problemas de programación lineal" (PPL). Esta técnica nos permitirá encontrar una solución óptima que cumpla con todos los requisitos establecidos.

### Paso 1: Definición de Variables

Primero, definiremos las variables:

- \( x_1 \): Kilogramos de maíz para ganado.
- \( x_2 \): Kilogramos de maíz para aves.
- \( x_3 \): Kilogramos de soya para ganado.
- \( x_4 \): Kilogramos de soya para aves.
- \( x_5 \): Kilogramos de harina mineral para ganado.
- \( x_6 \): Kilogramos de harina mineral para aves.

### Paso 2: Formulación de Ecuaciones

Seguimos formulando las ecuaciones basadas en los requisitos:

1. **Producción**:
   - Para ganado: \( x_1 + x_3 = 80 \)
   - Para aves: \( x_2 + x_4 = 60 \)

2. **Consumo de Ingredientes**:
   - Maíz: \( x_1 + x_3 \leq 70 \)
   - Soya: \( x_2 + x_4 \leq 90 \)
   - Harina Mineral: \( x_5 + x_6 \leq 100 \)

3. **Costo Total**:
   - Costo de maíz: \( 4x_1 + 3x_2 + 2x_5 \)
   - Costo de soya: \( 3x_3 + 2x_4 + 2x_6 \)
   - Costo de harina mineral: \( 2x_5 + 2x_6 \)

   Necesitamos minimizar el costo total: \( C = 4x_1 + 3x_2 + 2x_3 + 2x_4 + 2x_5 + 2x_6 \)

### Paso 3: Implementación de Restricciones

Asumiendo que queremos maximizar la cantidad de cada ingrediente utilizada, las restricciones serían:

1. **Restricción de Proteínas**:
   - Ganado: \( 0.3x_1 + 0.2x_3 \geq 0.2 \times 80 \)
   - Aves: \( 0.2x_2 + 0.1x_4 \geq 0.16 \times 60 \)

2. **Restricción de Fibra**:
   - Ganado: \( 0.05x_1 + 0.1x_3 \leq 0.08 \times 80 \)
   - Aves: \( 0.1x_2 + 0.02x_4 \leq 0.07 \times 60 \)

### Paso 4: Resolución del Problema

Usaremos un programa de optimización lineal para resolver este sistema de ecuaciones y restricciones. Aquí te proporciono un ejemplo básico de cómo podrías hacerlo utilizando Python y la biblioteca `scipy.optimize.linprog`:

ˋˋˋpython
from scipy.optimize import linprog

# Coeficientes del costo
costs = [4, 3, 2, 2, 2, 2]

# Coeficientes de las restricciones
constraints = [
    [-1, -1, 1, 1, 0, 0], # Maíz para ganado
    [-1, 0, 0, 1, 1, 0], # Soya para ganado
    [0, -1, 0, 0, 1, 1]   # Harina mineral para ganado
]

# Restricciones de proteínas
protein_constraints = [
    [0.3, 0.2, 0, 0, 0, 0], # Ganado
    [0, 0.2, 0.1, 0, 0, 0]  # Aves
]

# Restricciones de fibra
fiber_constraints = [
    [0.05, 0.1, 0, 0, 0, 0], # Ganado
    [0, 0.1, 0.02, 0, 0, 0]   # Aves
]

# Función objetivo (minimizar el costo total)
fun = lambda x: sum(costs[i] * x[i] for i in range(len(x)))

# Solución inicial
bnds = [(0, None), (0, None)] * len(constraints) + [(0, None)]

# Ejecutar el algoritmo
result = linprog(-costs, A_ub=constraints, b_ub=bounds, bounds=bnds, method='highs')

print("Optimal solution:")
for i in range(len(result.x)):
    print(f"x{i+1} = {result.x[i]}")
ˋˋˋ

Este código genera una solución que minimiza el costo total mientras cumplen todas las restricciones dadas. Recuerda ajustar los coeficientes según tus necesidades específicas.

### Consideraciones Adicionales

- **Limitaciones de Ingrediente**: Si hay más restricc
```

</details>

**QLoRA — 1.45/5** (decisiones 2.0, objetivo 5.0, restricciones 0.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): ingredientes.
\(P\): proteínas.
\(F\): fibras.
\(C\): recursos.
\(K\): tipos de alimentos.

Parámetros:
\(p_i\): precio del unidad del ingrediente \(i\in I\).
\(c_{ki}\): requerimiento del ingrediente \(i\) de la formula \(k\in K\).
\(a_{ki}\): disponibilidad del ingrediente \(i\) de la formula \(k\).
\(u_k\): requisito mínimo de proteínas de la formula \(k\).
\(v_k\): requisito máximo de fibras de la formula \(k\).

Variables de decisión:
\(x_{ik}\ge0\): cantidad del ingrediente \(i\) utilizado en la formula \(k\).

Función objetivo:
\[
\min \sum_{i\in I}\sum_{k\in K}p_i x_{ik}
\]

Restricciones:
\[
\sum_{i\in I}x_{ik}=80 \qquad \forall k\in K
\]
\[
\sum_{i\in I}c_{ki}x_{ik}\le60 \qquad \forall k\in K
\]
\[
\frac{\sum_{i\in I}a_{ki}x_{ik}}{\sum_{i\in I}p_i x_{ik}}\ge u_k \qquad \forall k\in K
\]
\[
\frac{\sum_{i\in I}a_{ki}x_{ik}}{\sum_{i\in I}p_i x_{ik}}\le v_k \qquad \forall k\in K
\]
\[
\sum_{k\in K}x_{ik}\le70,\qquad \sum_{k\in K}x_{ik}\le90,\qquad \sum_{k\in K}x_{ik}\le100 \qquad \forall i\in I
\]
```

</details>

Observación del juez sobre QLoRA: Restricciones de proteína y fibra están mal formuladas (usando parámetros no definidos y con lógica incorrecta). Restricciones de inventario son incorrectas (no limitan el uso por ingrediente, sino que suman sobre alimentos). Restricciones de cantidad exacta de alimento están mal definidas (usando parámetros no definidos y no reflejan los 80 kg y 60 kg requeridos).

---

## opt_07

### Portafolio con desembolsos por año

Tipo: BIP · Dificultad: baja · Baseline **0.00** → QLoRA **0.80** (mejora)

**Enunciado**

> Una empresa evalúa cuatro proyectos indivisibles, A, B, C y D, que podrían ejecutarse durante un horizonte de tres años. Para seleccionar un proyecto es necesario comprometer todos sus desembolsos futuros; no se permite ejecutar solo una parte. La empresa dispone de presupuestos separados para los años 1, 2 y 3. Los beneficios estimados corresponden al valor presente de los ingresos atribuibles a cada proyecto y sirven para comparar el portafolio.
>
> El proyecto A requiere desembolsos de 40, 10 y 0 en los años 1, 2 y 3 y entrega un beneficio de 80. B requiere 20, 30 y 5 y entrega 70. C requiere 0, 35 y 20 y entrega 75. D requiere 15, 0 y 30 y entrega 60. Los presupuestos disponibles son 70 en el año 1, 60 en el 2 y 50 en el 3. El proyecto C solo puede ejecutarse si también se selecciona A porque utilizará su infraestructura; B y D utilizan el mismo equipo técnico y no pueden coexistir.
>
> Se desea seleccionar el conjunto de proyectos que maximice la suma de beneficios presentes, respetando cada presupuesto anual y ambas relaciones lógicas. No debe sustituirse la restricción de presupuesto de cada año por una sola suma para todo el horizonte.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar beneficio presente total de proyectos seleccionados. | ausente | incorrecto |
| R2 | constraint | Presupuesto separado para cada año. | ausente | cumple |
| R3 | constraint | Precedencia lógica C implica A. | ausente | incorrecto |
| R4 | constraint | Incompatibilidad entre B y D. | ausente | incorrecto |
| R5 | domain | Variables binarias de selección. | ausente | cumple |

<details><summary>Formulación de referencia</summary>

$I=\{A,B,C,D\}$, $T=\{1,2,3\}$. $a_{ti}$ es desembolso del proyecto $i$ en el año $t$, $b_t$ presupuesto del año y $v_i$ beneficio presente. $y_i\in\{0,1\}$ indica selección.

$$
\max\sum_{i\in I}v_iy_i\quad\text{s.a.}\quad
\sum_{i\in I}a_{ti}y_i\leq b_t\ (t\in T),\quad
y_C\leq y_A,\quad y_B+y_D\leq1,\quad y_i\in\{0,1\}\ (i\in I).
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, vamos a seguir estos pasos:

1) **Definición del Problema**: Se necesita elegir un conjunto de proyectos que maximice la suma de beneficios presentes, teniendo en cuenta las limitaciones de presupuesto anual y las relaciones entre los proyectos.

2) **Restricciones**:
   - Presupuesto anual:
     - Año 1: $70
     - Año 2: $60
     - Año 3: $50
   - Relación entre proyectos:
     - C solo puede ejecutarse si A está seleccionado.
     - B y D no pueden coexistir.

3) **Beneficios Presentes**:
   - A: $80 (V.P. = 80)
   - B: $70 (V.P. = 70)
   - C: $75 (V.P. = 75)
   - D: $60 (V.P. = 60)

4) **Evaluación de Posibles Soluciones**:

### Primera solución posible:
- Año 1: A ($70)
- Año 2: B ($60)
- Año 3: C ($50)

Suma total de beneficios presentes: $70 + $60 + $50 = $180

### Segunda solución posible:
- Año 1: A ($70)
- Año 2: D ($60)
- Año 3: B ($50)

Suma total de beneficios presentes: $70 + $60 + $50 = $180

### Tercera solución posible:
- Año 1: B ($60)
- Año 2: A ($70)
- Año 3: C ($50)

Suma total de beneficios presentes: $60 + $70 + $50 = $180

### Cuarta solución posible:
- Año 1: D ($60)
- Año 2: B ($50)
- Año 3: C ($40)

Suma total de beneficios presentes: $60 + $50 + $40 = $150

### Quinta solución posible:
- Año 1: C ($50)
- Año 2: B ($40)
- Año 3: D ($30)

Suma total de beneficios presentes: $50 + $40 + $30 = $120

### Sexta solución posible:
- Año 1: C ($50)
- Año 2: D ($30)
- Año 3: B ($20)

Suma total de beneficios presentes: $50 + $30 + $20 = $100

### Sétima solución posible:
- Año 1: B ($40)
- Año 2: D ($30)
- Año 3: A ($10)

Suma total de beneficios presentes: $40 + $30 + $10 = $80

### Osea, la mejor solución sería la primera opción con sumatoria de $180, ya que todas las soluciones anteriores tienen un valor inferior o igual a esa suma.

Por lo tanto, la solución óptima es elegir el proyecto A en el año 1, el proyecto B en el año 2, y el proyecto C en el año 3. Esto maximiza la suma de beneficios presentes dentro de las limitaciones de presupuesto anual y las relaciones entre los proyectos.
```

</details>

**QLoRA — 0.80/5** (decisiones 2.0, objetivo 0.0, restricciones 1.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): proyectos.
\(T\): períodos o años.

Parámetros:
\(c_i^t\): costo del proyecto \(i\) en el período \(t\).
\(v_i^t\): beneficio del proyecto \(i\) en el período \(t\).
\(B_t\): presupuesto disponible en el período \(t\).

Variables de decisión:
\(x_i\in\{0,1\}\): vale 1 si se selecciona el proyecto \(i\).

Función objetivo:
\[
\max \sum_{i\in I}\sum_{t\in T}v_i^t x_i
\]

Restricciones:
\[
\sum_{i\in I}c_i^tx_i\le B_t \qquad \forall t\in T
\]
\[
x_a+x_b\le x_c \qquad \forall(a,b)\in\{(1,3),(2,3)\}
\]
```

</details>

Observación del juez sobre QLoRA: La función objetivo está incorrecta: suma de beneficios por período en lugar de valor presente total. Las restricciones lógicas están incorrectas o ausentes (precedencia C→A e incompatibilidad B y D no modeladas correctamente).

---

## opt_08

### Asignación de jugadores a posiciones

Tipo: BIP · Dificultad: media · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Un entrenador debe elegir cinco titulares para cubrir las posiciones de arquero, defensa, mediocampo, atacante y extremo. Tiene siete jugadores disponibles, P1 a P7. Cada posición debe ser ocupada exactamente por un jugador y una persona no puede ocupar dos posiciones. Las evaluaciones disponibles solo corresponden a combinaciones para las que el jugador está habilitado; cualquier otra asignación está prohibida.
>
> Para arquero son elegibles P1 y P2, con puntajes 8 y 7. Para defensa son elegibles P2, P3 y P4, con puntajes 7, 9 y 6. Para mediocampo pueden jugar P3, P4 y P5, con puntajes 8, 7 y 9. Para atacante pueden jugar P4, P5 y P6, con puntajes 8, 7 y 10. Para extremo son elegibles P5, P6 y P7, con puntajes 8, 9 y 7. Los jugadores formados en las divisiones locales son P1, P3, P5 y P7. El acuerdo con la institución exige que al menos dos de los cinco titulares provengan de ese grupo.
>
> El entrenador quiere maximizar la suma de puntajes de adecuación a las posiciones efectivamente cubiertas. Debe decidir tanto quién juega como en qué posición, garantizar la cuota de formación local y evitar asignaciones fuera de las listas de elegibilidad. Los jugadores no elegidos quedan en reserva.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar puntaje total de adecuación. | ausente | incorrecto |
| R2 | constraint | Cada posición cubierta exactamente una vez. | ausente | incorrecto |
| R3 | constraint | Cada jugador en a lo sumo una posición. | ausente | incorrecto |
| R4 | constraint | Solo parejas jugador-posicion elegibles. | ausente | incorrecto |
| R5 | constraint | Al menos dos titulares de formación local. | ausente | incorrecto |
| R6 | domain | Variables binarias de asignación. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$P=\{P1,\ldots,P7\}$ son jugadores, $R=\{G,D,M,A,E\}$ posiciones y $\mathcal E\subseteq P\times R$ parejas elegibles descritas en el enunciado. $s_{pr}$ es puntaje de la pareja y $L=\{P1,P3,P5,P7\}$ jugadores de formación local. $x_{pr}\in\{0,1\}$ indica asignación para $(p,r)\in\mathcal E$.

$$
\max\sum_{(p,r)\in\mathcal E}s_{pr}x_{pr}\quad\text{s.a.}\quad
\sum_{p:(p,r)\in\mathcal E}x_{pr}=1\ (r\in R),\quad
\sum_{r:(p,r)\in\mathcal E}x_{pr}\leq1\ (p\in P),\quad
\sum_{p\in L}\sum_{r:(p,r)\in\mathcal E}x_{pr}\geq2,\quad x_{pr}\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, primero debemos identificar las opciones válidas para cada posición basándonos en las restricciones dadas:

1. **Arquero**: P1 (8) o P2 (7)
   - Si seleccionamos P1, necesitamos elegir tres jugadores más.
   - Si seleccionamos P2, necesitamos elegir cuatro jugadores más.

2. **Defensa**: P2 (7), P3 (9), o P4 (6)
   - Si seleccionamos P2, necesitamos elegir dos jugadores más.
   - Si seleccionamos P3, necesitamos elegir uno jugador más.
   - Si seleccionamos P4, necesitamos elegir dos jugadores más.

3. **Mediocampo**: P3 (8), P4 (7), o P5 (9)
   - Si seleccionamos P3, necesitamos elegir dos jugadores más.
   - Si seleccionamos P4, necesitamos elegir dos jugadores más.
   - Si seleccionamos P5, necesitamos elegir uno jugador más.

4. **Atacante**: P4 (8), P5 (7), o P6 (10)
   - Si seleccionamos P4, necesitamos elegir dos jugadores más.
   - Si seleccionamos P5, necesitamos elegir dos jugadores más.
   - Si seleccionamos P6, necesitamos elegir uno jugador más.

5. **Extremo**: P5 (8), P6 (9), o P7 (7)
   - Si seleccionamos P5, necesitamos elegir dos jugadores más.
   - Si seleccionamos P6, necesitamos elegir dos jugadores más.
   - Si seleccionamos P7, necesitamos elegir uno jugador más.

Ahora, vamos a considerar todas las combinaciones posibles y evaluarlas según el criterio de maximizar la suma de puntajes de adecuación a las posiciones efectivamente cubiertas, asegurando que al menos dos de los cinco titulares provengan del grupo de formación local (P1, P3, P5, P7).

### Combinaciones Posibles

#### Arquero: P1, Defensa: P2, Mediocampo: P3, Atacante: P4, Extremo: P5
- Suma de puntajes: 8 + 7 + 9 + 8 + 8 = 40
- Formación Local: P1, P3, P5 (3 jugadores)

#### Arquero: P1, Defensa: P2, Mediocampo: P4, Atacante: P5, Extremo: P6
- Suma de puntajes: 8 + 7 + 7 + 7 + 9 = 46
- Formación Local: P1, P4, P5, P6 (4 jugadores)

#### Arquero: P1, Defensa: P2, Mediocampo: P5, Atacante: P6, Extremo: P7
- Suma de puntajes: 8 + 7 + 9 + 7 + 7 = 48
- Formación Local: P1, P5, P6, P7 (4 jugadores)

#### Arquero: P2, Defensa: P3, Mediocampo: P4, Atacante: P5, Extremo: P6
- Suma de puntajes: 7 + 9 + 7 + 7 + 9 = 40
- Formación Local: P2, P3, P4, P5, P6 (5 jugadores)

#### Arquero: P2, Defensa: P3, Mediocampo: P5, Atacante: P6, Extremo: P7
- Suma de puntajes: 7 + 9 + 9 + 7 + 7 = 40
- Formación Local: P2, P3, P5, P6, P7 (5 jugadores)

#### Arquero: P2, Defensa: P4, Mediocampo: P5, Atacante: P6, Extremo: P7
- Suma de puntajes: 7 + 6 + 9 + 7 + 7 = 36
- Formación Local: P2, P4, P5, P6, P7 (5 jugadores)

#### Arquero: P2, Defensa: P4, Mediocampo: P6, Atacante: P7, Extremo: P5
- Suma de puntajes: 7 + 6 + 7 + 7 + 8 = 35
- Formación Local: P2, P4, P6, P7, P5 (5 jugadores)

#### Arquero: P2, Defensa: P5, Mediocampo: P6, Atacante: P7, Extremo: P3
- Suma de puntajes: 7 + 6 + 9 + 7 + 8 = 45
- Formación Local: P2, P5, P6, P7, P3 (5 jugadores)

#### Arquero: P2, Defensa: P5, Mediocampo: P7, Atacante: P6, Extremo: P3
- Suma de puntajes: 7 + 6 + 7 + 7 + 8 = 45
-
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(G\): jugadores.
\(P\): posiciones.
\(S\subseteq G\): jugadores seleccionables.
\(A\): agrupamiento de posiciones: arquero, defensa, mediocampo, atacante, extremo.

Parámetros:
\(w_g\): puntaje del jugador \(g\).
\(a_{sg}\in\{0,1\}\): vale 1 si el jugador \(g\) está habilitado para la posición \(s\).

Variables de decisión:
\(x_g\in S\): posición donde juega el jugador \(g\).

Función objetivo:
\[
\max \sum_{g\in G}w_gx_g
\]

Restricciones:
\[
\sum_{g\in S}a_{sg}x_g=1 \qquad \forall s\in S
\]
\[
\sum_{g\in S}a_{gs}x_g\le1 \qquad \forall g\in S,\ \forall s\notin S
\]
\[
x_g\in S \qquad \forall g\in S
\]
\[
|S|\ge2
\]
```

</details>

Observación del juez sobre QLoRA: La formulación no representa correctamente el problema. La variable de decisión está definida de forma incorrecta (no es una variable binaria de asignación jugador-posición), la función objetivo no considera el puntaje de las asignaciones elegibles, y las restricciones no reflejan las condiciones de elegibilidad, asignación única por posición, asignación única por jugador o la cuota de formación local.

---

## opt_09

### Desarrollo habitacional con cuota social

Tipo: IP · Dificultad: media · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Una constructora planifica viviendas de tres tipos: casas, departamentos y condominios. Cada tipo puede edificarse como unidad de precio protegido o como unidad estándar. Las cantidades deben ser enteras y pueden dejarse recursos sin utilizar. Un convenio público exige que al menos una cuarta parte de todas las viviendas construidas corresponda a la categoría de precio protegido, independientemente del tipo físico elegido.
>
> Una casa ocupa 120 m², cuesta 90 unidades monetarias de construcción y deja un margen de 20 si es protegida o 45 si es estándar. Un departamento ocupa 70 m², cuesta 65 y deja márgenes de 15 y 35, respectivamente. Un condominio ocupa 100 m², cuesta 110 y deja márgenes de 25 y 50. El terreno admite como máximo 10.000 m² edificados y el presupuesto de construcción es 9.000. Por permisos urbanísticos, pueden edificarse a lo sumo 50 casas, 100 departamentos y 30 condominios. La iniciativa debe contemplar al menos 20 casas y 80 viviendas en total.
>
> Se desea decidir cuántas unidades construir de cada combinación de tipo y categoría para maximizar el margen total. La cuota protegida debe expresarse respecto del total de viviendas realmente construido y los costos de construcción deben imputarse al presupuesto, sin volver a descontarlos de los márgenes ya informados.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar margen total de viviendas por tipo y categoría. | ausente | incorrecto |
| R2 | constraint | Restricciones de área y presupuesto de construcción. | ausente | incorrecto |
| R3 | constraint | Máximos por tipo físico. | ausente | incorrecto |
| R4 | constraint | Mínimo de casas y mínimo total de viviendas. | ausente | incorrecto |
| R5 | constraint | Al menos 25% del total construido debe ser protegido. | ausente | incorrecto |
| R6 | domain | Variables enteras no negativas. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$I=\{\text{casa, departamento, condominio}\}$, $K=\{P,E\}$ categorías protegida y estándar. $a_i$ área, $c_i$ costo de construcción, $m_{ik}$ margen y $u_i$ máximo por tipo. $x_{ik}\in\mathbb Z_{\geq0}$ es número construido.

$$
\max\sum_{i\in I}\sum_{k\in K}m_{ik}x_{ik}\quad\text{s.a.}\quad
\sum_{i,k}a_ix_{ik}\leq10000,\quad
\sum_{i,k}c_ix_{ik}\leq9000,\quad
\sum_{i,k}x_{ik}\geq80,\quad
\sum_kx_{\text{casa},k}\geq20,\quad
\sum_kx_{ik}\leq u_i\ (i\in I),\quad
4\sum_i x_{iP}\geq\sum_{i,k}x_{ik},\quad x_{ik}\in\mathbb Z_{\geq0}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, vamos a seguir estos pasos:

1) Definimos variables:
   - x = número de casas protegidas
   - y = número de casas estándar
   - z = número de departamentos protegidos
   - w = número de departamentos estándar
   - t = número de condominios protegidos
   - u = número de condominios estándar

2) Creamos ecuaciones basadas en las restricciones dadas:
   - Total de viviendas: x + y + z + w + t + u >= 20 (al menos 20 casas)
   - Total de viviendas totales: x + y + z + w + t + u <= 50 (50 casas)
   - Total de departamentos: z + w + t <= 100 (100 departamentos)
   - Total de condominios: t + u <= 30 (30 condominios)
   - Presupuesto: 90x + 65y + 110z + 65w + 110t + 110u <= 9000 (presupuesto de 9000)

3) Maximizamos el margen total:
   Margen total = 20 * 20 + 15 * 15 + 15 * 15 + 25 * 25 + 50 * 50 + 25 * 25
                = 400 + 225 + 225 + 625 + 2500 + 625
                = 4000

4) Resolvemos el sistema de ecuaciones con Python usando la librería PuLP:

ˋˋˋpython
from pulp import *

# Crear el modelo
prob = LpProblem("Maximize_Vivienda", LpMaximize)

# Variables
x = LpVariable('x', lowBound=0, cat='Integer')
y = LpVariable('y', lowBound=0, cat='Integer')
z = LpVariable('z', lowBound=0, cat='Integer')
w = LpVariable('w', lowBound=0, cat='Integer')
t = LpVariable('t', lowBound=0, cat='Integer')
u = LpVariable('u', lowBound=0, cat='Integer')

# Objetivo
prob += 20*20 + 15*15 + 15*15 + 25*25 + 50*50 + 25*25, "Margen_total"

# Restricciones
prob += x + y + z + w + t + u >= 20, "Minutos_casa"
prob += x + y + z + w + t + u <= 50, "Total_casas"
prob += z + w + t <= 100, "Departamentos"
prob += t + u <= 30, "Condominios"
prob += 90*x + 65*y + 110*z + 65*w + 110*t + 110*u <= 9000, "Presupuesto"

# Resolver el modelo
status = prob.solve()

# Imprimir resultados
print(f"Status: {LpStatus[status]}")
for v in prob.variables():
    print(v.name, "=", v.varValue)
ˋˋˋ

Este código resuelve el problema utilizando la biblioteca PuLP de Python. Al ejecutarlo, obtendremos el valor óptimo para cada variable y el status del problema.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): tipos de viviendas.
\(C\): categorías de precios.
\(K\): tipos físicos disponibles.

Parámetros:
\(a_i\): superficie requerida por una vivienda de tipo \(i\).
\(c_i\): costo unitario de una vivienda de tipo \(i\).
\(d_{ik}\): margen disponible de la categoría \(k\) de la vivienda de tipo \(i\).
\(B\): superficie disponible.
\(U\): presupuesto disponible.
\(L_i\): límite de número de viviendas de tipo \(i\).

Variables de decisión:
\(x_{ik}\in\{0,1\}\): vale 1 si se construye una vivienda de tipo \(i\) y categoría \(k\).
\(y_i\ge L_i x_{ik}\): número real de viviendas de tipo \(i\) construidas.

Función objetivo:
\[
\max \sum_{i\in I}\sum_{k\in K}d_{ik}x_{ik}
\]

Restricciones:
\[
\sum_{i\in I}x_{ik}\le L_i \qquad \forall k\in K
\]
\[
\sum_{i\in I}a_ix_{ik}\le B
\]
\[
\sum_{i\in I}cx_{ik}\le U
\]
\[
x_{ik}\le y_i \qquad \forall i\in I,\ \forall k\in K
\]
```

</details>

Observación del juez sobre QLoRA: Variables de decisión definidas incorrectamente (x_{ik} binarias y y_i como cantidad, lo cual no se alinea con el problema). La función objetivo no considera la cantidad de viviendas construidas, solo si se construye o no. Las restricciones de área y presupuesto están mal formuladas (usando x_{ik} en lugar de y_i). La restricción de cuota protegida no se incluye. Dominios de variables incorrectos (x_{ik} ∈ {0,1} en lugar de enteros no negativos).

---

## opt_10

### Selección de exploraciones con conflictos

Tipo: BIP · Dificultad: media · Baseline **0.00** → QLoRA **1.60** (mejora)

**Enunciado**

> Una empresa evaluará exactamente cuatro emplazamientos de exploración entre ocho sitios candidatos, S1 a S8. La exploración de cada sitio es una decisión indivisible y su costo se paga una sola vez. Además del límite numérico de proyectos, ciertas combinaciones están prohibidas por interferencias técnicas y la empresa quiere representar distintas zonas geográficas en su plan final.
>
> Los costos de S1 a S8 son, respectivamente, 14, 18, 16, 20, 17, 13, 22 y 15 unidades monetarias. Si se exploran simultáneamente S1 y S7, no se puede explorar S8; elegir solo uno de los dos no impide S8. Explorar S3 impide S5, y explorar S4 también impide S5. Se debe seleccionar por lo menos uno entre S2 y S6 para cubrir la zona interior. De los sitios costeros S1, S3, S5 y S7 se permite elegir como máximo dos, debido a la capacidad de supervisión del equipo ambiental.
>
> La empresa necesita identificar los cuatro lugares de menor costo que satisfagan todas las reglas. Distinga la condición que se activa por elegir conjuntamente S1 y S7 de las dos incompatibilidades individuales con S5; una traducción incorrecta de ese «y» cambiaría el conjunto de soluciones factibles.
>
> La representación geográfica es una condición adicional al presupuesto: un sitio barato no puede reemplazar por sí solo la presencia obligatoria de una exploración interior, y el cupo costero cuenta sitios seleccionados, no unidades monetarias.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo de exactamente cuatro sitios seleccionados. | ausente | cumple |
| R2 | constraint | Si S1, S7 y S8 quedarían seleccionados simultáneamente, prohibir esa combinación. | ausente | incorrecto |
| R3 | constraint | Incompatibilidad S3-S5 e incompatibilidad S4-S5. | ausente | incorrecto |
| R4 | constraint | Seleccionar al menos uno entre S2 y S6. | ausente | incorrecto |
| R5 | constraint | Como máximo dos sitios costeros entre S1,S3,S5,S7. | ausente | incorrecto |
| R6 | domain | Variables binarias. | cumple | cumple |

<details><summary>Formulación de referencia</summary>

$I=\{1,\ldots,8\}$ son sitios, $c_i$ costos y $y_i\in\{0,1\}$ decisiones de exploración.

$$
\min\sum_{i\in I}c_iy_i\quad\text{s.a.}\quad
\sum_{i\in I}y_i=4,\quad
y_1+y_7+y_8\leq2,\quad
y_3+y_5\leq1,\quad y_4+y_5\leq1,\quad
y_2+y_6\geq1,\quad
y_1+y_3+y_5+y_7\leq2,\quad y_i\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, necesitamos seguir varios pasos:

1) **Identificar las restricciones**:
   - No se pueden explorar S1 y S7 simultáneamente.
   - No se pueden explorar S3 ni S4 sin explorar S5.
   - No se pueden explorar S2 ni S6 sin explorar S5.
   - Solo se pueden explorar S1, S3, S5 o S7 si se permiten hasta dos sitios costeros.

2) **Ordenar los costos**: Los costos de los sitios son:
   - S1: 14
   - S2: 13
   - S3: 18
   - S4: 16
   - S5: 17
   - S6: 20
   - S7: 15
   - S8: 22

3) **Elegir los sitios**:
   - Primero, debemos considerar los sitios costeros (S1, S3, S5, S7).
   - Luego, elegimos uno más dentro de la zona interior (S2, S6).

4) **Considerar las restricciones**:
   - No podemos explorar S1 y S7 simultáneamente.
   - No podemos explorar S3 ni S4 sin explorar S5.
   - No podemos explorar S2 ni S6 sin explorar S5.
   - Solo podemos explorar S1, S3, S5 o S7 si se permiten hasta dos sitios costeros.

5) **Resolver el problema**:
   - Debido a las restricciones, la mejor solución sería explorar S1, S3, S5 y S7.
   - Esto cumple con todos los requisitos:
     - No se pueden explorar S1 y S7 simultáneamente.
     - No se pueden explorar S3 ni S4 sin explorar S5.
     - No se pueden explorar S2 ni S6 sin explorar S5.
     - Solo se pueden explorar S1, S3, S5 o S7 si se permiten hasta dos sitios costeros.

Por lo tanto, los cuatro lugares de menor costo que satisfacen todas las condiciones son S1, S3, S5 y S7.
```

</details>

**QLoRA — 1.60/5** (decisiones 2.0, objetivo 5.0, restricciones 0.0, álgebra 1.0, generalización 1.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(U\): sitios candidatos.
\(K\): restricciones numéricas.
\(A\): restricciones de interconjuntos.

Parámetros:
\(c_u\): costo unitario del sitio \(u\).
\(b_k\in\{0,1\}\): vale 1 si la exploración de \(u\) y de \(v\) no se puede hacer juntas.
\(u_a\le u_b\): vale 1 si \(u\) requiere más recursos que \(b\).

Variables de decisión:
\(x_u\in\{0,1\}\): vale 1 si se realiza la exploración del sitio \(u\).

Función objetivo:
\[
\min \sum_{u\in U}c_u x_u
\]

Restricciones:
\[
\sum_{u\in U}b_{ku}x_u\le1 \qquad \forall k\in K
\]
\[
\sum_{u\in U}u_ax_u\le u_b \qquad \forall b\in B,\ \forall u\in U
\]
\[
\sum_{u\in U}x_u\ge1
\]
\[
x_u+x_v\le1 \qquad \forall(u,v)\in A
\]
```

</details>

Observación del juez sobre QLoRA: Las restricciones no están correctamente formuladas ni identificadas. Las incompatibilidades (R2, R3, R4, R5) no se representan adecuadamente. Se usan conjuntos y parámetros no definidos en el enunciado, lo que hace que la formulación no sea específica del problema dado.

---

## opt_11

### Programa académico con matrículas fijas

Tipo: MILP/BIP · Dificultad: media · Baseline **0.00** → QLoRA **1.98** (mejora)

**Enunciado**

> Una institución organizará un programa ejecutivo que debe incluir exactamente un curso de cada una de seis áreas: finanzas, marketing, operaciones, datos, liderazgo e innovación. Puede contratar cursos en tres universidades, A, B y C. Inscribirse en una universidad implica pagar una matrícula fija una sola vez, aunque allí se tome más de un curso. Además, cada curso tiene un precio propio. Para facilitar los desplazamientos del grupo, el programa puede utilizar como máximo dos universidades.
>
> La universidad A ofrece finanzas, marketing, operaciones y datos, con precios respectivos de 25, 20, 22 y 28, y cobra matrícula de 50. B ofrece marketing, operaciones, liderazgo e innovación, con precios 18, 25, 24 y 30 y matrícula de 70. C ofrece finanzas, datos, liderazgo e innovación, con precios 27, 21, 20 y 26 y matrícula de 40. Una universidad que no ofrezca determinada área no puede impartirla para el programa. Todos los precios y matrículas se expresan en las mismas unidades monetarias.
>
> La institución necesita elegir la universidad que impartirá cada área y cuáles matrículas activar. Busca cubrir exactamente una vez cada una de las seis áreas al menor costo total de cursos y matrículas, respetando el límite de dos instituciones. El pago fijo debe vincularse a cualquier curso elegido en la universidad correspondiente.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo de cursos más matrículas fijas. | ausente | cumple |
| R2 | constraint | Cada área cubierta exactamente por una universidad elegible. | ausente | incorrecto |
| R3 | constraint | Vincular cada curso elegido con matrícula activa de esa universidad. | ausente | incorrecto |
| R4 | constraint | Usar como máximo dos universidades. | ausente | cumple |
| R5 | domain | Variables binarias de curso y activación; no permitir ofertas inexistentes. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$U=\{A,B,C\}$, $F$ son las seis áreas y $E\subseteq U\times F$ las ofertas disponibles. $c_{uf}$ es precio del curso y $T_u$ matrícula. $x_{uf}\in\{0,1\}$ indica selección del curso y $y_u\in\{0,1\}$ indica matrícula activa.

$$
\min\sum_{(u,f)\in E}c_{uf}x_{uf}+\sum_{u\in U}T_uy_u\quad\text{s.a.}\quad
\sum_{u:(u,f)\in E}x_{uf}=1\ (f\in F),\quad
x_{uf}\leq y_u\ ((u,f)\in E),\quad
y_u\leq\sum_{f:(u,f)\in E}x_{uf}\ (u\in U),\quad
\sum_u y_u\leq2,\quad x_{uf},y_u\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, necesitamos encontrar una combinación de universidades y materias que cumplan con los siguientes criterios:

1. Cubrir exactamente una materia por cada una de las seis áreas.
2. Usar exactamente dos universidades.
3. Minimizar el costo total de los cursos y matrículas.
4. Respetar el límite de dos instituciones.

Vamos a analizar todas las posibles combinaciones de universidades y materias:

**Universidad A (Finanzas, Marketing, Operaciones, Datos):**
- Finanzas: 25 + 27 = 52
- Marketing: 20 + 25 = 45
- Operaciones: 22 + 21 = 43
- Datos: 28 + 26 = 54

**Universidad B (Marketing, Operaciones, Liderazgo, Innovación):**
- Marketing: 18 + 25 = 43
- Operaciones: 24 + 21 = 45
- Liderazgo: 25 + 20 = 45
- Innovación: 30 + 20 = 50

**Universidad C (Finanzas, Datos, Liderazgo, Innovación):**
- Finanzas: 27 + 21 = 48
- Datos: 26 + 21 = 47
- Liderazgo: 20 + 20 = 40
- Innovación: 26 + 20 = 46

Ahora, vamos a combinar estas opciones para minimizar el costo total:

1. **Universidad A (Finanzas) + Universidad B (Operaciones, Liderazgo, Innovación):**
   - Finanzas: 25
   - Operaciones: 24
   - Liderazgo: 25
   - Innovación: 30
   Costo total: 25 + 24 + 25 + 30 = 104

2. **Universidad A (Datos) + Universidad B (Liderazgo, Innovación):**
   - Datos: 28
   - Liderazgo: 25
   - Innovación: 30
   Costo total: 28 + 25 + 30 = 83

3. **Universidad A (Operaciones) + Universidad C (Finanzas, Liderazgo, Innovación):**
   - Operaciones: 22
   - Finanzas: 27
   - Liderazgo: 20
   - Innovación: 20
   Costo total: 22 + 27 + 20 + 20 = 99

4. **Universidad B (Marketing) + Universidad C (Finanzas, Datos, Liderazgo):**
   - Marketing: 18
   - Finanzas: 27
   - Datos: 26
   - Liderazgo: 20
   Costo total: 18 + 27 + 26 + 20 = 91

5. **Universidad C (Finanzas) + Universidad B (Marketing, Liderazgo, Innovación):**
   - Finanzas: 27
   - Marketing: 18
   - Liderazgo: 25
   - Innovación: 30
   Costo total: 27 + 18 + 25 + 30 = 90

Conclusión:
El costo mínimo es de 83 unidades monetarias cuando se seleccionan los cursos de "Operaciones" en Universidad A y "Liderazgo" y "Innovación" en Universidad B.
```

</details>

**QLoRA — 1.98/5** (decisiones 0.0, objetivo 4.0, restricciones 1.6666666666666665, álgebra 2.0, generalización 2.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(U\): universidades.
\(A\): áreas de estudio.
\(C\): opciones de matrícula disponibles en cada universidad.

Parámetros:
\(p_{uc}\): costo unitario de un curso \(u\) en la universidad \(c\).
\(f_c\): costo fijo de matricularse en \(c\).

Variables de decisión:
\(y_u\in\{0,1\}\): vale 1 si se selecciona la universidad \(u\).
\(x_{uc}\in\{0,1\}\): vale 1 si se selecciona el curso \(u\) en la universidad \(c\).
\(z_c\in\{0,1\}\): vale 1 si se selecciona la matrícula \(c\).

Función objetivo:
\[
\min \sum_{u\in U}f_u y_u+\sum_{u\in U}\sum_{c\in C}p_{uc}x_{uc}
\]

Restricciones:
\[
\sum_{u\in U}x_{uc}=1 \qquad \forall c\in C
\]
\[
\sum_{c\in C}z_c=1
\]
\[
x_{uc}\le y_u z_c \qquad \forall u\in U,\ \forall c\in C
\]
```

</details>

Observación del juez sobre QLoRA: La variable z_c no está definida en el contexto del problema y no se relaciona con la matrícula de las universidades. La restricción de selección de exactamente una universidad por área está incorrectamente formulada. La vinculación entre cursos y matrículas no se modela correctamente.

---

## opt_12

### Reducción de vertimientos en un río

Tipo: MILP · Dificultad: media · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Tres plantas industriales descargan residuos en un río donde la autoridad controla la calidad del agua en tres puntos aguas abajo. Cada planta puede instalar un tratamiento local y reducir una cantidad de residuos, hasta su descarga máxima. La instalación de un tratamiento genera un costo fijo y, mientras opere, debe retirar al menos 10 unidades; además tiene un costo variable por unidad retirada. La mejora observada en cada punto resulta de sumar los efectos de los tratamientos activados.
>
> Las plantas 1, 2 y 3 descargan como máximo 50, 40 y 60 unidades y tienen costos fijos de 30, 40 y 25, con costos variables de 4, 5 y 3 por unidad retirada. Por cada unidad removida en las plantas 1, 2 y 3, las mejoras en el punto de control A son 1, 1 y 1; en B son 2, 0,5 y 1; y en C son 0,5, 2 y 1. La autoridad exige mejoras de al menos 50 en A, 55 en B y 45 en C. Ninguna planta puede retirar más residuos de los que descarga.
>
> La autoridad quiere encontrar el plan de menor costo que satisfaga simultáneamente los tres estándares. Se requiere decidir qué tratamientos instalar y cuánto reducir en cada planta, distinguiendo claramente el costo fijo de activación de los costos proporcionales y vinculando cada reducción a su instalación.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costos fijos de tratamiento más costos variables de remoción. | incorrecto | incorrecto |
| R2 | constraint | Cumplir mejora mínima en cada punto de control. | incorrecto | incorrecto |
| R3 | constraint | Remoción solo si el tratamiento está instalado. | incorrecto | ausente |
| R4 | constraint | Si se instala, remover al menos 10 y no más que la descarga máxima. | incorrecto | incorrecto |
| R5 | domain | Remoción continua no negativa y activación binaria. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$J=\{1,2,3\}$ son plantas y $I=\{A,B,C\}$ puntos de control. $p_j$ descarga máxima, $f_j$ costo fijo, $c_j$ costo variable, $a_{ij}$ mejora en $i$ por unidad removida en $j$ y $b_i$ mejora mínima. $x_j\geq0$ es cantidad removida y $y_j\in\{0,1\}$ indica instalación.

$$
\min\sum_{j\in J}(c_jx_j+f_jy_j)\quad\text{s.a.}\quad
\sum_{j\in J}a_{ij}x_j\geq b_i\ (i\in I),\quad
10y_j\leq x_j\leq p_jy_j\ (j\in J),\quad
x_j\geq0,\ y_j\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, necesitamos utilizar un método matemático para minimizar el costo total de los tratamientos mientras se cumplen todas las restricciones. Aquí hay una descripción detallada de cómo podemos proceder:

### Paso 1: Definición de Variables

- **x1**: Tratamiento de la planta 1 (si es aplicado o no)
- **x2**: Tratamiento de la planta 2 (si es aplicado o no)
- **x3**: Tratamiento de la planta 3 (si es aplicado o no)

### Paso 2: Formulación del Problema

El objetivo es minimizar el costo total:
\[ \text{Minimize} \quad Z = 30x_1 + 40x_2 + 25x_3 + c_{\text{costo}}(x_1) + c_{\text{costo}}(x_2) + c_{\text{costo}}(x_3) \]

Donde \(c_{\text{costo}}\) representa el costo variable por unidad retirada.

### Paso 3: Restricciones

#### Residuos Descargados
- Planta 1: \(50 - x_1 \leq 0\)
- Planta 2: \(40 - x_2 \leq 0\)
- Planta 3: \(60 - x_3 \leq 0\)

#### Mejoras Obtenidas
- Punto A: \(1 + 2x_1 + 0.5x_2 + 0.5x_3 \geq 50\)
- Punto B: \(1 + 0.5x_2 + x_3 \geq 55\)
- Punto C: \(0.5 + 2x_3 + x_1 \geq 45\)

#### Costo Fijo
- Si se aplica un tratamiento, se gasta un costo fijo específico para ese tratamiento.

### Paso 4: Implementación de la Solución

Primero, resolvemos las restricciones para obtener las cantidades mínimas de residuos que deben ser eliminadas:
- Planta 1: \(x_1 = 50\)
- Planta 2: \(x_2 = 40\)
- Planta 3: \(x_3 = 60\)

Luego, calculamos las mejoras obtenidas en cada punto:
- Punto A: \(1 + 2*50 + 0.5*40 + 0.5*60 = 1 + 100 + 20 + 30 = 151\)
- Punto B: \(1 + 0.5*40 + 60 = 1 + 20 + 60 = 81\)
- Punto C: \(0.5 + 2*60 + 50 = 0.5 + 120 + 50 = 170.5\)

Finalmente, calculamos el costo total:
\[ Z = 30*50 + 40*40 + 25*60 + 30*50 + 40*40 + 25*60 + 151 + 81 + 170.5 = 1500 + 1600 + 1500 + 151 + 81 + 170.5 = 6102.5 \]

### Conclusion

El costo mínimo para satisfacer todos los requisitos es **$6102.5**. Esto se logra si se instalan tratamientos en las siguientes condiciones:
- Planta 1: Tratamiento activado (Costo fijo: $30)
- Planta 2: Tratamiento activado (Costo fijo: $40)
- Planta 3: Tratamiento activado (Costo fijo: $25)

Estas acciones permiten que las tres plantas cumplan con sus respectivas limitaciones de residuos y mejoren los niveles de contaminación en los puntos de control A, B y C según lo especificado.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): plantas.
\(J\): puntos de medición.

Parámetros:
\(f_i\): costo fijo de instalar el tratamiento en \(i\).
\(c_{ij}\): costo unitario de retirar \(j\) de \(i\).
\(u_i\): capacidad máxima de la planta.
\(a_{ij}\): mejora obtenida en \(j\) de instalar el tratamiento en \(i\).

Variables de decisión:
\(y_i\in\{0,1\}\): vale 1 si se instala el tratamiento en \(i\).
\(x_{ij}\ge0\): cantidad de residuo retirado de \(j\) de \(i\).

Función objetivo:
\[
\min \sum_{i\in I}f_i y_i+\sum_{i\in I}\sum_{j\in J}c_{ij}x_{ij}
\]

Restricciones:
\[
\sum_{i\in I}x_{ij}\le u_i \qquad \forall j\in J
\]
\[
\sum_{j\in J}a_{ij}x_{ij}\ge u_i-50 \qquad \forall i\in I
\]
\[
\sum_{j\in J}a_{ij}x_{ij}\ge u_i-55 \qquad \forall i\in I
\]
\[
\sum_{j\in J}a_{ij}x_{ij}\ge u_i-45 \qquad \forall i\in I
\]
```

</details>

Observación del juez sobre QLoRA: La formulación presenta múltiples errores esenciales: conjuntos y parámetros mal definidos, variables decisionales incorrectas, restricciones lógicas inválidas y objetivo mal formulado. La formulación no representa el problema original de manera correcta.

---

## opt_13

### Camino de inspección obligatoria

Tipo: BIP/red · Dificultad: media · Baseline **2.93** → QLoRA **1.80** (empeora)

**Enunciado**

> Un vehículo debe viajar desde el depósito A hasta el terminal E por una red de caminos dirigidos. Hay tres nodos intermedios, B, C y D, y todos los costos de arco son positivos. Antes de llegar al terminal, el vehículo debe detenerse en C para realizar una inspección técnica. Puede pasar por otros nodos, pero no puede recorrer una vía en sentido contrario ni utilizar una conexión que no figure entre las opciones disponibles.
>
> Las conexiones permitidas y sus costos son: A hacia B cuesta 4; A hacia C cuesta 7; B hacia C cuesta 2; B hacia D cuesta 6; C hacia D cuesta 3; C hacia E cuesta 8; y D hacia E cuesta 2. Cada tramo se paga una vez cuando se selecciona. La red no contiene ciclos dirigidos. La inspección se realiza exactamente una vez al atravesar C, sin un cargo adicional, y el costo del recorrido corresponde solo a los arcos utilizados.
>
> La empresa necesita seleccionar un camino conectado de A a E que pase por C y minimice el costo de viaje. La formulación debe imponer salida del origen, llegada al destino y continuidad en los nodos intermedios, además de la visita obligatoria. Indique decisiones binarias por arco, manteniendo el requisito de inspección separado de la conservación ordinaria del flujo.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo de arcos seleccionados. | cumple | cumple |
| R2 | constraint | Formar un camino dirigido de A a E mediante conservación de flujo. | incorrecto | incorrecto |
| R3 | constraint | Pasar obligatoriamente por C exactamente una vez. | incorrecto | ausente |
| R4 | constraint | Usar solo arcos disponibles. | cumple | cumple |
| R5 | domain | Decisiones binarias por arco. | cumple | cumple |

<details><summary>Formulación de referencia</summary>

$N=\{A,B,C,D,E\}$, $\mathcal A$ es el conjunto de arcos dirigidos descritos, $c_{ij}$ es su costo y $x_{ij}\in\{0,1\}$ indica uso. Se define $b_A=1$, $b_E=-1$ y $b_i=0$ en los otros nodos.

$$
\min\sum_{(i,j)\in\mathcal A}c_{ij}x_{ij}\quad\text{s.a.}\quad
\sum_{j:(i,j)\in\mathcal A}x_{ij}-\sum_{j:(j,i)\in\mathcal A}x_{ji}=b_i\ (i\in N),\quad
\sum_{i:(i,C)\in\mathcal A}x_{iC}=1,\quad
x_{ij}\in\{0,1\}\ ((i,j)\in\mathcal A).
$$

</details>

**Baseline — 2.93/5** (decisiones 5.0, objetivo 5.0, restricciones 1.6666666666666665, álgebra 2.0, generalización 2.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema de optimización de ruta, podemos usar un algoritmo de programación lineal o un algoritmo genético, dependiendo de la complejidad y el tamaño de la red. Aquí te presento cómo podrías estructurar tu modelo matemático:

### Variables Binarias:
- \( x_{ij} \): Variable binaria que indica si hay una ruta directa desde nodo i hasta nodo j.
- \( y_c \): Variable binaria que indica si se realiza la inspección en el nodo C (1 si realiza, 0 si no).

### Restricciones:
1. **Salida del Origen**:
   - Siempre hay una salida desde el nodo A.
     \[
     \sum_{i \in N} x_{Ai} = 1
     \]
     Donde \(N\) es el conjunto de nodos.

2. **Llegada al Destino**:
   - Siempre hay una llegada al nodo E.
     \[
     \sum_{j \in N} x_{Ej} = 1
     \]

3. **Continuidad en Nodos Intermedios**:
   - Para cada nodo i diferente de A y E, siempre hay una entrada y una salida.
     \[
     \sum_{j \in N} x_{Aj} + \sum_{j \in N} x_{i,j} = 1 \quad \text{para todo } i \neq A, E
     \]

4. **Visita Obligatoria en C**:
   - Se realiza la inspección en C.
     \[
     y_c = 1
     \]

5. **Costo Minimizado**:
   - El costo total de la ruta es la suma de los costos de los arcos utilizados.
     \[
     \min \sum_{(i,j) \in E} w_{ij} x_{ij}
     \]
     donde \(w_{ij}\) es el costo del arco (A->B=4, A->C=7, B->C=2, B->D=6, C->D=3, C->E=8, D->E=2).

### Modelo Matemático

\[
\begin{align*}
& \text{Minimize} & & \sum_{(i,j) \in E} w_{ij} x_{ij} \\
& \text{Subject to} & & \sum_{j \in N} x_{Aj} + \sum_{j \in N} x_{i,j} = 1 \quad \forall i \neq A, E \\
& & & \sum_{j \in N} x_{Ai} = 1 \quad \forall i \neq A \\
& & & \sum_{j \in N} x_{Ej} = 1 \quad \forall j \neq E \\
& & & y_c = 1 \\
& & & x_{ij} \in \{0, 1\} \quad \forall (i,j) \in E \\
& & & y_c \in \{0, 1\}
\end{align*}
\]

Donde:
- \(x_{ij}\) indica si existe una ruta directa desde i hasta j.
- \(y_c\) indica si se realiza la inspección en C.

Este modelo proporciona una forma algebraica de representar el problema y permite su resolución utilizando técnicas como el método simplex o heurísticas como el algoritmo genético.
```

</details>

**QLoRA — 1.80/5** (decisiones 2.0, objetivo 5.0, restricciones 1.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(N\): nodos.
\(E\subseteq N\times N\): aristas dirigidas.
\(s\in N\): origen.
\(t\in N\): destino.

Parámetros:
\(c_{ij}\): costo de la arista \((i,j)\in E\).

Variables de decisión:
\(x_{ij}\in\{0,1\}\}: vale 1 si se utiliza la arista \((i,j)\).
\(y_i\in\{0,1\}\): vale 1 si se visita el nodo \(i\).

Función objetivo:
\[
\min \sum_{(i,j)\in E}c_{ij}x_{ij}
\]

Restricciones:
\[
\sum_{j:(i,j)\in E}x_{ij}=1 \qquad \forall i\in N
\]
\[
\sum_{i:(i,j)\in E}x_{ij}=1 \qquad \forall j\in N
\]
\[
x_{sj}=1,\ x_{tn}=1
\]
\[
y_i-y_j+|N|x_{ij}\le |N|-1 \qquad \forall(i,j)\in E,\ i\ne j
\]
\[
y_i+y_j-|N|x_{ij}\le |N|-1 \qquad \forall(i,j)\in E,\ i=j
\]
```

</details>

Observación del juez sobre QLoRA: La formulación incluye variables de decisión adicionales (y_i) que no están en el gold y no resuelven el requisito de visita obligatoria en C. Las restricciones de flujo no son correctas y no garantizan un camino único de A a E. La restricción de pasar por C exactamente una vez no está presente.

---

## opt_14

### Flujo máximo en una red de abastecimiento

Tipo: LP/red · Dificultad: baja · Baseline **0.00** → QLoRA **0.30** (mejora)

**Enunciado**

> Un organismo de emergencia transporta agua desde una estación S hacia un depósito final T por una red dirigida. Puede repartir el caudal entre distintas rutas y los nodos intermedios A, B y C no consumen agua: todo lo que entra en ellos debe salir. La cantidad que llegará a T no está predeterminada; el objetivo es transportarla tan grande como lo permita la capacidad conjunta de los arcos. No existen costos de uso de los enlaces.
>
> Desde S puede enviarse hasta 25 unidades hacia A y 20 hacia B. Desde A se permiten hasta 10 unidades hacia B, 15 hacia C y 10 directamente hacia T. Desde B pueden enviarse hasta 15 hacia C y 10 hacia T. Finalmente, el arco C hacia T tiene capacidad 25. Estos son todos los arcos disponibles y cada capacidad restringe su propio enlace, con independencia de las cantidades enviadas por otros arcos.
>
> Se solicita formular el máximo flujo que puede salir de S y entrar a T, determinando simultáneamente el caudal de cada arco. Debe mantenerse la conservación en A, B y C y respetarse las capacidades individuales. Evite fijar de antemano una cantidad de entrega, porque precisamente esa cantidad es el valor que la organización quiere maximizar.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar el flujo total de S a T. | ausente | incorrecto |
| R2 | constraint | Conservación de flujo en nodos intermedios. | ausente | incorrecto |
| R3 | constraint | El flujo total debe coincidir con salida neta de S y entrada neta de T. | ausente | ausente |
| R4 | constraint | Capacidad individual y no negatividad en cada arco. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$N=\{S,A,B,C,T\}$, $E$ son arcos disponibles, $u_{ij}$ su capacidad, $x_{ij}\geq0$ el caudal y $F\geq0$ el flujo total.

$$
\max F\quad\text{s.a.}\quad
\sum_{j:(i,j)\in E}x_{ij}-\sum_{j:(j,i)\in E}x_{ji}
=\begin{cases}F&i=S,\\-F&i=T,\\0&i\in\{A,B,C\},\end{cases}\quad
0\leq x_{ij}\leq u_{ij}\ ((i,j)\in E),\quad F\geq0.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema de flujo máximo, podemos utilizar el algoritmo del Máximo Flujos-Mínimo Rutas (Max-Flow Min-Cut). Este algoritmo permite encontrar el máximo flujo posible entre dos nodos sin necesidad de predecir cuánto fluye exactamente.

### Paso 1: Identificar los Nodos y Arcos

Nodos:
- S (origen)
- A, B, C (intermediarios)
- T (destino)

Arcos:
- S-A: 25 unidades
- S-B: 20 unidades
- A-B: 10 unidades
- A-C: 15 unidades
- B-T: 15 unidades
- C-T: 25 unidades

### Paso 2: Crear la Matriz de Capacidades

|   | S | A | B | C | T |
|---|---|---|---|---|---|
| **S** | - | 25 | 0 | 0 | 0 |
| **A** | 0 | - | 10 | 15 | 0 |
| **B** | 0 | 0 | - | 15 | 10 |
| **C** | 0 | 0 | 0 | - | 25 |
| **T** | 0 | 0 | 0 | 0 | - |

### Paso 3: Implementar el Algoritmo Max-Flow Min-Cut

El algoritmo Max-Flow Min-Cut utiliza un conjunto de cortes para dividir el grafo en dos partes. El corte óptimo minimiza el flujo total mientras que el max-flow es el flujo máximo posible.

#### Paso 3.1: Primera Iteración

Primero, identificamos un corte óptimo. Un corte óptimo es aquel que divide el grafo en dos partes tales que el flujo mínimo entre ellas sea igual al flujo máximo posible.

En este caso, podemos considerar el corte que separa S y T. Esto divide el grafo en dos partes:

- Parte 1: {S, A, B}
- Parte 2: {C, T}

El flujo mínimo entre estas dos partes sería 10 + 15 = 25 unidades (el flujo máximo posible entre estos dos grupos).

#### Paso 3.2: Actualización del Grafo

Después de aplicar el corte, actualizamos la matriz de capacidades:

|   | S | A | B | C | T |
|---|---|---|---|---|---|
| **S** | - | 25 | 0 | 0 | 0 |
| **A** | 0 | - | 10 | 15 | 0 |
| **B** | 0 | 0 | - | 15 | 10 |
| **C** | 0 | 0 | 0 | - | 25 |
| **T** | 0 | 0 | 0 | 0 | - |

Ahora, el flujo máximo entre S y T es 25 unidades.

### Paso 4: Determinar el Flujo Múltiple

Como hemos encontrado el flujo máximo entre S y T, ahora debemos determinar cómo distribuirlo entre los diferentes arcos.

- S-A: 25 unidades
- A-B: 10 unidades
- A-C: 15 unidades
- B-T: 10 unidades
- C-T: 0 unidades

Estos son los valores máximos que pueden ser transportados por cada arco, manteniendo la conservación en A, B y C.

### Resultado Final

- **Flujo máximo:** 25 unidades
- **Flujo por arcos:**
  - S-A: 25 unidades
  - A-B: 10 unidades
  - A-C: 15 unidades
  - B-T: 10 unidades
  - C-T: 0 unidades

Este resultado asegura que el flujo máximo posible entre S y T se ha alcanzado, cumpliendo con todas las restricciones dadas.
```

</details>

**QLoRA — 0.30/5** (decisiones 2.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(N\): nodos.
\(E\subseteq N\times N\): aristas dirigidas.
\(s\in N\): origen.
\(t\in N\): destino.

Parámetros:
\(u_{ij}\): capacidad del arco \((i,j)\in E\).

Variables de decisión:
\(x_{ij}\ge0\): flujo por el arco \((i,j)\).

Función objetivo:
\[
\max \sum_{(i,j)\in E}x_{ij}
\]

Restricciones:
\[
\sum_{j:(i,j)\in E}x_{ij}-\sum_{j:(j,i)\in E}x_{ji}=u_{ij}
\qquad \forall i\in N\setminus\{s,t\}
\]
\[
\sum_{i:(i,j)\in E}x_{ij}=u_{sj}
\qquad \forall j\in N\setminus\{t\}
\]
\[
\sum_{i:(i,j)\in E}x_{ij}=u_{jt}
\qquad \forall j\in N\setminus\{t\}
\]
```

</details>

Observación del juez sobre QLoRA: La función objetivo está mal definida: no se maximiza el flujo desde S a T, sino la suma de todos los arcos, lo cual no tiene sentido. Las restricciones de conservación de flujo están incorrectas y no reflejan la lógica del problema. Las restricciones de capacidad no se aplican correctamente, ya que se igualan a u_ij en lugar de limitar x_ij.

---

## opt_15

### Envíos con dos plantas y centros de transbordo

Tipo: LP/red · Dificultad: media · Baseline **0.00** → QLoRA **0.35** (mejora)

**Enunciado**

> Dos plantas abastecen a tres clientes mediante dos centros de transbordo H1 y H2. Cada tonelada sale de una planta, atraviesa exactamente uno de los centros y llega a un cliente. Los centros no producen ni consumen mercancía, pero tienen una capacidad máxima de procesamiento. Los envíos pueden fraccionarse entre distintas rutas y cada cliente debe recibir exactamente su pedido.
>
> La planta A dispone de hasta 35 toneladas y B de hasta 30. Los clientes X, Y y Z necesitan 20, 25 y 20 toneladas. H1 puede procesar como máximo 40 toneladas y H2, 40. Los costos por tonelada desde A hacia H1 y H2 son 2 y 4; desde B, 3 y 2. Desde H1 hacia X, Y y Z los costos son 3, 5 y 4, respectivamente; desde H2 hacia esos mismos clientes son 5, 2 y 3. No existen enlaces directos entre plantas y clientes ni entre los dos centros.
>
> La empresa busca determinar los flujos en cada arco para atender los tres pedidos al menor costo de transporte. El modelo debe incluir los límites de las plantas, conservación del flujo en cada centro, capacidad de procesamiento de ambos centros y demanda de cada cliente. No se debe tratar a los centros como fuentes adicionales de producto.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo total planta-centro y centro-cliente. | incorrecto | incorrecto |
| R2 | constraint | Capacidad/oferta máxima de cada planta. | incorrecto | cumple |
| R3 | constraint | Conservación de flujo en cada centro de transbordo. | incorrecto | incorrecto |
| R4 | constraint | Capacidad máxima de procesamiento de cada centro. | incorrecto | incorrecto |
| R5 | constraint | Demanda exacta de cada cliente. | incorrecto | incorrecto |
| R6 | domain | Flujos continuos no negativos solo en arcos disponibles. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$P=\{A,B\}$ plantas, $H=\{H1,H2\}$ centros y $J=\{X,Y,Z\}$ clientes. $s_p$ es capacidad de planta, $K_h$ capacidad de centro, $d_j$ demanda, $c^{PH}_{ph}$ y $c^{HJ}_{hj}$ costos por tonelada. $x_{ph},z_{hj}\geq0$ son flujos por cada clase de arco.

$$
\min\sum_{p,h}c^{PH}_{ph}x_{ph}+\sum_{h,j}c^{HJ}_{hj}z_{hj}\quad\text{s.a.}\quad
\sum_hx_{ph}\leq s_p\ (p\in P),\quad
\sum_p x_{ph}=\sum_j z_{hj},\quad\sum_jz_{hj}\leq K_h\ (h\in H),\quad
\sum_h z_{hj}=d_j\ (j\in J),\quad x_{ph},z_{hj}\geq0.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema de transporte con restricciones de capacidad y costos, podemos utilizar el método de programación lineal o la formulación matricial. Aquí te presento cómo podrías estructurar tu problema:

### Variables:
- **xij**: Flujo de i a j (donde i es la planta y j es el centro).
- **yj**: Flujo de j a k (donde k es el cliente).

### Restricciones:
1. **Capacidad de producción**:
   - La planta A tiene 35 toneladas.
     \[ x_A + x_B = 35 \]

2. **Capacidad de procesamiento**:
   - H1 puede procesar hasta 40 toneladas.
     \[ x_H1 + x_B = 40 \]
   - H2 puede procesar hasta 40 toneladas.
     \[ x_H2 + x_A = 40 \]

3. **Conservación del flujo**:
   - El flujo de cada centro a cada cliente debe ser igual al pedido de ese cliente.
     \[ x_H1 + x_H2 = 20 \]
     \[ x_H1 + x_H2 = 25 \]
     \[ x_H1 + x_H2 = 20 \]

4. **Flujo mínimo**:
   - Para evitar que haya fugas de flujo, debemos asegurarnos de que el flujo de cada centro sea mayor o igual al requerido por sus clientes.
     \[ x_H1 \geq 20 \]
     \[ x_H2 \geq 25 \]
     \[ x_A \geq 20 \]

5. **Costos**:
   - Costo de transporte desde A a H1: $2/tonelada
   - Costo de transporte desde A a H2: $4/tonelada
   - Costo de transporte desde B a H1: $3/tonelada
   - Costo de transporte desde B a H2: $2/tonelada

6. **Flujo de salida**:
   - Debe haber un flujo suficiente para satisfacer todas las demandas.
     \[ x_H1 + x_H2 = 20 \]
     \[ x_H1 + x_H2 = 25 \]
     \[ x_H1 + x_H2 = 20 \]

7. **Flujo de entrada**:
   - Debe haber un flujo suficiente para satisfacer todas las demandas.
     \[ x_H1 + x_H2 = 20 \]
     \[ x_H1 + x_H2 = 25 \]
     \[ x_H1 + x_H2 = 20 \]

8. **Restricción de conservación de flujo**:
   - El flujo de cada centro a cada cliente debe ser igual al pedido de ese cliente.
     \[ x_H1 + x_H2 = 20 \]
     \[ x_H1 + x_H2 = 25 \]
     \[ x_H1 + x_H2 = 20 \]

9. **Flujo mínimo**:
   - Para evitar fugas de flujo, debemos asegurarnos de que el flujo de cada centro sea mayor o igual al requerido por sus clientes.
     \[ x_H1 \geq 20 \]
     \[ x_H2 \geq 25 \]
     \[ x_A \geq 20 \]

### Modelo Matricial:
ˋˋˋ
Minimize:
   2*x_A + 4*x_B + 3*x_H1 + 2*x_H2 + 5*y_X + 4*y_Y + 3*y_Z

Subject to:
   x_A + x_B <= 35
   x_H1 + x_B <= 40
   x_H2 + x_A <= 40
   x_H1 + x_H2 >= 20
   x_H1 + x_H2 >= 25
   x_H1 + x_H2 >= 20
   x_H1 >= 20
   x_H2 >= 25
   x_A >= 20
   x_H1 + x_H2 = 20
   x_H1 + x_H2 = 25
   x_H1 + x_H2 = 20
ˋˋˋ

### Solución:
Este modelo puede ser resuelto utilizando técnicas de optimización lineal, como el método simplex o software especializado como Gurobi, CPLEX, etc., para encontrar el flujo óptimo que minimiza el costo de transporte.

### Consideraciones finales:
- **Efectividad**: Este modelo considera eficientemente las restricciones de capacidad y costos, pero puede ser complejo si hay muchos clientes y centros.
- **Optimidad**: Si la solución obtenida es ineficaz, podría ser necesario ajustar las restricciones o considerar alternativas más complejas.
- **Simulación**: Podría ser útil simular diferentes escenarios para verificar la robustez del modelo y garantizar que cumple con todas las condiciones establecidas.

Recuerda que esta es una descripción general y puede necesitar ajustes específicos dependiendo de tus datos reales.
```

</details>

**QLoRA — 0.35/5** (decisiones 0.0, objetivo 0.0, restricciones 1.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): plantas.
\(J\): clientes.
\(K\): centros de transbordo.

Parámetros:
\(s_i\): capacidad máxima de la planta \(i\).
\(d_j\): demanda del cliente \(j\).
\(c_{ik}\): costo unitario de enviar desde \(i\) a \(k\).
\(u_k\): capacidad máxima del centro \(k\).

Variables de decisión:
\(x_{ij}\ge0\): cantidad enviada desde \(i\) a \(j\).
\(y_{ik}\in\{0,1\}\): vale 1 si el centro \(k\) procesa la planta \(i\).

Función objetivo:
\[
\min \sum_{i\in I}\sum_{j\in J}c_{ik}x_{ij}
+\sum_{i\in I}\sum_{k\in K}c_{ik}u_ky_{ik}
\]

Restricciones:
\[
\sum_{i\in I}x_{ij}=d_j \qquad \forall j\in J
\]
\[
\sum_{j\in J}x_{ij}\le s_i \qquad \forall i\in I
\]
\[
\sum_{k\in K}y_{ik}\le u_k \qquad \forall i\in I
\]
```

</details>

Observación del juez sobre QLoRA: La formulación no representa correctamente el problema. Las variables de decisión no modelan los flujos entre plantas-centros y centros-clientes, sino que usan una variable binaria irrelevante (y_ik). Las restricciones no reflejan la conservación de flujo en los centros ni las capacidades de los centros. La función objetivo no incluye los costos de los arcos centro-cliente y está mal definida.

---

## opt_16

### Dos productos sobre arcos compartidos

Tipo: LP/red · Dificultad: media · Baseline **0.00** → QLoRA **0.55** (mejora)

**Enunciado**

> Una red logística debe transportar dos productos diferentes sin mezclarlos: 25 unidades de X desde S1 hasta T1 y 20 unidades de Y desde S2 hasta T2. Ambos productos pueden utilizar los nodos H y J como puntos intermedios. Aunque cada mercancía conserva su propio origen y destino, las capacidades de los arcos son compartidas: se aplica un solo límite a la suma de las unidades de X e Y que atraviesan cada conexión.
>
> Los arcos dirigidos, con costo unitario y capacidad entre paréntesis, son S1–H (2; 25), S1–J (4; 20), S2–H (3; 20), S2–J (2; 25), H–J (1; 15), H–T1 (5; 20), H–T2 (4; 20), J–T1 (3; 25) y J–T2 (2; 25). Los costos por unidad son iguales para ambos productos en un mismo arco. Cada unidad debe conservar su identidad al pasar por los nodos; un envío de X no satisface la demanda de Y.
>
> Se requiere determinar cuánto flujo de cada producto enviar por cada arco para cumplir exactamente ambos pedidos al menor costo total. Incluya balances separados por producto y nodo, y aplique la capacidad una sola vez a la suma de los flujos de ambos productos sobre cada arco.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo total de ambos productos. | ausente | parcial |
| R2 | constraint | Balance de flujo separado por producto y nodo con origen/destino propios. | ausente | incorrecto |
| R3 | constraint | Cada demanda exacta debe cumplirse. | ausente | ausente |
| R4 | constraint | Capacidad de cada arco aplicada a la suma de ambos productos. | ausente | incorrecto |
| R5 | domain | Flujos continuos no negativos. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$K=\{X,Y\}$, $N=\{S1,S2,H,J,T1,T2\}$ y $E$ son los nueve arcos dirigidos del enunciado. $b_{nk}$ representa oferta positiva en el origen de $k$, demanda negativa en su destino y cero en los demás nodos. $c_{ij}$ y $u_{ij}$ son costo y capacidad de arco. $x_{ij}^k\geq0$ es el flujo de mercancía $k$ en el arco $(i,j)$.

$$
\min\sum_{k\in K}\sum_{(i,j)\in E}c_{ij}x_{ij}^k\quad\text{s.a.}\quad
\sum_{j:(n,j)\in E}x_{nj}^k-\sum_{i:(i,n)\in E}x_{in}^k=b_{nk}\ (n\in N,k\in K),\quad
\sum_{k\in K}x_{ij}^k\leq u_{ij}\ ((i,j)\in E),\quad x_{ij}^k\geq0.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, vamos a seguir estos pasos:

1. **Definición del Problema**: Nuestro objetivo es minimizar el costo total de transporte de dos tipos de productos (X y Y) entre dos destinos (T1 y T2).

2. **Modelación del Problema**:
   - Definimos variables binarias `x_ij` que representan si hay un flujo de producto X por el arco `(i,j)` o no.
   - Definimos variables binarias `y_jt` que representan si hay un flujo de producto Y por el nodo `j` hacia el destino `t`.

3. **Restricciones**:
   - Para cada arco `(i,j)`, tenemos que `x_ij + x_ji = 1` (una única ruta).
   - Para cada nodo `j`, tenemos que `y_jt + y_tj = 1` (una única salida).
   - La cantidad de producto X que pasa por el arco `(S1,H)` es igual a la cantidad de X que llega a `T1`: `sum(x_ij * c_ij | i in {S1}, j in {H}) = 25`.
   - La cantidad de producto Y que pasa por el arco `(S2,J)` es igual a la cantidad de Y que llega a `T2`: `sum(y_jt * d_jt | j in {S2}, t in {J}) = 20`.
   - La cantidad de producto X que pasa por el arco `(S1,J)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {S1}, j in {J}) = 25`.
   - La cantidad de producto Y que pasa por el arco `(S2,H)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {S2}, t in {H}) = 20`.
   - La cantidad de producto X que pasa por el arco `(H,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {H}, j in {T1}) = 20`.
   - La cantidad de producto Y que pasa por el arco `(H,T2)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {H}, t in {T2}) = 25`.
   - La cantidad de producto X que pasa por el arco `(J,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {J}, j in {T1}) = 25`.
   - La cantidad de producto Y que pasa por el arco `(J,T2)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {J}, t in {T2}) = 20`.
   - La cantidad de producto X que pasa por el arco `(H,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {H}, j in {T1}) = 20`.
   - La cantidad de producto Y que pasa por el arco `(H,T2)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {H}, t in {T2}) = 25`.
   - La cantidad de producto X que pasa por el arco `(J,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {J}, j in {T1}) = 25`.
   - La cantidad de producto Y que pasa por el arco `(J,T2)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {J}, t in {T2}) = 20`.
   - La cantidad de producto X que pasa por el arco `(H,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {H}, j in {T1}) = 20`.
   - La cantidad de producto Y que pasa por el arco `(H,T2)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {H}, t in {T2}) = 25`.
   - La cantidad de producto X que pasa por el arco `(J,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {J}, j in {T1}) = 25`.
   - La cantidad de producto Y que pasa por el arco `(J,T2)` es igual a la cantidad de Y que sale de `T2`: `sum(y_jt * d_jt | j in {J}, t in {T2}) = 20`.
   - La cantidad de producto X que pasa por el arco `(H,T1)` es igual a la cantidad de X que sale de `T1`: `sum(x_ij * c_ij | i in {H}, j in {T1}) = 20`.
   - La cantidad de producto Y que pasa por el arco `(H,T2)` es igual a la cantidad de Y que sale de `T
```

</details>

**QLoRA — 0.55/5** (decisiones 0.0, objetivo 2.0, restricciones 0.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(N\): nodos.
\(E\subseteq N\times N\): arcos dirigidos.
\(K\): tipos de mercancías.
\(B\in\mathbb Z^{k}\): oferta máxima de cada tipo de mercancía.

Parámetros:
\(c_{ij}\in\mathbb Z^{k}\): costo unitario del arco \((i,j)\).
\(u_{ij}\in\mathbb Z^{k}:\) capacidad del arco \((i,j)\).

Variables de decisión:
\(x_{ik}\ge0:\) flujo de la mercancía \(i\) por el arco \((i,j)\).

Función objetivo:
\[
\min \sum_{i\in K}\sum_{j\in N}c_{ij}x_{ij}
\]

Restricciones:
\[
\sum_{j\in N}x_{ij}\le u_{ij}\qquad \forall i\in K,\ \forall j\in N
\]
\[
\sum_{i\in K}x_{ij}=b_j \qquad \forall j\in N
\]
```

</details>

Observación del juez sobre QLoRA: Variables de decisión mal definidas (falta índice de arco y producto) Restricciones de balance no separadas por producto y nodo Capacidad aplicada incorrectamente (a cada producto por separado en vez de a la suma) No se incluyen las demandas específicas de X e Y

---

## opt_17

### Red de fibra con conexión de todas las estaciones

Tipo: BIP/red · Dificultad: alta · Baseline **0.00** → QLoRA **1.60** (mejora)

**Enunciado**

> Una universidad desea conectar cinco estaciones de comunicación, A, B, C, D y E, mediante enlaces de fibra bidireccionales. La conexión debe permitir que cualquier estación se comunique con todas las demás a través de una secuencia de enlaces instalados. El costo de instalar cada enlace se paga una vez y no depende de la dirección en que luego se transmitan los datos. Los enlaces disponibles forman una red que contiene varias rutas posibles.
>
> Los costos de los enlaces son: A–B cuesta 4, A–C cuesta 5, B–C cuesta 2, B–D cuesta 7, C–D cuesta 3, C–E cuesta 6, D–E cuesta 2 y B–E cuesta 8. No es posible construir otros enlaces ni instalar un enlace parcialmente. La universidad no exige redundancia: una única ruta de comunicación entre cada par de estaciones es suficiente para este proyecto. Por tanto, los ciclos que no sean necesarios para conectar la red no aportan un beneficio adicional.
>
> Se debe elegir el conjunto de enlaces que conecte las cinco estaciones al menor costo de instalación. Una formulación válida debe garantizar conectividad global, y no solo que cada estación tenga al menos un enlace incidente; también debe evitar seleccionar enlaces superfluos cuando se describa la solución como un árbol.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo de enlaces instalados. | ausente | cumple |
| R2 | constraint | Garantizar conectividad global de las cinco estaciones. | ausente | incorrecto |
| R3 | constraint | Seleccionar una estructura de árbol o formulación equivalente sin ciclos superfluos. | ausente | incorrecto |
| R4 | domain | Variables binarias por enlace. | ausente | cumple |

<details><summary>Formulación de referencia</summary>

$V=\{A,B,C,D,E\}$, $E$ son los enlaces bidireccionales propuestos y $c_e$ es costo de cada uno. $x_e\in\{0,1\}$ indica instalación. Para $S\subset V$, $\delta(S)$ es el conjunto de enlaces con un extremo en $S$ y otro fuera de $S$.

$$
\min\sum_{e\in E}c_ex_e\quad\text{s.a.}\quad
\sum_{e\in\delta(S)}x_e\geq1\quad(\varnothing\ne S\subsetneq V),\quad
\sum_{e\in E}x_e=|V|-1,\quad x_e\in\{0,1\}.
$$

Las restricciones de corte garantizan conectividad y la cardinalidad de cuatro enlaces elimina ciclos de la solución conectada.

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un algoritmo conocido como "Algoritmo de Prim" o "Algoritmo de Kruskal". Ambos algoritmos son eficientes para encontrar el árbol mínimo costoso (o equivalente, el camino más corto) en un grafo dirigido sin ciclos.

### Algoritmo de Prim

1. **Inicialización**: Selecciona un nodo inicial arbitrario.
2. **Iteración**:
   - Busca el enlace más barato que no está ya incluido en el árbol.
   - Agrega ese enlace al árbol si no lo hace ya.
   - Repite hasta que todos los nodos están incluidos en el árbol.

### Algoritmo de Kruskal

1. **Ordenamiento**: Ordena los arcos del grafo por su costo.
2. **Iteración**:
   - Selecciona el arco más barato.
   - Si añadir ese arco no crea un ciclo, lo agrega al árbol.
   - Repite hasta que todos los nodos están conectados.

### Implementación:

#### Algoritmo de Prim

ˋˋˋpython
def prim(graph):
    n = len(graph)
    visited = [False] * n
    parent = [-1] * n
    min_cost = float('inf')

    # Inicializa el primer nodo como raíz
    root_node = 0

    for i in range(n):
        if graph[root_node][i] < min_cost:
            min_cost = graph[root_node][i]
            selected_edge = (root_node, i)

    while not all(visited):
        visited[selected_edge[0]] = True
        visited[selected_edge[1]] = True

        for j in range(n):
            if not visited[j]:
                if graph[selected_edge[0]][j] < min_cost and graph[selected_edge[1]][j] > 0:
                    min_cost = graph[selected_edge[0]][j]
                    new_edge = (selected_edge[0], j)

        parent[selected_edge[0]] = new_edge[0]
        parent[new_edge[1]] = selected_edge[1]
        selected_edge = new_edge

    return parent

# Ejemplo de uso
graph = [
    [0, 4, 0, 0, 0],
    [4, 0, 2, 2, 8],
    [0, 2, 0, 5, 1],
    [0, 2, 5, 0, 3],
    [0, 8, 1, 3, 0]
]

parent = prim(graph)
print("Parent array:", parent)
ˋˋˋ

#### Algoritmo de Kruskal

ˋˋˋpython
import heapq

def kruskal(graph):
    n = len(graph)
    edges = []
    result = []
    mst_cost = 0

    # Ordenamos los arcos por costo
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((graph[i][j], i, j))

    heapq.heapify(edges)

    while edges:
        edge_cost, u, v = heapq.heappop(edges)
        if not is_tree(u, v):
            mst_cost += edge_cost
            result.append((u, v))
            union(u, v)

    return result, mst_cost

def is_tree(node, neighbor):
    parent[node] = node
    for child in adj_list[node]:
        if child == neighbor or find(child) != find(parent[child]):
            return False
    return True

def union(x, y):
    x_root = find(x)
    y_root = find(y)
    if x_root != y_root:
        parent[x_root] = y_root

# Ejemplo de uso
adj_list = [[] for _ in range(len(graph))]
for u, v, w in graph:
    adj_list[u].append((v, w))

result, mst_cost = kruskal(adj_list)
print("MST Cost:", mst_cost)
print("Edges in MST:", result)
ˋˋˋ

Ambas implementaciones deben devolver un árbol conexo que conecte todos los nodos con el menor costo posible. En este caso, ambos algoritmos deberían dar la misma solución debido a la naturaleza del problema.
```

</details>

**QLoRA — 1.60/5** (decisiones 2.0, objetivo 5.0, restricciones 0.0, álgebra 1.0, generalización 1.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(V\): nodos.
\(E\): aristas o enlaces.

Parámetros:
\(w_{ij}\): costo de instalar la arista \((i,j)\in E\).

Variables de decisión:
\(y_{ij}\in\{0,1\}\): vale 1 si se instala la arista \((i,j)\).
\(F\subseteq V\times V\): arcos dirigidos de la red resultante.

Función objetivo:
\[
\min \sum_{(i,j)\in E} w_{ij} y_{ij}
\]

Restricciones:
\[
\forall (i,j)\in F:\qquad y_{ij}=y_{ji}
\]
\[
\sum_{j:(i,j)\in E}y_{ij}=1 \qquad \forall i\in V
\]
\[
\sum_{i:(i,j)\in E}y_{ij}\ge1 \qquad \forall j\in V
\]
```

</details>

Observación del juez sobre QLoRA: Las restricciones no garantizan conectividad global ni evitan ciclos superfluos. La formulación incluye variables y restricciones que no corresponden a un problema de árbol de expansión mínima, como el uso de arcos dirigidos y restricciones de grado.

---

## opt_18

### Recorrido circular de visitas técnicas

Tipo: MILP/TSP · Dificultad: alta · Baseline **0.00** → QLoRA **0.45** (mejora)

**Enunciado**

> Un equipo de inspección saldrá de su oficina, identificada como nodo 0, visitará exactamente una vez a cuatro clientes numerados del 1 al 4 y finalmente regresará a la oficina. Puede desplazarse directamente entre cualquier par de lugares y el costo de un trayecto es el mismo en ambos sentidos. Sin embargo, debe elegirse una sola gira continua: dos circuitos separados no constituyen un recorrido válido aunque cada lugar tenga una entrada y una salida.
>
> Los costos de desplazamiento entre la oficina y los clientes 1, 2, 3 y 4 son, respectivamente, 6, 8, 7 y 9. Entre clientes, los costos son 1–2: 3; 1–3: 5; 1–4: 7; 2–3: 4; 2–4: 6; y 3–4: 2. Todos los costos son positivos y no hay otras restricciones de horario o capacidad. Un cliente puede ser el primero o el último visitado, pero solo una vez en toda la gira.
>
> La empresa solicita la formulación de la gira de costo mínimo. Debe representarse la elección de arcos de viaje, la visita única a cada cliente, la salida y el retorno a la oficina, y una condición que elimine subtours formados solamente por clientes.
>
> Aunque el costo entre dos lugares sea simétrico, el orden de las visitas no está fijado: viajar de un nodo a otro constituye una decisión dirigida dentro de la secuencia completa que empieza y termina en 0.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo total de una gira que sale y vuelve a 0. | ausente | incorrecto |
| R2 | constraint | Cada nodo tiene exactamente una salida y una entrada. | ausente | incorrecto |
| R3 | constraint | Eliminar subtours que no incluyen el depósito mediante MTZ, cortes u otra formulación equivalente. | ausente | ausente |
| R4 | domain | Variables binarias de arcos y variables auxiliares válidas si se usan. | ausente | parcial |

<details><summary>Formulación de referencia</summary>

$V=\{0,1,2,3,4\}$ y $C=V\setminus\{0\}$. Para todos los arcos dirigidos entre nodos distintos, $c_{ij}$ es el costo simétrico dado y $x_{ij}\in\{0,1\}$ indica viaje. $u_i$ ordena las visitas de los clientes.

$$
\min\sum_{i\ne j}c_{ij}x_{ij}\quad\text{s.a.}\quad
\sum_{j\ne i}x_{ij}=1,\quad\sum_{j\ne i}x_{ji}=1\ (i\in V),\quad
u_i-u_j+4x_{ij}\leq3\ (i,j\in C,\ i\ne j),\quad
1\leq u_i\leq4\ (i\in C),\quad x_{ij}\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un algoritmo de búsqueda en grafos para encontrar el camino óptimo. Aquí te presento cómo podrías proceder:

### Paso 1: Representar el Problema como un Grafo

Primero, necesitamos representar nuestro problema como un grafo. Los nodos del grafo son los lugares (oficina y clientes), y los arcos son los caminos permitidos entre ellos con sus respectivos costos.

ˋˋˋplaintext
Nodos:
0 - Oficina
1 - Cliente 1
2 - Cliente 2
3 - Cliente 3
4 - Cliente 4

Arcos:
(0, 1) = 6
(0, 2) = 8
(0, 3) = 7
(0, 4) = 9

(1, 2) = 3
(1, 3) = 5
(1, 4) = 7

(2, 3) = 4
(2, 4) = 6

(3, 4) = 2
ˋˋˋ

### Paso 2: Implementar el Algoritmo de Dijkstra

Dijkstra's algorithm se utiliza para encontrar el camino más corto desde un nodo inicial hasta todos los demás nodos en un grafo ponderado. En este caso, queremos encontrar el camino más corto desde el nodo 0 (oficina).

#### Función Dijkstra:

ˋˋˋpython
def dijkstra(graph, start):
    # Inicializar el diccionario de distancias
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    # Inicializar el diccionario de predecesores
    predecessors = {node: None for node in graph}

    # Crear una cola de prioridad
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, predecessors
ˋˋˋ

### Paso 3: Calcular el Camino Optimo

Utilizaremos el resultado de Dijkstra para calcular el camino óptimo.

ˋˋˋpython
# Ejemplo de uso
graph = {
    '0': {'1': 6, '2': 8, '3': 7, '4': 9},
    '1': {'2': 3, '3': 5, '4': 7},
    '2': {'3': 4, '4': 6},
    '3': {'4': 2},
}

start_node = '0'
distances, predecessors = dijkstra(graph, start_node)

print("Distancias:", distances)
print("Predecessores:", predecessors)
ˋˋˋ

### Paso 4: Construir el Camino Completo

Con los resultados de Dijkstra, construimos el camino completo utilizando el diccionario de predecesores.

ˋˋˋpython
def reconstruct_path(predecessors, end_node):
    path = []
    current_node = end_node
    while current_node is not None:
        path.append(current_node)
        current_node = predecessors.get(current_node, None)
    path.reverse()
    return path

end_node = '4'  # El último cliente visitado
path = reconstruct_path(predecessors, end_node)
print("Camino óptimo:", path)
ˋˋˋ

### Resultado Final

El resultado final incluiría el camino óptimo, la visita a cada cliente, la salida y el retorno a la oficina, así como la eliminación de subtours formados solamente por clientes.

Este proceso asegura que el camino seleccionado cumpla todas las condiciones solicitadas y minimice el costo total del viaje.
```

</details>

**QLoRA — 0.45/5** (decisiones 2.0, objetivo 0.0, restricciones 0.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(N\): nodos.
\(s\in N\): nodo origen.
\(T=\{n\in N:s\not=n \text{ y } s\ne n\}\): nodos destinos.

Parámetros:
\(c_{sn}\): costo de un arco de conexión entre \(s\) y \(n\).
\(w_{mn}\): costo de un arco de tránsito entre \(m\) y \(n\).

Variables de decisión:
\(x_{sn}\in\{0,1\}\): vale 1 si se utiliza el arco \((s,n)\).
\(y_{mn}\in\{0,1\}\): vale 1 si se utiliza el arco \((m,n)\).

Función objetivo:
\[
\min \sum_{s\in N}\sum_{n\in T}c_{sn}x_{sn}
+\sum_{s\in N}\sum_{n\in T}w_{sn}y_{sn}
\]

Restricciones:
\[
\sum_{n\in T}x_{sn}=1 \qquad \forall s\in N
\]
\[
\sum_{s\in T}x_{sn}\le1 \qquad \forall n\in N
\]
\[
\sum_{s\in N}y_{sn}=1 \qquad \forall n\in N
\]
\[
\sum_{n\in N}y_{sn}\le1 \qquad \forall s\in N
\]
\[
x_{sm}+x_{mn}-x_{sn}\le1 \qquad \forall s<m<n
\]
```

</details>

Observación del juez sobre QLoRA: La formulación presenta variables redundantes (x y y) y no modela correctamente la estructura del problema. La función objetivo no representa el costo total de una gira única que comienza y termina en 0. Las restricciones no garantizan la conectividad del circuito ni eliminan subtours.

---

## opt_19

### Rutas de dos vehículos con carga limitada

Tipo: MILP/CVRP · Dificultad: alta · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Un depósito debe repartir mercancía a cuatro clientes con dos vehículos idénticos. Cada ruta empieza y termina en el depósito, representado por 0. Los clientes 1, 2, 3 y 4 demandan 4, 6, 3 y 5 unidades; cada pedido debe ser entregado íntegramente por un único vehículo. Cada vehículo puede transportar a lo sumo 10 unidades en su ruta. Se permite que un vehículo quede sin utilizar, aunque ambos están disponibles.
>
> Los costos simétricos de viaje desde el depósito a los clientes 1, 2, 3 y 4 son 4, 5, 6 y 7. Entre clientes, los costos son 1–2: 3; 1–3: 4; 1–4: 6; 2–3: 5; 2–4: 4; y 3–4: 3. No existen ventanas de tiempo ni costos fijos por vehículo: el objetivo es minimizar la distancia total recorrida. Un vehículo puede atender a varios clientes en un orden elegido libremente si respeta su capacidad.
>
> Se requiere decidir qué vehículo sirve a cada cliente y en qué orden los visita. La formulación debe garantizar que cada cliente aparezca en una sola ruta, que cada vehículo utilizado salga del depósito y regrese a él, que no se exceda su capacidad y que no existan circuitos desconectados del depósito.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar distancia total de las rutas de hasta dos vehículos. | incorrecto | incorrecto |
| R2 | constraint | Cada cliente servido exactamente por un vehículo. | incorrecto | incorrecto |
| R3 | constraint | Conservación de ruta por vehículo y salida/regreso al depósito solo para vehículos usados. | incorrecto | incorrecto |
| R4 | constraint | Capacidad de 10 por vehículo considerando demandas indivisibles. | incorrecto | incorrecto |
| R5 | constraint | Eliminar subtours desconectados del depósito. | incorrecto | incorrecto |
| R6 | domain | Variables binarias de asignación/arcos y auxiliares consistentes. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$V=\{0,1,2,3,4\}$, $C=V\setminus\{0\}$, $K=\{1,2\}$ y $Q=10$. $d_i$ es pedido de $i\in C$ y $c_{ij}$ costo de desplazamiento. $x_{ij}^k\in\{0,1\}$ indica arco usado por vehículo $k$, $z_i^k\in\{0,1\}$ indica cliente servido por $k$, $a_k\in\{0,1\}$ uso del vehículo y $u_i^k\geq0$ carga acumulada al terminar en $i$.

$$
\min\sum_{k\in K}\sum_{i\ne j}c_{ij}x_{ij}^k\quad\text{s.a.}\quad
\sum_k z_i^k=1\ (i\in C),\quad
\sum_{j\in V\setminus\{i\}}x_{ij}^k=\sum_{j\in V\setminus\{i\}}x_{ji}^k=z_i^k\ (i\in C,k\in K),\quad
\sum_{j\in C}x_{0j}^k=\sum_{i\in C}x_{i0}^k=a_k\ (k\in K),
$$
$$
\sum_{i\in C}d_iz_i^k\leq Qa_k,\quad
d_iz_i^k\leq u_i^k\leq Qz_i^k\ (i\in C,k\in K),\quad
u_j^k\geq u_i^k+d_j-20(1-x_{ij}^k)\ (i,j\in C,\ i\ne j,k\in K),
$$

con dominios binarios para $x,z,a$, carga no negativa y $x_{ii}^k$ prohibido. El valor 20 es una cota grande válida porque $u_i^k\leq10$ y $d_j\leq6$.

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema de distribución de carga, podemos usar un algoritmo de programación lineal para optimizar la ruta y el orden de visitas. Aquí te presento cómo podrías estructurar tu modelo matemático:

### Variables

- **x_ij** = 1 si el vehículo i visita al cliente j.
- **y_i** = 1 si el vehículo i está activo (utilizado).
- **z_j** = 1 si el cliente j es visitado.

### Función Objetivo

Minimizar la suma de las distancias entre el depósito y los clientes, considerando la cantidad de unidades transportadas:

\[ \text{Minimize} \quad \sum_{i=1}^{n} \sum_{j=1}^{m} d_{ij} x_{ij} z_j + \sum_{i=1}^{n} c_i y_i \]

Donde:
- \(d_{ij}\) es la distancia entre el depósito y el cliente j.
- \(c_i\) es el costo de viajar desde el depósito hasta el cliente i.
- \(y_i\) indica si el vehículo i está activo o no.

### Restricciones

1. **Cuantidad máxima de unidades transportadas**:
   - Para cada vehículo i:
     \[ \sum_{j=1}^{m} x_{ij} \leq 10 \]

2. **Restricción de capacidad**:
   - Para cada cliente j:
     \[ \sum_{i=1}^{n} x_{ij} \geq q_j \]
     donde \(q_j\) es la cantidad mínima de unidades requerida por el cliente j.

3. **Restricción de ruta**:
   - El vehículo debe comenzar y terminar en el depósito:
     \[ \sum_{i=1}^{n} x_{0i} = 1 \]
     \[ \sum_{i=1}^{n} x_{in} = 1 \]

4. **Restricción de vuelta al depósito**:
   - El vehículo debe volver al depósito después de visitar todos los clientes:
     \[ \sum_{i=1}^{n} x_{ik} = \sum_{i=1}^{n} x_{ki} \quad \forall k \neq 0, n \]

5. **Restricción de orden de visitas**:
   - El orden de visitas debe respetar la cantidad de unidades necesarias por cada cliente:
     \[ \sum_{k=1}^{m} x_{kj} = q_j \quad \forall j \]

6. **Restricción de no existencia de ciclos desconexos**:
   - Debe haber una única ruta completa desde el depósito hasta cada cliente y viceversa.

### Ejemplo Matemático

Supongamos que tenemos 4 clientes y 2 vehículos, y que los datos son como sigue:

| Cliente | Distancia | Costo |
|---------|-----------|-------|
| 1       | 4         | 4     |
| 2       | 5         | 5     |
| 3       | 6         | 6     |
| 4       | 7         | 7     |

Vehículo 1:
- Capacidad: 10 unidades
- Viajes a: 1, 2, 3, 4
- Viaja desde: 0, 0, 0, 0
- Viaja a: 0, 0, 0, 0

Vehículo 2:
- Capacidad: 10 unidades
- Viajas a: 1, 2, 3, 4
- Viaja desde: 0, 0, 0, 0
- Viaja a: 0, 0, 0, 0

### Solución

Primero, definimos las variables y luego construimos la función objetivo y las restricciones. Luego, utilizamos un algoritmo de programación lineal para encontrar la solución óptima.

### Algoritmo de Programación Lineal

1. Definimos las variables.
2. Definimos la función objetivo.
3. Definimos las restricciones.
4. Utilizamos un algoritmo de programación lineal para resolver el sistema.

Este proceso generalmente se realiza utilizando software de programación lineal como Gurobi, CPLEX, o Python con librerías como PuLP.

### Resultado

Después de resolver el sistema, obtenemos la mejor ruta y el orden de visitas para minimizar la distancia total recorrida.

Es importante notar que esta es una descripción general y podría necesitar ajustes específicos dependiendo de los detalles adicionales de tu problema, como la ubicación exacta de los clientes, las capacidades reales de los vehículos, etc.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): clientes.
\(S=\{i\in I:i\ne0\}\): clientes distintos al depósito.
\(K=\binom{I}{2}\): pares de clientes no ordenados.

Parámetros:
\(c_{is}\): costo de viajar de \(i\) a \(s\).
\(w_{is}\): peso o capacidad de la ruta \((i,s)\).
\(B\): capacidad de cada vehículo.

Variables de decisión:
\(x_{ks}\in\{0,1\}\): vale 1 si el vehículo \(k\) viaja de \(s\) a \(t\).
\(u_k\ge0\): carga acumulada del vehículo \(k\).

Función objetivo:
\[
\min \sum_{k\in K}c_{0k}x_{0k}+\sum_{k\in K}\sum_{s\in S}w_{ks}x_{ks}
\]

Restricciones:
\[
\sum_{k\in K}x_{ks}=1 \qquad \forall s\in S
\]
\[
\sum_{s\in S}x_{ks}=1 \qquad \forall k\in K
\]
\[
\sum_{k\in K}x_{ks}B\le B+|I|-1 \qquad \forall s\in S
\]
\[
u_{k+B-1}-u_{k-1}\le B-w_{ks} \qquad \forall k\in K,\ \forall s\in S
\]
```

</details>

Observación del juez sobre QLoRA: La formulación no representa correctamente el problema como un VRP con múltiples vehículos. Las variables y restricciones no capturan la estructura de rutas, la asignación de clientes a vehículos, ni la capacidad de los vehículos. La definición de K como pares de clientes no ordenados es incorrecta y no representa los vehículos disponibles. La función objetivo no refleja el costo total de las rutas, sino una combinación de parámetros no definidos (w_{ks}) y una estructura incorrecta. Las restricciones no garantizan que cada cliente sea servido exactamente una vez, que los vehículos salgan y regresen al depósito, ni que no haya subtours. La variable u_k no está correctamente definida ni usada para modelar la capacidad del vehículo.

---

## opt_20

### Secuenciación de trabajos con preparación

Tipo: MILP/secuenciación · Dificultad: alta · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Una máquina debe procesar cuatro trabajos, J1 a J4, uno a la vez y sin interrupciones. Cada trabajo tiene una duración, una fecha prometida y una penalización por cada hora de atraso. Preparar la máquina para el siguiente trabajo toma un tiempo que depende de cuál se terminó antes. También hay un tiempo de preparación inicial desde el estado vacío. Se puede terminar un trabajo antes de su fecha sin penalización, pero no se permite procesar dos trabajos simultáneamente.
>
> Las duraciones de J1, J2, J3 y J4 son 2, 3, 4 y 2 horas; sus fechas prometidas son 6, 8, 10 y 9; y sus penalizaciones por hora de atraso son 4, 3, 5 y 2. Las preparaciones iniciales hacia J1, J2, J3 y J4 toman 1, 2, 1 y 2 horas. Si el trabajo anterior es J1, la preparación hacia J2, J3 y J4 toma 1, 2 y 3 horas; desde J2 hacia J1, J3 y J4 toma 2, 2 y 1; desde J3 hacia J1, J2 y J4 toma 3, 1 y 2; desde J4 hacia J1, J2 y J3 toma 2, 3 y 1.
>
> Se desea determinar la secuencia, los comienzos y las horas de atraso que minimicen la penalización total. Incluya una decisión de sucesor inmediato, la continuidad de una única secuencia desde el estado inicial hasta su término, y relaciones temporales activadas solo entre trabajos consecutivos.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar penalización ponderada por atraso. | ausente | incorrecto |
| R2 | constraint | Cada trabajo pertenece a una única secuencia desde un inicio ficticio hasta un término. | ausente | incorrecto |
| R3 | constraint | Decisión de sucesor inmediato sin ciclos desconectados. | ausente | incorrecto |
| R4 | constraint | Relaciones temporales de inicio activadas para sucesores consecutivos incluyendo preparación. | ausente | incorrecto |
| R5 | constraint | Atraso no negativo y al menos finalización menos fecha prometida. | ausente | incorrecto |
| R6 | domain | Variables de secuencia binarias y tiempos continuos no negativos. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$J=\{1,2,3,4\}$, nodo ficticio 0 de inicio y 5 de término. $A$ contiene $(0,j)$, $(i,j)$ para trabajos distintos y $(i,5)$, con $i,j\in J$. $p_j$ es duración, $d_j$ fecha, $w_j$ penalización, $s_{ij}$ preparación entre trabajos y $s_{0j}$ preparación inicial. $a_{ij}\in\{0,1\}$ selecciona sucesor inmediato, $S_j\geq0$ comienzo y $T_j\geq0$ atraso. Se usa $M=100$ como cota grande válida.

$$
\min\sum_{j\in J}w_jT_j\quad\text{s.a.}\quad
\sum_{j\in J}a_{0j}=1,\quad\sum_{i\in J}a_{i5}=1,\quad
\sum_{i:(i,j)\in A}a_{ij}=1,\quad\sum_{h:(j,h)\in A}a_{jh}=1\ (j\in J),
$$
$$
S_j\geq s_{0j}-M(1-a_{0j}),\quad
S_j\geq S_i+p_i+s_{ij}-M(1-a_{ij})\ (i,j\in J,i\ne j),\quad
T_j\geq S_j+p_j-d_j\ (j\in J),\quad S_j,T_j\geq0,\ a_{ij}\in\{0,1\}.
$$

Las duraciones positivas y las restricciones de tiempo impiden ciclos desconectados entre trabajos.

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un algoritmo de programación dinámica o una solución de árbol de decisión. Aquí te presento cómo podrías proceder:

### Paso 1: Definir Variables y Datos

Primero, definimos las variables necesarias y los datos proporcionados:

- Duraciones de los trabajos (J1, J2, J3, J4): 2, 3, 4, 2 horas.
- Fechas prometidas de los trabajos: 6, 8, 10, 9.
- Penalizaciones por hora de atraso: 4, 3, 5, 2.
- Tiempo de preparación inicial: 1, 2, 1, 2 horas.
- Tiempo de preparación después del primer trabajo: 1, 2, 3, 2 horas.

### Paso 2: Crear la Matriz de Penalidades

Creamos una matriz donde cada fila representa un trabajo y cada columna representa una fecha. La celda en la posición `(i, j)` indica la penalidad si el trabajo `i` se termina justo antes de la fecha `j`.

ˋˋˋplaintext
|   | 6 | 7 | 8 | 9 |
---------------------------------
J1 | 0 | 4 | 8 | 12|
---------------------------------
J2 | 0 | 4 | 7 | 10|
---------------------------------
J3 | 0 | 4 | 8 | 12|
---------------------------------
J4 | 0 | 4 | 8 | 12|
ˋˋˋ

### Paso 3: Implementar el Algoritmo

Implementamos un algoritmo de programación dinámica para encontrar la secuencia óptima de trabajo con mínima penalidad. Este algoritmo considerará todas las posibles secuencias de trabajo y calculará la penalidad asociada a cada una.

#### Función de Programación Dinámica:
ˋˋˋpython
def min_penalty(work_schedule):
    n = len(work_schedule)

    # Crear una matriz de penalidades
    penalty_matrix = [[float('inf')] * (n + 1) for _ in range(n)]

    # Preparación inicial
    penalty_matrix[0][0] = work_schedule[0][1]

    # Preparación después del primer trabajo
    penalty_matrix[1][1] = work_schedule[1][1] - work_schedule[0][2]

    # Calcular penalidades para cada trabajo
    for i in range(2, n):
        for j in range(i+1):
            if j == 0:
                penalty_matrix[i][j] = max(penalty_matrix[i-1][j], penalty_matrix[i-1][j+1])
            else:
                penalty_matrix[i][j] = min(
                    penalty_matrix[i-1][j],
                    penalty_matrix[i-1][j-1] + work_schedule[j][1] - work_schedule[i-1][2]
                )

    return penalty_matrix[n-1][0]

# Ejemplo de uso
work_schedule = [
    [2, 6, 1],
    [3, 8, 2],
    [4, 10, 3],
    [2, 9, 2]
]

print(min_penalty(work_schedule))
ˋˋˋ

### Resultado

El resultado de ejecutar el código anterior debería ser 12, lo cual coincide con la penalidad mínima calculada.

### Decisión de Sucesor Inmediato

La decisión de sucesor inmediato se basa en la menor penalidad posible para cada trabajo. Por ejemplo, para J1, la penalidad sería 4 si se termina justo antes de la fecha 6, pero si se termina antes de la fecha 7, la penalidad sería 8.

### Continuidad de Una Secuencia Desde el Estado Inicial Hasta su Término

La continuidad de una única secuencia desde el estado inicial hasta su término se refleja en la matriz de penalidades. Cada celda en la diagonal superior muestra la penalidad si todos los trabajos se completan exactamente en su fecha prometida.

### Relaciones Temporales Activadas Solo Entre Trabajos Consecutivos

Estas relaciones temporales se representan en la matriz de penalidades, donde cada celda muestra la penalidad si un trabajo se termina justo antes de otra fecha.

Este proceso asegura que la máquina procese los trabajos de manera eficiente, minimizando la penalidad total mientras cumple con todas las condiciones dadas.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(J\): trabajos.
\(P=\{(i,j)\in J\times J:i<j\}\): pares de precedencia.
\(S=\{1,\ldots,m\}\): orden natural de los trabajos.

Parámetros:
\(d_j\): duración del trabajo \(j\).
\(p_j\): penalización por hora de atraso del trabajo \(j\).
\(a_{is}\): tiempo de preparación inicial hacia \(j\) desde \(i\).
\(r_{ij}\): tiempo de preparación de \(j\) después de \(i\).

Variables de decisión:
\(x_j\in\mathbb Z_{\ge0}\): duración del trabajo \(j\).
\(y_{is}\in\mathbb Z_{\ge0}\): tiempo de preparación inicial de \(j\) desde \(i\).
\(u_{is}\in\mathbb Z_{\ge0}\): tiempo de inicio del trabajo \(j\) desde \(i\).

Función objetivo:
\[
\min \sum_{j\in J}p_jx_j+\sum_{(i,j)\in P}a_{ij}y_{ij}
+\sum_{(i,j)\in S^2}r_{ij}u_{ij}
\]

Restricciones:
\[
\sum_{j:(i,j)\in P}x_j=d_i \qquad \forall i\in S
\]
\[
\sum_{j:(i,j)\in S^2}y_{ij}=d_i-x_i \qquad \forall i\in S
\]
\[
u_{is}\le d_is+x_j-r_{ij}+y_{ij}\qquad \forall(i,j)\in P,\ i<j
\]
\[
u_{is}\le u_{js}-r_{ij}+y_{ij}\qquad \forall(i,j),\ (j,i)\in P
\]
```

</details>

Observación del juez sobre QLoRA: La formulación no representa correctamente el problema. La función objetivo no refleja la minimización de penalización por atraso, sino una combinación de duraciones, preparaciones y tiempos de inicio. Las variables y restricciones no modelan una secuencia de trabajos con preparaciones entre ellos, ni incluyen variables de atraso. Las restricciones no garantizan una secuencia única desde un inicio ficticio hasta un término, ni modelan las relaciones temporales entre trabajos consecutivos con preparaciones.

---

## opt_21

### Corte de barras con patrones y merma

Tipo: IP · Dificultad: media · Baseline **1.00** → QLoRA **0.00** (empeora)

**Enunciado**

> Un taller compra barras de 11 metros y las corta para cumplir pedidos de piezas de 2, 3 y 5 metros. Por razones de calibración dispone de cinco patrones de corte autorizados, que no pueden modificarse. Cada aplicación de un patrón consume una barra completa y produce las piezas indicadas; cualquier longitud sobrante se descarta. El taller puede entregar más piezas que las solicitadas, pero no menos, y las cantidades de barras cortadas deben ser enteras.
>
> El patrón P1 genera tres piezas de 2 metros y una de 5; P2 produce dos de 3 y una de 5; P3 produce cuatro de 2 y una de 3; P4 produce dos de 5 y deja un metro de merma; y P5 produce una de 5 y dos de 3. Las demandas mínimas son 25 piezas de 2 metros, 18 de 3 metros y 15 de 5 metros. Cada barra comprada cuesta 11 unidades monetarias, independientemente del patrón. Además, disponer de cada metro de merma tiene un costo de 2 unidades. Los patrones P1, P2, P3 y P5 aprovechan toda la longitud de la barra.
>
> La empresa debe decidir cuántas veces utilizar cada patrón para cubrir los tres pedidos y minimizar el costo conjunto de barras y disposición de merma. No se permite construir patrones nuevos ni considerar piezas adicionales como merma: únicamente cuenta la longitud sobrante de cada barra cortada.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo de barras más costo de merma de los patrones. | incorrecto | incorrecto |
| R2 | constraint | Cubrir al menos la demanda de cada longitud de pieza. | incorrecto | incorrecto |
| R3 | constraint | Usar únicamente los cinco patrones autorizados. | cumple | incorrecto |
| R4 | domain | Variables enteras no negativas por patrón. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$P=\{P1,\ldots,P5\}$ son patrones, $I=\{2,3,5\}$ longitudes de pieza, $a_{ip}$ piezas $i$ por patrón $p$, $d_i$ pedido mínimo y $w_p$ metros sobrantes ($w_{P4}=1$; los demás son cero). $x_p\in\mathbb Z_{\geq0}$ indica barras cortadas con $p$.

$$
\min\sum_{p\in P}(11+2w_p)x_p\quad\text{s.a.}\quad
\sum_{p\in P}a_{ip}x_p\geq d_i\ (i\in I),\quad
x_p\in\mathbb Z_{\geq0}\ (p\in P).
$$

</details>

**Baseline — 1.00/5** (decisiones 0.0, objetivo 0.0, restricciones 2.0, álgebra 2.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos usar un algoritmo de programación dinámica o una solución de programación lineal para optimizar el uso de los patrones y minimizar el costo total. Aquí te presento una solución basada en programación lineal:

### Variables:
- **x1**: número de veces que se utiliza el patrón P1.
- **x2**: número de veces que se utiliza el patrón P2.
- **x3**: número de veces que se utiliza el patrón P3.
- **x4**: número de veces que se utiliza el patrón P4.
- **x5**: número de veces que se utiliza el patrón P5.

### Ecuaciones de restricción:
1. **Demanda de 2 metros**:
   - 2 * x1 + 3 * x2 + 2 * x3 + 5 * x4 = 25

2. **Demanda de 3 metros**:
   - 3 * x1 + 2 * x2 + 3 * x3 + 3 * x5 = 18

3. **Demanda de 5 metros**:
   - 5 * x1 + 5 * x2 + 3 * x3 + 2 * x5 = 15

4. **Patrones disponibles**:
   - x1 + x2 + x3 + x4 + x5 ≤ 5 (cada patrón solo usa una barra)

5. **Costo**:
   - 11 * (x1 + x2 + x3 + x4 + x5) + 2 * (5 * x4 + 3 * x5) = objetivo

### Formulación matemática:
\[
\begin{align*}
2x_1 + 3x_2 + 2x_3 + 5x_4 &= 25 \\
3x_1 + 2x_2 + 3x_3 + 3x_5 &= 18 \\
5x_1 + 5x_2 + 3x_3 + 2x_5 &= 15 \\
x_1 + x_2 + x_3 + x_4 + x_5 &\leq 5 \\
11(x_1 + x_2 + x_3 + x_4 + x_5) + 2(5x_4 + 3x_5) &\geq \text{objetivo} \\
\end{align*}
\]

### Solución:
Primero, resolvemos la parte de la programación lineal:

1. **Demanda de 2 metros**:
   - 2x1 + 3x2 + 2x3 + 5x4 = 25

2. **Demanda de 3 metros**:
   - 3x1 + 2x2 + 3x3 + 3x5 = 18

3. **Demanda de 5 metros**:
   - 5x1 + 5x2 + 3x3 + 2x5 = 15

Resolviendo estas ecuaciones simultáneamente es complicado por falta de información sobre las cantidades exactas de cada patrón. Sin embargo, podemos probar diferentes combinaciones de patrones para ver qué soluciones satisfacen todas las condiciones y minimizan el costo.

Por ejemplo, si usamos todos los patrones P1, P2, P3, y P5, entonces:
- 2x1 + 3x2 + 2x3 + 5x4 = 25
- 3x1 + 2x2 + 3x3 + 3x5 = 18
- 5x1 + 5x2 + 3x3 + 2x5 = 15

Si tomamos valores enteros positivos para x1, x2, x3, x4, y x5 que cumplan con estas ecuaciones, podríamos encontrar una solución óptima.

Finalmente, calculamos el costo total utilizando la fórmula proporcionada:

\[
\text{Costo} = 11(x_1 + x_2 + x_3 + x_4 + x_5) + 2(5x_4 + 3x_5)
\]

Este método combina la programación lineal con la restricción de que cada patrón solo usa una barra, lo cual implica que cada variable x_i debe ser entera y no mayor que 1.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): patrones disponibles.
\(Q\): requerimientos mínimos.

Parámetros:
\(l_i\): longitud de una barra usando el patrón \(i\).
\(c\): costo unitario de una barra.
\(p_{\min}\): requerimiento mínimo de cada tamaño.

Variables de decisión:
\(x_i\in\{0,1\}\): vale 1 si se usa el patrón \(i\).

Función objetivo:
\[
\min \sum_{i\in I}c l_i x_i+2\sum_{i\in I}(l_i-p_{\min})x_i
\]

Restricciones:
\[
\sum_{i\in I}x_i=K
\]
\[
\sum_{i\in I}l_ix_i\ge q_j \qquad \forall j\in Q
\]
```

</details>

Observación del juez sobre QLoRA: Variables de decisión definidas incorrectamente (deben ser enteras no negativas, no binarias) La función objetivo no representa correctamente el costo total (incluye términos no válidos y no considera la merma correctamente) Las restricciones no reflejan correctamente la cobertura de demandas No se respeta el requisito de usar únicamente los cinco patrones autorizados

---

## opt_22

### Producción por lotes e inventario limitado

Tipo: MILP · Dificultad: media · Baseline **0.92** → QLoRA **0.00** (empeora)

**Enunciado**

> Una línea fabrica un producto durante cuatro períodos consecutivos. La demanda de cada período debe atenderse en ese mismo período o desde inventario previamente acumulado; no se permiten faltantes. Si se inicia la producción en un período se paga un costo fijo de preparación y debe fabricarse al menos un lote mínimo de 10 unidades. También existe un máximo de producción y el almacenamiento disponible al cierre de cualquier período tiene capacidad limitada.
>
> Las demandas de los períodos 1, 2, 3 y 4 son 20, 30, 15 y 25 unidades. Las capacidades de producción son 40, 35, 35 y 40; los costos variables por unidad son 5, 4, 6 y 5; y los costos fijos de preparación son 30, 40, 25 y 35, respectivamente. Mantener una unidad al cierre de un período cuesta 1 unidad monetaria y pueden guardarse como máximo 20 unidades. Se inicia sin inventario y se debe terminar el período 4 también sin existencias. Una línea que no se prepara no puede fabricar nada durante ese período.
>
> La empresa busca determinar en qué períodos activar la línea, cuánto producir y cuánto almacenar para satisfacer todos los pedidos al mínimo costo total. La formulación debe incluir el balance entre períodos, ambos límites de producción condicionados a la activación y el tope de almacenamiento.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo variable de producción, preparación fija e inventario. | parcial | incorrecto |
| R2 | constraint | Balance de inventario entre períodos sin faltantes. | incorrecto | incorrecto |
| R3 | constraint | Producción nula si no se activa y entre lote mínimo y capacidad si se activa. | incorrecto | incorrecto |
| R4 | constraint | Capacidad máxima de inventario. | parcial | incorrecto |
| R5 | constraint | Inventario inicial y final iguales a cero. | incorrecto | incorrecto |
| R6 | domain | Activación binaria; producción e inventario no negativos. | parcial | incorrecto |

<details><summary>Formulación de referencia</summary>

$T=\{1,2,3,4\}$, $d_t$ demanda, $K_t$ capacidad, $c_t$ costo unitario, $f_t$ preparación y $h=1$ costo de inventario. $x_t\geq0$ es producción, $I_t\geq0$ inventario final y $y_t\in\{0,1\}$ activación. $I_0=0$.

$$
\min\sum_{t\in T}(c_tx_t+f_ty_t+hI_t)\quad\text{s.a.}\quad
I_{t-1}+x_t=d_t+I_t\ (t\in T),\quad
10y_t\leq x_t\leq K_ty_t\ (t\in T),\quad
0\leq I_t\leq20\ (t\in T),\quad I_4=0,\quad
x_t\geq0,\ y_t\in\{0,1\}.
$$

</details>

**Baseline — 0.92/5** (decisiones 2.0, objetivo 2.0, restricciones 0.625, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un modelo de programación lineal (LP) con restricciones de tiempo y capacidad de almacenamiento. Aquí está cómo podrías estructurar tu modelo:

### Variables:
- \( x_{ij} \): Cantidad de unidades producidas en el periodo \( i \) y almacenadas en el periodo \( j \).
- \( y_i \): Indica si la línea está activa en el periodo \( i \).

### Restricciones:
1. **Producción**: Para cada periodo \( i \), la cantidad producida debe ser igual a la suma de las cantidades almacenadas en ese periodo y en los anteriores.
   - \( x_{ij} = x_{i+1,j} + x_{i,j-1} \)

2. **Almacenamiento**: El número de unidades almacenadas en un periodo no puede superar el límite de almacenamiento.
   - \( x_{ij} \leq M \cdot y_i \)

3. **Límites de producción**: No se puede producir más unidades que la capacidad del proceso.
   - \( x_{ij} \leq P_j \)

4. **Costo de producción**: La producción ocurre en períodos donde la línea está activa.
   - \( x_{ij} \geq 0 \)

5. **Costo de almacenamiento**: Los únicos costos considerados son mantener una unidad al cierre de un período.
   - \( x_{ij} \geq 0 \)

6. **Falta de producción**: No se puede producir menos unidades que el lote mínimo.
   - \( x_{ij} \geq L_m \)

7. **Inventario inicial**: Inicialmente, no hay inventario.
   - \( x_{i,i-1} = 0 \)

8. **Finalización de producción**: Finalizar el período 4 sin existencias.
   - \( x_{i,4} = 0 \)

9. **Actividad de línea**: Solo se puede producir cuando la línea está activa.
   - \( y_i \in \{0, 1\} \)

### Función objetivo:
Minimizar el costo total, que es la suma de los costos de producción y almacenamiento.
- Minimizar: \( Z = \sum_{i=1}^{4} \sum_{j=i}^{4} (C_{ij} \cdot x_{ij}) + S \cdot y_i \)
  - Donde \( C_{ij} \) es el costo unitario de producción en el periodo \( i \) y almacenado en el periodo \( j \).
  - \( S \) es el costo de mantenimiento de una unidad al cierre de un período.

### Ejemplo de implementación en Python usando PuLP:
ˋˋˋpython
from pulp import *

# Definir los datos
P = [40, 35, 35, 40] # Capacidades de producción
C = [[5, 4, 6, 5], [30, 40, 25, 35]] # Costos unitarios de producción
M = 20 # Máximo de almacenamiento
L_m = 10 # Lote mínimo de producción

# Crear el problema LP
prob = LpProblem("Production_Scheduling", LpMinimize)

# Variables
y = LpVariable.dicts('y', range(1, 5), cat='Binary')
x = LpVariable.dicts('x', [(i, j) for i in range(1, 5) for j in range(i, 5)], lowBound=0, upBound=P[i-1])

# Función objetivo
prob += lpSum([C[i][j]*x[(i, j)] for i in range(1, 5) for j in range(i, 5)])

# Restricciones
for i in range(1, 5):
    prob += lpSum([x[(i, j)] for j in range(i, 5)]) == sum(P[j-1] if j <= i else 0 for j in range(i, 5))

for i in range(1, 5):
    prob += x[(i, i-1)] == 0
    prob += x[(i, i)] <= M * y[i]
    prob += x[(i, i)] >= L_m

# Resolver el problema
status = prob.solve()

# Imprimir resultados
print(f"Status: {LpStatus[status]}")
print(f"Cantidad de unidades producidas:")
for i in range(1, 5):
    print(f"Periodo {i}: {value(x[(i, i)])}")
ˋˋˋ

Este código utiliza la biblioteca `PuLP` para definir y resolver el modelo de programación lineal. Asegúrate de tener instalada la biblioteca antes de ejecutarlo (`pip install pulp`). Este ejemplo proporciona una base para resolver el problema, pero necesitarás ajustarlo según tus especificaciones específicas.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(T\): períodos.

Parámetros:
\(d_t\): demanda en \(t\).
\(c_{pt}\): costo variable unitario.
\(f_p\): costo fijo de preparación.
\(u_p\): capacidad de producción.
\(L_s\): límite de almacenamiento.

Variables de decisión:
\(x_{tp}\ge0\): unidades producidas en \(t\) y \(p\).
\(I_{ts}\ge0\): unidades almacenadas al final de \(s\).

Función objetivo:
\[
\min \sum_{t\in T}\sum_{p\in P}(c_{pt}x_{tp}+f_pI_{tp})
\]

Restricciones:
\[
I_{ts-1}+x_{ts}-I_{ts}=d_s \qquad \forall s\in S,\ \forall p\in P
\]
\[
\sum_{p\in P}x_{tp}\le u_p \qquad \forall t\in T
\]
\[
I_{ts}\le L_s \qquad \forall s\in S,\ \forall t\in T
\]
```

</details>

Observación del juez sobre QLoRA: La formulación presenta múltiples errores esenciales: variables decisionales incorrectas (x_{tp} e I_{ts} no están definidas correctamente), función objetivo mal definida (incluye I_{tp} en lugar de inventario final), restricciones de balance incorrectas, límites de producción mal formulados, y no se incluyen variables de activación binarias. La formulación no representa el problema descrito.

---

## opt_23

### Contratación con un mes de capacitación

Tipo: IP · Dificultad: media · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Una empresa necesita personal técnico calificado durante tres meses. Comienza el primer mes con 12 técnicos habilitados. Puede incorporar personas a un programa de capacitación al inicio de cada mes, pero estas no pueden atender la demanda de ese mismo mes: terminan su formación al cierre y se suman al personal habilitado para el mes siguiente. La empresa no contempla despidos ni bajas durante el horizonte y las incorporaciones deben expresarse en números enteros.
>
> Los requerimientos mínimos de técnicos habilitados son 12 en el mes 1, 15 en el mes 2 y 18 en el mes 3. Puede capacitar como máximo a cuatro personas en cada mes. Cada ingreso al programa cuesta 100 unidades monetarias en el mes de capacitación. Mantener a un técnico habilitado durante un mes cuesta 1000, incluso si fue capacitado el mes anterior. Los aprendices en formación no se contabilizan como habilitados ni reciben ese salario hasta el mes siguiente. No se exige una dotación final superior al mínimo del tercer mes.
>
> La gerencia quiere decidir cuántas personas incorporar al programa en cada mes y con cuántos técnicos habilitados operará, minimizando gastos de formación y salarios. Es indispensable representar el desfase temporal: contratar aprendices en el mes 2 puede cubrir el mes 3, pero no la necesidad del mes 2.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costos de capacitación y salarios del personal habilitado. | incorrecto | incorrecto |
| R2 | constraint | Dotación inicial 12. | incorrecto | incorrecto |
| R3 | constraint | Capacitados en t se incorporan al personal habilitado en t+1, no en el mismo mes. | incorrecto | incorrecto |
| R4 | constraint | Cumplir requerimiento mínimo mensual. | incorrecto | incorrecto |
| R5 | constraint | Máximo cuatro aprendices por mes. | incorrecto | incorrecto |
| R6 | domain | Variables enteras no negativas. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$T=\{1,2,3\}$, $d_t$ necesidad de personal habilitado, $S_1=12$ dotación inicial, $H_t\in\mathbb Z_{\geq0}$ aprendices que comienzan formación en $t$ y $S_t\in\mathbb Z_{\geq0}$ personal habilitado que trabaja en $t$.

$$
\min\sum_{t\in T}(100H_t+1000S_t)\quad\text{s.a.}\quad
S_1=12,\quad S_{t+1}=S_t+H_t\ (t=1,2),\quad
S_t\geq d_t\ (t\in T),\quad
0\leq H_t\leq4,\ H_t\in\mathbb Z\ (t\in T),\quad
S_t\in\mathbb Z_{\geq0}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, vamos a seguir estos pasos:

1) **Definición de variables**:
   - `t`: número de técnicos habilitados en el mes i.
   - `c_i`: número de técnicos capacitados en el mes i (i = 1, 2, 3).
   - `g_i`: costo total de formación en el mes i.
   - `s_i`: costo total de salarios en el mes i.

2) **Restricciones**:
   - El número mínimo de técnicos habilitados es constante:
     - t_1 >= 12
     - t_2 >= 15
     - t_3 >= 18

   - Se pueden incorporar entre 0 y 4 técnicos capacitados en cada mes.

   - El costo total de formación y salarios debe ser mínimo.

3) **Objetivo**:
   Minimizar el costo total de formación y salarios.

4) **Ecuaciones**:
   - Formación:
     - Mes 1: t_1 + c_1 = 12
     - Mes 2: t_2 + c_2 = 15
     - Mes 3: t_3 + c_3 = 18

   - Salarios:
     - Mes 1: s_1 = 100 * t_1
     - Mes 2: s_2 = 100 * t_2
     - Mes 3: s_3 = 100 * t_3

   - Costo total:
     - g_1 = 100 * c_1
     - g_2 = 100 * c_2
     - g_3 = 100 * c_3
     - s_1 + s_2 + s_3 = 1000 * (t_1 + t_2 + t_3)

5) **Implementación**:
   Vamos a usar Python y la librería PuLP para modelar esta situación.

ˋˋˋpython
from pulp import *

# Definir los problemas de optimización
prob = LpProblem("TecnicoHabilitado", LpMinimize)

# Variables de decisión
t1 = LpVariable('t1', lowBound=0)
t2 = LpVariable('t2', lowBound=0)
t3 = LpVariable('t3', lowBound=0)
c1 = LpVariable('c1', lowBound=0)
c2 = LpVariable('c2', lowBound=0)
c3 = LpVariable('c3', lowBound=0)
s1 = LpVariable('s1', lowBound=0)
s2 = LpVariable('s2', lowBound=0)
s3 = LpVariable('s3', lowBound=0)

# Restricciones
prob += t1 == 12
prob += t2 == 15
prob += t3 == 18

prob += c1 <= 4
prob += c2 <= 4
prob += c3 <= 4

prob += s1 == 100 * t1
prob += s2 == 100 * t2
prob += s3 == 100 * t3

# Objetivo
prob += g1 + g2 + g3 + s1 + s2 + s3

# Resolver el problema
prob.solve()

# Mostrar resultados
print(f"Status: {LpStatus[prob.status]}")
for v in prob.variables():
    print(v.name, "=", v.varValue)
print(f"Costo Total: {value(prob.objective)}")

# Obtener valores finales
t_final = value(t1) + value(t2) + value(t3)
c_final = value(c1) + value(c2) + value(c3)
s_final = value(s1) + value(s2) + value(s3)

print(f"Técnicos Habilitados Final: {t_final}")
print(f"Técnicos Capacitados Final: {c_final}")
print(f"Salarios Financiados Final: {s_final}")
ˋˋˋ

Este código define los problemas de optimización utilizando PuLP, incluyendo restricciones y objetivos. Luego, utiliza PuLP para resolver el problema y mostrar los resultados finales.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): meses.
\(S\): habilidades o programas de capacitación disponibles.

Parámetros:
\(r_i\): requerimiento mínimo de técnicos en el mes \(i\).
\(c_s\): costo unitario de capacitación.
\(p_s\): pago unitario por técnico habilitado.
\(u_{is}\in\{0,1\}\): vale 1 si en el mes \(i\) se selecciona el programa \(s\).

Variables de decisión:
\(x_is\in\mathbb Z_{\ge0}\): número de personas asignadas al programa \(s\) en el mes \(i\).

Función objetivo:
\[
\min \sum_{i\in I}\sum_{s\in S}c_sp_{is}x_is
\]

Restricciones:
\[
\sum_{s\in S}x_is=r_i \qquad \forall i\in I
\]
\[
\sum_{i\in I}x_is\le4 \qquad \forall s\in S
\]
```

</details>

Observación del juez sobre QLoRA: La formulación no representa correctamente el problema. Las variables, parámetros y restricciones no están alineadas con el enunciado. La lógica de desfase temporal entre capacitación y disponibilidad de técnicos no se modela. La función objetivo y las restricciones no reflejan los costos ni las limitaciones del problema original.

---

## opt_24

### Despacho eléctrico con batería

Tipo: LP · Dificultad: media · Baseline **0.00** → QLoRA **0.00** (igual)

**Enunciado**

> Una instalación dispone de un generador y una batería para atender su demanda eléctrica en tres horas consecutivas. La energía producida puede suministrarse de inmediato o cargarse en la batería; a su vez, la batería puede descargarse para atender la demanda. Se considera que la carga y la descarga no tienen pérdidas en este ejercicio. No es posible comprar energía externa ni dejar demanda sin satisfacer, y el nivel de batería debe permanecer entre cero y su capacidad física.
>
> Las demandas de las horas 1, 2 y 3 son 40, 60 y 50 unidades. Las capacidades de generación son 60, 70 y 60, mientras que los costos por unidad generada son 4, 8 y 5, respectivamente. La batería comienza con 10 unidades, puede almacenar como máximo 20 y permite cargar o descargar como máximo 15 unidades por hora. Al terminar la hora 3 deben quedar al menos 5 unidades para la jornada siguiente. La energía que se almacena al cierre de una hora queda disponible en la siguiente, y el costo de generación se paga cuando se produce.
>
> Se desea decidir la generación, la carga, la descarga y el nivel de batería de cada hora para minimizar el costo total. El modelo debe equilibrar la demanda eléctrica de cada hora y la evolución de la batería sin contar una misma unidad de energía dos veces.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo total de generación. | incorrecto | incorrecto |
| R2 | constraint | Balance energético por hora entre generación, descarga, demanda y carga. | incorrecto | incorrecto |
| R3 | constraint | Evolución intertemporal del nivel de batería desde nivel inicial 10. | incorrecto | incorrecto |
| R4 | constraint | Capacidades de generación, carga, descarga y almacenamiento. | incorrecto | incorrecto |
| R5 | constraint | Nivel final al menos 5. | incorrecto | incorrecto |
| R6 | domain | Variables continuas no negativas. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$T=\{1,2,3\}$, $d_t$ demanda, $K_t$ capacidad de generación, $c_t$ costo unitario y $B_0=10$ carga inicial. $g_t,ch_t,dis_t\geq0$ son generación, carga y descarga, y $B_t\geq0$ energía almacenada al cierre.

$$
\min\sum_{t\in T}c_tg_t\quad\text{s.a.}\quad
g_t+dis_t=d_t+ch_t\ (t\in T),\quad
B_t=B_{t-1}+ch_t-dis_t\ (t\in T),\quad
0\leq g_t\leq K_t,\quad 0\leq ch_t,dis_t\leq15,\quad
0\leq B_t\leq20\ (t\in T),\quad B_3\geq5.
$$

Una solución con carga y descarga simultáneas puede eliminar ambas cantidades en igual medida sin alterar costo ni balances, por lo que no se necesita una decisión binaria adicional para obtener un plan óptimo sin simultaneidad.

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un algoritmo de programación lineal para optimizar el consumo de energía. Aquí te presento cómo podrías proceder:

1) **Definición del Problema:**
   - Generación máxima: 60 + 70 + 60 = 190 kWh
   - Batería máxima: 20 kWh
   - Costo por kWh: 4 (hora 1), 8 (hora 2), 5 (hora 3)
   - Demanda: 40 + 60 + 50 = 150 kWh

2) **Modelo Matemático:**

   Primero, definimos variables:
   - \( x_i \): cantidad de energía generada en la hora i.
   - \( y_i \): cantidad de energía cargada en la batería en la hora i.
   - \( z_i \): cantidad de energía descargada de la batería en la hora i.

   Los límites de generación y carga/bajada de la batería son:
   - \( 0 \leq x_i \leq 190 \)
   - \( 0 \leq y_i \leq 20 \)
   - \( 0 \leq z_i \leq 15 \)

   Además, tenemos restricciones de demanda:
   - \( x_1 + y_1 \geq 40 \)
   - \( x_2 + y_2 \geq 60 \)
   - \( x_3 + y_3 \geq 50 \)

   Finalmente, queremos maximizar el costo total:
   - \( \text{Costo} = 4x_1 + 8x_2 + 5x_3 \)

3) **Implementación del Modelo:**

   Usaremos Python junto con la librería PuLP para modelar y resolver el problema.

ˋˋˋpython
from pulp import *

# Definir los datos
demands = [40, 60, 50]
capacities = [60, 70, 60]
costs = [4, 8, 5]
battery_capacity = 20
max_charge_discharge = 15
min_battery_level = 5

# Crear el problema de LP
prob = LpProblem("EnergyManagement", LpMinimize)

# Variables
x = LpVariable.dicts("Generacion", range(1, 4), lowBound=0, upBound=190, cat='Continuous')
y = LpVariable.dicts("CargaBateria", range(1, 4), lowBound=0, upBound=battery_capacity, cat='Continuous')
z = LpVariable.dicts("DescargaBateria", range(1, 4), lowBound=-max_charge_discharge, upBound=max_charge_discharge, cat='Continuous')

# Función objetivo
prob += lpSum([costs[i] * x[i] for i in range(1, 4)])

# Restricciones de demanda
for i in range(1, 4):
    prob += x[i] + y[i] >= demands[i]

# Restricción mínima de batería
for i in range(1, 4):
    prob += y[i] + z[i] <= battery_capacity

# Restricción máxima de batería
for i in range(1, 4):
    prob += y[i] + z[i] >= min_battery_level

# Resolver el problema
prob.solve()

print(f"Status: {LpStatus[prob.status]}")
print(f"Cantidad de energía generada en cada hora: {lpSum(x[i].varValue for i in range(1, 4))}")
print(f"Cantidad de energía cargada en la batería en cada hora: {lpSum(y[i].varValue for i in range(1, 4))}")
print(f"Cantidad de energía descargada de la batería en cada hora: {lpSum(z[i].varValue for i in range(1, 4))}")

ˋˋˋ

Este código define el problema matemático y lo resuelve utilizando PuLP, una biblioteca de Python para problemas de programación lineal. Después de ejecutarlo, obtendrás la solución óptima para la cantidad de energía que debe ser generada, cargada y descargada en cada hora, así como el costo total asociado.
```

</details>

**QLoRA — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(T\): horas.
\(P\): tipos de energía: producción, carga y descarga.

Parámetros:
\(D_t\): demanda en \(t\).
\(C_p\): costo unitario de la energía del tipo \(p\).
\(U_p\): capacidad máxima de la energía del tipo \(p\).
\(B_0\): nivel inicial de la batería.
\(U_b\): capacidad de almacenamiento de la batería.
\(L_b\): nivel mínimo de la batería.

Variables de decisión:
\(G_t^{gen}\in\{0,U_p\}:\) energía producida en \(t\).
\(G_t^{load}\in\{-U_p,B_0\}:\) energía cargada a la batería en \(t\).
\(G_t^{sink}\in\{-U_p,U_b\}:\) energía descargada en \(t\).
\(B_t\in[0,B_0+U_b]:\) nivel de la batería en \(t\).

Función objetivo:
\[
\min \sum_{t\in T}C_{G_t^{gen}}G_t^{gen}+\sum_{t\in T}|G_t^{load}|+\sum_{t\in T}|G_t^{sink}|
\]

Restricciones:
\[
B_{t-1}+G_t^{load}-G_t^{sink}=D_t-G_t^{gen}
\qquad \forall t\in T
\]
\[
0\le G_t^{load}\le B_0-U_p \qquad \forall t\in T
\]
\[
0\le G_t^{sink}\le U_b \qquad \forall t\in T
\]
\[
L_b\le B_t\le B_0+U_b \qquad \forall t\in T
\]
```

</details>

Observación del juez sobre QLoRA: La función objetivo no es correcta: incluye términos de carga y descarga con valor absoluto, lo cual no corresponde al enunciado. El costo solo se paga por la generación, no por la carga o descarga. Las variables de decisión no están correctamente definidas: G_t^{load} y G_t^{sink} tienen dominios incorrectos y no representan adecuadamente la carga y descarga. Las restricciones de balance energético y evolución de la batería son incorrectas o no coherentes con el enunciado. Las restricciones de capacidades no están correctamente formuladas y no reflejan los límites dados en el enunciado. La restricción de nivel final no está correctamente formulada.

---

## opt_25

### Localización con peor distancia de servicio

Tipo: MILP/localización · Dificultad: media · Baseline **0.00** → QLoRA **0.74** (mejora)

**Enunciado**

> Una red de atención primaria instalará exactamente dos módulos entre tres lugares candidatos: Norte, Centro y Sur. Debe asignar por completo cada una de cuatro comunidades, A, B, C y D, a un solo módulo abierto. Cada módulo puede recibir varias comunidades sin limitación de capacidad. A diferencia de una medida que suma las distancias, la red quiere que la comunidad peor situada quede lo más cerca posible de su módulo asignado.
>
> Las distancias en kilómetros desde Norte hacia A, B, C y D son 2, 5, 8 y 9. Desde Centro son 4, 2, 4 y 7; desde Sur son 9, 6, 3 y 2. No se consideran diferencias de población ni costos de apertura; cada comunidad cuenta de igual forma al evaluar el mayor desplazamiento individual. La red puede escoger cualquiera de las tres parejas de ubicaciones, pero no puede enviar a una comunidad a un lugar que permanezca cerrado. Las distancias asignadas deben calcularse según el lugar y la comunidad específicos.
>
> Se pide formular las decisiones de apertura y asignación y una variable adicional para la distancia máxima soportada por cualquier comunidad. El objetivo es minimizar ese máximo, garantizando dos módulos abiertos, asignación única y coherencia entre cada asignación y su apertura.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar la máxima distancia de servicio R, no la suma de distancias. | incorrecto | incorrecto |
| R2 | constraint | Abrir exactamente dos ubicaciones. | incorrecto | cumple |
| R3 | constraint | Asignar cada comunidad exactamente a una ubicación. | incorrecto | incorrecto |
| R4 | constraint | Asignar solo a ubicaciones abiertas. | incorrecto | ausente |
| R5 | constraint | R debe acotar la distancia de toda asignación activa. | incorrecto | ausente |
| R6 | domain | Variables de apertura/asignación binarias y R no negativa. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$I=\{N,CT,S\}$ ubicaciones Norte, Centro y Sur; $J=\{A,B,C,D\}$ comunidades, $d_{ij}$ distancia y $K=2$. $y_i\in\{0,1\}$ indica apertura, $x_{ij}\in\{0,1\}$ asignación y $R\geq0$ máxima distancia de servicio.

$$
\min R\quad\text{s.a.}\quad
\sum_{i\in I}y_i=K,\quad
\sum_{i\in I}x_{ij}=1\ (j\in J),\quad
x_{ij}\leq y_i\ (i\in I,j\in J),\quad
R\geq d_{ij}x_{ij}\ (i\in I,j\in J),\quad
x_{ij},y_i\in\{0,1\},\ R\geq0.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un algoritmo de programación lineal o heurística basada en búsqueda greedy. Aquí te presento cómo podrías proceder:

1. **Definir Variables**:
   - `x_ij`: Variable binaria que indica si la comunidad i está asignada al módulo j (0 si no, 1 si sí).
   - `d_max`: Distancia máxima soportada por cualquier comunidad.

2. **Restricciones**:
   - Para cada módulo, debe haber al menos dos comunitades asignadas.
     \[
     \sum_{i} x_{ij} = 2 \quad \text{para todos los módulos j}
     \]
   - Para cada comunidad, debe estar asignada a un único módulo.
     \[
     \sum_j x_{ij} = 1 \quad \text{para todas las comunidades i}
     \]

3. **Objetivo**:
   Minimizar `d_max`, donde `d_max` es la distancia máxima entre cualquier comunidad y su módulo asignado.

4. **Algoritmo Greedy**:
   - Ordena las comunidades por su distancia a sus respectivos módulos.
   - Asigna primero a las comunidades con menor distancia.
   - Si hay múltiples opciones, asigna a la comunidad con menor distancia disponible.

Aquí tienes un ejemplo de cómo podría implementarse en Python utilizando la biblioteca PuLP:

ˋˋˋpython
from pulp import *

# Definir variables
prob = LpProblem("Minimize_Distance_Max", LpMinimize)

# Variables binarias
x = LpVariable.dicts("x", [(i,j) for i in range(1,5) for j in range(1,4)], cat='Binary')

# Restricciones
for j in range(1,4):
    prob += lpSum([x[i,j] * d[i-1][j-1] for i in range(1,5)]) >= 2

for i in range(1,5):
    prob += lpSum([x[i,j] for j in range(1,4)]) == 1

# Objetivo
prob += lpSum([x[i,j] * d[i-1][j-1] for i in range(1,5) for j in range(1,4)])

# Resolver el problema
prob.solve()

# Imprimir resultados
print(f"Status: {LpStatus[prob.status]}")
print(f"D_max: {value(prob.objective)}")

# Obtener asignaciones y aperturas
asignaciones = {}
aperturas = {}

for v in prob.variables():
    if v.varValue > 0 and v.name.split('_')[0].isdigit() and v.name.split('_')[1].isdigit():
        asignaciones[v.name] = int(v.name.split('_')[0])
        aperturas[v.name] = int(v.name.split('_')[1])

print("Asignaciones:")
for k,v in asignaciones.items():
    print(f"{k}: {v}")

print("\nAperturas:")
for k,v in aperturas.items():
    print(f"{k}: {v}")
ˋˋˋ

Este código define las variables, establece las restricciones y el objetivo, luego resuelve el problema usando PuLP. Finalmente, imprime las asignaciones y las aperturas resultantes.

Recuerda ajustar el código según tus necesidades específicas y asegúrate de tener instalada la biblioteca PuLP (`pip install pulp`).
```

</details>

**QLoRA — 0.74/5** (decisiones 0.0, objetivo 0.0, restricciones 1.25, álgebra 2.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(U\): sitios candidatos.
\(V\): comunidades.

Parámetros:
\(d_{uv}\): distancia entre los sitios \(u\) y \(v\).
\(a_{uv}\in\{0,1\}\): vale 1 si \(u\) abre \(v\).

Variables de decisión:
\(y_u\in\{0,1\}\): vale 1 si \(u\) abre.
\(x_{vu}\in\{0,1\}\): vale 1 si \(u\) asigna a \(v\).
\(M\): constante suficientemente grande.

Función objetivo:
\[
\min \max_{v\in V} d_{uv}x_{vu}
\]

Restricciones:
\[
\sum_{v\in V}y_v=2
\]
\[
\sum_{v\in V}x_{vu}=1 \qquad \forall u\in U
\]
\[
x_{vu}+x_{vw}\le1 \qquad \forall u\ne v,y_u=1,y_v=1
\]
```

</details>

Observación del juez sobre QLoRA: La función objetivo no está formulada correctamente como una minimización de una variable R que acota las distancias, sino como un max que no se traduce a una variable de decisión. Las restricciones no incluyen la lógica de acotación de R ni la coherencia entre asignación y apertura.

---

## opt_26

### Cobertura de barrios bajo un presupuesto

Tipo: BIP/cobertura · Dificultad: media · Baseline **0.35** → QLoRA **1.18** (mejora)

**Enunciado**

> Una municipalidad estudia instalar módulos móviles en cuatro ubicaciones, U1 a U4. Cada ubicación cubre un conjunto predefinido de barrios, pero las áreas pueden solaparse: la población de un barrio se cuenta una sola vez aunque quede al alcance de dos módulos. Por razones presupuestarias no todas las ubicaciones pueden instalarse, y el equipo operativo puede administrar a lo sumo dos módulos simultáneamente.
>
> Los barrios 1 a 6 tienen poblaciones de 12, 18, 9, 15, 11 y 14 cientos de habitantes, respectivamente. U1 cubre los barrios 1, 2 y 4; U2 cubre 2, 3 y 5; U3 cubre 1, 4 y 6; y U4 cubre 3, 5 y 6. Los costos de instalación de U1, U2, U3 y U4 son 5, 4, 6 y 3 unidades presupuestarias. El presupuesto disponible es 9. Un barrio se considera atendido si al menos una ubicación seleccionada lo cubre, sin necesidad de asignar personas a un módulo específico.
>
> La municipalidad desea seleccionar ubicaciones para maximizar la suma de poblaciones cubiertas, cumpliendo presupuesto y límite de dos módulos. La formulación debe enlazar correctamente la variable de cobertura de cada barrio con los módulos abiertos y evitar sumar dos veces su población.
>
> El presupuesto es un límite de instalación y no una obligación de gastarlo por completo. Un barrio sin ninguna ubicación seleccionada que lo alcance no aporta habitantes al objetivo, por grande que sea su población.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Maximizar población cubierta sin doble conteo. | incorrecto | incorrecto |
| R2 | constraint | Presupuesto de instalación máximo 9. | cumple | incorrecto |
| R3 | constraint | A lo sumo dos módulos abiertos. | cumple | cumple |
| R4 | constraint | Un barrio puede contarse cubierto solo si al menos una ubicación abierta lo cubre. | incorrecto | incorrecto |
| R5 | domain | Variables binarias de apertura y cobertura. | incorrecto | parcial |

<details><summary>Formulación de referencia</summary>

$I=\{U1,U2,U3,U4\}$ son ubicaciones, $J=\{1,\ldots,6\}$ barrios, $a_{ij}=1$ si $i$ cubre $j$, $p_j$ población en cientos, $c_i$ costo y $B=9$. $y_i,z_j\in\{0,1\}$ indican instalación y cobertura.

$$
\max\sum_{j\in J}p_jz_j\quad\text{s.a.}\quad
\sum_i c_iy_i\leq B,\quad\sum_i y_i\leq2,\quad
z_j\leq\sum_i a_{ij}y_i\ (j\in J),\quad
z_j\geq a_{ij}y_i\ (i\in I,j\in J),\quad
y_i,z_j\in\{0,1\}.
$$

</details>

**Baseline — 0.35/5** (decisiones 0.0, objetivo 0.0, restricciones 1.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un modelo de programación lineal (LP) o un algoritmo genético para encontrar la solución óptima. Aquí te presento cómo podrías estructurar tu modelo LP:

### Variables:
- **x_ij**: Variable binaria que indica si el barrio i está cubierto por la ubicación j.
- **y_j**: Variable binaria que indica si la ubicación j está abierta.

### Restricciones:
1. **Cobertura del Barrio**:
   - Para cada barrio i, la suma de x_ij debe ser igual a 1 si el barrio i está cubierto.
     \[
     \sum_{j=1}^{n} x_{ij} = 1 \quad \forall i \in \{1, 2, ..., n\}
     \]

2. **Cobertura de Ubicaciones**:
   - Para cada ubicación j, la suma de x_ij debe ser igual a 1 si la ubicación j cubre algún barrio.
     \[
     \sum_{i=1}^{m} x_{ij} = 1 \quad \forall j \in \{1, 2, ..., n\}
     \]

3. **Presupuesto**:
   - La suma total de los costos de las ubicaciones abiertas no superará el presupuesto disponible.
     \[
     \sum_{j=1}^{n} c_j y_j \leq P
     \]
     Donde \(P\) es el presupuesto disponible y \(c_j\) es el costo de la ubicación j.

4. **Límites de Módulos**:
   - No más de dos módulos pueden estar abiertos simultáneamente.
     \[
     \sum_{j=1}^{n} y_j \leq 2
     \]

### Objetivo:
Maximizar la suma de las poblaciones cubiertas:
\[
\max \sum_{i=1}^{n} p_i \cdot x_{ii}
\]
Donde \(p_i\) es la población del barrio i.

### Formulación Matemática:
Aquí tienes la formulación matemática completa:

\[
\begin{align*}
& \text{Minimizar } Z \\
& \text{Sujeto a:} \\
& \sum_{j=1}^{n} x_{ij} = 1 & \forall i \in \{1, 2, ..., n\} \\
& \sum_{i=1}^{m} x_{ij} = 1 & \forall j \in \{1, 2, ..., n\} \\
& \sum_{j=1}^{n} c_j y_j \leq P \\
& \sum_{j=1}^{n} y_j \leq 2 \\
& x_{ij}, y_j \in \{0, 1\} & \forall i, j
\end{align*}
\]

### Ejemplo de Implementación en Python usando PuLP:
ˋˋˋpython
from pulp import *

# Definir variables
prob = LpProblem("Ubicacion", LpMaximize)

# Definir variables
x = LpVariable.dicts("x", [(i, j) for i in range(1, 7) for j in range(1, 5)], lowBound=0, upBound=1, cat='Binary')
y = LpVariable.dicts("y", [j for j in range(1, 5)], lowBound=0, upBound=1, cat='Binary')

# Definir restricciones
prob += lpSum([p * x[i][j] for i in range(1, 7) for j in range(1, 5)]) <= 9

# Definir objetivos
prob += lpSum([p * x[i][i] for i in range(1, 7)])

# Resolver el problema
prob.solve()

# Imprimir resultados
print(f"Status: {LpStatus[prob.status]}")
for v in prob.variables():
    print(v.name, "=", v.varValue)
ˋˋˋ

Este código utiliza la biblioteca `PuLP` para definir y resolver el modelo. Asegúrate de tener la librería `PuLP` instalada en tu entorno de desarrollo.
```

</details>

**QLoRA — 1.18/5** (decisiones 2.0, objetivo 0.0, restricciones 1.6666666666666665, álgebra 2.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(U\): ubicaciones.
\(B\): barrios.

Parámetros:
\(p_u\): costo de instalar \(u\in U\).
\(c_{ub}\): población del barrio \(b\) cubierto por \(u\).
\(B'\subseteq B\): barrios disponibles.
\(S\): máximo número de módulos que se pueden abrir.

Variables de decisión:
\(y_u\in\{0,1\}\): vale 1 si se instala \(u\).
\(x_b^{(u)}\in\{0,1\}\): vale 1 si el barrio \(b\) se atende usando \(u\).

Función objetivo:
\[
\max \sum_{u\in U}p_u y_u+\sum_{u\in U}\sum_{b\in B'}c_{ub}x_b^{(u)}
\]

Restricciones:
\[
\sum_{u\in U}y_u\le S
\]
\[
\sum_{u\in U}c_{ub}x_b^{(u)}\le B'
\qquad \forall b\in B'
\]
\[
x_b^{(u)}\le y_u \qquad \forall u\in U,\ \forall b\in B'
\]
```

</details>

Observación del juez sobre QLoRA: La función objetivo suma poblaciones de barrios en lugar de maximizar la población cubierta sin duplicaciones Las restricciones no enlazan correctamente la cobertura de barrios con los módulos abiertos La restricción de presupuesto está mal formulada y usa un conjunto como límite

---

## opt_27

### Bodegas con apertura, capacidad y reparto

Tipo: MILP/localización · Dificultad: media · Baseline **0.00** → QLoRA **0.95** (mejora)

**Enunciado**

> Una distribuidora puede habilitar tres bodegas candidatas, B1, B2 y B3, para atender cuatro tiendas. Cada habilitación implica un costo fijo y un volumen mínimo de operación: no resulta viable abrir una bodega para despachar solo unas pocas unidades. Las tiendas pueden repartir sus pedidos entre bodegas, pero ciertas rutas quedan descartadas porque superan el tiempo máximo de entrega. Una ubicación cerrada no puede enviar mercancía.
>
> Los costos fijos de B1, B2 y B3 son 75, 110 y 85, y sus capacidades de despacho son 45, 40 y 55 unidades. Las tiendas 1, 2, 3 y 4 requieren 20, 15, 30 y 25 unidades. Toda bodega abierta debe despachar al menos 15 unidades en total. B1 puede servir a las tiendas 1, 2 y 3, con costos unitarios de 3, 4 y 6; B2 puede servir a las tiendas 2, 3 y 4, con costos 5, 3 y 4; B3 puede atender a las cuatro tiendas, con costos 6, 5, 4 y 3. Las rutas B1–4 y B2–1 están prohibidas, aunque serían físicamente posibles. El costo fijo se paga una sola vez por bodega abierta.
>
> Se solicita escoger qué bodegas abrir y cuánto enviar en cada ruta permitida, minimizando aperturas y transporte. La formulación debe garantizar cada pedido, excluir las rutas no autorizadas y vincular tanto el volumen mínimo como la capacidad máxima con la decisión de apertura.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costos fijos de bodegas más costos de envío. | incorrecto | cumple |
| R2 | constraint | Satisfacer exactamente la demanda de cada tienda. | incorrecto | incorrecto |
| R3 | constraint | Usar solo rutas permitidas. | incorrecto | ausente |
| R4 | constraint | Si una bodega abre, despacho total entre mínimo 15 y su capacidad; si cierra, despacho cero. | incorrecto | incorrecto |
| R5 | domain | Apertura binaria y envíos continuos no negativos. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$I=\{B1,B2,B3\}$ son bodegas, $J=\{1,2,3,4\}$ tiendas y $E\subseteq I\times J$ las diez rutas permitidas. $f_i$ costo fijo, $K_i$ capacidad, $d_j$ pedido y $c_{ij}$ costo unitario de la ruta. $y_i\in\{0,1\}$ indica apertura y $x_{ij}\geq0$ cantidad enviada solo para $(i,j)\in E$.

$$
\min\sum_{i\in I} f_iy_i+\sum_{(i,j)\in E}c_{ij}x_{ij}\quad\text{s.a.}\quad
\sum_{i:(i,j)\in E}x_{ij}=d_j\ (j\in J),\quad
15y_i\leq\sum_{j:(i,j)\in E}x_{ij}\leq K_iy_i\ (i\in I),\quad
x_{ij}\geq0\ ((i,j)\in E),\quad y_i\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un modelo de programación lineal no convencional (PLNC) que considera los límites de capacidad, costos y restricciones de ruta. Aquí está cómo podrías estructurar tu modelo:

### Variables:
- **x_ij**: Variable binaria que indica si la bodega i es utilizada para atender la tienda j.
- **y_j**: Variable continua que representa el volumen de productos que la bodega i envía a la tienda j.

### Restricciones:
1. **Capacidad de la bodega**:
   - Para cada bodega i:
     \[
     \sum_{j} x_{ij} \leq c_i \quad \text{donde } c_i = \min(45, 55, 85)
     \]

2. **Volumen mínimo requerido**:
   - Para cada bodega i:
     \[
     \sum_{j} y_{ij} \geq m_i \quad \text{donde } m_i = \max(15, 15, 15)
     \]

3. **Rutas no autorizadas**:
   - Si hay una ruta i-j prohibida, entonces \(x_{ij} = 0\).

4. **Restricción de ruta**:
   - Para cada ruta i-j:
     \[
     y_{ij} \leq d_{ij}
     \]
     donde \(d_{ij}\) es el volumen máximo que la ruta permite transportar.

5. **Costos**:
   - Para cada bodega i y cada ruta i-j:
     \[
     z_{ij} = w_{ij} + c_{ij} y_{ij}
     \]
     donde \(w_{ij}\) es el costo unitario de la ruta i-j y \(c_{ij}\) es el costo unitario de la bodega i.

### Objetivo:
Minimizar el costo total de apertura y transporte:
\[
\min \sum_{i,j} z_{ij} x_{ij}
\]

### Formulación matemática:
La formulación completa sería algo así:

\[
\begin{align*}
& \text{Minimize} & & \sum_{i,j} z_{ij} x_{ij} \\
& \text{Subject to} & & \sum_{j} x_{ij} \leq c_i \quad \forall i \\
& & & \sum_{j} y_{ij} \geq m_i \quad \forall i \\
& & & y_{ij} \leq d_{ij} \quad \forall i,j \\
& & & x_{ij} \in \{0,1\} \quad \forall i,j \\
& & & y_{ij} \in [0,d_{ij}] \quad \forall i,j
\end{align*}
\]

Donde:
- \(z_{ij}\): Costo total de la ruta i-j.
- \(c_i\), \(m_i\), \(d_{ij}\): Constantes definidas según las restricciones del problema.
- \(w_{ij}\): Costo unitario de la ruta i-j.
- \(x_{ij}\): Variable binaria indicando si la bodega i es utilizada para atender la tienda j.
- \(y_{ij}\): Variable continua representando el volumen de productos que la bodega i envía a la tienda j.

Este modelo puede ser resuelto utilizando técnicas de optimización lineal o heurísticas basadas en algoritmos genéticos o tabu search para encontrar una solución óptima o aproximada.
```

</details>

**QLoRA — 0.95/5** (decisiones 0.0, objetivo 4.0, restricciones 0.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): bodegas candidatas.
\(J\): tiendas.

Parámetros:
\(f_i\): costo fijo de abrir \(i\in I\).
\(c_{ij}\): costo unitario de envío de \(i\) a \(j\).
\(u_j\): capacidad de despacho de \(j\).
\(b_j\): oferta mínima requerida de \(j\).
\(R_{ij}\): conjunto de tiendas alcanzables directamente desde \(i\) y no restringida por una ruta no autorizada.

Variables de decisión:
\(y_i\in\{0,1\}\): vale 1 si se abre \(i\).
\(x_{ij}\ge0\): cantidad enviada de \(i\) a \(j\).

Función objetivo:
\[
\min \sum_{i\in I}f_i y_i+\sum_{i\in I}\sum_{j\in J}c_{ij}x_{ij}
\]

Restricciones:
\[
\sum_{i\in I}x_{ij}\ge b_j \qquad \forall j\in J
\]
\[
\sum_{j\in J}x_{ij}\le u_i \qquad \forall i\in I
\]
\[
\sum_{j\in R_{ij}}x_{ij}\ge b_j-\sum_{k\in R_{ik}}x_{kj} \qquad \forall i\in I,\ \forall j\in J
\]
```

</details>

Observación del juez sobre QLoRA: La restricción R2 está incorrecta: se especifica una desigualdad >= en lugar de una igualdad para satisfacer exactamente la demanda. La restricción R3 no se aborda en absoluto. La restricción R4 está incorrecta: no se vincula el volumen de despacho con la variable de apertura mediante una relación de tipo 15y_i <= ... <= K_iy_i. La definición de dominios en R5 es incorrecta: se menciona 'oferta mínima requerida de j' y 'capacidad de despacho de j', lo cual no corresponde a la descripción del problema.

---

## opt_28

### Trabajos indivisibles en impresoras con horas limitadas

Tipo: MILP/asignación · Dificultad: media · Baseline **0.00** → QLoRA **0.45** (mejora)

**Enunciado**

> Una imprenta debe ejecutar cuatro pedidos, P1 a P4, asignando cada uno por completo a una de tres impresoras. Preparar una impresora para los pedidos de esta semana tiene un costo fijo, incluso si finalmente procesa solo un pedido. Los tiempos y costos variables dependen de la pareja pedido–impresora. Una máquina que no se prepare debe quedar sin trabajos, y un pedido no puede dividirse entre equipos.
>
> En la impresora 1, P1, P2, P3 y P4 consumen 3, 4, 2 y 5 horas y tienen costos variables de 7, 6, 9 y 8. En la impresora 2 consumen 4, 2, 3 y 4 horas y cuestan 8, 5, 7 y 7. En la impresora 3 los tiempos son 2, 4, 3 y 3 horas y los costos son 6, 8, 6 y 5. Las impresoras 1, 2 y 3 disponen de 9, 8 y 7 horas, respectivamente, y sus costos de preparación son 10, 12 y 9. Por formato del papel, P2 no puede producirse en la impresora 3; los tiempos y costos indicados para esa combinación solo permiten reconocer que la prohibición es contractual, no de capacidad.
>
> La empresa requiere un plan de costo total mínimo que incluya costos de preparación y de ejecución. Debe asignar cada pedido una vez, respetar horas disponibles, impedir P2 en la impresora 3 y cobrar la preparación únicamente a las impresoras utilizadas.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo variable de pedidos más costos fijos de preparación. | ausente | incorrecto |
| R2 | constraint | Asignar cada pedido exactamente a una impresora permitida. | ausente | incorrecto |
| R3 | constraint | Respetar horas disponibles de cada impresora. | ausente | incorrecto |
| R4 | constraint | No permitir P2 en impresora 3. | ausente | ausente |
| R5 | constraint | Una impresora no preparada no puede recibir trabajos; activación coherente con uso. | ausente | incorrecto |
| R6 | domain | Variables binarias. | ausente | parcial |

<details><summary>Formulación de referencia</summary>

$M=\{1,2,3\}$ impresoras, $J=\{P1,P2,P3,P4\}$ pedidos y $E=(M\times J)\setminus\{(3,P2)\}$ parejas permitidas. $t_{mj}$ son horas, $c_{mj}$ costo variable, $f_m$ costo de preparación y $K_m$ capacidad semanal. $x_{mj}\in\{0,1\}$ indica asignación y $y_m\in\{0,1\}$ activación.

$$
\min\sum_{(m,j)\in E}c_{mj}x_{mj}+\sum_{m\in M}f_my_m\quad\text{s.a.}\quad
\sum_{m:(m,j)\in E}x_{mj}=1\ (j\in J),\quad
\sum_{j:(m,j)\in E}t_{mj}x_{mj}\leq K_my_m\ (m\in M),\quad
y_m\leq\sum_{j:(m,j)\in E}x_{mj}\ (m\in M),\quad
x_{mj},y_m\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, necesitamos encontrar una asignación óptima de pedidos a impresoras que minimice el costo total (costo de preparación + costo de ejecución). Vamos a seguir estos pasos:

1) **Definimos los datos:**
   - Impresoras:
     - Impresora 1: Tiempo = [3, 4, 2, 5], Costo = [7, 6, 9, 8]
     - Impresora 2: Tiempo = [4, 2, 3, 4], Costo = [8, 5, 7, 7]
     - Impresora 3: Tiempo = [2, 4, 3, 3], Costo = [6, 8, 6, 5]

   - Horas disponibles:
     - Impresora 1: 9 horas
     - Impresora 2: 8 horas
     - Impresora 3: 7 horas

   - Requisitos específicos:
     - No se pueden dividir pedidos.
     - P2 no puede ser producido en la impresora 3.
     - La impresora 1 no puede estar vacía.

2) **Implementamos un algoritmo de asignación óptima:**

   Primero, ordenamos los pedidos según su costo variable más bajo primero. Luego, intentamos asignarlos a las impresoras con menos tiempo disponible primero.

3) **Asignación paso a paso:**

   - Pedidos con menor costo variable:
     - P1: Impresora 1 (tiempo = 3)
     - P2: Impresora 2 (tiempo = 2)
     - P3: Impresora 3 (tiempo = 3)
     - P4: Impresora 1 (tiempo = 5)

   - Asignación actual:
     - Impresora 1: P1, P3, P4
     - Impresora 2: P2
     - Impresora 3: Vacía

   - Verificamos si podemos cumplir todos los requisitos:
     - P2 no está en la impresora 3.
     - Impresora 1 no está vacía.
     - Impresoras 2 y 3 están llenas.

4) **Calcular el costo total:**

   - Costo de preparación:
     - Impresora 1: $10
     - Impresora 2: $12
     - Impresora 3: $9

   - Costo de ejecución:
     - Impresora 1: $7 + $9 + $8 = $24
     - Impresora 2: $5 + $7 = $12
     - Impresora 3: $6 + $6 = $12

   - Total costo:
     - Costo de preparación: $10 + $12 + $9 = $31
     - Costo de ejecución: $24 + $12 + $12 = $48
     - Total: $31 + $48 = $79

Por lo tanto, el plan de costo total mínimo que cumple con todas las restricciones es de $79.
```

</details>

**QLoRA — 0.45/5** (decisiones 2.0, objetivo 0.0, restricciones 0.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): formatos de papel.
\(P\): impresoras disponibles.

Parámetros:
\(p_{ij}\): tiempo requerido del formato \(i\) en la impresora \(j\).
\(c_{ij}\): costo variable de preparación del formato \(i\) en la impresora \(j\).
\(u_{ij}\): costo fijo de preparación de la impresora \(j\) independiente del formato.
\(s_j\): horario disponible de la impresora \(j\).

Variables de decisión:
\(x_{ij}\in\{0,1\}\): vale 1 si la formato \(i\) se asigna a la impresora \(j\).
\(y_j\ge u_{ij}\): costo fijo de preparación de la impresora \(j\).

Función objetivo:
\[
\min \sum_{i\in I}\sum_{j\in P}c_{ij}x_{ij}+s_jy_j
\]

Restricciones:
\[
\sum_{j\in P}x_{ij}\le1 \qquad \forall i\in I
\]
\[
\sum_{i\in I}p_{ij}x_{ij}\le s_j \qquad \forall j\in P
\]
\[
i\not=j \Rightarrow p_{ij}+p_{ji}>s_j
\]
```

</details>

Observación del juez sobre QLoRA: La variable y_j no está correctamente definida ni usada en la función objetivo Falta la restricción que impide asignar P2 a la impresora 3 La restricción i≠j⇒p_ij+p_ji>s_j no tiene sentido en el contexto del problema La definición de variables y parámetros no coincide con el enunciado original

---

## opt_29

### Selección de rutas de cuadrillas ya diseñadas

Tipo: BIP/partición · Dificultad: media · Baseline **1.75** → QLoRA **0.80** (empeora)

**Enunciado**

> Una empresa de mantenimiento tiene cinco tareas que deben realizarse exactamente una vez durante una jornada. Por restricciones de traslado y habilidades, las cuadrillas solo pueden utilizar siete rutas previamente diseñadas; cada ruta incluye un conjunto fijo de tareas y se contrata completa. Si una ruta se utiliza, se paga su costo íntegro, aunque algunas tareas pudieran cubrirse por otra ruta. El plan no puede duplicar tareas entre cuadrillas.
>
> Las rutas disponibles son R1, que cubre tareas 1 y 2 por costo 12; R2 cubre 2 y 3 por 10; R3 cubre 3 y 4 por 11; R4 cubre 4 y 5 por 9; R5 cubre 1 y 5 por 13; R6 cubre 1, 3 y 5 por 16; y R7 cubre 2 y 4 por 12. La empresa dispone de como máximo dos cuadrillas, de modo que se pueden activar a lo sumo dos rutas. Cada tarea incluida en una ruta activada se considera ejecutada y no puede volver a aparecer en otra ruta seleccionada. No se permite diseñar combinaciones adicionales de tareas.
>
> Se busca determinar qué rutas contratar para cubrir exactamente las cinco tareas al menor costo. La formulación debe distinguir la cobertura exacta de una condición de cobertura mínima y contabilizar una cuadrilla por ruta seleccionada.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar costo total de rutas contratadas. | cumple | incorrecto |
| R2 | constraint | Cada tarea cubierta exactamente una vez, no al menos una vez. | incorrecto | incorrecto |
| R3 | constraint | Seleccionar como máximo dos rutas. | cumple | cumple |
| R4 | constraint | Solo rutas prediseñadas y variables binarias. | incorrecto | incorrecto |

<details><summary>Formulación de referencia</summary>

$R=\{R1,\ldots,R7\}$ son rutas y $J=\{1,\ldots,5\}$ tareas. $a_{jr}=1$ si la ruta $r$ incluye la tarea $j$ y 0 si no; $c_r$ es su costo. $y_r\in\{0,1\}$ indica contratación.

$$
\min\sum_{r\in R}c_ry_r\quad\text{s.a.}\quad
\sum_{r\in R}a_{jr}y_r=1\ (j\in J),\quad
\sum_{r\in R}y_r\leq2,\quad y_r\in\{0,1\}.
$$

</details>

**Baseline — 1.75/5** (decisiones 2.0, objetivo 4.0, restricciones 1.0, álgebra 1.0, generalización 1.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos usar el método de programación lineal para minimizar costos. Aquí está cómo podrías estructurar tu modelo matemático:

### Variables:
- **x_i** = 1 si ruta i es utilizada, 0 caso contrario.
- **y_j** = 1 si tarea j es asignada a una ruta, 0 caso contrario.

### Restricciones:
1. **Cuantidad máxima de rutas**:
   \[
   x_1 + x_2 + x_3 + x_4 + x_5 + x_6 + x_7 \leq 2
   \]

2. **Tarea obligatoria**:
   - Tarea 1: \(x_1 + x_6 = 1\)
   - Tarea 2: \(x_1 + x_2 = 1\)
   - Tarea 3: \(x_2 + x_3 = 1\)
   - Tarea 4: \(x_3 + x_4 = 1\)
   - Tarea 5: \(x_4 + x_5 = 1\)

3. **No repetición de tareas**:
   - Para cada ruta, todas las tareas deben ser únicas.
     \[
     y_{ij} = 1 \text{ si } (i,j) \text{ pertenece a una ruta}
     \]

### Función objetivo:
Minimizar el costo total de las rutas utilizadas:
\[
\min \sum_{i=1}^{7} c_i x_i
\]
donde \(c_i\) es el costo de la ruta \(i\).

### Formulación del modelo:
Aquí tienes la formulación matemática completa:

\[
\begin{align*}
& \text{Minimize} & & \sum_{i=1}^{7} c_i x_i \\
& \text{Subject to} & & x_1 + x_2 + x_3 + x_4 + x_5 + x_6 + x_7 \leq 2 \\
& & & x_1 + x_6 = 1 \\
& & & x_1 + x_2 = 1 \\
& & & x_2 + x_3 = 1 \\
& & & x_3 + x_4 = 1 \\
& & & x_4 + x_5 = 1 \\
& & & y_{ij} = 1 \text{ si } (i,j) \text{ pertenece a una ruta} \\
& & & y_{ij} = 0 \text{ si } (i,j) \text{ no pertenece a ninguna ruta}
\end{align*}
\]

### Ejecución del Modelo:
Con esta formulación, puedes utilizar un programa de optimización lineal o un software específico para resolverlo. Algunas opciones populares incluyen Python con librerías como PuLP, Gurobi, o CPLEX.

Este modelo asegura que se utilicen exactamente las cinco tareas y se minimice el costo total de las rutas contratadas.
```

</details>

**QLoRA — 0.80/5** (decisiones 2.0, objetivo 0.0, restricciones 1.0, álgebra 1.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(U\): tareas.
\(S\): rutas disponibles.

Parámetros:
\(c_{us}\): costo de usar la ruta \(s\) para la tarea \(u\).

Variables de decisión:
\(y_s\in\{0,1\}\): vale 1 si se usa la ruta \(s\).
\(x_u\in\{0,1\}\): vale 1 si la tarea \(u\) se selecciona.

Función objetivo:
\[
\min \sum_{s\in S}c_{us}y_s
\]

Restricciones:
\[
\sum_{s\in S}y_s\le2 \qquad \text{(conjuntos de cuadrillas)}
\]
\[
\sum_{s\in S}c_{us}y_s\le x_u \qquad \forall u\in U
\]
```

</details>

Observación del juez sobre QLoRA: La variable x_u no está definida ni utilizada correctamente; la formulación no garantiza que cada tarea sea cubierta exactamente una vez, violando R2 La función objetivo utiliza c_us en lugar de c_s, lo cual no está definido en los parámetros y no representa el costo de las rutas correctamente

---

## opt_30

### Proyecto con precedencias y recurso compartido

Tipo: MILP/proyecto · Dificultad: media · Baseline **0.00** → QLoRA **0.40** (mejora)

**Enunciado**

> Un equipo debe planificar cinco actividades de un proyecto, A, B, C, D y E. Cada actividad comienza una sola vez y dura una cantidad fija de tiempo, sin interrupciones. Algunas actividades solo pueden comenzar cuando otras hayan terminado. Las actividades C y D necesitan al mismo especialista y, por ello, no pueden ejecutarse simultáneamente; el equipo puede escoger cuál de las dos va primero. Las demás actividades pueden superponerse si las precedencias lo permiten.
>
> Las duraciones de A, B, C, D y E son 2, 3, 2, 4 y 3 días. A debe terminar antes de que comiencen C y D; B también debe terminar antes de que comience D. E necesita que tanto C como D estén completas. Todas las actividades están disponibles desde el inicio del día 0 y no existen otras restricciones de recurso. El especialista realiza por completo C o D antes de empezar la otra; su disponibilidad no depende de A, B ni E. El proyecto termina cuando finaliza E.
>
> Se busca el calendario de inicio de cada actividad que minimice el día de terminación del proyecto. La formulación debe representar las precedencias, la decisión binaria sobre el orden entre C y D, la no superposición de estas dos actividades y una variable para el instante final.

**Requisitos y cumplimiento según el juez**

| Req. | Tipo | Requisito | Baseline | QLoRA |
|---|---|---|---|---|
| R1 | objective | Minimizar el instante final del proyecto. | ausente | cumple |
| R2 | constraint | Precedencias A->C, A->D, B->D, C->E y D->E. | ausente | incorrecto |
| R3 | constraint | C y D no pueden solaparse; una decisión binaria elige cuál precede a cuál. | ausente | incorrecto |
| R4 | constraint | El makespan debe ser al menos la finalización de E. | ausente | ausente |
| R5 | domain | Tiempos de inicio no negativos y binaria de orden. | ausente | incorrecto |

<details><summary>Formulación de referencia</summary>

$I=\{A,B,C,D,E\}$, $p_i$ duración y $S_i\geq0$ día de inicio. $M\geq0$ representa el término del proyecto; $b\in\{0,1\}$ vale 1 si C precede a D. Una cota grande válida para este horizonte es $L=30$ días.

$$
\min M\quad\text{s.a.}\quad
S_C\geq S_A+p_A,\quad S_D\geq S_A+p_A,\quad S_D\geq S_B+p_B,\quad
S_E\geq S_C+p_C,\quad S_E\geq S_D+p_D,\quad
S_D\geq S_C+p_C-L(1-b),\quad
S_C\geq S_D+p_D-Lb,\quad
M\geq S_E+p_E,\quad S_i,M\geq0,\ b\in\{0,1\}.
$$

</details>

**Baseline — 0.00/5** (decisiones 0.0, objetivo 0.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Para resolver este problema, podemos utilizar un modelo matemático llamado Programación Dinámica (PD) o Modelización de Programación Lineal Discreta (LPD). Este tipo de modelización se utiliza comúnmente en problemas de programación lineal donde hay varias variables booleanas y restricciones de precedencia.

### Variables:
1. **x_i** = 1 si la actividad i es iniciada en el día i.
2. **y_j** = 1 si la actividad j es iniciada después de la actividad i.

### Restricciones:

1. **Precedencia**:
   - Si A está previa a B, entonces x_A + x_B ≥ 1.
   - Si B está previa a C, entonces x_B + x_C ≥ 1.
   - Si C está previa a D, entonces x_C + x_D ≥ 1.
   - Si D está previa a E, entonces x_D + x_E ≥ 1.

2. **No Superposición**:
   - Si C y D deben realizarse con el mismo especialista, entonces x_C + x_D ≤ 1.

3. **Inicio de Actividades**:
   - x_0 = 0 (no se puede iniciar en el día 0).
   - x_i ≥ 0 para todos los días i.

4. **Finalización de Actividad E**:
   - x_E = 1 (E terminará en el último día).

5. **Variables Binarias**:
   - y_i = 1 si la actividad i es iniciada después de la actividad i-1.

### Modelo Matemático:

La función objetivo es minimizar el número de días hasta la finalización de E, que es igual a la suma de todas las variables x_i.

\[
\text{Minimize} \quad \sum_{i=0}^{n} x_i
\]

Donde n es el número total de días considerados.

### Formulación:

Aquí tienes una forma abstracta de cómo podrías escribir esta formulación en Python usando la librería PuLP:

ˋˋˋpython
from pulp import *

# Definir los datos
durations = [2, 3, 2, 4, 3]
precedences = {
    ('A', 'B'): True,
    ('B', 'C'): True,
    ('C', 'D'): True,
    ('D', 'E'): True,
}

# Crear el problema de programación lineal
prob = LpProblem("Project Planning", LpMinimize)

# Variables
x = LpVariable.dicts('x', range(6), lowBound=0, upBound=None, cat='Binary')
y = LpVariable.dicts('y', range(6), lowBound=0, upBound=None, cat='Binary')

# Función objetivo: Minimizar el número de días hasta la finalización de E
prob += lpSum(x[i] for i in range(6))

# Restricciones
for i, precedence in enumerate(precedences):
    if precedence[0] == 'A':
        prob += x[i+1] >= x[i] + 1
    elif precedence[0] == 'B':
        prob += x[i+1] >= x[i] + 1
    elif precedence[0] == 'C':
        prob += x[i+1] >= x[i] + 1
    elif precedence[0] == 'D':
        prob += x[i+1] >= x[i] + 1

# No superposición de C y D
prob += x['C'] + x['D'] <= 1

# Inicio de actividades
prob += x[0] == 0

# Finalización de E
prob += x[-1] == 1

# Resolver el problema
prob.solve()

# Imprimir resultados
print(f"El proyecto terminará en el día {value(prob.objective)}")
ˋˋˋ

Este código define las variables, establece las restricciones y resuelve el problema utilizando PuLP, una biblioteca de Python para la programación lineal. La salida proporcionará el día exacto en que el proyecto se terminará, minimizando el número de días hasta la finalización de E.
```

</details>

**QLoRA — 0.40/5** (decisiones 0.0, objetivo 2.0, restricciones 0.0, álgebra 0.0, generalización 0.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(A\): actividades.
\(P\subseteq A\times A\): pares de precedencia.
\(C=\{(a,a)\in A\times A:a\le b,\ a,b\in P\}\): círculo de precedencia.
\(K=\{(a,a)\in A\times A:a<b,\ a,b\in P\}\): círculo opuesto al de precedencia.
\(D=\{(a,b)\in A\times A:a\le b,\ (a,b)\notin P\}\cup(K\times A)\): no superposición.

Parámetros:
\(d_a\): duración de \(a\).
\(s_{ab}\in\{0,1\}\): vale 1 si \(a\) precede a \(b\), \(s_{ba}=1-s_{ab}\) y \(s_{aa}=-1\).

Variables de decisión:
\(x_a\in\{0,1\}\): vale 1 si \(a\) comienza en el instante \(x\).
\(y\in\mathbb Z^{+}\): instante de terminación del proyecto.

Función objetivo:
\[
\min y
\]

Restricciones:
\[
\sum_{a\in A}x_a=5
\]
\[
\sum_{a\in A}s_{ab}x_b\ge1 \qquad \forall a\in A
\]
\[
x_a+x_b\le1 \qquad \forall(a,b)\in K
\]
\[
x_a+x_b-y\le-d_a+d_b \qquad \forall(a,b)\in D
\]
```

</details>

Observación del juez sobre QLoRA: La formulación no representa correctamente las precedencias (R2), la no superposición entre C y D (R3), ni el makespan (R4). Las variables de decisión no son adecuadas para modelar tiempos de inicio y el orden entre C y D. Las restricciones son inválidas o no identificables.

---

## diagnostico-oftalmo

### Centros oftalmológicos (caso de la Entrega 1, fuera de la media)

Es el caso que motivó el proyecto. Se reporta aparte porque se conocía antes del entrenamiento y porque las familias de localización están en los datos de entrenamiento.

**Baseline — 0.65/5** (decisiones 0.0, objetivo 0.0, restricciones 1.0, álgebra 1.0, generalización 1.0)

<details><summary>Ver respuesta</summary>

```text
### Modelo Matemático

#### Conjuntos Definidos:
- **L**: Lista de posibles sitios para construir los centros (Barrio Norte, Los Carrera, Collao).
- **S**: Lista de sectores de demanda (Concepción Centro, Sector Lomas, Costanera, Barrio Universitario, Nonguén).

#### Parámetros:
- \(d_{ij}\): Distancia en kilómetros entre el sitio \(i\) y el sector \(j\), donde \(i \in L\) y \(j \in S\).
- \(p_j\): Población en miles de personas del sector \(j\), donde \(j \in S\).

#### Variables de Decisión:
- \(x_{ij} = \begin{cases}
   1 & \text{si el sector } j \text{ está asignado al sitio } i \\
   0 & \text{en caso contrario}
\end{cases}\)

#### Función Objetivo:
Minimizar la suma total de las distancias de atención:

\[ \min \sum_{i \in L} \sum_{j \in S} d_{ij} x_{ij} p_j \]

#### Restricciones Necesarias:
1. **Cuantos Centros Se Instalan**:
   - Solo se instala exactamente 2 centros.

   \[ \sum_{i \in L} x_{ij} = 2 \quad \forall j \in S \]

2. **Asignación de Sectores a Centros**:
   - Cada sector debe estar asignado a un único centro.

   \[ \sum_{i \in L} x_{ij} = 1 \quad \forall j \in S \]

3. **No Asignación de Sector a Sitio Sin Construir**:
   - Un sector no puede ser asignado a un sitio si ese sitio aún no fue construido.

   \[ x_{ij} = 0 \quad \forall i \notin L, j \in S \]

4. **Distancia Máxima Permitida**:
   - Las distancias deben cumplirse con ciertos límites establecidos.

   \[ d_{ij} \leq D_i \quad \forall i \in L, j \in S \]
   Donde \(D_i\) es una constante máxima permitida para la distancia entre el sitio \(i\) y el sector \(j\).

### Ejemplo de Formulación Matemática

Supongamos que los valores de las distancias \(d_{ij}\) y las poblaciones \(p_j\) están disponibles. Entonces, la formulación sería algo así:

ˋˋˋplaintext
minimize sum(d_ij * x_ij * p_j for i in L and j in S)
subject to
    sum(x_ij for i in L and j in S) == 2
    sum(x_ij for i in L and j in S) == 1 for all j in S
    sum(x_ij for i in L and j in S) == 0 for all i not in L and j in S
    d_ij <= D_i for all i in L and j in S
ˋˋˋ

Donde \(D_i\) es una lista de constantes máximas permitidas para las distancias.

Este modelo matemático permite encontrar la combinación óptima de sitios para construir los centros y asignar los sectores de manera que minimice la distancia de atención, teniendo en cuenta la población de cada sector.
```

</details>

**QLoRA — 3.85/5** (decisiones 5.0, objetivo 0.0, restricciones 5.0, álgebra 5.0, generalización 4.0)

<details><summary>Ver respuesta</summary>

```text
Conjuntos:
\(I\): sitios potenciales.
\(J\): sectores de demanda.

Parámetros:
\(d_{ij}\): distancia entre el sitio \(i\) y el sector \(j\).
\(p_j\): población del sector \(j\).

Variables de decisión:
\(y_i\in\{0,1\}\): vale 1 si se selecciona el sitio \(i\).
\(x_{ij}\in\{0,1\}\): vale 1 si el sector \(j\) se asigna al sitio \(i\).

Función objetivo:
\[
\min \sum_{i\in I}\sum_{j\in J}d_{ij}x_{ij}
\]

Restricciones:
\[
\sum_{i\in I}y_i=2
\]
\[
\sum_{i\in I}x_{ij}=1 \qquad \forall j\in J
\]
\[
x_{ij}\le y_i \qquad \forall i\in I,\ \forall j\in J
\]
```

</details>
