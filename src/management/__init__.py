"""
Management Module

Provides tech lead coordination and task planning for autonomous development.
Enables hierarchical management of multiple Claude Code instances.
"""

from .tech_lead_system import (
    TechLeadSystem,
    TaskPlan,
    TaskBreakdown,
    ProgressReport,
    BottleneckDetection,
)
from .task_planner import (
    TaskPlanner,
    TaskTemplate,
    TaskDependency,
    PlanningStrategy,
)

__all__ = [
    "TechLeadSystem",
    "TaskPlan",
    "TaskBreakdown",
    "ProgressReport",
    "BottleneckDetection",
    "TaskPlanner",
    "TaskTemplate",
    "TaskDependency",
    "PlanningStrategy",
]

__version__ = "0.1.0"
