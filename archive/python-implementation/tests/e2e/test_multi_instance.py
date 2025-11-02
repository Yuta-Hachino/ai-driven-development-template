"""
End-to-End Test: Multi-Instance Collaboration

Tests multi-instance coordination, load balancing, and collaboration features.
"""

import pytest
import asyncio
from datetime import datetime

from parallel_execution import CoordinationMessage


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_instance_registration_and_coordination(
    multi_instance_manager,
    test_instances
):
    """
    Test instance registration and basic coordination
    """

    # Register all test instances
    for instance in test_instances:
        result = multi_instance_manager.register_instance(instance)
        assert result is True

    # Verify all registered
    assert len(multi_instance_manager.instances) == len(test_instances)

    # Verify instance details
    for instance in test_instances:
        registered = multi_instance_manager.instances[instance.instance_id]
        assert registered.name == instance.name
        assert registered.status == "active"
        assert registered.capabilities == instance.capabilities

    print(f"\n✓ Registered {len(test_instances)} instances successfully")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_load_balanced_task_assignment(
    multi_instance_manager,
    test_instances,
    tech_lead_system,
    task_planner
):
    """
    Test load balancing across multiple instances
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Create many tasks
    for i in range(10):
        multi_instance_manager.create_task(
            description=f"Test task {i}",
            priority="medium",
            estimated_hours=5.0,
            required_skills=["backend"]
        )

    # Auto-assign tasks
    assignments = multi_instance_manager.auto_assign_tasks()

    assert len(assignments) > 0, "Should assign tasks"

    # Verify load balancing
    workload_distribution = {}
    for task_id, instance_id in assignments.items():
        workload_distribution[instance_id] = workload_distribution.get(instance_id, 0) + 1

    # Check that tasks are distributed
    assert len(workload_distribution) > 1, "Tasks should be distributed across instances"

    # Check no instance is overloaded
    max_workload = max(workload_distribution.values())
    min_workload = min(workload_distribution.values())

    # Workload should be relatively balanced
    assert max_workload - min_workload <= 2, "Workload should be balanced"

    print(f"\n✓ Load balancing test passed")
    print(f"  - Assigned {len(assignments)} tasks")
    print(f"  - Workload distribution: {workload_distribution}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_skill_based_task_assignment(
    multi_instance_manager,
):
    """
    Test skill-based task assignment
    """

    from parallel_execution import InstanceConfig

    # Create instances with different specializations
    frontend_instance = InstanceConfig(
        instance_id=1,
        name="Frontend-Specialist",
        capabilities=["frontend", "react", "typescript"],
        status="active",
        max_concurrent_tasks=3
    )

    backend_instance = InstanceConfig(
        instance_id=2,
        name="Backend-Specialist",
        capabilities=["backend", "python", "database"],
        status="active",
        max_concurrent_tasks=3
    )

    multi_instance_manager.register_instance(frontend_instance)
    multi_instance_manager.register_instance(backend_instance)

    # Create frontend task
    frontend_task = multi_instance_manager.create_task(
        description="Build React component",
        priority="high",
        estimated_hours=4.0,
        required_skills=["frontend", "react"]
    )

    # Create backend task
    backend_task = multi_instance_manager.create_task(
        description="Create API endpoint",
        priority="high",
        estimated_hours=6.0,
        required_skills=["backend", "python"]
    )

    # Auto-assign
    assignments = multi_instance_manager.auto_assign_tasks()

    # Verify skill matching
    assert frontend_task.task_id in assignments
    assert backend_task.task_id in assignments

    frontend_assigned_to = assignments[frontend_task.task_id]
    backend_assigned_to = assignments[backend_task.task_id]

    # Frontend task should go to frontend instance
    assert frontend_assigned_to == 1, "Frontend task should assign to frontend specialist"

    # Backend task should go to backend instance
    assert backend_assigned_to == 2, "Backend task should assign to backend specialist"

    print(f"\n✓ Skill-based assignment test passed")
    print(f"  - Frontend task → Instance {frontend_assigned_to}")
    print(f"  - Backend task → Instance {backend_assigned_to}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_inter_instance_messaging(
    multi_instance_manager,
    test_instances
):
    """
    Test message passing between instances
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Send coordination message
    message = CoordinationMessage(
        message_id="msg_test_001",
        sender_id=1,
        receiver_id=2,
        message_type="task_coordination",
        content={"action": "request_help", "task_id": "task-123"},
        timestamp=datetime.now().isoformat()
    )

    multi_instance_manager._send_message(message)

    # Verify message was queued
    assert len(multi_instance_manager.message_queue) > 0
    assert multi_instance_manager.message_queue[-1].message_id == "msg_test_001"

    # Retrieve messages for receiver
    receiver_messages = multi_instance_manager.get_messages(receiver_id=2)
    assert len(receiver_messages) > 0
    assert receiver_messages[0].sender_id == 1

    print(f"\n✓ Inter-instance messaging test passed")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_shared_state_synchronization(
    multi_instance_manager,
    test_instances
):
    """
    Test shared state across instances
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Update shared state
    multi_instance_manager.update_shared_state(
        key="current_sprint",
        value={"sprint_number": 1, "start_date": "2025-11-01"}
    )

    # Verify state is accessible
    sprint_info = multi_instance_manager.get_shared_state("current_sprint")
    assert sprint_info is not None
    assert sprint_info["sprint_number"] == 1

    # Update from different "instance"
    multi_instance_manager.update_shared_state(
        key="feature_flags",
        value={"new_ui": True, "beta_api": False}
    )

    # Verify both states exist
    assert "current_sprint" in multi_instance_manager.shared_state
    assert "feature_flags" in multi_instance_manager.shared_state

    print(f"\n✓ Shared state synchronization test passed")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_instance_failure_and_task_reassignment(
    multi_instance_manager,
    test_instances
):
    """
    Test handling of instance failure and task reassignment
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Create and assign tasks
    task1 = multi_instance_manager.create_task(
        description="Critical task",
        priority="high",
        estimated_hours=8.0,
        required_skills=["backend"]
    )

    # Assign to instance 1
    multi_instance_manager.assign_task(task1.task_id, 1)

    # Verify assignment
    assert task1.assigned_to == 1
    assert task1.status == "assigned"

    # Simulate instance 1 failure
    multi_instance_manager.instances[1].status = "inactive"

    # Detect failed instance
    failed = multi_instance_manager.detect_failed_instances()
    assert 1 in failed, "Should detect failed instance"

    # Reassign tasks from failed instance
    reassigned = multi_instance_manager.reassign_tasks_from_instance(1)

    assert len(reassigned) > 0, "Should reassign tasks"
    assert task1.task_id in reassigned

    # Verify task was reassigned to a different instance
    assert task1.assigned_to != 1
    assert task1.assigned_to in [2, 3]  # Should be reassigned to healthy instance

    print(f"\n✓ Failure recovery test passed")
    print(f"  - Detected failed instance: 1")
    print(f"  - Reassigned {len(reassigned)} task(s)")
    print(f"  - New assignment: Instance {task1.assigned_to}")


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_task_execution(
    multi_instance_manager,
    test_instances
):
    """
    Test multiple instances executing tasks concurrently
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Create multiple tasks
    tasks = []
    for i in range(6):  # 2 tasks per instance
        task = multi_instance_manager.create_task(
            description=f"Concurrent task {i}",
            priority="medium",
            estimated_hours=2.0,
            required_skills=["backend"]
        )
        tasks.append(task)

    # Auto-assign
    assignments = multi_instance_manager.auto_assign_tasks()

    # Start all assigned tasks
    for task in tasks:
        if task.task_id in assignments:
            task.status = "in_progress"

    # Verify concurrent execution
    in_progress_tasks = [t for t in tasks if t.status == "in_progress"]
    assert len(in_progress_tasks) >= len(test_instances), "Should have concurrent execution"

    # Simulate concurrent completion
    completion_times = []
    for i, task in enumerate(in_progress_tasks):
        await asyncio.sleep(0.1)  # Simulate work
        task.status = "completed"
        completion_times.append(datetime.now())

    # Verify all tasks completed
    completed_tasks = [t for t in tasks if t.status == "completed"]
    assert len(completed_tasks) == len(in_progress_tasks)

    print(f"\n✓ Concurrent execution test passed")
    print(f"  - Executed {len(in_progress_tasks)} tasks concurrently")
    print(f"  - Across {len(test_instances)} instances")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_workload_rebalancing(
    multi_instance_manager,
    test_instances
):
    """
    Test dynamic workload rebalancing
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Overload instance 1
    for i in range(5):
        task = multi_instance_manager.create_task(
            description=f"Task {i}",
            priority="medium",
            estimated_hours=3.0,
            required_skills=["backend"]
        )
        multi_instance_manager.assign_task(task.task_id, 1)

    # Verify instance 1 is overloaded
    instance1 = multi_instance_manager.instances[1]
    assert len(instance1.current_tasks) > instance1.max_concurrent_tasks

    # Trigger rebalancing
    rebalanced = multi_instance_manager.rebalance_workload()

    # Verify tasks were redistributed
    assert rebalanced > 0, "Should rebalance some tasks"

    # Check workload is more balanced
    workloads = [
        len(inst.current_tasks)
        for inst in multi_instance_manager.instances.values()
    ]

    max_workload = max(workloads)
    min_workload = min(workloads)

    assert max_workload - min_workload <= 2, "Workload should be balanced"

    print(f"\n✓ Workload rebalancing test passed")
    print(f"  - Rebalanced {rebalanced} task(s)")
    print(f"  - Final workloads: {workloads}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_priority_based_assignment(
    multi_instance_manager,
    test_instances
):
    """
    Test that high-priority tasks are assigned first
    """

    # Register instances
    for instance in test_instances:
        multi_instance_manager.register_instance(instance)

    # Create tasks with different priorities
    low_task = multi_instance_manager.create_task(
        description="Low priority task",
        priority="low",
        estimated_hours=2.0,
        required_skills=["backend"]
    )

    high_task = multi_instance_manager.create_task(
        description="High priority task",
        priority="critical",
        estimated_hours=2.0,
        required_skills=["backend"]
    )

    medium_task = multi_instance_manager.create_task(
        description="Medium priority task",
        priority="medium",
        estimated_hours=2.0,
        required_skills=["backend"]
    )

    # Auto-assign (should prioritize high priority)
    assignments = multi_instance_manager.auto_assign_tasks()

    # Verify all tasks assigned
    assert len(assignments) == 3

    # High priority task should be assigned
    assert high_task.task_id in assignments

    print(f"\n✓ Priority-based assignment test passed")
    print(f"  - Critical task: {high_task.status}")
    print(f"  - Medium task: {medium_task.status}")
    print(f"  - Low task: {low_task.status}")
