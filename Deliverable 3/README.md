# Entrega 3 · Sistema de agentes para formulación LP/MILP

Esta carpeta contiene la estructura inicial del sistema. **Aún no hay una corrida de agentes ni resultados de la Entrega 3.** La implementación se repartirá entre infraestructura, generación y verificación conforme a [AGENTS.md](../AGENTS.md).

La entrada es un enunciado en español. La salida evaluable conserva exactamente el formato textual de la columna `candidate` de la [Entrega 2](../Deliverable%202/): `Conjuntos`, `Parámetros`, `Variables de decisión`, `Función objetivo` y `Restricciones`. El sistema formula el problema; no obtiene el óptimo.

```mermaid
flowchart LR
    E[Enunciado] --> A[Analista]
    A -->|cantidades y unidades| X[extract_data_spans]
    X -->|fragmentos| A
    A -->|ProblemSpec| F[Formulador]
    F -->|candidate| V[Verificador]
    V -->|CoverageMap| T[audit_model]
    T -->|observaciones| V
    V -->|revisión: máx. una| F
    F -->|aclaración: máx. una| A
    V -->|aceptar o detener| S[Formulación final + traza]
```

Los mensajes de control y cobertura se guardan separados de `candidate`. El contrato completo está en [docs/contratos.md](docs/contratos.md); las decisiones y cuestiones pendientes están en [docs/decisiones.md](docs/decisiones.md).

| Ruta | Propósito |
|---|---|
| `agents/`, `tools/` | Agentes y herramientas de cada responsable. |
| `prompts/` | Un archivo versionado por agente y revisión. |
| `config/` | Configuración de desarrollo y, después del piloto, configuración congelada. |
| `data/benchmark_30_generation_only.jsonl` | Los 30 enunciados, sin referencia ni requisitos oficiales. |
| `dev_cases/` | Ocho casos nuevos para desarrollar y congelar prompts. |
| `eval/` | Evaluación posterior con FOM-5 v2, separada de los agentes. |
| `results/`, `traces/` | Salidas por variante y mensajes completos por entrada. |
| `informe/` | Informe final de una página en LaTeX y PDF. |

El modelo base, el adapter y los resultados archivados se obtienen desde la Entrega 2 publicada. El conjunto con referencias oficiales se abre únicamente en la etapa de evaluación. Las instrucciones de reproducción de la corrida y del video se completarán cuando exista un sistema ejecutable.
