# GenAI-Optimization

Formulación matemática LP/MILP desde enunciados en español con un modelo pequeño. Proyecto de Inteligencia Artificial Generativa (580694), Universidad de Concepción.

| Entrega | Material principal |
|---|---|
| [Deliverable 1](Deliverable%201/) | [Informe](Deliverable%201/Grupo1_GenAI.pdf) y [notebook original](Deliverable%201/Deliverable_1.ipynb). Diagnóstico del caso oftalmológico. |
| [Deliverable 2](Deliverable%202/) | [Informe de una página](Deliverable%202/report/informe.pdf), [código y datos](Deliverable%202/README.md), [respuestas y juicios](Deliverable%202/outputs/). |

**[Abrir Deliverable 2 en Google Colab](https://colab.research.google.com/github/Jose21531/GenAI-Optimization/blob/main/Deliverable%202/Deliverable_2.ipynb)** · Seleccionar T4 GPU.

El notebook descarga los datos y el **adapter QLoRA entrenado** desde este repositorio y verifica sus hashes: **no requiere nuestro Gmail ni Drive**. La sección 2 muestra la evaluación pareada de los mismos 30 problemas: **0.5884 → 0.8024/5**, con 14 mejoras, 8 empates y 8 degradaciones. El baseline se tomó de las respuestas oficiales guardadas: no se volvió a ejecutar para producir esa media. El mismo notebook también permite **volver a generar los 30 problemas con cada variante** (sección 4) y evaluarlos después con FOM-5 v2 (sección 6), guardando los resultados nuevos por separado. La sección 5 ejecuta dos inferencias nuevas sobre el caso de Entrega 1 y muestra los textos lado a lado; la sección 7 permite volver a entrenar desde los 1050 ejemplos públicos.

Para reproducir la demostración del video: abrir el enlace Colab con una T4, ejecutar las secciones 1 y 2, cargar el modelo y el adapter público en la sección 3, omitir la ejecución larga opcional de la sección 4 y ejecutar la celda de generación de la sección 5. La celda siguiente muestra ambas respuestas lado a lado. Los puntajes 0.650 y 3.850 del caso diagnóstico corresponden a respuestas archivadas, no a las dos inferencias nuevas de esa celda.

El [README de Deliverable 2](Deliverable%202/README.md) explica el origen de cada archivo, las limitaciones y cómo reconstruir datos y resultados. El video de pantalla se añadirá aquí tras grabar la ejecución real; el enunciado exige mostrar la generación visible y trazable al código del repositorio.
