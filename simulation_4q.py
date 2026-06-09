import random
import zipfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from scipy import stats
except ImportError:
    print("Scipy no está instalado. Algunas funciones estadísticas avanzadas no estarán disponibles.")
    stats = None

try:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
except ImportError:
    print("statsmodels no está instalado. Tukey HSD no estará disponible.")
    pairwise_tukeyhsd = None


# ============================================================
# Utils
# ============================================================

def create_zip(output_dir: Path) -> Path:
    zip_path = output_dir.with_suffix(".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in output_dir.rglob("*"):
            if file.is_file():
                zipf.write(file, file.relative_to(output_dir))

    return zip_path


def create_output_folder() -> Path:
    today = datetime.now()
    run_id = random.randint(10000, 99999)
    folder_name = f"random_{run_id}_4qAgile_{today.day:02d}{today.month:02d}{today.year}"
    output_dir = Path(folder_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ============================================================
# Scenarios
# ============================================================

class Scenario(Enum):
    SCRUM_5D = "Scrum 5 días"
    JLR_4D_NO_ADAPTATION = "JLR-4D sin adaptación"
    JLR_4D_ADAPTED = "JLR-4D adaptado"
    FOUR_Q = "4Q Agile Framework"


# ============================================================
# Models
# ============================================================

@dataclass
class TeamProfile:
    name: str
    team_size: int
    productivity: float
    blocking_factor: float
    rework_factor: float
    handoff_quality: float
    maturity: float
    morale: float


@dataclass
class WorkloadProfile:
    name: str
    tasks: int
    dependency_factor: float
    complexity_factor: float


@dataclass
class Task:
    id: int
    effort: int
    remaining: int
    arrival_day: int
    blocked: bool = False
    completed: bool = False
    started_day: Optional[int] = None
    completed_day: Optional[int] = None
    blocked_days: int = 0
    worked_days: int = 0
    rework_events: int = 0


# ============================================================
# Configuration
# ============================================================

TEAMS = [
    TeamProfile("Equipo senior", 6, 1.12, 0.80, 0.80, 0.85, 0.90, 0.85),
    TeamProfile("Equipo mixto", 6, 1.00, 1.00, 1.00, 0.70, 0.70, 0.75),
    TeamProfile("Equipo junior", 6, 0.84, 1.25, 1.30, 0.55, 0.50, 0.68),
    TeamProfile("Equipo distribuido", 6, 0.93, 1.35, 1.15, 0.58, 0.60, 0.70),
]

WORKLOADS = [
    WorkloadProfile("Carga baja", 30, 0.85, 0.85),
    WorkloadProfile("Carga media", 40, 1.00, 1.00),
    WorkloadProfile("Carga alta", 55, 1.25, 1.15),
    WorkloadProfile("Alta dependencia", 40, 1.65, 1.25),
]


# ============================================================
# Task generation
# ============================================================

def generate_tasks(workload: WorkloadProfile, sprint_days: int) -> list[Task]:
    tasks = []

    for i in range(workload.tasks):
        effort = random.choices(
            [1, 2, 3, 5, 8],
            weights=[0.22, 0.30, 0.25, 0.17, 0.06],
        )[0]

        arrival_day = random.randint(0, max(0, sprint_days // 2 - 1))

        tasks.append(
            Task(
                id=i,
                effort=effort,
                remaining=effort,
                arrival_day=arrival_day,
            )
        )

    return tasks


# ============================================================
# Scenario logic
# ============================================================

def available_devs(scenario: Scenario, day: int, team_size: int) -> int:
    weekday = day % 5

    if scenario == Scenario.SCRUM_5D:
        return team_size

    if scenario == Scenario.JLR_4D_NO_ADAPTATION:
        return 0 if weekday == 4 else team_size

    if scenario == Scenario.JLR_4D_ADAPTED:
        return max(1, team_size // 2) if weekday == 4 else team_size

    if scenario == Scenario.FOUR_Q:
        # Staggered schedule: half team on Monday (incoming group) and Friday (outgoing group)
        # Tuesday–Thursday are Full Coverage days with complete team overlap
        return max(2, team_size // 2) if weekday in (0, 4) else team_size

    return team_size


def learning_factor(scenario: Scenario, sprint_id: int, team: TeamProfile) -> float:
    if scenario != Scenario.FOUR_Q:
        return 1.0

    base = 0.94
    learning = min(0.08, sprint_id * 0.004)
    maturity_bonus = (team.maturity - 0.60) * 0.05

    return max(0.90, min(1.04, base + learning + maturity_bonus))


# Allows sensitivity analysis to override 4Q modifiers without refactoring
_four_q_modifier_overrides: dict = {}


def morale_drift(scenario: Scenario, sprint_id: int, team: TeamProfile) -> float:
    """Models sustained morale change over sprints.
    4Q: slight positive drift from improved work-life balance.
    JLR-4D no adaptation: gradual decline from unresolved coordination stress.
    """
    if scenario == Scenario.FOUR_Q:
        drift = min(0.06, sprint_id * 0.0025)
    elif scenario == Scenario.JLR_4D_NO_ADAPTATION:
        drift = -min(0.08, sprint_id * 0.003)
    else:
        drift = 0.0
    return max(0.50, min(1.10, team.morale + drift))


def scenario_modifiers(scenario: Scenario, sprint_id: int, team: TeamProfile) -> dict:
    if scenario == Scenario.SCRUM_5D:
        return {
            "capacity": 1.00,
            "blocking": 1.00,
            "rework": 1.00,
            "unblock": 0.62,
            "meeting_penalty": 0.05,
        }

    if scenario == Scenario.JLR_4D_NO_ADAPTATION:
        return {
            "capacity": 0.88,
            "blocking": 2.45,
            "rework": 1.85,
            "unblock": 0.34,
            "meeting_penalty": 0.12,
        }

    if scenario == Scenario.JLR_4D_ADAPTED:
        return {
            "capacity": 0.93,
            "blocking": 1.42,
            "rework": 1.28,
            "unblock": 0.58,
            "meeting_penalty": 0.08,
        }

    if scenario == Scenario.FOUR_Q:
        lf = learning_factor(scenario, sprint_id, team)

        base = {
            "capacity": 0.95 * lf,
            "blocking": 1.18 / lf,
            "rework": 1.12 / lf,
            "unblock": 0.70 * lf,
            "meeting_penalty": 0.075,
        }
        base.update(_four_q_modifier_overrides)
        return base

    return {
        "capacity": 1.00,
        "blocking": 1.00,
        "rework": 1.00,
        "unblock": 0.50,
        "meeting_penalty": 0.10,
    }


# ============================================================
# Random organizational events
# ============================================================

def random_event_effect(scenario: Scenario) -> dict:
    events = [
        ("Sin evento", 1.00, 1.00, 1.00),
        ("Enfermedad", 0.88, 1.10, 1.05),
        ("Vacaciones", 0.90, 1.05, 1.00),
        ("Feriado", 0.92, 1.03, 1.00),
        ("Renuncia", 0.80, 1.30, 1.18),
        ("Contratación", 0.96, 1.18, 1.12),
        ("Feedback tardío", 0.98, 1.12, 1.25),
        ("Management positivo", 1.03, 0.92, 0.95),
        ("Management negativo", 0.95, 1.18, 1.12),
        ("Presión de deadline", 1.05, 1.18, 1.22),
    ]

    event_probability = 0.25

    if scenario == Scenario.JLR_4D_NO_ADAPTATION:
        event_probability = 0.30
    elif scenario == Scenario.FOUR_Q:
        event_probability = 0.23

    if random.random() < event_probability:
        name, capacity, blocking, rework = random.choice(events[1:])
    else:
        name, capacity, blocking, rework = events[0]

    return {
        "event": name,
        "capacity": capacity,
        "blocking": blocking,
        "rework": rework,
    }


def focus_factor(scenario: Scenario, team: TeamProfile, event: dict) -> float:
    base = {
        Scenario.SCRUM_5D: 0.90,
        Scenario.JLR_4D_NO_ADAPTATION: 0.78,
        Scenario.JLR_4D_ADAPTED: 0.84,
        Scenario.FOUR_Q: 0.88,
    }[scenario]

    team_adjustment = {
        "Equipo senior": 0.05,
        "Equipo mixto": 0.00,
        "Equipo junior": -0.06,
        "Equipo distribuido": -0.04,
    }.get(team.name, 0.0)

    event_penalty = 0.0
    if event["event"] != "Sin evento":
        event_penalty = random.uniform(0.03, 0.10)

    noise = random.uniform(-0.04, 0.04)

    return max(0.60, min(0.97, base + team_adjustment - event_penalty + noise))


# ============================================================
# Probabilities
# ============================================================

def blocking_probability(
    scenario: Scenario,
    team: TeamProfile,
    workload: WorkloadProfile,
    event: dict,
    sprint_id: int,
) -> float:
    mods = scenario_modifiers(scenario, sprint_id, team)

    base = 0.05

    probability = (
        base
        * team.blocking_factor
        * workload.dependency_factor
        * workload.complexity_factor
        * mods["blocking"]
        * event["blocking"]
    )

    return min(0.90, max(0.01, probability))


def rework_probability(
    scenario: Scenario,
    team: TeamProfile,
    workload: WorkloadProfile,
    event: dict,
    sprint_id: int,
) -> float:
    mods = scenario_modifiers(scenario, sprint_id, team)

    base = 0.04

    probability = (
        base
        * team.rework_factor
        * workload.dependency_factor
        * workload.complexity_factor
        * mods["rework"]
        * event["rework"]
    )

    return min(0.90, max(0.01, probability))


def unblock_probability(
    scenario: Scenario,
    team: TeamProfile,
    sprint_id: int,
) -> float:
    mods = scenario_modifiers(scenario, sprint_id, team)
    value = mods["unblock"] * (0.70 + team.handoff_quality * 0.35)

    return min(0.95, max(0.05, value))


# ============================================================
# Sprint simulation
# ============================================================

def simulate_sprint(
    scenario: Scenario,
    team: TeamProfile,
    workload: WorkloadProfile,
    experiment_id: int,
    sprint_id: int,
    sprint_days: int = 10,
    seed: Optional[int] = None,
) -> dict:
    if seed is not None:
        random.seed(seed)

    mods = scenario_modifiers(scenario, sprint_id, team)
    event = random_event_effect(scenario)
    tasks = generate_tasks(workload, sprint_days)
    effective_morale = morale_drift(scenario, sprint_id, team)

    blocked_events = 0
    rework_events = 0
    total_capacity = 0
    used_capacity = 0

    for day in range(sprint_days):
        devs = available_devs(scenario, day, team.team_size)
        weekday = day % 5

        theoretical_capacity = (
            devs
            * team.productivity
            * effective_morale
            * mods["capacity"]
            * event["capacity"]
            * (1 - mods["meeting_penalty"])
        )

        focus = focus_factor(scenario, team, event)

        daily_capacity = round(theoretical_capacity * focus)
        daily_capacity = max(0, daily_capacity)

        total_capacity += round(theoretical_capacity)

        for task in tasks:
            if task.blocked and not task.completed:
                task.blocked_days += 1

        ub_prob = unblock_probability(scenario, team, sprint_id)
        if scenario == Scenario.FOUR_Q and weekday in (0, 4):
            # Hand-off days: the incoming group actively reviews and resolves blockers
            ub_prob = min(0.95, ub_prob * 1.40)

        for task in tasks:
            if task.blocked and not task.completed:
                if random.random() < ub_prob:
                    task.blocked = False

        available_tasks = [
            t for t in tasks
            if not t.completed and not t.blocked and t.arrival_day <= day
        ]

        available_tasks.sort(key=lambda t: t.remaining)

        for task in available_tasks:
            if daily_capacity <= 0:
                break

            if task.started_day is None:
                task.started_day = day

            if random.random() < blocking_probability(
                scenario, team, workload, event, sprint_id
            ):
                task.blocked = True
                blocked_events += 1
                continue

            if random.random() < rework_probability(
                scenario, team, workload, event, sprint_id
            ):
                task.remaining += 1
                task.rework_events += 1
                rework_events += 1

            task.remaining -= 1
            task.worked_days += 1
            used_capacity += 1
            daily_capacity -= 1

            if task.remaining <= 0:
                task.completed = True
                task.completed_day = day

    completed = [t for t in tasks if t.completed]
    incomplete = [t for t in tasks if not t.completed]

    worked_days = sum(t.worked_days for t in completed)
    blocked_days_completed = sum(t.blocked_days for t in completed)
    blocked_days_all = sum(t.blocked_days for t in tasks)

    flow_efficiency = (
        worked_days / (worked_days + blocked_days_completed)
        if worked_days + blocked_days_completed > 0
        else 0
    )

    cycle_times = [
        t.completed_day - t.started_day + 1
        for t in completed
        if t.started_day is not None and t.completed_day is not None
    ]

    lead_times = [
        t.completed_day - t.arrival_day + 1
        for t in completed
        if t.completed_day is not None
    ]

    return {
        "experiment_id": experiment_id,
        "sprint_id": sprint_id,
        "scenario": scenario.value,
        "team_profile": team.name,
        "workload_profile": workload.name,
        "event": event["event"],
        "completed_tasks": len(completed),
        "incomplete_tasks": len(incomplete),
        "blocked_events": blocked_events,
        "blocked_days": blocked_days_all,
        "rework_events": rework_events,
        "flow_efficiency": flow_efficiency,
        "capacity_utilization": used_capacity / total_capacity if total_capacity > 0 else 0,
        "avg_cycle_time_completed_only": (
            sum(cycle_times) / len(cycle_times) if cycle_times else 0
        ),
        "avg_lead_time_completed_only": (
            sum(lead_times) / len(lead_times) if lead_times else 0
        ),
    }


# ============================================================
# Run simulation
# ============================================================

def run_simulation(
    experiments: int = 50,
    sprints: int = 24,
    sprint_days: int = 10,
) -> pd.DataFrame:
    results = []

    for experiment_id in range(experiments):
        for sprint_id in range(sprints):
            for team in TEAMS:
                for workload in WORKLOADS:
                    for scenario in Scenario:
                        seed = abs(
                            hash(
                                (
                                    experiment_id,
                                    sprint_id,
                                    team.name,
                                    workload.name,
                                    scenario.value,
                                )
                            )
                        ) % 1_000_000

                        results.append(
                            simulate_sprint(
                                scenario=scenario,
                                team=team,
                                workload=workload,
                                experiment_id=experiment_id,
                                sprint_id=sprint_id,
                                sprint_days=sprint_days,
                                seed=seed,
                            )
                        )

    return pd.DataFrame(results)


# ============================================================
# Plots
# ============================================================

def scenario_order() -> list[str]:
    return [
        Scenario.SCRUM_5D.value,
        Scenario.JLR_4D_ADAPTED.value,
        Scenario.FOUR_Q.value,
        Scenario.JLR_4D_NO_ADAPTATION.value,
    ]


def plot_bar(df: pd.DataFrame, metric: str, title: str, ylabel: str, filename: Path):
    data = df.groupby("scenario")[metric].mean().reindex(scenario_order())

    plt.figure(figsize=(11, 6))
    data.plot(kind="bar")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Escenario")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_line(df: pd.DataFrame, metric: str, title: str, ylabel: str, filename: Path):
    data = df.groupby(["sprint_id", "scenario"])[metric].mean().reset_index()

    plt.figure(figsize=(12, 6))

    for scenario in scenario_order():
        scenario_data = data[data["scenario"] == scenario]
        plt.plot(
            scenario_data["sprint_id"],
            scenario_data[metric],
            marker="o",
            label=scenario,
        )

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Sprint")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_dimension(
    df: pd.DataFrame,
    dimension: str,
    metric: str,
    title: str,
    ylabel: str,
    filename: Path,
):
    data = df.groupby([dimension, "scenario"])[metric].mean().unstack()
    data = data[scenario_order()]

    plt.figure(figsize=(13, 7))
    data.plot(kind="bar", ax=plt.gca())
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(dimension)
    plt.xticks(rotation=20, ha="right")
    plt.legend(title="Escenario")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


# ============================================================
# Statistics and interpretation
# ============================================================

def _cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Computes Cohen's d (pooled SD) between two groups."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    pooled_var = ((na - 1) * a.std(ddof=1) ** 2 + (nb - 1) * b.std(ddof=1) ** 2) / (na + nb - 2)
    pooled_std = pooled_var ** 0.5
    return float((a.mean() - b.mean()) / pooled_std) if pooled_std > 0 else 0.0


def statistical_analysis(df: pd.DataFrame, output_dir: Path):
    metrics = [
        "completed_tasks",
        "blocked_events",
        "blocked_days",
        "rework_events",
        "flow_efficiency",
        "capacity_utilization",
    ]

    lines = []
    lines.append("ANÁLISIS ESTADÍSTICO DE LA SIMULACIÓN")
    lines.append("=" * 60)
    lines.append("")

    tukey_rows = []

    for metric in metrics:
        lines.append(f"Métrica: {metric}")
        lines.append("-" * 60)

        grouped = [
            group[metric].dropna().values
            for _, group in df.groupby("scenario")
        ]

        if stats is not None:
            f_stat, p_value = stats.f_oneway(*grouped)
            lines.append(f"ANOVA F-statistic: {f_stat:.4f}")
            lines.append(f"ANOVA p-value: {p_value:.8f}")

            if p_value < 0.05:
                lines.append("Resultado: diferencias estadísticamente significativas entre escenarios.")
            else:
                lines.append("Resultado: no se observan diferencias estadísticamente significativas.")
        else:
            lines.append("Scipy no está instalado. No se ejecutó ANOVA.")

        lines.append("")

        scenario_means = (
            df.groupby("scenario")[metric]
            .agg(["mean", "std"])
            .reset_index()
        )

        for _, row in scenario_means.iterrows():
            lines.append(
                f"{row['scenario']}: media={row['mean']:.4f}, desvío={row['std']:.4f}"
            )

        lines.append("")
        lines.append("Cohen's d — tamaño del efecto (4Q Agile Framework vs otros):")
        four_q_vals = df[df["scenario"] == Scenario.FOUR_Q.value][metric].dropna().values
        for sc in [Scenario.SCRUM_5D, Scenario.JLR_4D_ADAPTED, Scenario.JLR_4D_NO_ADAPTATION]:
            other_vals = df[df["scenario"] == sc.value][metric].dropna().values
            d = _cohens_d(four_q_vals, other_vals)
            lines.append(f"  4Q vs {sc.value}: d={d:.3f}")
        lines.append("")

        if pairwise_tukeyhsd is not None:
            lines.append("Tukey HSD - Comparaciones por pares")
            lines.append("-" * 60)

            tukey = pairwise_tukeyhsd(
                endog=df[metric],
                groups=df["scenario"],
                alpha=0.05,
            )

            tukey_table = pd.DataFrame(
                data=tukey._results_table.data[1:],
                columns=tukey._results_table.data[0],
            )

            lines.append(str(tukey_table))
            lines.append("")

            tukey_table.insert(0, "metric", metric)
            tukey_rows.append(tukey_table)
        else:
            lines.append("statsmodels no está instalado. No se ejecutó Tukey HSD.")
            lines.append("")

        lines.append("")

    with open(output_dir / "statistical_analysis.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    if tukey_rows:
        tukey_df = pd.concat(tukey_rows, ignore_index=True)
        tukey_df.to_csv(output_dir / "tukey_hsd_results.csv", index=False)


def generate_interpretation(df: pd.DataFrame, output_dir: Path):
    summary = df.groupby("scenario").mean(numeric_only=True)

    scrum = summary.loc[Scenario.SCRUM_5D.value]
    jlr = summary.loc[Scenario.JLR_4D_ADAPTED.value]
    four_q = summary.loc[Scenario.FOUR_Q.value]
    no_adapt = summary.loc[Scenario.JLR_4D_NO_ADAPTATION.value]

    four_q_vs_scrum = ((four_q["completed_tasks"] / scrum["completed_tasks"]) - 1) * 100
    four_q_vs_jlr = ((four_q["completed_tasks"] / jlr["completed_tasks"]) - 1) * 100
    four_q_vs_no_adapt = ((four_q["completed_tasks"] / no_adapt["completed_tasks"]) - 1) * 100

    blocked_reduction = (1 - (four_q["blocked_days"] / no_adapt["blocked_days"])) * 100
    rework_reduction = (1 - (four_q["rework_events"] / no_adapt["rework_events"])) * 100
    efficiency_gap = (four_q["flow_efficiency"] - no_adapt["flow_efficiency"]) * 100

    text = f"""
RESUMEN INTERPRETATIVO DE RESULTADOS

Los resultados de la simulación muestran que Scrum tradicional de cinco días mantiene la mayor productividad absoluta en términos de tareas completadas. Sin embargo, el 4Q Agile Framework logra mantener un rendimiento cercano al escenario Scrum, con una diferencia de {four_q_vs_scrum:.2f}% en tareas completadas.

En comparación con una jornada laboral reducida adaptada de manera parcial, 4Q Agile Framework muestra una diferencia de {four_q_vs_jlr:.2f}% en tareas completadas.

En comparación con una jornada laboral reducida sin adaptación metodológica, 4Q Agile Framework muestra una mejora de {four_q_vs_no_adapt:.2f}% en tareas completadas.

Además, 4Q Agile Framework reduce los días bloqueados en {blocked_reduction:.2f}% respecto del escenario JLR-4D sin adaptación y reduce los eventos de retrabajo en {rework_reduction:.2f}%.

La diferencia de eficiencia de flujo entre 4Q Agile Framework y JLR-4D sin adaptación es de {efficiency_gap:.2f} puntos porcentuales.

Estos resultados sugieren que la reducción de la jornada laboral sin modificaciones metodológicas produce una degradación significativa del flujo de trabajo. En cambio, la incorporación de mecanismos específicos de coordinación, transferencia de conocimiento, cobertura operativa y resolución de bloqueos permite recuperar parte importante del rendimiento perdido.

El resultado no debe interpretarse como una demostración empírica definitiva, sino como evidencia simulada preliminar sobre la plausibilidad del framework propuesto.
"""

    with open(output_dir / "interpretation_summary.txt", "w", encoding="utf-8") as file:
        file.write(text.strip())


# ============================================================
# Outputs
# ============================================================

# ============================================================
# Sensitivity analysis
# ============================================================

def run_sensitivity(
    output_dir: Path,
    experiments: int = 10,
    sprints: int = 24,
    sprint_days: int = 10,
) -> None:
    """Varies the 4Q unblock modifier by ±20% to test robustness of key results.
    Runs a lighter simulation (fewer experiments) for speed.
    """
    global _four_q_modifier_overrides

    rows = []
    for label, unblock_value in [("−20%", 0.56), ("baseline", 0.70), ("+20%", 0.84)]:
        _four_q_modifier_overrides = {} if label == "baseline" else {"unblock": unblock_value}
        df_s = run_simulation(experiments, sprints, sprint_days)
        four_q = df_s[df_s["scenario"] == Scenario.FOUR_Q.value]
        scrum = df_s[df_s["scenario"] == Scenario.SCRUM_5D.value]
        rows.append({
            "variation": label,
            "unblock_modifier": unblock_value,
            "4q_completed_tasks_mean": round(four_q["completed_tasks"].mean(), 4),
            "4q_blocked_days_mean": round(four_q["blocked_days"].mean(), 4),
            "4q_flow_efficiency_mean": round(four_q["flow_efficiency"].mean(), 4),
            "gap_vs_scrum_pct": round(
                (four_q["completed_tasks"].mean() / scrum["completed_tasks"].mean() - 1) * 100, 2
            ),
        })

    _four_q_modifier_overrides = {}

    sensitivity_df = pd.DataFrame(rows)
    sensitivity_df.to_csv(output_dir / "sensitivity_unblock.csv", index=False)
    print("\nSensitivity analysis — 4Q unblock modifier ±20%:")
    print(sensitivity_df.to_string(index=False))


def generate_outputs(df: pd.DataFrame, output_dir: Path):
    df.to_csv(output_dir / "simulation_results_4q.csv", index=False)

    summary = df.groupby("scenario").mean(numeric_only=True).reset_index()
    summary.to_csv(output_dir / "scenario_summary_4q.csv", index=False)

    detailed_summary = (
        df.groupby(["scenario", "team_profile", "workload_profile"])
        .agg(
            completed_tasks_mean=("completed_tasks", "mean"),
            completed_tasks_std=("completed_tasks", "std"),
            blocked_events_mean=("blocked_events", "mean"),
            blocked_days_mean=("blocked_days", "mean"),
            rework_events_mean=("rework_events", "mean"),
            flow_efficiency_mean=("flow_efficiency", "mean"),
            capacity_utilization_mean=("capacity_utilization", "mean"),
        )
        .reset_index()
    )

    detailed_summary.to_csv(output_dir / "detailed_summary_4q.csv", index=False)

    plot_bar(df, "completed_tasks", "Tareas completadas promedio por escenario", "Tareas completadas", output_dir / "01_completed_tasks_by_scenario.png")
    plot_bar(df, "blocked_events", "Eventos de bloqueo promedio por escenario", "Eventos de bloqueo", output_dir / "02_blocked_events_by_scenario.png")
    plot_bar(df, "blocked_days", "Días bloqueados promedio por escenario", "Días bloqueados", output_dir / "03_blocked_days_by_scenario.png")
    plot_bar(df, "rework_events", "Eventos de retrabajo promedio por escenario", "Eventos de retrabajo", output_dir / "04_rework_events_by_scenario.png")
    plot_bar(df, "flow_efficiency", "Eficiencia de flujo promedio por escenario", "Eficiencia de flujo", output_dir / "05_flow_efficiency_by_scenario.png")
    plot_bar(df, "capacity_utilization", "Utilización de capacidad promedio por escenario", "Utilización de capacidad", output_dir / "06_capacity_utilization_by_scenario.png")

    plot_line(df, "completed_tasks", "Evolución de tareas completadas por sprint", "Tareas completadas", output_dir / "07_completed_tasks_over_time.png")
    plot_line(df, "blocked_days", "Evolución de días bloqueados por sprint", "Días bloqueados", output_dir / "08_blocked_days_over_time.png")
    plot_line(df, "flow_efficiency", "Evolución de eficiencia de flujo por sprint", "Eficiencia de flujo", output_dir / "09_flow_efficiency_over_time.png")
    plot_line(df, "capacity_utilization", "Evolución de utilización de capacidad por sprint", "Utilización de capacidad", output_dir / "10_capacity_utilization_over_time.png")

    plot_dimension(df, "team_profile", "completed_tasks", "Tareas completadas por perfil de equipo", "Tareas completadas", output_dir / "11_completed_tasks_by_team.png")
    plot_dimension(df, "workload_profile", "completed_tasks", "Tareas completadas por carga de trabajo", "Tareas completadas", output_dir / "12_completed_tasks_by_workload.png")
    plot_dimension(df, "team_profile", "blocked_days", "Días bloqueados por perfil de equipo", "Días bloqueados", output_dir / "13_blocked_days_by_team.png")
    plot_dimension(df, "workload_profile", "blocked_days", "Días bloqueados por carga de trabajo", "Días bloqueados", output_dir / "14_blocked_days_by_workload.png")

    statistical_analysis(df, output_dir)
    generate_interpretation(df, output_dir)

    print("\nResumen general:")
    print(summary)

    print(f"\nArchivos generados en: {output_dir.resolve()}")
    print("- statistical_analysis.txt")
    print("- interpretation_summary.txt")
    print("- tukey_hsd_results.csv")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    output_dir = create_output_folder()

    df = run_simulation(
        experiments=50,
        sprints=24,
        sprint_days=10,
    )

    generate_outputs(df, output_dir)
    run_sensitivity(output_dir)

    zip_file = create_zip(output_dir)

    print(f"ZIP generado: {zip_file}")