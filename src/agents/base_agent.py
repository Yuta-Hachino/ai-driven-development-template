"""
Base Agent Implementation

Provides the foundational BaseAgent class that all specialized agents inherit from.
Implements security checks, rate limiting, and audit logging.
"""

import asyncio
import time
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent type enumeration based on Google ADK specification"""
    BASE = "BaseAgent"
    LLM = "LlmAgent"
    SEQUENTIAL = "SequentialAgent"
    IF_ELSE = "IfElseAgent"
    FOR_LOOP = "ForLoopAgent"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str
    agent_type: AgentType
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    specialization: List[str] = field(default_factory=list)
    model: Optional[str] = None
    max_tokens: int = 4096
    timeout: int = 300
    retry_limit: int = 3
    resource_limits: Dict[str, str] = field(default_factory=dict)
    security_profile: str = "enterprise"
    worktree_pattern: Optional[str] = None


@dataclass
class AgentExecutionResult:
    """Result of agent execution"""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Rate limiting for agent operations"""

    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []

    def check_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        current_time = time.time()
        # Remove old requests outside time window
        self.requests = [
            req_time for req_time in self.requests
            if current_time - req_time < self.time_window
        ]

        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(current_time)
        return True


class BaseAgent(ABC):
    """
    Base agent class implementing core functionality for all agents.

    Features:
    - Security checks and validation
    - Rate limiting
    - Audit logging
    - Error handling and retry logic
    - Resource management
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.IDLE
        self.rate_limiter = RateLimiter(max_requests=100)
        self.execution_count = 0
        self.error_count = 0
        self._setup_security()

    def _setup_security(self):
        """Initialize security settings"""
        self.session_id = secrets.token_hex(16)
        logger.info(
            f"Agent {self.config.name} initialized with session {self.session_id}"
        )

    def validate_permissions(self, required_permission: str) -> bool:
        """Validate if agent has required permission"""
        if "*" in self.config.permissions:
            return True
        return required_permission in self.config.permissions

    def security_check(self, operation: str) -> bool:
        """
        Perform security check before operation.

        Args:
            operation: The operation to check

        Returns:
            True if security check passes
        """
        # Check rate limit
        if not self.rate_limiter.check_limit():
            logger.warning(
                f"Rate limit exceeded for agent {self.config.name}"
            )
            return False

        # Validate permissions
        permission_required = f"execute:{operation}"
        if not self.validate_permissions(permission_required):
            logger.warning(
                f"Permission denied for agent {self.config.name} "
                f"to execute {operation}"
            )
            return False

        return True

    async def audit_log(
        self,
        task: Any,
        result: AgentExecutionResult
    ):
        """
        Log agent action for audit trail.

        Args:
            task: The task that was executed
            result: The execution result
        """
        log_entry = {
            "timestamp": time.time(),
            "agent_name": self.config.name,
            "agent_type": self.config.agent_type.value,
            "session_id": self.session_id,
            "task": str(task),
            "success": result.success,
            "execution_time": result.execution_time,
            "error": result.error,
        }

        logger.info(f"Audit log: {log_entry}")

    async def handle_error(self, error: Exception) -> None:
        """
        Handle errors during execution.

        Args:
            error: The exception that occurred
        """
        self.error_count += 1
        logger.error(
            f"Error in agent {self.config.name}: {str(error)}",
            exc_info=True
        )

    @abstractmethod
    async def process(self, task: Any) -> Any:
        """
        Process the task. Must be implemented by subclasses.

        Args:
            task: The task to process

        Returns:
            The processed result
        """
        pass

    async def execute(self, task: Any) -> AgentExecutionResult:
        """
        Execute a task with security checks, error handling, and audit logging.

        Args:
            task: The task to execute

        Returns:
            AgentExecutionResult containing the execution outcome
        """
        start_time = time.time()
        self.status = AgentStatus.RUNNING

        try:
            # Security check
            if not self.security_check("task"):
                raise PermissionError(
                    f"Security check failed for agent {self.config.name}"
                )

            # Process with timeout
            result = await asyncio.wait_for(
                self.process(task),
                timeout=self.config.timeout
            )

            execution_time = time.time() - start_time
            self.execution_count += 1

            execution_result = AgentExecutionResult(
                success=True,
                output=result,
                execution_time=execution_time,
                metadata={
                    "agent_name": self.config.name,
                    "execution_count": self.execution_count,
                }
            )

            self.status = AgentStatus.COMPLETED

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Task execution timeout after {self.config.timeout}s"

            await self.handle_error(TimeoutError(error_msg))

            execution_result = AgentExecutionResult(
                success=False,
                output=None,
                error=error_msg,
                execution_time=execution_time,
            )

            self.status = AgentStatus.FAILED

        except Exception as e:
            execution_time = time.time() - start_time

            await self.handle_error(e)

            execution_result = AgentExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
            )

            self.status = AgentStatus.FAILED

        # Audit log
        await self.audit_log(task, execution_result)

        return execution_result

    async def execute_with_retry(
        self,
        task: Any,
        max_retries: Optional[int] = None
    ) -> AgentExecutionResult:
        """
        Execute task with retry logic.

        Args:
            task: The task to execute
            max_retries: Maximum number of retries (uses config.retry_limit if None)

        Returns:
            AgentExecutionResult containing the execution outcome
        """
        max_retries = max_retries or self.config.retry_limit

        for attempt in range(max_retries + 1):
            result = await self.execute(task)

            if result.success:
                return result

            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(
                    f"Retry {attempt + 1}/{max_retries} for agent "
                    f"{self.config.name} after {wait_time}s"
                )
                await asyncio.sleep(wait_time)

        return result

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "session_id": self.session_id,
        }


class LlmAgent(BaseAgent):
    """
    LLM-powered agent for complex reasoning tasks.

    This agent type uses Large Language Models (e.g., Claude, Gemini)
    to process tasks requiring natural language understanding and generation.
    """

    def __init__(self, config: AgentConfig):
        config.agent_type = AgentType.LLM
        super().__init__(config)
        self.model = config.model or "claude-3-opus"
        self.max_tokens = config.max_tokens

    async def process(self, task: Any) -> Any:
        """Process task using LLM"""
        # Placeholder for LLM integration
        # In production, this would call Claude API or Vertex AI
        logger.info(
            f"LLM Agent {self.config.name} processing task with model {self.model}"
        )

        # Simulate LLM processing
        await asyncio.sleep(0.1)

        return {
            "agent": self.config.name,
            "model": self.model,
            "task": str(task),
            "result": "Task processed successfully",
        }


class SequentialAgent(BaseAgent):
    """
    Agent that executes tasks in sequence.

    Useful for multi-step processes where order matters.
    """

    def __init__(self, config: AgentConfig):
        config.agent_type = AgentType.SEQUENTIAL
        super().__init__(config)
        self.steps: List[Any] = []

    async def process(self, task: Any) -> Any:
        """Process task sequentially"""
        results = []

        # If task is a list, process each item sequentially
        tasks = task if isinstance(task, list) else [task]

        for i, subtask in enumerate(tasks):
            logger.info(
                f"Sequential Agent {self.config.name} "
                f"processing step {i+1}/{len(tasks)}"
            )
            results.append(f"Step {i+1} completed: {subtask}")
            await asyncio.sleep(0.1)

        return results


class IfElseAgent(BaseAgent):
    """
    Decision-making agent with conditional logic.

    Evaluates conditions and makes decisions based on criteria.
    """

    def __init__(self, config: AgentConfig):
        config.agent_type = AgentType.IF_ELSE
        super().__init__(config)
        self.decision_threshold = getattr(config, 'decision_threshold', 0.5)

    async def process(self, task: Any) -> Any:
        """Process task with conditional logic"""
        # Evaluate condition (placeholder)
        score = 0.8  # Simulated evaluation score

        decision = "approve" if score >= self.decision_threshold else "reject"

        logger.info(
            f"IfElse Agent {self.config.name} made decision: {decision} "
            f"(score: {score}, threshold: {self.decision_threshold})"
        )

        return {
            "decision": decision,
            "score": score,
            "threshold": self.decision_threshold,
            "task": str(task),
        }


class ForLoopAgent(BaseAgent):
    """
    Agent that iterates over tasks.

    Useful for batch processing and repeated operations.
    """

    def __init__(self, config: AgentConfig):
        config.agent_type = AgentType.FOR_LOOP
        super().__init__(config)
        self.max_iterations = 10

    async def process(self, task: Any) -> Any:
        """Process task with iteration"""
        results = []

        # If task has items, iterate over them
        items = task if isinstance(task, list) else [task]
        items = items[:self.max_iterations]  # Limit iterations

        for i, item in enumerate(items):
            logger.info(
                f"ForLoop Agent {self.config.name} "
                f"iteration {i+1}/{len(items)}"
            )
            results.append(f"Iteration {i+1}: {item}")
            await asyncio.sleep(0.1)

        return results
