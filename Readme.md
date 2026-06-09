# JLR-4D

Simulación en Python para analizar el impacto de distintos esquemas de trabajo sobre el rendimiento de equipos de desarrollo.

El proyecto compara tres escenarios operativos:

- **Scrum 5 días**
- **JLR-4D sin adaptación**
- **JLR-4D adaptado**

La simulación evalúa cómo cambian métricas como tareas completadas, bloqueos, retrabajo, eficiencia de flujo y utilización de capacidad según:

- el perfil del equipo,
- la carga de trabajo,
- la condición del proceso,
- el nivel de soporte de IA,
- y eventos organizacionales aleatorios.

## Objetivo

Este repositorio busca explorar, de forma experimental, cómo distintas condiciones organizacionales y operativas afectan la productividad y el flujo de trabajo de un equipo de software.

El modelo permite comparar escenarios con diferentes restricciones de disponibilidad, fatiga de reuniones, calidad de backlog, handoff entre personas/equipos y soporte de IA.

## Qué hace la simulación

El archivo principal es `Simulation.py`, que:

1. Define perfiles de equipo, carga y proceso.
2. Genera tareas con esfuerzo, prioridad, complejidad y día de llegada.
3. Simula varios sprints por experimento.
4. Introduce eventos organizacionales aleatorios como:
   - enfermedad,
   - vacaciones,
   - feriados,
   - renuncias,
   - contrataciones,
   - intervenciones de management,
   - feedback del cliente,
   - presión por deadlines.
5. Calcula métricas operativas por sprint.
6. Exporta resultados agregados en archivos CSV.
7. Genera visualizaciones en PNG para comparar escenarios.

## Escenarios simulados

### 1. Scrum 5 días
Modelo base de trabajo continuo durante 5 días hábiles.

### 2. JLR-4D sin adaptación
Asume una reducción a 4 días de trabajo sin rediseñar el proceso.  
En este escenario, el quinto día no aporta capacidad del equipo.

### 3. JLR-4D adaptado
Asume un modelo de 4 días con adaptación operativa.  
El quinto día mantiene capacidad parcial, reduciendo parte del impacto negativo del cambio.

## Variables del modelo

### Perfiles de equipo
La simulación incluye distintos tipos de equipos:

- **Equipo senior**
- **Equipo mixto**
- **Equipo junior**
- **Equipo distribuido**

Cada perfil define factores como:

- tamaño del equipo,
- productividad,
- probabilidad de bloqueo,
- probabilidad de retrabajo,
- madurez,
- moral,
- satisfacción salarial,
- distribución del conocimiento,
- riesgo de rotación.

### Perfiles de carga de trabajo

- **Carga baja**
- **Carga media**
- **Carga alta**
- **Alta dependencia**

Cada perfil modifica:

- cantidad de tareas,
- dependencia entre tareas,
- urgencia,
- complejidad promedio.

### Condiciones del proceso

- **Condición favorable**
- **Condición estándar**
- **Backlog débil**
- **Hand-off débil**
- **Alta fatiga de reuniones**

Estas condiciones impactan en:

- calidad del backlog,
- calidad del handoff,
- fatiga de reuniones,
- calidad de management,
- calidad del feedback del cliente.

### Soporte de IA

- **Sin IA**
- **IA moderada**
- **IA alta**

El soporte de IA afecta principalmente:

- bloqueo,
- retrabajo,
- calidad efectiva de backlog,
- calidad de handoff,
- productividad.

## Métricas generadas

La simulación produce, entre otras, las siguientes métricas:

- tareas completadas,
- tareas incompletas,
- eventos de bloqueo,
- días bloqueados,
- eventos de retrabajo,
- tiempo de ciclo promedio,
- lead time promedio,
- eficiencia de flujo,
- utilización de capacidad,
- moral efectiva,
- cantidad de eventos activos.

## Estructura del repositorio

- `Simulation.py`: script principal de simulación.
- `simulation_results.csv`: resultados detallados por sprint.
- `simulation_summary.csv`: resumen agregado por escenario, perfil de equipo, carga, condición y soporte de IA.
- `scenario_summary.csv`: resumen global por escenario.
- `ai_summary.csv`: resumen por escenario y nivel de IA.
- `event_summary.csv`: resumen de resultados con eventos activos.
- `config_team_profiles.csv`: configuración de perfiles de equipo.
- `config_workload_profiles.csv`: configuración de perfiles de carga.
- `config_process_conditions.csv`: configuración de condiciones de proceso.
- `config_events.csv`: configuración de eventos aleatorios.

### Gráficos generados

El script también exporta visualizaciones, por ejemplo:

- `01_completed_tasks_by_scenario.png`
- `02_blocked_events_by_scenario.png`
- `03_blocked_days_by_scenario.png`
- `04_rework_events_by_scenario.png`
- `05_flow_efficiency_by_scenario.png`
- `06_completed_tasks_over_time.png`
- `07_blocked_days_over_time.png`
- `08_flow_efficiency_over_time.png`
- `09_completed_tasks_by_team.png`
- `10_completed_tasks_by_workload.png`
- `11_blocked_days_by_team.png`
- `12_blocked_days_by_workload.png`
- `13_completed_tasks_by_condition.png`
- `14_blocked_days_by_condition.png`
- `15_flow_efficiency_by_condition.png`
- `16_completed_tasks_by_event.png`
- `17_blocked_days_by_event.png`
- `18_completed_tasks_by_ai.png`
- `19_blocked_days_by_ai.png`

## Requisitos

Este proyecto usa Python y depende de:

- `pandas`
- `matplotlib`

Instalación sugerida:

```bash
pip install pandas matplotlib
```

## Cómo ejecutar

Ejecutar el script principal:

```bash
python Simulation.py
```

Esto generará automáticamente:

- resultados en CSV,
- archivos de configuración exportados,
- y gráficos en PNG.

## Configuración principal

Dentro de `Simulation.py`, la ejecución por defecto está definida como:

```python
df = run_experiments(
    num_experiments=20,
    num_sprints=12,
    sprint_days=10,
)
```

Esto significa que el modelo corre:

- **20 experimentos**
- **12 sprints por experimento**
- **10 días por sprint**

Puedes modificar estos valores directamente en el script para ajustar el nivel de análisis o el costo computacional.

## Lógica general de simulación

A alto nivel, cada sprint:

1. aplica efectos de eventos activos,
2. ajusta moral, backlog, handoff y fatiga,
3. genera tareas según el perfil de carga,
4. calcula capacidad diaria según el escenario,
5. simula bloqueos, desbloqueos y retrabajo,
6. registra tareas completadas e incompletas,
7. agrega métricas de desempeño.

## Resultados esperados

A partir de los archivos ya generados en el repositorio, el proyecto permite analizar comparativamente:

- productividad promedio por escenario,
- impacto del soporte de IA,
- efecto de backlog/handoff débiles,
- sensibilidad frente a eventos organizacionales,
- diferencias entre equipos senior, junior y distribuidos.

## Posibles extensiones

Algunas mejoras futuras posibles:

- parametrización por línea de comandos,
- archivo de configuración externo,
- notebooks para análisis exploratorio,
- tests automáticos,
- exportación de resultados más detallados,
- dashboards interactivos,
- calibración del modelo con datos reales.

## Licencia

Agregar la licencia correspondiente si se desea publicar o reutilizar formalmente el proyecto.
