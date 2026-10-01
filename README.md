# GenAI-Optimization

**Formulación automática de modelos de optimización a partir de enunciados en lenguaje natural, con un modelo de lenguaje pequeño.**

Proyecto semestral de Inteligencia Artificial Generativa (580694), Universidad de Concepción · Grupo 1: Rayen Muñoz, Isidora Rivera, Sebastián Soto y José Luis Erices.

## De qué trata

Muchos problemas de planificación (dónde abrir instalaciones, cómo asignar recursos, cuánto producir, qué rutas usar) se modelan con programación lineal y lineal entera. **Formularlos** exige traducir el enunciado a conjuntos, parámetros, variables, función objetivo y restricciones coherentes entre sí. Un índice mal puesto o una restricción olvidada puede cambiar las decisiones admisibles.

Este proyecto estudia si un modelo de lenguaje **pequeño y abierto**, ejecutable en una GPU T4 de Google Colab, puede producir un **borrador de formulación paramétrica y verificable**. La revisión matemática sigue siendo parte del procedimiento.

- **Entrada:** el enunciado de un problema de optimización lineal o lineal entera, en español y de nivel universitario.
- **Salida:** conjuntos, parámetros, variables con sus dominios, función objetivo y restricciones, escritos con índices coherentes.
- **Modelo:** Qwen2.5-1.5B-Instruct (1.500 millones de parámetros).

## Entregas

| Entrega | Qué contiene | Informe | Código |
|---|---|---|---|
| [Deliverable 1](Deliverable%201/) | Definición de la tarea, comparación de tres modelos candidatos y diagnóstico de por qué fallan con prompting directo. | [PDF](Deliverable%201/Grupo1_GenAI.pdf) | [Notebook](Deliverable%201/Deliverable_1.ipynb) |
| [Deliverable 2](Deliverable%202/) | Intervención con fine-tuning QLoRA, comparación contra el baseline en 30 problemas, caso de falla y demostración. | [PDF](Deliverable%202/informe.pdf) · [LaTeX](Deliverable%202/informe.tex) · [Video](https://drive.google.com/drive/folders/1NwKmSSmr4_v8Gd-W1X92eswox6rcSRxV) | [Notebook](Deliverable%202/Deliverable_2.ipynb) · [Abrir en Colab](https://colab.research.google.com/github/Jose21531/GenAI-Optimization/blob/main/Deliverable%202/Deliverable_2.ipynb) |

## Resultado actual en una línea

En 30 problemas de distintos tipos (producción, redes, localización, rutas, secuenciación…), el ajuste con QLoRA cambió el puntaje medio de **0,5884 a 0,8024 sobre 5** y redujo los casos con puntaje cero de 21 a 12. El intervalo bootstrap del cambio incluye cero y 8 casos empeoraron. El detalle, los límites y la forma de reproducirlo están en el [README de la Entrega 2](Deliverable%202/README.md).
