# Prompts de la Entrega 3

La configuración congelada en [`v3-freeze`](https://github.com/Jose21531/GenAI-Optimization/tree/v3-freeze) selecciona estos archivos:

| Mensaje | Prompt |
|---|---|
| Analista | `analista_v6.md` |
| Analista sin citas (`no_evidence`) | `analista_v6_noevidence.md` |
| Formulador | `formulador_v3.md` |
| Formulador sin plan (`no_plan`) | `formulador_v3_noplan.md` |
| Verificador | `verificador_v10.md` |
| Control del orquestador | `orquestador_v1.md` |

[`config/frozen.yaml`](../config/frozen.yaml) fija la selección exacta y los límites de generación. Las versiones anteriores se conservan porque documentan el desarrollo, son usadas por pruebas y permiten interpretar las decisiones registradas en [`docs/decisiones.md`](../docs/decisiones.md). Los textos de los prompts no se incrustan en Python.
