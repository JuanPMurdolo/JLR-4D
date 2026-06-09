import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SCENARIOS
# ============================================================

class Scenario(Enum):
    SCRUM_5D = "Scrum 5 días"
    JLR_4D_NO_ADAPTATION = "JLR-4D sin adaptación"
    JLR_4D_ADAPTED = "JLR-4D adaptado"


class AISupport(Enum):
    NONE = "Sin IA"
    MODERATE = "IA moderada"
    HIGH = "IA alta"


# ============================================================
# PROFILES
# ============================================================

@dataclass
class TeamProfile:
    name: str
    team_size: int
    productivity_factor: float
    blocking_factor: float
    rework_factor: float
    maturity_factor: float
    morale: float
    salary_satisfaction: float
    knowledge_distribution: float
    turnover_risk: float


@dataclass
class WorkloadProfile:
    name: str
    num_tasks: int
    dependency_factor: float
    urgency_factor: float
    average_complexity: float


@dataclass
class ProcessCondition:
    name: str
    backlog_quality: float
    handoff_quality: float
    meeting_fatigue: float
    management_quality: float
    client_feedback_quality: float


@dataclass
class Task:
    id: int
    effort: int
    remaining: int
    priority: str
    arrival_day: int
    complexity: float
    blocked: bool = False
    completed: bool = False
    started_day: Optional[int] = None
    completed_day: Optional[int] = None
    blocked_days: int = 0
    rework_events: int = 0
    worked_days: int = 0


@dataclass
class SprintEvent:
    name: str
    capacity_multiplier: float = 1.0
    blocking_multiplier: float = 1.0
    rework_multiplier: float = 1.0
    meeting_fatigue_delta: float = 0.0
    morale_delta: float = 0.0
    backlog_quality_delta: float = 0.0
    handoff_quality_delta: float = 0.0
    team_size_delta: int = 0
    onboarding_penalty: float = 0.0
    duration_sprints: int = 1


# ============================================================
# BASE CONFIGURATION
# ============================================================

TEAM_PROFILES = [
    TeamProfile(
        name="Equipo senior",
        team_size=6,
        productivity_factor=1.15,
        blocking_factor=0.80,
        rework_factor=0.75,
        maturity_factor=1.20,
        morale=0.85,
        salary_satisfaction=0.80,
        knowledge_distribution=0.85,
        turnover_risk=0.04,
    ),
    TeamProfile(
        name="Equipo mixto",
        team_size=6,
        productivity_factor=1.00,
        blocking_factor=1.00,
        rework_factor=1.00,
        maturity_factor=1.00,
        morale=0.75,
        salary_satisfaction=0.70,
        knowledge_distribution=0.70,
        turnover_risk=0.07,
    ),
    TeamProfile(
        name="Equipo junior",
        team_size=6,
        productivity_factor=0.85,
        blocking_factor=1.25,
        rework_factor=1.30,
        maturity_factor=0.80,
        morale=0.68,
        salary_satisfaction=0.65,
        knowledge_distribution=0.55,
        turnover_risk=0.10,
    ),
    TeamProfile(
        name="Equipo distribuido",
        team_size=6,
        productivity_factor=0.95,
        blocking_factor=1.35,
        rework_factor=1.15,
        maturity_factor=0.85,
        morale=0.70,
        salary_satisfaction=0.68,
        knowledge_distribution=0.60,
        turnover_risk=0.09,
    ),
]


WORKLOAD_PROFILES = [
    WorkloadProfile(
        name="Carga baja",
        num_tasks=30,
        dependency_factor=0.85,
        urgency_factor=0.80,
        average_complexity=0.85,
    ),
    WorkloadProfile(
        name="Carga media",
        num_tasks=40,
        dependency_factor=1.00,
        urgency_factor=1.00,
        average_complexity=1.00,
    ),
    WorkloadProfile(
        name="Carga alta",
        num_tasks=55,
        dependency_factor=1.25,
        urgency_factor=1.20,
        average_complexity=1.15,
    ),
    WorkloadProfile(
        name="Alta dependencia",
        num_tasks=40,
        dependency_factor=1.60,
        urgency_factor=1.10,
        average_complexity=1.25,
    ),
]


