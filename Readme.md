# JLR-4D

Simulación en Python para analizar el impacto de distintos esquemas de trabajo sobre el rendimiento operativo de equipos de desarrollo de software.

El repositorio contiene dos líneas de simulación:

* **`Simulation.py`**, utilizada como soporte experimental para el artículo.
* **`simulation_4q.py`**, utilizada como soporte de simulación para la tesis y orientada al análisis del enfoque **4Q / 4Q Agile Framework**.

El proyecto permite comparar escenarios vinculados con la jornada laboral reducida y observar cómo varían métricas como tareas completadas, bloqueos, retrabajo, eficiencia de flujo y utilización de capacidad bajo diferentes condiciones de equipo, carga de trabajo, proceso, soporte de IA y eventos organizacionales.

La simulación no pretende reemplazar una validación empírica con equipos reales, sino funcionar como una herramienta experimental para analizar tendencias, riesgos y posibles efectos bajo distintos supuestos de modelado.

## Versiones de la simulación

El repositorio contiene dos versiones principales de la simulación, utilizadas con objetivos distintos.

### `Simulation.py`

Corresponde a la versión de simulación utilizada para el artículo.

Esta versión permite comparar escenarios operativos relacionados con la jornada laboral reducida y analizar métricas como tareas completadas, bloqueos, retrabajo, eficiencia de flujo y utilización de capacidad bajo diferentes condiciones de equipo, carga de trabajo, proceso, soporte de IA y eventos organizacionales.

Su objetivo principal es servir como soporte experimental para el análisis presentado en el artículo.

### `simulation_4q.py`

Corresponde a la versión de simulación utilizada para la tesis.

Esta versión está orientada al análisis del enfoque **4Q / 4Q Agile Framework**, incorporando los elementos conceptuales y operativos definidos para la propuesta metodológica de la tesis.

Su objetivo principal es permitir la evaluación exploratoria del comportamiento del modelo 4Q frente a escenarios comparativos, considerando restricciones de disponibilidad, coordinación, handoff, backlog, reuniones, capacidad operativa y adaptación del proceso.

---

## Qué hace la simulación

El repositorio permite ejecutar simulaciones para analizar el impacto de distintos esquemas de trabajo sobre equipos de desarrollo de software.

A nivel general, las simulaciones:

1. Definen perfiles de equipo, carga de trabajo y condiciones del proceso.
2. Generan tareas con esfuerzo, prioridad, complejidad y día de llegada.
3. Simulan múltiples sprints por experimento.
4. Incorporan eventos organizacionales aleatorios.
5. Calculan métricas operativas por sprint.
6. Exportan resultados detallados y agregados en archivos CSV.
7. Generan visualizaciones en formato PNG para comparar escenarios.

---

## Estructura del repositorio

```text
JLR-4D/
│
├── Simulation.py
├── simulation_4q.py
│
├── simulation_results.csv
├── simulation_summary.csv
├── scenario_summary.csv
├── ai_summary.csv
├── event_summary.csv
│
├── config_team_profiles.csv
├── config_workload_profiles.csv
├── config_process_conditions.csv
├── config_events.csv
│
├── 01_completed_tasks_by_scenario.png
├── 02_blocked_events_by_scenario.png
├── 03_blocked_days_by_scenario.png
├── 04_rework_events_by_scenario.png
├── 05_flow_efficiency_by_scenario.png
├── 06_completed_tasks_over_time.png
├── 07_blocked_days_over_time.png
├── 08_flow_efficiency_over_time.png
├── 09_completed_tasks_by_team.png
├── 10_completed_tasks_by_workload.png
├── 11_blocked_days_by_team.png
├── 12_blocked_days_by_workload.png
├── 13_completed_tasks_by_condition.png
├── 14_blocked_days_by_condition.png
├── 15_flow_efficiency_by_condition.png
├── 16_completed_tasks_by_event.png
├── 17_blocked_days_by_event.png
├── 18_completed_tasks_by_ai.png
└── 19_blocked_days_by_ai.png
```

---

## Archivos principales

### `Simulation.py`

Script de simulación utilizado para el artículo.
Contiene la definición de escenarios, perfiles, generación de tareas, lógica de ejecución de sprints, cálculo de métricas y exportación de resultados asociados al análisis experimental del artículo.

### `simulation_4q.py`

Script de simulación utilizado para la tesis.
Está orientado al análisis del enfoque **4Q / 4Q Agile Framework** y permite evaluar el comportamiento de la propuesta metodológica bajo diferentes condiciones de equipo, carga de trabajo, disponibilidad y adaptación del proceso.

### `simulation_results.csv`

Resultados detallados por sprint, experimento y combinación de variables.

### `simulation_summary.csv`

Resumen agregado por escenario, perfil de equipo, carga de trabajo, condición de proceso y nivel de soporte de IA.

### `scenario_summary.csv`

Resumen global por escenario simulado.

### `ai_summary.csv`

Resumen de resultados agrupados por escenario y nivel de soporte de IA.

### `event_summary.csv`

Resumen de resultados considerando la presencia de eventos organizacionales activos.

### Archivos `config_*.csv`

Exportan la configuración utilizada para los perfiles de equipo, cargas de trabajo, condiciones de proceso y eventos aleatorios.
Sirven como documentación del modelo y permiten revisar los supuestos utilizados en cada corrida.

---

## Cómo ejecutar

Para ejecutar la simulación utilizada en el artículo:

```bash
python Simulation.py
```

Para ejecutar la simulación utilizada en la tesis:

```bash
python simulation_4q.py
```

La ejecución genera automáticamente, según el script utilizado:

* archivos CSV con resultados,
* archivos CSV con configuración del modelo,
* gráficos comparativos en formato PNG.

---

## Configuración principal

En `Simulation.py`, la ejecución por defecto está definida como:

```python
df = run_experiments(
    num_experiments=20,
    num_sprints=12,
    sprint_days=10,
)
```

Esto significa que el modelo ejecuta:

* **20 experimentos**
* **12 sprints por experimento**
* **10 días por sprint**

En `simulation_4q.py`, los parámetros pueden variar según la configuración definida para el modelo de tesis.
Estos valores pueden modificarse directamente en el script para ajustar la profundidad del análisis o el costo computacional.
