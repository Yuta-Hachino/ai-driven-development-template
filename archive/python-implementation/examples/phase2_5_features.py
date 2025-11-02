"""
Phase 2.5 Features Example

Demonstrates the multi-instance collaboration features added in Phase 2.5:
- Multi-instance coordination
- Project Memory system
- Tech Lead management
- Notification hub
- Auto-documentation
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parallel_execution import MultiInstanceManager, InstanceConfig
from memory import ProjectMemory, KnowledgeType
from management import TechLeadSystem, TaskPlanner, PlanningStrategy
from monitoring import NotificationHub, NotificationPriority, NotificationChannel
from documentation import AutoDocumenter


def example_multi_instance_coordination():
    """Example: Register and coordinate multiple Claude Code instances"""
    print("\n=== Multi-Instance Coordination ===\n")

    manager = MultiInstanceManager()

    # Register instances
    print("Registering Claude Code instances...\n")

    instance1 = InstanceConfig(
        instance_id=1,
        name="Frontend-Specialist",
        capabilities=["frontend", "ui", "react"],
        status="active",
        max_concurrent_tasks=2
    )

    instance2 = InstanceConfig(
        instance_id=2,
        name="Backend-Specialist",
        capabilities=["backend", "api", "database"],
        status="active",
        max_concurrent_tasks=3
    )

    instance3 = InstanceConfig(
        instance_id=3,
        name="Full-Stack",
        capabilities=["frontend", "backend", "testing"],
        status="active",
        max_concurrent_tasks=2
    )

    manager.register_instance(instance1)
    manager.register_instance(instance2)
    manager.register_instance(instance3)

    print(f"✓ Registered {len(manager.instances)} instances\n")

    # Create tasks
    print("Creating development tasks...\n")

    task1 = manager.create_task(
        description="Implement user authentication UI",
        priority="high",
        estimated_hours=8.0,
        required_skills=["frontend", "ui"]
    )

    task2 = manager.create_task(
        description="Build authentication API endpoints",
        priority="high",
        estimated_hours=12.0,
        required_skills=["backend", "api"]
    )

    task3 = manager.create_task(
        description="Write integration tests",
        priority="medium",
        estimated_hours=6.0,
        required_skills=["testing"]
    )

    print(f"✓ Created {len(manager.tasks)} tasks\n")

    # Auto-assign tasks
    print("Auto-assigning tasks based on skills and workload...\n")

    assignments = manager.auto_assign_tasks()

    for task_id, instance_id in assignments.items():
        task = manager.tasks[task_id]
        instance = manager.instances[instance_id]
        print(f"  • Task '{task.description[:40]}...' → {instance.name}")

    print()


def example_project_memory():
    """Example: Use Project Memory to preserve knowledge"""
    print("\n=== Project Memory System ===\n")

    memory = ProjectMemory(project_root=".")

    # Record architecture decision
    print("Recording architecture decision...\n")

    memory.record_decision(
        title="Use React for Frontend",
        decision="Adopt React with TypeScript for all frontend components",
        rationale="React provides component reusability, strong ecosystem, and TypeScript adds type safety",
        decided_by="tech_lead",
        alternatives=["Vue.js", "Angular", "Svelte"]
    )

    # Record implementation pattern
    print("Recording implementation pattern...\n")

    memory.record_pattern(
        title="API Error Handling Pattern",
        description="Standardized error handling for API endpoints",
        example="""