PROCESS_CONDITIONS = [
    ProcessCondition(
        name="Condición favorable",
        backlog_quality=0.90,
        handoff_quality=0.90,
        meeting_fatigue=0.05,
        management_quality=0.85,
        client_feedback_quality=0.85,
    ),
    ProcessCondition(
        name="Condición estándar",
        backlog_quality=0.75,
        handoff_quality=0.75,
        meeting_fatigue=0.10,
        management_quality=0.70,
        client_feedback_quality=0.70,
    ),
    ProcessCondition(
        name="Backlog débil",
        backlog_quality=0.55,
        handoff_quality=0.75,
        meeting_fatigue=0.12,
        management_quality=0.65,
        client_feedback_quality=0.65,
    ),
    ProcessCondition(
        name="Hand-off débil",
        backlog_quality=0.75,
        handoff_quality=0.50,
        meeting_fatigue=0.12,
        management_quality=0.65,
        client_feedback_quality=0.65,
    ),
    ProcessCondition(
        name="Alta fatiga de reuniones",
        backlog_quality=0.70,
        handoff_quality=0.70,
        meeting_fatigue=0.25,
        management_quality=0.55,
        client_feedback_quality=0.65,
    ),
]


# ============================================================
# HELPERS
# ============================================================

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def stable_seed(*values: object) -> int:
    text = "|".join(str(v) for v in values)
    return abs(hash(text)) % 1_000_000_000


def ai_effects(ai_support: AISupport) -> dict:
    if ai_support == AISupport.NONE:
        return {
            "blocking_multiplier": 1.00,
            "rework_multiplier": 1.00,
            "backlog_bonus": 0.00,
            "handoff_bonus": 0.00,
            "productivity_bonus": 0.00,
        }

    if ai_support == AISupport.MODERATE:
        return {
            "blocking_multiplier": 0.93,
            "rework_multiplier": 0.90,
            "backlog_bonus": 0.05,
            "handoff_bonus": 0.05,
            "productivity_bonus": 0.03,
        }

    if ai_support == AISupport.HIGH:
        return {
            "blocking_multiplier": 0.85,
            "rework_multiplier": 0.80,
            "backlog_bonus": 0.10,
            "handoff_bonus": 0.10,
            "productivity_bonus": 0.06,
        }

    return {
        "blocking_multiplier": 1.00,
        "rework_multiplier": 1.00,
        "backlog_bonus": 0.00,
        "handoff_bonus": 0.00,
        "productivity_bonus": 0.00,
    }


# ============================================================
# EVENTS
# ============================================================

def possible_random_events() -> list[SprintEvent]:
    return [
        SprintEvent(
            name="Enfermedad",
            capacity_multiplier=0.88,
            blocking_multiplier=1.10,
            rework_multiplier=1.05,
            morale_delta=-0.02,
            duration_sprints=1,
        ),
        SprintEvent(
            name="Vacaciones",
            capacity_multiplier=0.90,
            blocking_multiplier=1.05,
            rework_multiplier=1.00,
            morale_delta=0.01,
            duration_sprints=1,
        ),
        SprintEvent(
            name="Feriado",
            capacity_multiplier=0.92,
            blocking_multiplier=1.03,
            duration_sprints=1,
        ),
        SprintEvent(
            name="Paternidad/Maternidad",
            capacity_multiplier=0.82,
            blocking_multiplier=1.18,
            rework_multiplier=1.08,
            morale_delta=0.02,
            duration_sprints=4,
        ),
        SprintEvent(
            name="Renuncia",
            capacity_multiplier=0.80,
            blocking_multiplier=1.30,
            rework_multiplier=1.18,
            morale_delta=-0.12,
            team_size_delta=-1,
            duration_sprints=3,
        ),
        SprintEvent(
            name="Despido",
            capacity_multiplier=0.78,
            blocking_multiplier=1.35,
            rework_multiplier=1.20,
            morale_delta=-0.18,
            team_size_delta=-1,
            duration_sprints=4,
        ),
        SprintEvent(
            name="Contratación",
            capacity_multiplier=1.05,
            blocking_multiplier=1.20,
            rework_multiplier=1.12,
            morale_delta=0.03,
            team_size_delta=1,
            onboarding_penalty=0.15,
            duration_sprints=3,
        ),
        SprintEvent(
            name="Intervención positiva de management",
            capacity_multiplier=1.02,
            blocking_multiplier=0.90,
            rework_multiplier=0.95,
            meeting_fatigue_delta=-0.03,
            morale_delta=0.06,
            backlog_quality_delta=0.05,
            duration_sprints=2,
        ),
        SprintEvent(
            name="Intervención negativa de management",
            capacity_multiplier=0.95,
            blocking_multiplier=1.15,
            rework_multiplier=1.10,
            meeting_fatigue_delta=0.08,
            morale_delta=-0.08,
            duration_sprints=2,
        ),
        SprintEvent(
            name="Feedback positivo del cliente",
            capacity_multiplier=1.00,
            blocking_multiplier=0.95,
            rework_multiplier=0.92,
            backlog_quality_delta=0.04,
            morale_delta=0.03,
            duration_sprints=1,
        ),
        SprintEvent(
            name="Feedback tardío del cliente",
            capacity_multiplier=0.98,
            blocking_multiplier=1.08,
            rework_multiplier=1.25,
            backlog_quality_delta=-0.03,
            morale_delta=-0.03,
            duration_sprints=1,
        ),
        SprintEvent(
            name="Ajuste salarial",
            capacity_multiplier=1.02,
            blocking_multiplier=0.98,
            morale_delta=0.08,
            duration_sprints=2,
        ),
        SprintEvent(
            name="Congelamiento salarial",
            capacity_multiplier=0.98,
            blocking_multiplier=1.05,
            rework_multiplier=1.03,
            morale_delta=-0.08,
            duration_sprints=3,
        ),
        SprintEvent(
            name="Presión de deadline",
            capacity_multiplier=1.08,
            blocking_multiplier=1.12,
            rework_multiplier=1.20,
            meeting_fatigue_delta=0.05,
            morale_delta=-0.04,
            duration_sprints=1,
        ),
    ]


