# Evaluación FOM-5 v2 · rol C

Este paquete evalúa formulaciones **después** de generarlas. Qwen3-14B es un
juez externo; no se importa desde los agentes, herramientas u orquestador.
El código de C queda implementado; el piloto GPU y el experimento completo
requieren la integración ejecutable de infraestructura y sus salidas.

## Qué se conserva de Entrega 2

`vendor/fom5_v2.py` es una copia textual de la celda 15 de
`Deliverable 2/Deliverable_2.ipynb`, sin cambiar el prompt, extractor, validación,
agregación, pesos, caps, decodificación ni reintentos del juez. La calibración
se extrajo de la celda 16: opt_02, opt_10, opt_14 y opt_16 del baseline archivado,
con techos 2,8; 1,5; 1,5 y 1,8. No se vuelve a generar baseline ni QLoRA.

`legacy.py` verifica huellas fijas antes de cargar las funciones. La parte pura
usa los mismos objetos globales que el notebook. La función de inferencia se
carga con su decorador original solo cuando se proporciona el backend. Las
envolturas de observación registran mensajes, respuestas y errores, sin cambiar
los argumentos ni el flujo de reintentos.

El backend conserva Qwen/Qwen3-14B, revisión
`40c069824f4251a91eefaf281ebe4c544efd3e18`, NF4 con doble cuantización, fp16,
device_map 0, thinking desactivado cuando la plantilla lo admite, 12.000 tokens
de entrada máximos y 600 de salida. Un prompt demasiado largo falla; no se trunca.

## Verificación CPU disponible ahora

Desde la raíz del repositorio:

```powershell
python -m pip install -r "Deliverable 3/eval/requirements.txt"
python "Deliverable 3/eval/run_eval.py" verify-archives
python -m unittest discover -s "Deliverable 3/tests"
python -m unittest discover -s "Deliverable 3/eval/tests"
```

El primer comando de evaluación verifica los SHA-256 del benchmark y los dos
CSV publicados, recalcula los 60 puntajes desde sus JSON de juez y reproduce la
comparación pareada. Excluye la fila diagnóstica de Entrega 1 de las medias.
El informe `archive_validation.json` documenta esta comprobación offline; no es
una nueva corrida. No se copian datos, respuestas archivadas ni pesos pesados.

La validación inicial reúne 98 pruebas existentes y 27 de evaluación, 125 en
total, en Python 3.14. Incluye interrupciones, calibración fallida, checkpoints
duplicados/truncados, identidad de candidatos, congelamiento, protocolo original
del backend y revisión humana del auditor. No carga pesos reales.

## Contrato con infraestructura

Por variante, run.py debe guardar un JSONL con **todos** sus `RunResult` de
`schemas.py`, tal como los devuelve el orquestador. Cada fila tiene
`problem_id`, `variant`, `final_text`, `status` y las métricas correspondientes.
No se sustituyen IDs ni se rellenan candidatos después de la generación.
Las salidas fallidas se conservan y se evalúan; no se excluyen de la media.

Para desarrollo se requieren los ocho IDs dev01..dev08. Para el experimento
oficial, exactamente los 30 IDs opt_01..opt_30 en cada una de las cinco variantes:
full, no_evidence, no_plan, no_audit y no_review. Se rechazan duplicados,
variantes mezcladas y conjuntos incompletos.

Después de guardar las salidas, ejecutar el subcomando `manifest` para crear un
sidecar `<predictions>.manifest.json`. Debe ejecutarse con el mismo código y
configuración que generaron esos archivos. Guarda la identidad del archivo,
los enunciados y la configuración/código de generación. No demuestra por sí
solo que el modelo produjo una respuesta correcta ni sustituye las trazas.
Si se cambia la configuración de un piloto, evaluar cada conjunto con su
configuración correspondiente; no mezclar archivos de distintas corridas.

Ejemplo de desarrollo, suponiendo que A ya generó sus ocho salidas:

```powershell
python "Deliverable 3/eval/run_eval.py" manifest --mode development --variant full --predictions "Deliverable 3/results/pilot/full.jsonl"
python "Deliverable 3/eval/run_eval.py" preflight --mode development --source "full=Deliverable 3/results/pilot/full.jsonl"
```

Se puede probar el transporte y los checkpoints con
`evaluate --mode development --source full=RUTA --output DIRECTORIO --mock`.
Los puntajes de MockJudge son sintéticos: quedan rotulados `execution_kind=mock`,
`valid_experiment=false` y `official_result=false`. No sirven para medir calidad
ni para dar por validado el juez real. `--mock` está prohibido en modo oficial.

## Piloto real en Colab T4

1. Infraestructura genera los ocho casos con Qwen2.5-1.5B y guarda resultados y
   trazas. Comparar el adapter del Verificador encendido/apagado en corridas
   identificadas; conservar los mismos límites y prompts salvo el factor probado.
2. Guardar archivos y manifiestos. Liberar el modelo de generación o reiniciar
   el runtime, conservando los archivos y el checkout/configuración pertinentes.
   Instalar `eval/requirements-gpu.txt` en una T4 de Colab. No mantener los dos
   modelos cargados a la vez.
