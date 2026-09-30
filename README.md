# GenAI-Optimization

Proyecto de **Generative Artificial Intelligence (580694)**: convertir enunciados de programación lineal y entera mixta en formulaciones matemáticas paramétricas, sin resolver la instancia.

La [Entrega 1](deliverables/Deliverable1.pdf) diagnostica errores de índices, apertura de centros y restricciones contradictorias en modelos pequeños. La **Entrega 2** conserva Qwen2.5-1.5B-Instruct y estudia un ajuste QLoRA en una GPU Tesla T4. Los experimentos, los datos, la evaluación FOM-5 v2 y los resultados medidos están documentados en [entrega2/README.md](entrega2/README.md). El informe de una página se compila desde [LaTeX](entrega2/report/entrega2.tex); el PDF con el enlace del video se añadirá después de la grabación.

Para reproducir la demostración se abre [el notebook de generación](entrega2/notebooks/02_generacion_final_31.ipynb) en Colab con T4, se monta Drive con el paquete y el adapter indicados en el README de Entrega 2, y se activa la celda final `RUN_LIVE_DEMO=True`. Esa celda ejecuta el baseline directo y el adapter sobre el mismo caso oftalmológico fijado en Entrega 1; guarda sus salidas y tiempos. La comparación de 30 casos usa las respuestas congeladas del baseline y el juez original, no selecciona una muestra favorable.

El notebook [`notebooks/Deliverable2.ipynb`](notebooks/Deliverable2.ipynb) se conserva como versión anterior del trabajo. La ejecución controlada y los manifiestos verificables están en `entrega2/`.
