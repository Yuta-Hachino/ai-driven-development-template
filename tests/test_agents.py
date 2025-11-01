"""
Tests for Agent Framework
"""

import pytest
import asyncio
from src.agents.base_agent import (
    BaseAgent,
    AgentConfig,
    AgentType,
    LlmAgent,
    SequentialAgent,
    IfElseAgent,
)


@pytest.fixture
def base_config():
    """Base agent configuration"""
    return AgentConfig(
        name="test_agent",
        agent_type=AgentType.BASE,
        description="Test agent",
        permissions=["execute:task"],
    )


@pytest.mark.asyncio
async def test_base_agent_creation(base_config):
    """Test base agent creation"""

    class TestAgent(BaseAgent):
        async def process(self, task):
            return {"result": "processed"}

    agent = TestAgent(base_config)

    assert agent.config.name == "test_agent"
    assert agent.config.agent_type == AgentType.BASE
    assert len(agent.config.permissions) > 0


@pytest.mark.asyncio
async def test_agent_execution(base_config):
    """Test agent task execution"""

    class TestAgent(BaseAgent):
        async def process(self, task):
            return {"result": f"processed: {task}"}

    agent = TestAgent(base_config)
    result = await agent.execute("test_task")

    assert result.success is True
    assert result.output["result"] == "processed: test_task"
    assert result.execution_time >= 0


@pytest.mark.asyncio
async def test_agent_security_check(base_config):
    """Test agent security checks"""

    class TestAgent(BaseAgent):
        async def process(self, task):
            return {"result": "processed"}

    agent = TestAgent(base_config)

    # Should pass with correct permission
    assert agent.security_check("task") is True

    # Modify permissions to test failure
    agent.config.permissions = []
    assert agent.security_check("task") is False


@pytest.mark.asyncio
async def test_llm_agent():
    """Test LLM agent"""
    config = AgentConfig(
        name="llm_test",
        agent_type=AgentType.LLM,
        model="claude-3-opus",
    )

    agent = LlmAgent(config)
    result = await agent.execute("test task")

    assert result.success is True
    assert "result" in result.output


@pytest.mark.asyncio
async def test_sequential_agent():
    """Test sequential agent"""
    config = AgentConfig(
        name="seq_test",
        agent_type=AgentType.SEQUENTIAL,
    )

    agent = SequentialAgent(config)
    tasks = ["task1", "task2", "task3"]
    result = await agent.execute(tasks)

    assert result.success is True
    assert len(result.output) == 3


@pytest.mark.asyncio
async def test_ifelse_agent():
    """Test if-else decision agent"""
    config = AgentConfig(
        name="decision_test",
        agent_type=AgentType.IF_ELSE,
    )

    agent = IfElseAgent(config)
    result = await agent.execute("decision task")

    assert result.success is True
    assert "decision" in result.output
    assert result.output["decision"] in ["approve", "reject"]


@pytest.mark.asyncio
async def test_agent_retry():
    """Test agent retry logic"""

    class FailingAgent(BaseAgent):
        def __init__(self, config):
            super().__init__(config)
            self.attempt = 0

        async def process(self, task):
            self.attempt += 1
            if self.attempt < 3:
                raise Exception("Simulated failure")
            return {"result": "success after retries"}

    config = AgentConfig(
        name="retry_test",
        agent_type=AgentType.BASE,
        retry_limit=3,
    )

    agent = FailingAgent(config)
    result = await agent.execute_with_retry("test")

    assert result.success is True
    assert agent.attempt == 3


def test_agent_status():
    """Test agent status reporting"""

    class TestAgent(BaseAgent):
        async def process(self, task):
            return {"result": "processed"}

    config = AgentConfig(
        name="status_test",
        agent_type=AgentType.BASE,
    )

    agent = TestAgent(config)
    status = agent.get_status()

    assert status["name"] == "status_test"
    assert status["type"] == "BaseAgent"
    assert "session_id" in status
