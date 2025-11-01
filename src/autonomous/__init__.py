"""
Autonomous System Module

Self-healing and autonomous operation capabilities.
"""

from .failure_analyzer import FailureAnalyzer, FailureReport, FailureType
from .auto_healer import AutoHealer, HealingStrategy

__all__ = [
    "FailureAnalyzer",
    "FailureReport",
    "FailureType",
    "AutoHealer",
    "HealingStrategy",
]

__version__ = "0.1.0"
