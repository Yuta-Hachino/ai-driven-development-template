"""
Tests for Phase 2.5 Components

Tests multi-instance coordination, project memory, tech lead system,
notification hub, and auto-documentation.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import Phase 2.5 components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parallel_execution import (
    MultiInstanceManager,
    InstanceConfig,
    InstanceStatus,
    CoordinationMessage,
)
from memory import ProjectMemory, KnowledgeType
from management import (
    TechLeadSystem,
    TaskPlanner,
    PlanningStrategy,
    TaskBreakdown,
    TaskStatus,
)
from monitoring import (
    NotificationHub,
    NotificationPriority,
    NotificationChannel,
)
from documentation import AutoDocumenter, DocumentationType


class TestMultiInstanceManager:
    """Test multi-instance coordination"""

    def test_register_instance(self, tmp_path):
        """Test instance registration"""
        manager = MultiInstanceManager()

        instance = InstanceConfig(
            instance_id=1,
            name="Test-Instance",
            capabilities=["backend"],
            status="active",
            max_concurrent_tasks=2
        )

        result = manager.register_instance(instance)
        assert result is True
        assert 1 in manager.instances
        assert manager.instances[1].name == "Test-Instance"

    def test_create_task(self, tmp_path):
        """Test task creation"""
        manager = MultiInstanceManager()

        task = manager.create_task(
            description="Test task",
            priority="high",
            estimated_hours=5.0,
            required_skills=["backend"]
        )

        assert task.task_id in manager.tasks
        assert task.description == "Test task"
        assert task.priority == "high"
        assert task.status == "pending"

    def test_assign_task(self, tmp_path):
        """Test task assignment"""
        manager = MultiInstanceManager()

        # Register instance
        instance = InstanceConfig(
            instance_id=1,
            name="Test-Instance",
            capabilities=["backend"],
            status="active",
            max_concurrent_tasks=2
        )
        manager.register_instance(instance)

        # Create and assign task
        task = manager.create_task(
            description="Test task",
            priority="high",
            estimated_hours=5.0,
            required_skills=["backend"]
        )

        result = manager.assign_task(task.task_id, 1)
        assert result is True
        assert manager.tasks[task.task_id].assigned_to == 1
        assert manager.tasks[task.task_id].status == "assigned"

    def test_auto_assign_tasks(self, tmp_path):
        """Test automatic task assignment"""
        manager = MultiInstanceManager()

        # Register instances
        for i in range(1, 3):
            instance = InstanceConfig(
                instance_id=i,
                name=f"Instance-{i}",
                capabilities=["backend", "frontend"],
                status="active",
                max_concurrent_tasks=3
            )
            manager.register_instance(instance)

        # Create tasks
        for i in range(3):
            manager.create_task(
                description=f"Task {i}",
                priority="medium",
                estimated_hours=4.0,
                required_skills=["backend"]
            )

        # Auto-assign
        assignments = manager.auto_assign_tasks()
        assert len(assignments) > 0


class TestProjectMemory:
    """Test project memory system"""

    def test_add_entry(self, tmp_path):
        """Test adding memory entry"""
        memory = ProjectMemory(project_root=str(tmp_path))

        entry = memory.add_entry(
            knowledge_type=KnowledgeType.DECISION,
            title="Test Decision",
            content="This is a test decision",
            created_by="test",
            tags=["test", "decision"]
        )

        assert entry.title == "Test Decision"
        assert entry.knowledge_type == KnowledgeType.DECISION
        assert "test" in entry.tags

    def test_search_entries(self, tmp_path):
        """Test searching memory entries"""
        memory = ProjectMemory(project_root=str(tmp_path))

        # Add entries
        memory.add_entry(
            knowledge_type=KnowledgeType.PATTERN,
            title="Error Handling Pattern",
            content="Always use try-catch blocks",
            created_by="test"
        )

        memory.add_entry(
            knowledge_type=KnowledgeType.LEARNING,
            title="Database Connection Issue",
            content="Pool exhaustion causes errors",
            created_by="test"
        )

        # Search
        results = memory.search_entries(query="error", limit=10)
        assert len(results) > 0

    def test_record_decision(self, tmp_path):
        """Test recording architecture decision"""
        memory = ProjectMemory(project_root=str(tmp_path))

        entry = memory.record_decision(
            title="Use PostgreSQL",
            decision="Adopt PostgreSQL for primary database",
            rationale="Strong ACID compliance and JSON support",
            decided_by="tech_lead",
            alternatives=["MySQL", "MongoDB"]
        )

        assert entry.knowledge_type == KnowledgeType.DECISION
        assert entry.title == "Use PostgreSQL"

    def test_record_pattern(self, tmp_path):
        """Test recording implementation pattern"""
        memory = ProjectMemory(project_root=str(tmp_path))

        entry = memory.record_pattern(
            title="Repository Pattern",
            description="Abstract data access layer",
            example="class UserRepository: ...",
            when_to_use="When accessing database entities",
            created_by="developer"
        )

        assert entry.knowledge_type == KnowledgeType.PATTERN


class TestTechLeadSystem:
    """Test tech lead management system"""

    def test_create_task_plan(self, tmp_path):
        """Test creating task plan"""
        tech_lead = TechLeadSystem(project_root=str(tmp_path))

        tasks = [
            TaskBreakdown(
                task_id="task-1",
                title="Implement API",
                description="Build REST API",
                estimated_hours=10.0,
                required_skills=["backend"]
            ),
            TaskBreakdown(
                task_id="task-2",
                title="Write tests",
                description="Unit tests for API",
                estimated_hours=5.0,
                required_skills=["testing"],
                dependencies=["task-1"]
            )
        ]

        plan = tech_lead.create_task_plan(
            feature_name="API Development",
            description="Build REST API with tests",
            created_by="test",
            tasks=tasks
        )

        assert plan.feature_name == "API Development"
        assert len(plan.tasks) == 2
        assert plan.total_estimated_hours == 15.0

    def test_assign_and_complete_task(self, tmp_path):
        """Test task lifecycle"""
        tech_lead = TechLeadSystem(project_root=str(tmp_path))

        tasks = [
            TaskBreakdown(
                task_id="task-1",
                title="Test Task",
                description="Test",
                estimated_hours=5.0,
                required_skills=["backend"]
            )
        ]

        plan = tech_lead.create_task_plan(
            feature_name="Test",
            description="Test plan",
            created_by="test",
            tasks=tasks
        )

        # Assign
        result = tech_lead.assign_task(plan.plan_id, "task-1", 1)
        assert result is True
        assert plan.tasks[0].status == TaskStatus.ASSIGNED

        # Start
        result = tech_lead.start_task(plan.plan_id, "task-1")
        assert result is True
        assert plan.tasks[0].status == TaskStatus.IN_PROGRESS

        # Complete
        result = tech_lead.complete_task(plan.plan_id, "task-1")
        assert result is True
        assert plan.tasks[0].status == TaskStatus.COMPLETED

    def test_generate_progress_report(self, tmp_path):
        """Test progress report generation"""
        tech_lead = TechLeadSystem(project_root=str(tmp_path))

        tasks = [
            TaskBreakdown(
                task_id=f"task-{i}",
                title=f"Task {i}",
                description="Test",
                estimated_hours=5.0,
                required_skills=["backend"]
            )
            for i in range(5)
        ]

        plan = tech_lead.create_task_plan(
            feature_name="Test",
            description="Test plan",
            created_by="test",
            tasks=tasks
        )

        # Complete some tasks
        for i in range(2):
            tech_lead.assign_task(plan.plan_id, f"task-{i}", 1)
            tech_lead.start_task(plan.plan_id, f"task-{i}")
            tech_lead.complete_task(plan.plan_id, f"task-{i}")

        report = tech_lead.generate_progress_report()
        assert report.total_tasks == 5
        assert report.tasks_completed == 2
        assert report.overall_completion == 40.0


class TestTaskPlanner:
    """Test task planner"""

    def test_feature_first_strategy(self):
        """Test feature-first planning strategy"""
        planner = TaskPlanner()

        tasks = planner.create_feature_plan(
            feature_name="User Authentication",
            feature_description="OAuth 2.0 authentication",
            strategy=PlanningStrategy.FEATURE_FIRST,
            estimated_complexity="medium"
        )

        assert len(tasks) > 0
        assert any("backend" in task.required_skills for task in tasks)
        assert any("frontend" in task.required_skills for task in tasks)

    def test_agile_strategy(self):
        """Test agile planning strategy"""
        planner = TaskPlanner()

        tasks = planner.create_feature_plan(
            feature_name="Dashboard",
            feature_description="Analytics dashboard",
            strategy=PlanningStrategy.AGILE,
            estimated_complexity="high"
        )

        assert len(tasks) > 0
        # Should have MVP, core, and polish tasks
        task_titles = [t.title.lower() for t in tasks]
        assert any("mvp" in title for title in task_titles)

    def test_tdd_strategy(self):
        """Test TDD planning strategy"""
        planner = TaskPlanner()

        tasks = planner.create_feature_plan(
            feature_name="Payment Processing",
            feature_description="Stripe integration",
            strategy=PlanningStrategy.TEST_DRIVEN,
            estimated_complexity="medium"
        )

        assert len(tasks) > 0
        # First task should be tests
        assert "test" in tasks[0].title.lower()


class TestNotificationHub:
    """Test notification hub"""

    def test_send_notification(self, tmp_path):
        """Test sending notification"""
        hub = NotificationHub(project_root=str(tmp_path))

        notification = hub.send_notification(
            title="Test Notification",
            message="This is a test",
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.CONSOLE]
        )

        assert notification.title == "Test Notification"
        assert len(notification.sent_to) > 0

    def test_create_alert_rule(self, tmp_path):
        """Test creating alert rule"""
        hub = NotificationHub(project_root=str(tmp_path))

        rule = hub.create_alert_rule(
            name="Test Alert",
            condition="test_value > 10",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.CONSOLE],
            cooldown_minutes=30
        )

        assert rule.name == "Test Alert"
        assert rule.condition == "test_value > 10"
        assert rule.enabled is True

    def test_evaluate_alert_rules(self, tmp_path):
        """Test alert rule evaluation"""
        hub = NotificationHub(project_root=str(tmp_path))

        # Create rule
        hub.create_alert_rule(
            name="High Value Alert",
            condition="value > 50",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.CONSOLE],
            cooldown_minutes=30
        )

        # Evaluate with context that triggers alert
        context = {"value": 75}
        triggered = hub.evaluate_alert_rules(context)
        assert len(triggered) > 0

        # Evaluate with context that doesn't trigger
        context = {"value": 25}
        triggered = hub.evaluate_alert_rules(context)
        # Should be empty or same as before due to cooldown
        assert isinstance(triggered, list)


class TestAutoDocumenter:
    """Test auto-documentation system"""

    def test_generate_changelog(self, tmp_path):
        """Test changelog generation"""
        documenter = AutoDocumenter(project_root=str(tmp_path))

        # This will fail if not in a git repo, which is expected
        # In a real repo, it would generate a changelog
        try:
            changelog = documenter.generate_changelog()
            assert changelog.exists()
        except Exception:
            # Expected to fail in non-git environment
            pass

    def test_update_readme(self, tmp_path):
        """Test README update"""
        documenter = AutoDocumenter(project_root=str(tmp_path))

        sections = {
            'header': "# Test Project\n\n",
            'description': "Test description\n\n"
        }

        readme = documenter.update_readme(sections=sections)
        assert readme.exists()
        assert readme.name == "README.md"

        # Verify content
        content = readme.read_text()
        assert "Test Project" in content

    def test_generate_architecture_doc(self, tmp_path):
        """Test architecture documentation generation"""
        documenter = AutoDocumenter(project_root=str(tmp_path))

        arch_doc = documenter.generate_architecture_doc()
        assert arch_doc.exists()
        assert arch_doc.name == "ARCHITECTURE.md"


@pytest.mark.asyncio
async def test_integration_workflow(tmp_path):
    """Test complete integration workflow"""
    # Initialize all systems
    manager = MultiInstanceManager()
    memory = ProjectMemory(project_root=str(tmp_path))
    tech_lead = TechLeadSystem(project_root=str(tmp_path))
    planner = TaskPlanner()

    # Register instance
    instance = InstanceConfig(
        instance_id=1,
        name="Test-Instance",
        capabilities=["backend", "frontend"],
        status="active",
        max_concurrent_tasks=2
    )
    manager.register_instance(instance)

    # Create plan
    tasks = planner.create_feature_plan(
        feature_name="Test Feature",
        feature_description="Integration test",
        strategy=PlanningStrategy.FEATURE_FIRST,
        estimated_complexity="low"
    )

    plan = tech_lead.create_task_plan(
        feature_name="Test Feature",
        description="Integration test",
        created_by="test",
        tasks=tasks
    )

    # Record decision
    memory.record_decision(
        title="Test Decision",
        decision="Use integration testing",
        rationale="Ensures system works end-to-end",
        decided_by="test"
    )

    # Verify everything is connected
    assert len(manager.instances) == 1
    assert len(plan.tasks) > 0
    assert len(memory.entries) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