def event_probability(
    scenario: Scenario,
    team: TeamProfile,
    condition: ProcessCondition,
) -> float:
    base = 0.20

    if scenario == Scenario.JLR_4D_NO_ADAPTATION:
        base += 0.06

    if team.name == "Equipo distribuido":
        base += 0.04

    if team.salary_satisfaction < 0.70:
        base += 0.03

    if condition.management_quality < 0.60:
        base += 0.04

    return clamp(base, 0.05, 0.45)


def select_random_events(
    scenario: Scenario,
    team: TeamProfile,
    condition: ProcessCondition,
) -> list[SprintEvent]:
    events = []
    probability = event_probability(scenario, team, condition)

    if random.random() < probability:
        events.append(random.choice(possible_random_events()))

    # Turnover risk is explicit and salary-related.
    adjusted_turnover_risk = team.turnover_risk * (1.20 - team.salary_satisfaction)
    if random.random() < adjusted_turnover_risk:
        events.append(
            SprintEvent(
                name="Renuncia por baja satisfacción",
                capacity_multiplier=0.82,
                blocking_multiplier=1.25,
                rework_multiplier=1.15,
                morale_delta=-0.12,
                team_size_delta=-1,
                duration_sprints=3,
            )
        )

    return events


# ============================================================
# TASK GENERATION
# ============================================================