@app.route('/api/users')
def get_users():
    try:
        users = fetch_users()
        return jsonify(users), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'Internal server error'}), 500
        """,
        when_to_use="All API endpoints should follow this pattern",
        created_by="backend_specialist"
    )

    # Record learning from failure
    print("Recording learning from failure...\n")

    memory.record_learning(
        title="Database Connection Pool Exhaustion",
        what_happened="Application crashed due to connection pool exhaustion under load",
        what_learned="Need to configure proper connection pool size and implement connection timeouts",
        action_items=[
            "Increase pool size from 10 to 50",
            "Add connection timeout of 30 seconds",
            "Implement connection health checks",
            "Add monitoring for pool usage"
        ],
        created_by="devops_specialist"
    )

    # Search knowledge base
    print("Searching knowledge base...\n")

    results = memory.search_entries(query="error handling", limit=5)
    print(f"Found {len(results)} relevant entries:\n")
    for entry in results:
        print(f"  • [{entry.knowledge_type.value}] {entry.title}")

    print()


def example_tech_lead_system():
    """Example: Use Tech Lead System for task planning"""
    print("\n=== Tech Lead Management System ===\n")

    # Create task planner
    planner = TaskPlanner()

    print("Creating task plan using Feature-First strategy...\n")

    tasks = planner.create_feature_plan(
        feature_name="User Authentication",
        feature_description="Implement secure user authentication with OAuth 2.0",
        strategy=PlanningStrategy.FEATURE_FIRST,
        estimated_complexity="medium"
    )

    print(f"✓ Generated {len(tasks)} tasks:\n")
    for task in tasks:
        print(f"  {task.task_id}:")
        print(f"    Title: {task.title}")
        print(f"    Estimated: {task.estimated_hours}h")
        print(f"    Skills: {', '.join(task.required_skills)}")
        print()

    # Create plan in Tech Lead system
    tech_lead = TechLeadSystem(project_root=".")

    plan = tech_lead.create_task_plan(
        feature_name="User Authentication",
        description="Implement secure user authentication with OAuth 2.0",
        created_by="human",
        tasks=tasks
    )

    print(f"✓ Created task plan: {plan.plan_id}")
    print(f"  Total estimated hours: {plan.total_estimated_hours}h")
    print()

    # Generate progress report
    print("Generating progress report...\n")

    # Simulate some completed tasks
    if tasks:
        tech_lead.assign_task(plan.plan_id, tasks[0].task_id, 1)
        tech_lead.start_task(plan.plan_id, tasks[0].task_id)
        tech_lead.complete_task(plan.plan_id, tasks[0].task_id)

    report = tech_lead.generate_progress_report()

    print(f"  Overall completion: {report.overall_completion:.1f}%")
    print(f"  Velocity: {report.velocity:.1f} tasks/day")
    print(f"  Tasks: {report.tasks_completed} completed, {report.tasks_in_progress} in progress")
    print()


def example_notification_hub():
    """Example: Send notifications through multiple channels"""
    print("\n=== Notification Hub ===\n")

    hub = NotificationHub(project_root=".")

    # Send a simple notification
    print("Sending notification...\n")

    notification = hub.send_notification(
        title="Build completed successfully",
        message="The development build completed with all tests passing.",
        priority=NotificationPriority.LOW,
        channels=[NotificationChannel.CONSOLE]
    )

    print(f"✓ Notification sent via {len(notification.sent_to)} channels\n")

    # Create alert rule
    print("Creating alert rule...\n")

    rule = hub.create_alert_rule(
        name="Too many test failures",
        condition="test_failures > 5",
        priority=NotificationPriority.HIGH,
        channels=[NotificationChannel.CONSOLE, NotificationChannel.GITHUB_ISSUE],
        cooldown_minutes=30
    )

    print(f"✓ Created alert rule: {rule.name}\n")

    # Evaluate alert rules
    print("Evaluating alert rules...\n")

    context = {
        "test_failures": 7,
        "tasks_blocked": 2,
        "velocity": 2.5
    }

    triggered = hub.evaluate_alert_rules(context)

    if triggered:
        print(f"✓ Triggered {len(triggered)} alert(s):\n")
        for alert in triggered:
            print(f"  • {alert.title}")
    else:
        print("  No alerts triggered\n")

    print()


def example_auto_documentation():
    """Example: Automatically generate documentation"""
    print("\n=== Auto-Documentation System ===\n")

    documenter = AutoDocumenter(project_root=".")

    # Generate API documentation
    print("Generating API documentation...\n")

    api_files = documenter.generate_api_documentation(
        module_path="src/parallel_execution/multi_instance_manager.py"
    )

    print(f"✓ Generated {len(api_files)} API documentation file(s)\n")

    # Update README
    print("Updating README.md...\n")

    readme_sections = {
        'header': "# Autonomous Development System\n\n",
        'description': "A multi-instance collaborative development system powered by Claude Code.\n\n",
        'features': """## Features

