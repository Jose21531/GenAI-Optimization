# Bitácora del rol C · verificación y evaluación

## 2026-10-30 · Ajustes de revisión del PR #9

Se declara un perfil GPU para Entrega 3: torch 2.6.0+cu124 y sus versiones
compatibles de torchvision/torchaudio. No consta la versión histórica de torch
de Entrega 2 y no se le atribuye este perfil. El cargador comprueba la versión
cargada y conserva la exigencia de Colab T4 de AGENTS.md.

Se añadió `recover-jsonl`, explícito, para respaldar y retirar únicamente una
cola truncada sin salto final. Las líneas intermedias inválidas siguen siendo
errores. Se preservan las últimas líneas válidas sin salto al seguir escribiendo.
Las claves id/judge_v2_raw faltantes se rechazan con ValueError y el CLI también
presenta un diagnóstico para KeyError. Se documentó cómo recuperar y reanudar.

El README principal incluye ahora ambas suites CPU. Validación: 136 pruebas,
98 existentes y 38 de evaluación, sin cargar pesos ni ejecutar el perfil GPU.

## 2026-10-30 · Evaluación posterior FOM-5 v2

Se implementó `eval/` reutilizando sin cambios el núcleo de la celda 15 y la
calibración de la celda 16 del notebook de Entrega 2. Se verifican sus huellas
y las de los datos/CSV publicados; se reproducen los 60 puntajes archivados,
las medias 0,5884 / 0,8024 y el bootstrap pareado publicado.

El evaluador consume RunResult JSONL por variante y sidecars de procedencia,
conserva todos los estados de generación, calibra antes de evaluar, registra
intentos del juez y reanuda checkpoints compatibles. Oficial exige las cinco
variantes, 30 IDs, configuración congelada y tag v3-freeze con código coincidente.
MockJudge solo sirve para pruebas de desarrollo y queda identificado como mock.

Se agregó exportación de trazas del piloto para revisar falsos positivos del
auditor con etiquetas humanas; no_verificado no se convierte en falso positivo.
El flujo rechaza trazas oficiales para impedir calibrar con el benchmark.

Validación inicial CPU: 125 tests, 98 existentes y 27 de evaluación. No se cargó
Qwen3 ni se generaron resultados oficiales nuevos. Instrucciones e interfaz con
A en `eval/README.md`.

La implementación de C queda preparada para revisión. Faltan el piloto real
T4, la elección/fijación conjunta de configuración y la evaluación oficial
posterior. Esas etapas requieren los resultados y trazas de infraestructura;
no se crea un congelamiento antes del piloto.