def generate_tasks(
    num_tasks: int,
    sprint_days: int,
    workload: WorkloadProfile,
    backlog_quality: float,
) -> list[Task]:
    tasks = []

    for i in range(num_tasks):
        effort = random.choices(
            [1, 2, 3, 5, 8],
            weights=[0.20, 0.30, 0.25, 0.18, 0.07],
        )[0]

        priority = random.choices(
            ["high", "medium", "low"],
            weights=[
                0.25 * workload.urgency_factor,
                0.50,
                0.25,
            ],
        )[0]

        # Poor backlog quality means tasks arrive less clearly and later.
        max_arrival_window = int((sprint_days // 2) * (1.30 - backlog_quality))
        max_arrival_window = clamp(max_arrival_window, 1, sprint_days)
        arrival_day = random.choice(range(0, int(max_arrival_window)))

        complexity = random.uniform(
            0.75 * workload.average_complexity,
            1.25 * workload.average_complexity,
        )

        tasks.append(
            Task(
                id=i,
                effort=effort,
                remaining=effort,
                priority=priority,
                arrival_day=arrival_day,
                complexity=complexity,
            )
        )

    return tasks


# ============================================================
# SCENARIO BEHAVIOR
# ============================================================

def get_available_devs(scenario: Scenario, day: int, team_size: int) -> int:
    weekday = day % 5

    if scenario == Scenario.SCRUM_5D:
        return team_size

    if scenario == Scenario.JLR_4D_NO_ADAPTATION:
        if weekday == 4:
            return 0
        return team_size

    if scenario == Scenario.JLR_4D_ADAPTED:
        if weekday == 4:
            return max(1, team_size // 2)
        return team_size

    return team_size


def daily_meeting_penalty(
    scenario: Scenario,
    meeting_fatigue: float,
) -> float:
    if scenario == Scenario.SCRUM_5D:
        return meeting_fatigue * 0.50

    if scenario == Scenario.JLR_4D_NO_ADAPTATION:
        return meeting_fatigue * 1.25

    if scenario == Scenario.JLR_4D_ADAPTED:
        return meeting_fatigue * 0.75

    return meeting_fatigue


def blocking_probability(
    scenario: Scenario,
    task: Task,
    team: TeamProfile,
    workload: WorkloadProfile,
    backlog_quality: float,
    event_blocking_multiplier: float,
    ai_support: AISupport,
) -> float:
    base = {
        Scenario.SCRUM_5D: 0.05,
        Scenario.JLR_4D_NO_ADAPTATION: 0.18,
        Scenario.JLR_4D_ADAPTED: 0.08,
    }[scenario]

    if task.priority == "high":
        base += 0.05

    ai = ai_effects(ai_support)

    backlog_penalty = 1 + (1 - backlog_quality)
    complexity_penalty = task.complexity
    dependency_penalty = workload.dependency_factor
    knowledge_bonus = 1.15 - team.knowledge_distribution

    probability = (
        base
        * team.blocking_factor
        * dependency_penalty
        * complexity_penalty
        * backlog_penalty
        * knowledge_bonus
        * event_blocking_multiplier
        * ai["blocking_multiplier"]
    )

    return clamp(probability, 0.01, 0.90)


def rework_probability(
    scenario: Scenario,
    task: Task,
    team: TeamProfile,
    workload: WorkloadProfile,
    backlog_quality: float,
    handoff_quality: float,
    event_rework_multiplier: float,
    ai_support: AISupport,
) -> float:
    base = {
        Scenario.SCRUM_5D: 0.04,
        Scenario.JLR_4D_NO_ADAPTATION: 0.15,
        Scenario.JLR_4D_ADAPTED: 0.07,
    }[scenario]

    if task.priority == "high":
        base += 0.03

    ai = ai_effects(ai_support)

    backlog_penalty = 1 + (1 - backlog_quality)
    handoff_penalty = 1 + (1 - handoff_quality)
    complexity_penalty = task.complexity

    probability = (
        base
        * team.rework_factor
        * workload.dependency_factor
        * backlog_penalty
        * handoff_penalty
        * complexity_penalty
        * event_rework_multiplier
        * ai["rework_multiplier"]
    )

    return clamp(probability, 0.01, 0.90)


def unblock_probability(
    scenario: Scenario,
    team: TeamProfile,
    handoff_quality: float,
) -> float:
    base = {
        Scenario.SCRUM_5D: 0.60,
        Scenario.JLR_4D_NO_ADAPTATION: 0.35,
        Scenario.JLR_4D_ADAPTED: 0.75,
    }[scenario]

    if scenario == Scenario.JLR_4D_ADAPTED:
        base *= handoff_quality
    else:
        base *= 0.80 + (team.maturity_factor * 0.10)

    if team.name == "Equipo distribuido":
        base -= 0.10

    if team.name == "Equipo senior":
        base += 0.05

    return clamp(base, 0.05, 0.95)


# ============================================================
# ACTIVE EVENTS
# ============================================================

def combine_active_events(active_events: list[SprintEvent]) -> dict:
    if not active_events:
        return {
            "capacity_multiplier": 1.0,
            "blocking_multiplier": 1.0,
            "rework_multiplier": 1.0,
            "meeting_fatigue_delta": 0.0,
            "morale_delta": 0.0,
            "backlog_quality_delta": 0.0,
            "handoff_quality_delta": 0.0,
            "team_size_delta": 0,
            "onboarding_penalty": 0.0,
        }

    capacity_multiplier = 1.0
    blocking_multiplier = 1.0
    rework_multiplier = 1.0
    meeting_fatigue_delta = 0.0
    morale_delta = 0.0
    backlog_quality_delta = 0.0
    handoff_quality_delta = 0.0
    team_size_delta = 0
    onboarding_penalty = 0.0

    for event in active_events:
        capacity_multiplier *= event.capacity_multiplier
        blocking_multiplier *= event.blocking_multiplier
        rework_multiplier *= event.rework_multiplier
        meeting_fatigue_delta += event.meeting_fatigue_delta
        morale_delta += event.morale_delta
        backlog_quality_delta += event.backlog_quality_delta
        handoff_quality_delta += event.handoff_quality_delta
        team_size_delta += event.team_size_delta
        onboarding_penalty += event.onboarding_penalty

    return {
        "capacity_multiplier": capacity_multiplier,
        "blocking_multiplier": blocking_multiplier,
        "rework_multiplier": rework_multiplier,
        "meeting_fatigue_delta": meeting_fatigue_delta,
        "morale_delta": morale_delta,
        "backlog_quality_delta": backlog_quality_delta,
        "handoff_quality_delta": handoff_quality_delta,
        "team_size_delta": team_size_delta,
        "onboarding_penalty": onboarding_penalty,
    }


def age_events(active_events: list[tuple[SprintEvent, int]]) -> list[tuple[SprintEvent, int]]:
    updated = []
    for event, remaining in active_events:
        if remaining - 1 > 0:
            updated.append((event, remaining - 1))
    return updated


# ============================================================
# SIMULATION
# ============================================================

def simulate_sprint(
    scenario: Scenario,
    team: TeamProfile,
    workload: WorkloadProfile,
    condition: ProcessCondition,
    ai_support: AISupport,
    experiment_id: int,
    sprint_id: int,
    active_events: list[SprintEvent],
    sprint_days: int = 10,
    seed: Optional[int] = None,
) -> dict:
    if seed is not None:
        random.seed(seed)

    event_effects = combine_active_events(active_events)
    ai = ai_effects(ai_support)

    current_morale = clamp(team.morale + event_effects["morale_delta"], 0.20, 1.00)

    current_backlog_quality = clamp(
        condition.backlog_quality
        + event_effects["backlog_quality_delta"]
        + ai["backlog_bonus"],
        0.20,
        1.00,
    )

    current_handoff_quality = clamp(
        condition.handoff_quality
        + event_effects["handoff_quality_delta"]
        + ai["handoff_bonus"],
        0.20,
        1.00,
    )

    current_meeting_fatigue = clamp(
        condition.meeting_fatigue
        + event_effects["meeting_fatigue_delta"],
        0.00,
        0.60,
    )

    current_team_size = max(1, team.team_size + event_effects["team_size_delta"])

    productivity_adjustment = (
        team.productivity_factor
        * event_effects["capacity_multiplier"]
        * (0.80 + current_morale * 0.25)
        * (1 + ai["productivity_bonus"])
        * (1 - event_effects["onboarding_penalty"])
    )

    tasks = generate_tasks(
        num_tasks=workload.num_tasks,
        sprint_days=sprint_days,
        workload=workload,
        backlog_quality=current_backlog_quality,
    )

    total_blocked_events = 0
    total_rework_events = 0
    total_available_capacity = 0
    total_used_capacity = 0

    for day in range(sprint_days):
        available_devs = get_available_devs(
            scenario=scenario,
            day=day,
            team_size=current_team_size,
        )

        meeting_penalty = daily_meeting_penalty(
            scenario=scenario,
            meeting_fatigue=current_meeting_fatigue,
        )

        effective_capacity = available_devs * productivity_adjustment
        effective_capacity *= (1 - meeting_penalty)

        daily_capacity = max(0, int(round(effective_capacity)))
        total_available_capacity += daily_capacity

        for task in tasks:
            if task.blocked and not task.completed:
                task.blocked_days += 1

        for task in tasks:
            if task.blocked and not task.completed:
                if random.random() < unblock_probability(
                    scenario=scenario,
                    team=team,
                    handoff_quality=current_handoff_quality,
                ):
                    task.blocked = False

        available_tasks = [
            t for t in tasks
            if not t.completed
            and not t.blocked
            and t.arrival_day <= day
        ]

        priority_order = {"high": 0, "medium": 1, "low": 2}
        available_tasks.sort(key=lambda t: priority_order[t.priority])

        for task in available_tasks:
            if daily_capacity <= 0:
                break

            if task.started_day is None:
                task.started_day = day

            if random.random() < blocking_probability(
                scenario=scenario,
                task=task,
                team=team,
                workload=workload,
                backlog_quality=current_backlog_quality,
                event_blocking_multiplier=event_effects["blocking_multiplier"],
                ai_support=ai_support,
            ):
                task.blocked = True
                total_blocked_events += 1
                continue

            if random.random() < rework_probability(
                scenario=scenario,
                task=task,
                team=team,
                workload=workload,
                backlog_quality=current_backlog_quality,
                handoff_quality=current_handoff_quality,
                event_rework_multiplier=event_effects["rework_multiplier"],
                ai_support=ai_support,
            ):
                task.remaining += 1
                task.rework_events += 1
                total_rework_events += 1

            task.remaining -= 1
            task.worked_days += 1
            daily_capacity -= 1
            total_used_capacity += 1

            if task.remaining <= 0:
                task.completed = True
                task.completed_day = day

    completed_tasks = [t for t in tasks if t.completed]
    incomplete_tasks = [t for t in tasks if not t.completed]

    cycle_times = [
        t.completed_day - t.started_day + 1
        for t in completed_tasks
        if t.started_day is not None and t.completed_day is not None
    ]

    lead_times = [
        t.completed_day - t.arrival_day + 1
        for t in completed_tasks
        if t.completed_day is not None
    ]

    total_worked_days_completed = sum(t.worked_days for t in completed_tasks)
    total_blocked_days_completed = sum(t.blocked_days for t in completed_tasks)
    total_blocked_days_all = sum(t.blocked_days for t in tasks)

    flow_efficiency = (
        total_worked_days_completed
        / (total_worked_days_completed + total_blocked_days_completed)
        if total_worked_days_completed + total_blocked_days_completed > 0
        else 0
    )

    capacity_utilization = (
        total_used_capacity / total_available_capacity
        if total_available_capacity > 0
        else 0
    )

    return {
        "experiment_id": experiment_id,
        "sprint_id": sprint_id,
        "scenario": scenario.value,
        "team_profile": team.name,
        "workload_profile": workload.name,
        "condition_profile": condition.name,
        "ai_support": ai_support.value,
        "team_size": current_team_size,
        "num_tasks": workload.num_tasks,
        "effective_backlog_quality": current_backlog_quality,
        "effective_handoff_quality": current_handoff_quality,
        "effective_meeting_fatigue": current_meeting_fatigue,
        "effective_morale": current_morale,
        "active_events": ", ".join([event.name for event in active_events]) if active_events else "Sin evento",
        "event_count": len(active_events),
        "completed_tasks": len(completed_tasks),
        "incomplete_tasks": len(incomplete_tasks),
        "blocked_events": total_blocked_events,
        "blocked_days": total_blocked_days_all,
        "rework_events": total_rework_events,
        "avg_cycle_time_completed_only": (
            sum(cycle_times) / len(cycle_times) if cycle_times else 0
        ),
        "avg_lead_time_completed_only": (
            sum(lead_times) / len(lead_times) if lead_times else 0
        ),
        "flow_efficiency": flow_efficiency,
        "capacity_utilization": capacity_utilization,
    }


# ============================================================
# EXPERIMENTS
# ============================================================

def run_experiments(
    num_experiments: int = 20,
    num_sprints: int = 12,
    sprint_days: int = 10,
) -> pd.DataFrame:
    results = []

    for experiment_id in range(num_experiments):
        for team in TEAM_PROFILES:
            for workload in WORKLOAD_PROFILES:
                for condition in PROCESS_CONDITIONS:
                    for ai_support in AISupport:
                        for scenario in Scenario:
                            active_event_state: list[tuple[SprintEvent, int]] = []

                            for sprint_id in range(num_sprints):
                                seed = stable_seed(
                                    experiment_id,
                                    sprint_id,
                                    team.name,
                                    workload.name,
                                    condition.name,
                                    ai_support.value,
                                    scenario.value,
                                )
                                random.seed(seed)

                                active_event_state = age_events(active_event_state)

                                new_events = select_random_events(
                                    scenario=scenario,
                                    team=team,
                                    condition=condition,
                                )

                                for event in new_events:
                                    active_event_state.append(
                                        (event, event.duration_sprints)
                                    )

                                active_events = [
                                    event for event, _ in active_event_state
                                ]

                                result = simulate_sprint(
                                    scenario=scenario,
                                    team=team,
                                    workload=workload,
                                    condition=condition,
                                    ai_support=ai_support,
                                    experiment_id=experiment_id,
                                    sprint_id=sprint_id,
                                    active_events=active_events,
                                    sprint_days=sprint_days,
                                    seed=seed,
                                )

                                results.append(result)

    return pd.DataFrame(results)


# ============================================================
# EXPORTS
# ============================================================

def export_experiment_config() -> None:
    pd.DataFrame([t.__dict__ for t in TEAM_PROFILES]).to_csv(
        "config_team_profiles.csv", index=False
    )
    pd.DataFrame([w.__dict__ for w in WORKLOAD_PROFILES]).to_csv(
        "config_workload_profiles.csv", index=False
    )
    pd.DataFrame([c.__dict__ for c in PROCESS_CONDITIONS]).to_csv(
        "config_process_conditions.csv", index=False
    )
    pd.DataFrame([e.__dict__ for e in possible_random_events()]).to_csv(
        "config_events.csv", index=False
    )


def create_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(
        [
            "scenario",
            "team_profile",
            "workload_profile",
            "condition_profile",
            "ai_support",
        ]
    ).agg(
        completed_tasks_mean=("completed_tasks", "mean"),
        completed_tasks_std=("completed_tasks", "std"),
        incomplete_tasks_mean=("incomplete_tasks", "mean"),
        blocked_events_mean=("blocked_events", "mean"),
        blocked_days_mean=("blocked_days", "mean"),
        rework_events_mean=("rework_events", "mean"),
        flow_efficiency_mean=("flow_efficiency", "mean"),
        capacity_utilization_mean=("capacity_utilization", "mean"),
        effective_morale_mean=("effective_morale", "mean"),
        event_count_mean=("event_count", "mean"),
    ).reset_index()


# ============================================================
# PLOTS
# ============================================================

def ordered_scenarios() -> list[str]:
    return [
        Scenario.SCRUM_5D.value,
        Scenario.JLR_4D_ADAPTED.value,
        Scenario.JLR_4D_NO_ADAPTATION.value,
    ]


def plot_bar_by_scenario(
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    filename: str,
) -> None:
    summary = df.groupby("scenario")[metric].mean().reindex(ordered_scenarios())

    plt.figure(figsize=(10, 6))
    summary.plot(kind="bar")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Escenario")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_line_over_time(
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    filename: str,
) -> None:
    summary = df.groupby(["sprint_id", "scenario"])[metric].mean().reset_index()

    plt.figure(figsize=(12, 6))

    for scenario in ordered_scenarios():
        scenario_data = summary[summary["scenario"] == scenario]
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
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_metric_by_dimension(
    df: pd.DataFrame,
    dimension: str,
    metric: str,
    title: str,
    ylabel: str,
    xlabel: str,
    filename: str,
) -> None:
    pivot = df.groupby([dimension, "scenario"])[metric].mean().unstack()
    pivot = pivot[ordered_scenarios()]

    plt.figure(figsize=(14, 7))
    pivot.plot(kind="bar", ax=plt.gca())
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.xticks(rotation=20, ha="right")
    plt.legend(title="Escenario")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_ai_impact(
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    filename: str,
) -> None:
    pivot = df.groupby(["ai_support", "scenario"])[metric].mean().unstack()
    pivot = pivot[ordered_scenarios()]

    plt.figure(figsize=(12, 6))
    pivot.plot(kind="bar", ax=plt.gca())
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Nivel de soporte IA")
    plt.xticks(rotation=20, ha="right")
    plt.legend(title="Escenario")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_event_impact(df: pd.DataFrame) -> None:
    event_df = df[df["active_events"] != "Sin evento"].copy()

    if event_df.empty:
        return

    event_df["main_event"] = event_df["active_events"].str.split(",").str[0]

    top_events = (
        event_df["main_event"]
        .value_counts()
        .head(8)
        .index
        .tolist()
    )

    filtered = event_df[event_df["main_event"].isin(top_events)]

    pivot = filtered.groupby(["main_event", "scenario"])["completed_tasks"].mean().unstack()
    pivot = pivot[ordered_scenarios()]

    plt.figure(figsize=(14, 7))
    pivot.plot(kind="bar", ax=plt.gca())
    plt.title("Tareas completadas bajo eventos organizacionales")
    plt.ylabel("Tareas completadas")
    plt.xlabel("Evento")
    plt.xticks(rotation=25, ha="right")
    plt.legend(title="Escenario")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("16_completed_tasks_by_event.png", dpi=300)
    plt.close()

    pivot = filtered.groupby(["main_event", "scenario"])["blocked_days"].mean().unstack()
    pivot = pivot[ordered_scenarios()]

    plt.figure(figsize=(14, 7))
    pivot.plot(kind="bar", ax=plt.gca())
    plt.title("Días bloqueados bajo eventos organizacionales")
    plt.ylabel("Días bloqueados")
    plt.xlabel("Evento")
    plt.xticks(rotation=25, ha="right")
    plt.legend(title="Escenario")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("17_blocked_days_by_event.png", dpi=300)
    plt.close()


def create_plots(df: pd.DataFrame) -> None:
    plot_bar_by_scenario(
        df,
        "completed_tasks",
        "Tareas completadas promedio por escenario",
        "Tareas completadas",
        "01_completed_tasks_by_scenario.png",
    )

    plot_bar_by_scenario(
        df,
        "blocked_events",
        "Eventos de bloqueo promedio por escenario",
        "Eventos de bloqueo",
        "02_blocked_events_by_scenario.png",
    )

    plot_bar_by_scenario(
        df,
        "blocked_days",
        "Días bloqueados promedio por escenario",
        "Días bloqueados",
        "03_blocked_days_by_scenario.png",
    )

    plot_bar_by_scenario(
        df,
        "rework_events",
        "Eventos de retrabajo promedio por escenario",
        "Eventos de retrabajo",
        "04_rework_events_by_scenario.png",
    )

    plot_bar_by_scenario(
        df,
        "flow_efficiency",
        "Eficiencia de flujo promedio por escenario",
        "Eficiencia de flujo",
        "05_flow_efficiency_by_scenario.png",
    )

    plot_line_over_time(
        df,
        "completed_tasks",
        "Evolución de tareas completadas por sprint",
        "Tareas completadas",
        "06_completed_tasks_over_time.png",
    )

    plot_line_over_time(
        df,
        "blocked_days",
        "Evolución de días bloqueados por sprint",
        "Días bloqueados",
        "07_blocked_days_over_time.png",
    )

    plot_line_over_time(
        df,
        "flow_efficiency",
        "Evolución de eficiencia de flujo por sprint",
        "Eficiencia de flujo",
        "08_flow_efficiency_over_time.png",
    )

    plot_metric_by_dimension(
        df,
        "team_profile",
        "completed_tasks",
        "Tareas completadas por perfil de equipo",
        "Tareas completadas",
        "Perfil de equipo",
        "09_completed_tasks_by_team.png",
    )

    plot_metric_by_dimension(
        df,
        "workload_profile",
        "completed_tasks",
        "Tareas completadas por carga de trabajo",
        "Tareas completadas",
        "Carga de trabajo",
        "10_completed_tasks_by_workload.png",
    )

    plot_metric_by_dimension(
        df,
        "team_profile",
        "blocked_days",
        "Días bloqueados por perfil de equipo",
        "Días bloqueados",
        "Perfil de equipo",
        "11_blocked_days_by_team.png",
    )

    plot_metric_by_dimension(
        df,
        "workload_profile",
        "blocked_days",
        "Días bloqueados por carga de trabajo",
        "Días bloqueados",
        "Carga de trabajo",
        "12_blocked_days_by_workload.png",
    )

    plot_metric_by_dimension(
        df,
        "condition_profile",
        "completed_tasks",
        "Tareas completadas por condición de proceso",
        "Tareas completadas",
        "Condición de proceso",
        "13_completed_tasks_by_condition.png",
    )

    plot_metric_by_dimension(
        df,
        "condition_profile",
        "blocked_days",
        "Días bloqueados por condición de proceso",
        "Días bloqueados",
        "Condición de proceso",
        "14_blocked_days_by_condition.png",
    )

    plot_metric_by_dimension(
        df,
        "condition_profile",
        "flow_efficiency",
        "Eficiencia de flujo por condición de proceso",
        "Eficiencia de flujo",
        "Condición de proceso",
        "15_flow_efficiency_by_condition.png",
    )

    plot_ai_impact(
        df,
        "completed_tasks",
        "Impacto del soporte IA sobre tareas completadas",
        "Tareas completadas",
        "18_completed_tasks_by_ai.png",
    )

    plot_ai_impact(
        df,
        "blocked_days",
        "Impacto del soporte IA sobre días bloqueados",
        "Días bloqueados",
        "19_blocked_days_by_ai.png",
    )

    plot_event_impact(df)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    df = run_experiments(
        num_experiments=20,
        num_sprints=12,
        sprint_days=10,
    )

    summary = create_summary(df)
    scenario_summary = df.groupby("scenario").mean(numeric_only=True).reset_index()
    ai_summary = df.groupby(["scenario", "ai_support"]).mean(numeric_only=True).reset_index()
    event_summary = (
        df[df["active_events"] != "Sin evento"]
        .groupby(["scenario", "active_events"])
        .mean(numeric_only=True)
        .reset_index()
    )

    df.to_csv("simulation_results.csv", index=False)
    summary.to_csv("simulation_summary.csv", index=False)
    scenario_summary.to_csv("scenario_summary.csv", index=False)
    ai_summary.to_csv("ai_summary.csv", index=False)
    event_summary.to_csv("event_summary.csv", index=False)

    export_experiment_config()
    create_plots(df)

    total_sprints = len(df)

    print("\nSimulación finalizada.")
    print(f"Sprints simulados: {total_sprints}")

    print("\nResumen general por escenario:")
    print(scenario_summary)

    print("\nArchivos generados:")
    print("- simulation_results.csv")
    print("- simulation_summary.csv")
    print("- scenario_summary.csv")
    print("- ai_summary.csv")
    print("- event_summary.csv")
    print("- config_team_profiles.csv")
    print("- config_workload_profiles.csv")
    print("- config_process_conditions.csv")
    print("- config_events.csv")
    print("- 01_completed_tasks_by_scenario.png")
    print("- 02_blocked_events_by_scenario.png")
    print("- 03_blocked_days_by_scenario.png")
    print("- 04_rework_events_by_scenario.png")
    print("- 05_flow_efficiency_by_scenario.png")
    print("- 06_completed_tasks_over_time.png")
    print("- 07_blocked_days_over_time.png")
    print("- 08_flow_efficiency_over_time.png")
    print("- 09_completed_tasks_by_team.png")
    print("- 10_completed_tasks_by_workload.png")
    print("- 11_blocked_days_by_team.png")
    print("- 12_blocked_days_by_workload.png")
    print("- 13_completed_tasks_by_condition.png")
    print("- 14_blocked_days_by_condition.png")
    print("- 15_flow_efficiency_by_condition.png")
    print("- 16_completed_tasks_by_event.png")
    print("- 17_blocked_days_by_event.png")
    print("- 18_completed_tasks_by_ai.png")
    print("- 19_blocked_days_by_ai.png")