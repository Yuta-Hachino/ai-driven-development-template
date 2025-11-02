"""
Autonomous Development Agent Framework

This module provides the core agent framework for the autonomous development system,
implementing Google ADK patterns with enterprise security.
"""

from .base_agent import BaseAgent, AgentConfig, AgentExecutionResult
from .development_agents import (
    FrontendAgent,
    BackendAgent,
    AlgorithmAgent,
    DevOpsAgent,
)
from .management_agents import (
    ApprovalAgent,
    SecurityAgent,
    IntegrationAgent,
)

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentExecutionResult",
    "FrontendAgent",
    "BackendAgent",
    "AlgorithmAgent",
    "DevOpsAgent",
    "ApprovalAgent",
    "SecurityAgent",
    "IntegrationAgent",
]

__version__ = "0.1.0"