- **Multi-Instance Coordination**: Multiple Claude Code instances working in parallel
- **Project Memory**: Shared knowledge base and context preservation
- **Tech Lead System**: Intelligent task planning and assignment
- **Self-Healing**: Automatic failure detection and recovery
- **Auto-Documentation**: Keep docs in sync with code

"""
    }

    readme = documenter.update_readme(sections=readme_sections)
    print(f"✓ Updated {readme}\n")

    # Generate changelog
    print("Generating changelog...\n")

    changelog = documenter.generate_changelog()
    print(f"✓ Generated {changelog}\n")

    print()


async def example_complete_workflow():
    """Example: Complete workflow combining all Phase 2.5 features"""
    print("\n" + "="*60)
    print("Complete Phase 2.5 Workflow")
    print("="*60 + "\n")

    # Step 1: Initialize systems
    print("Step 1: Initializing systems...\n")

    manager = MultiInstanceManager()
    memory = ProjectMemory(project_root=".")
    tech_lead = TechLeadSystem(project_root=".")
    hub = NotificationHub(project_root=".")
    planner = TaskPlanner()

    # Step 2: Register instances
    print("Step 2: Registering Claude Code instances...\n")

    for i in range(1, 4):
        instance = InstanceConfig(
            instance_id=i,
            name=f"Instance-{i}",
            capabilities=["backend", "frontend", "testing"],
            status="active",
            max_concurrent_tasks=2
        )
        manager.register_instance(instance)

    # Step 3: Create task plan
    print("Step 3: Creating task plan...\n")

    tasks = planner.create_feature_plan(
        feature_name="Dashboard Analytics",
        feature_description="Build analytics dashboard with real-time metrics",
        strategy=PlanningStrategy.AGILE,
        estimated_complexity="high"
    )

    plan = tech_lead.create_task_plan(
        feature_name="Dashboard Analytics",
        description="Build analytics dashboard",
        created_by="workflow",
        tasks=tasks
    )

    # Step 4: Assign tasks
    print("Step 4: Assigning tasks to instances...\n")

    for task in tasks[:3]:  # Assign first 3 tasks
        # Find best instance
        best_instance = manager.instances[1]  # Simplified
        tech_lead.assign_task(plan.plan_id, task.task_id, best_instance.instance_id)

    # Step 5: Record decision in memory
    print("Step 5: Recording architectural decision...\n")

    memory.record_decision(
        title="Use Chart.js for Analytics",
        decision="Adopt Chart.js for dashboard visualizations",
        rationale="Lightweight, good performance, extensive chart types",
        decided_by="workflow",
        alternatives=["D3.js", "Recharts"]
    )

    # Step 6: Send progress notification
    print("Step 6: Sending progress notification...\n")

    hub.send_notification(
        title="Task Plan Created",
        message=f"Created plan {plan.plan_id} with {len(tasks)} tasks for Dashboard Analytics",
        priority=NotificationPriority.MEDIUM,
        channels=[NotificationChannel.CONSOLE]
    )

    # Step 7: Generate progress report
    print("Step 7: Generating progress report...\n")

    report = tech_lead.generate_progress_report()
    print(f"  Progress: {report.overall_completion:.1f}%")
    print(f"  Velocity: {report.velocity:.1f} tasks/day\n")

    print("="*60)
    print("Workflow Complete!")
    print("="*60 + "\n")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Phase 2.5 Features - Interactive Examples")
    print("="*60)

    # Individual feature examples
    example_multi_instance_coordination()
    await asyncio.sleep(0.5)

    example_project_memory()
    await asyncio.sleep(0.5)

    example_tech_lead_system()
    await asyncio.sleep(0.5)

    example_notification_hub()
    await asyncio.sleep(0.5)

    example_auto_documentation()
    await asyncio.sleep(0.5)

    # Complete workflow
    await example_complete_workflow()

    print("\n💡 Tip: These examples demonstrate Phase 2.5 capabilities.")
    print("   In production, these systems work together automatically.\n")


if __name__ == "__main__":
    asyncio.run(main())