3. Ejecutar `evaluate --mode development --source full=RUTA --output DIRECTORIO`
   sin `--mock`. Antes de los casos de desarrollo se ejecuta la calibración
   original del juez. Si falla, se detiene sin ajustar sus techos o prompt.
4. Revisar decisiones y errores matemáticos. Para el auditor, exportar los
   hallazgos desde las trazas:

```powershell
python "Deliverable 3/eval/run_eval.py" audit-review --trace "Deliverable 3/traces/pilot-dev01.jsonl" --output "Deliverable 3/results/pilot/audit_review.jsonl"
```

`--trace` se puede repetir para los ocho casos. Completar `assessment` con
`true_positive`, `false_positive` o `uncertain` y explicar el motivo en
`review_note`. Los `no_verificado` se conservan como `unverified`. No se deben
editar los hallazgos originales. El resumen se obtiene con:

```powershell
python "Deliverable 3/eval/run_eval.py" audit-summary --annotations "Deliverable 3/results/pilot/audit_review.jsonl"
```

Este flujo rechaza trazas oficiales: no se calibra el auditor con el benchmark.
La precisión se informa solo sobre etiquetas humanas verdaderas/falsas,
mostrando por separado inciertos y no verificados. No cambia severidades de
forma automática. La elección final y sus limitaciones deben registrarse antes
del congelamiento.

## Evaluación oficial después de congelar

El equipo debe terminar el piloto, copiar la configuración elegida a
`config/frozen.yaml`, declarar sus prompts y crear el tag `v3-freeze`. El
evaluador verifica que el tag sea ancestro del checkout y que configuración,
prompts y módulos de generación coincidan con el tag. Rechaza cambios posteriores
y exige que model.py, orchestrator.py y run.py estén integrados. Este paquete
no crea el tag ni el archivo congelado para eludir esos pasos.

Después de generar las cinco variantes, crear cada manifiesto, por ejemplo:

```powershell
python "Deliverable 3/eval/run_eval.py" manifest --mode official --variant full --predictions "Deliverable 3/results/full/outputs.jsonl"
```

Repetir para las otras cuatro variantes, con su nombre y ruta. Evaluar en un
runtime de Colab T4 dedicado al juez:

```powershell
python "Deliverable 3/eval/run_eval.py" evaluate --mode official --source "full=Deliverable 3/results/full/outputs.jsonl" --source "no_evidence=Deliverable 3/results/no_evidence/outputs.jsonl" --source "no_plan=Deliverable 3/results/no_plan/outputs.jsonl" --source "no_audit=Deliverable 3/results/no_audit/outputs.jsonl" --source "no_review=Deliverable 3/results/no_review/outputs.jsonl" --output "Deliverable 3/results/evaluation-official"
```

`preflight` acepta los mismos argumentos de modo/fuentes y comprueba entradas
sin cargar el juez. Cada ejecución real conserva su entorno y las huellas de
los artefactos, el juez y la calibración. Los pesos se descargan solo al ejecutar
la evaluación real y solo después del preflight.

## Artefactos, reanudación y lectura

El directorio de evaluación contiene:

- `evaluation.json`: identidad, datos de procedencia y estado running/failed/complete.
- `calibration-<id>.jsonl`: los cuatro juicios de calibración de cada sesión.
- `judge_calls.jsonl`: mensajes y respuestas disponibles de cada intento, incluidos errores.
- `<variante>/judgments.jsonl`: checkpoint de juicios completos por ID, con candidato y métricas.
- `<variante>/scored.csv`: exportación legible de todos los casos de la variante.
- `summary.json`: medias, ceros, estados/costos de generación y diferencias pareadas.

Para reanudar, repetir exactamente el comando con los mismos archivos y
directorio. Se valida identidad y contenido de checkpoints antes de llamar al
juez. Se repite la calibración y se evalúan solo los IDs pendientes. Un fallo
del juez no recibe un puntaje inventado. Un checkpoint truncado o manipulado
se rechaza y requiere inspección; no se borra ni repara silenciosamente.

Leer el resumen solo si `evaluation.json` está complete y comprobar mode y
execution_kind. Las comparaciones oficiales usan los puntajes archivados de
baseline/QLoRA y comparan además cada ablación con full sobre los mismos IDs.
Se usa el bootstrap pareado original: semilla 42, 10.000 remuestreos e IC 95 %.
Las comparaciones son descriptivas; un intervalo que incluya cero no demuestra
una mejora. No se seleccionan prompts con resultados oficiales.

## Estado de cierre de C

La implementación de C incluye Verificador, prompts, auditoría y evaluación
posterior, pruebas y protocolo de piloto. El cierre experimental requiere aún
ejecutar y revisar el piloto T4, fijar la configuración del equipo y, después
del congelamiento, obtener los juicios reales de las cinco variantes. No hay
puntajes nuevos oficiales de Entrega 3 ni una validación GPU atribuida a estas
pruebas CPU.
