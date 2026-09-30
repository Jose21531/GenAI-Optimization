# Falla real después de QLoRA: localización oftalmológica

Caso fijado antes del entrenamiento por la Entrega 1. No pertenece a la media principal de 30 casos.

## Enunciado exacto

En la ciudad de Concepción se requiere construir 2 centros oftalmológicos para atender las consultas médicas de la población. Existen 3 lugares potenciales donde estos centros pueden ser ubicados: Barrio Norte, Los Carrera y Collao.

Debido al tamaño de la zona, la comuna se ha dividido en 5 sectores de demanda: Concepción Centro, Sector Lomas, Costanera, Barrio Universitario y Nonguén. La población de cada sector, expresada en miles de personas, es la siguiente: Concepción Centro tiene 30 mil habitantes, Sector Lomas 15 mil, Costanera 5 mil, Barrio Universitario 2 mil y Nonguén 10 mil habitantes.

Las distancias entre los lugares potenciales para construir los centros y los sectores de demanda se expresan en kilómetros. Desde Barrio Norte, las distancias son de 1,3 km a Concepción Centro, 0,5 km a Sector Lomas, 2,5 km a Costanera, 2,0 km a Barrio Universitario y 3,0 km a Nonguén.

Desde Los Carrera, las distancias son de 0,3 km a Concepción Centro, 2,0 km a Sector Lomas, 1,2 km a Costanera, 1,0 km a Barrio Universitario y 1,9 km a Nonguén.

Finalmente, desde Collao, las distancias son de 1,6 km a Concepción Centro, 2,3 km a Sector Lomas, 2,1 km a Costanera, 1,5 km a Barrio Universitario y 0,4 km a Nonguén.

Se debe formular un modelo matemático que permita determinar cuáles 2 de los 3 lugares potenciales deben seleccionarse para instalar los centros oftalmológicos y cómo asignar los sectores de demanda a estos centros, buscando minimizar la distancia de atención considerando la población de cada sector.

Para la formulación del modelo, se deben definir los conjuntos, parámetros y variables de decisión, plantear la función objetivo correspondiente e incorporar las restricciones necesarias para garantizar que cada sector sea atendido por un único centro, que los sectores solo puedan ser asignados a centros que hayan sido construidos y que se instalen exactamente 2 centros oftalmológicos.

## Baseline directo determinista recuperado

FOM-5 v2 histórico: 0.650/5.

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

```plaintext
minimize sum(d_ij * x_ij * p_j for i in L and j in S)
subject to 
    sum(x_ij for i in L and j in S) == 2
    sum(x_ij for i in L and j in S) == 1 for all j in S
    sum(x_ij for i in L and j in S) == 0 for all i not in L and j in S
    d_ij <= D_i for all i in L and j in S
```

Donde \(D_i\) es una lista de constantes máximas permitidas para las distancias.

Este modelo matemático permite encontrar la combinación óptima de sitios para construir los centros y asignar los sectores de manera que minimice la distancia de atención, teniendo en cuenta la población de cada sector.

## QLoRA final, generación nueva

FOM-5 v2: 3.85/5. Tokens: 232; latencia: 18.4 s.

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

## Qué sigue mal

El adapter sí introduce la variable binaria de apertura, la asignación única y el vínculo $x_{ij}\le y_i$. Sin embargo, define $p_j$ y luego no lo multiplica en el objetivo: minimiza $\sum_{ij}d_{ij}x_{ij}$ en lugar de $\sum_{ij}p_jd_{ij}x_{ij}$. Por tanto, pondera igual todos los sectores y puede seleccionar centros distintos. No es una formulación matemáticamente equivalente.
