# GenAI-Optimization

Formulación matemática LP/MILP desde enunciados en español con Qwen2.5-1.5B-Instruct. El caso de localización de centros oftalmológicos ilustra la relevancia: omitir la población cambia el objetivo y omitir la apertura de centros permite asignaciones inviables. El proyecto produce borradores paramétricos para revisión matemática.

| Entrega | Contenido |
|---|---|
| [Deliverable 1](Deliverable%201/) | [Diagnóstico y ejemplo original](Deliverable%201/README.md). |
| [Deliverable 2](Deliverable%202/) | [Ajuste QLoRA, benchmark de 30 casos y demostración](Deliverable%202/README.md). |

**[Abrir Deliverable 2 en Colab](https://colab.research.google.com/github/Jose21531/GenAI-Optimization/blob/main/Deliverable%202/Deliverable_2.ipynb)** · [Informe PDF](Deliverable%202/informe.pdf)

Para reproducir el video, selecciona una GPU T4, ejecuta las secciones **1–3** y luego la **4**. Esa celda muestra el enunciado, genera baseline y QLoRA sobre el mismo caso de Entrega 1 y presenta ambas respuestas junto con la formulación de referencia. Las secciones 5–7 reproducen la evaluación extensa y el ajuste completo.

En los **30 casos oficiales**, el promedio FOM-5 v2 fue **0.5884/5** para el baseline y **0.8024/5** para QLoRA: 14 mejoraron, 8 empataron y 8 empeoraron. Los dos CSV con respuestas y juicios por caso están en [Deliverable 2/output](Deliverable%202/output/).
