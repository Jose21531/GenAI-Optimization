# GenAI-Optimization

Segundo entregable del proyecto de **Generative Artificial Intelligence (580694)**.

El proyecto aborda la **formulación automática de modelos de optimización desde lenguaje natural**.  
El modelo principal del segundo entregable es **Qwen2.5-1.5B-Instruct** y la ejecución se realiza en **Google Colab con GPU**.

## Ejecutar en Google Colab

El notebook principal del proyecto es:

`Deliverable2.ipynb`

Una vez publicado este repositorio en GitHub, reemplaza `TU_USUARIO` en el enlace siguiente por el nombre de usuario u organización que contiene el repositorio:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jose21531/GenAI-Optimization/blob/main/Deliverable2.ipynb)

También puede abrirse manualmente desde Google Colab:

1. Ir a **File / Archivo → Open notebook / Abrir cuaderno**.
2. Seleccionar la pestaña **GitHub**.
3. Buscar el repositorio `GenAI-Optimization`.
4. Abrir `Deliverable2.ipynb`.
5. Seleccionar un entorno con GPU.
6. Ejecutar las celdas del notebook en orden.

## Estructura

```text
GenAI-Optimization/
├── README.md
├── Deliverable2.ipynb
├── requirements.txt
└── Deliverable2.pdf
```

`Deliverable2.pdf` corresponde al documento técnico de una página y se incorporará al repositorio una vez finalizado.

## Dependencias

Las dependencias principales están indicadas en `requirements.txt`.

En Google Colab pueden instalarse mediante:

```python
!pip install -r requirements.txt
```

> Nota: si el notebook se abre directamente desde GitHub en Colab, solo se abre el `.ipynb`; no se clona automáticamente el repositorio completo. Si el notebook necesita leer `requirements.txt` u otros archivos del repositorio durante la ejecución, conviene clonar el repositorio primero. Mientras el notebook sea autocontenido, puede ejecutarse directamente.
