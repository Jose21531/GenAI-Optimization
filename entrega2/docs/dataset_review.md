# Revisión independiente del dataset OR-SFT v1.2

La revisión permite usar este conjunto como **primer experimento de adaptación al formato paramétrico**, con límites explícitos. No demuestra generalización amplia ni certifica que todas las instancias numéricas sean factibles.

## Verificado en esta sesión

- Los 11 archivos del manifiesto SHA256 coinciden con el ZIP recibido.
- 1050 problemas distintos; 50 familias con 21 ejemplos cada una.
- 315 LP y 735 MILP; dificultad declarada: 168 básicos, 546 intermedios y 336 difíciles.
- 50 respuestas diferentes: cada familia tiene una única formulación canónica, repetida 21 veces.
- 875 textos distintos después de sustituir todas las cifras por un marcador; este conteo no es una medida de diversidad semántica.
- Roles, enunciados y respuestas de los splits coinciden exactamente con la versión rica.
- 840/210 por familias sin IDs ni familias compartidas. Pilot 200 con cuatro registros por familia.
- Tokenizer real `Qwen/Qwen2.5-1.5B-Instruct`, revisión `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`: media 581.11, p95 778.55, p99 914.51 y máximo 930 tokens por conversación. **1024 basta para los 1050 ejemplos**, sin truncamiento.
- La máscara revisada recupera exactamente el texto assistant de los 1050 registros; todos incluyen EOS supervisado. Entre 120 y 387 tokens assistant por ejemplo, media 232.56.

Estas últimas comprobaciones se ejecutaron en CPU; no equivalen a entrenar el modelo.

## Revisión matemática y diversidad

Se inspeccionaron enunciado y referencia de una muestra de cada una de las 50 familias y las formulaciones del catálogo. Cubren recursos y mezclas, flujos simples y múltiples, asignación, apertura, cobertura, selección, inventario, secuenciación, rutas, grafos y energía. Las referencias separan apropiadamente decisiones continuas, enteras y binarias y presentan formulaciones compactas apropiadas para SFT.

Hay diversidad de familias, pero menos diversidad estructural que 50 problemas independientes: product mix y crop planning tienen la misma estructura básica; dotación cíclica y turnos comparten una cobertura entera; job shop y scheduling de proyectos usan precedencias y disyunciones similares. El split excluye etiquetas de familia, no todas las estructuras relacionadas. Conviene describir la validación como transferencia a familias nominalmente no vistas.

La dificultad es constante dentro de cada familia (un único valor para sus 21 ejemplos). No hay evidencia de que cada familia cubra varios niveles, pese a lo sugerido en el contexto. Cambiar cantidades y frases iniciales enseña invariancia numérica y formato, pero no enseña por sí mismo a decidir cuándo añadir o quitar una restricción. Algunas topologías y conjuntos permanecen fijos.

## Matices de las referencias

| Familias | Hallazgo y alcance |
|---|---|
| F44, F46, F47 | Big-M se declara «suficientemente grande», sin una cota construida. Para implementar un solver hace falta especificar horizonte y una cota válida. Bajo los supuestos actuales de disponibilidad inicial y ausencia de ventanas, la suma de duraciones da un horizonte que contiene un óptimo; agregar límites de finalización hace explícita su justificación. No afirmar equivalencia del conjunto factible con todos los horarios arbitrariamente tardíos. |
| F30, F31, F32, F48, F49 | Los balances usan t-1: es conveniente explicitar T={1,...,H}, condiciones iniciales y unidades. El enunciado entrega las condiciones iniciales; las referencias las parametrizan. |
| F49 | v>=u_t-u_(t-1) fuerza un arranque real. Con costos de arranque positivos, minimizar evita arranques espurios en el óptimo. La equivalencia lógica exacta de v requiere además v<=u_t y v<=1-u_(t-1). Es una distinción entre validez óptima y semántica de todas las soluciones factibles. |
| F19 | z<=cobertura y pesos positivos permite recuperar la cobertura verdadera al maximizar; la igualdad lógica de z fuera del óptimo no queda completamente forzada. Es una formulación de optimización estándar. |
| F48 | La ausencia de exclusividad carga/descarga está expresamente solicitada: no añadir binarias sería correcto. Es recomendable declarar períodos horarios para compatibilizar potencia y energía. |
| F50 | «Consumo de tierra por hectárea» usa coeficientes distintos de uno. El álgebra reproduce esos coeficientes, pero la interpretación física es ambigua si toda la tierra está medida en hectáreas homogéneas; debe aclararse la unidad o corregirse en una versión futura antes de un nuevo estudio. |

No se modificó el ZIP original ni se ajustaron ejemplos a partir del benchmark. Estos matices no justifican afirmar «cero errores matemáticos certificados»; sí justifican documentar el alcance del primer ensayo. Para este experimento se conserva v1.2 y sus hashes, evitando mezclar versiones con un entrenamiento previo. Una futura ampliación debe variar requisitos y sus etiquetas conjuntamente, con revisión matemática, no solo parafrasear los mismos targets.

La auditoría histórica del ZIP declara factibilidad F43/F49 y baja similitud textual con el benchmark. Aquí se verificó la integridad de esos archivos, pero no se reprodujo su generador original ni esa metodología de similitud. No presentar sus cifras como una nueva medición independiente.

## Reproducción

`python scripts/audit_dataset.py` genera la auditoría estructural y el CSV por familia.
`python scripts/verify_tokenizer_and_metric.py` verifica las longitudes, máscara y agregación exacta de los 32 juicios históricos. Requiere las dependencias CPU indicadas en el README.
