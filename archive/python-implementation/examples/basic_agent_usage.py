"""
Basic Agent Usage Example

Demonstrates how to use different agent types in the autonomous development system.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents import (
    FrontendAgent,
    BackendAgent,
    AlgorithmAgent,
    DevOpsAgent,
    AgentConfig,
)


async def example_frontend_agent():
    """Example: Using Frontend Agent"""
    print("\n=== Frontend Agent Example ===\n")

    config = AgentConfig(
        name="ui_specialist",
        model="claude-3-opus",
        specialization=["React", "TypeScript", "Accessibility"]
    )

    agent = FrontendAgent(config)

    # Execute task
    task = "Create a responsive login component with accessibility features"
    print(f"Task: {task}\n")

    result = await agent.execute(task)

    if result.success:
        print("✓ Success!")
        print(f"Output: {result.output}")
        print(f"Execution time: {result.execution_time:.2f}s")
    else:
        print(f"✗ Failed: {result.error}")


async def example_backend_agent():
    """Example: Using Backend Agent"""
    print("\n=== Backend Agent Example ===\n")

    config = AgentConfig(
        name="api_specialist",
        model="claude-3-opus",
        specialization=["API", "Database", "Performance"]
    )

    agent = BackendAgent(config)

    # Execute task
    task = "Optimize database queries for user authentication"
    print(f"Task: {task}\n")

    result = await agent.execute(task)

    if result.success:
        print("✓ Success!")
        print(f"Output: {result.output}")
    else:
        print(f"✗ Failed: {result.error}")


async def example_algorithm_agent():
    """Example: Using Algorithm Agent"""
    print("\n=== Algorithm Agent Example ===\n")

    config = AgentConfig(
        name="optimization_specialist",
        specialization=["Optimization", "Data Structures"]
    )

    agent = AlgorithmAgent(config)

    # Execute task
    task = "Implement efficient sorting algorithm for large datasets"
    print(f"Task: {task}\n")

    result = await agent.execute(task)

    if result.success:
        print("✓ Success!")
        print(f"Output: {result.output}")
    else:
        print(f"✗ Failed: {result.error}")


async def example_agent_retry():
    """Example: Agent with retry logic"""
    print("\n=== Agent Retry Example ===\n")

    config = AgentConfig(
        name="retry_agent",
        retry_limit=3,
        timeout=10
    )

    agent = DevOpsAgent(config)

    task = "Setup CI/CD pipeline with security scanning"
    print(f"Task: {task}\n")
    print("Attempting with retry logic (max 3 retries)...\n")

    result = await agent.execute_with_retry(task)

    if result.success:
        print("✓ Success after retries!")
        print(f"Output: {result.output}")
    else:
        print(f"✗ Failed after all retries: {result.error}")


async def example_multiple_agents():
    """Example: Running multiple agents concurrently"""
    print("\n=== Multiple Agents Concurrent Example ===\n")

    # Create multiple agents
    agents = [
        FrontendAgent(AgentConfig(name="frontend", model="claude-3-opus")),
        BackendAgent(AgentConfig(name="backend", model="claude-3-opus")),
        DevOpsAgent(AgentConfig(name="devops", model="claude-3-sonnet")),
    ]

    tasks = [
        "Create user dashboard",
        "Implement user API",
        "Setup deployment pipeline"
    ]

    print("Running 3 agents concurrently...\n")

    # Execute all concurrently
    results = await asyncio.gather(
        *[agent.execute(task) for agent, task in zip(agents, tasks)]
    )

    # Display results
    for agent, task, result in zip(agents, tasks, results):
        status = "✓" if result.success else "✗"
        print(f"{status} {agent.config.name}: {task}")
        if result.success:
            print(f"   Time: {result.execution_time:.2f}s")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Autonomous Development System - Agent Examples")
    print("="*60)

    # Run examples
    await example_frontend_agent()
    await asyncio.sleep(0.5)

    await example_backend_agent()
    await asyncio.sleep(0.5)

    await example_algorithm_agent()
    await asyncio.sleep(0.5)

    await example_agent_retry()
    await asyncio.sleep(0.5)

    await example_multiple_agents()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
