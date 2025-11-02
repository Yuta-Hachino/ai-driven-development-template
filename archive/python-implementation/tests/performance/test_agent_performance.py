"""
Performance Benchmarks: Agent Operations

Benchmarks for autonomous agent operations including:
- Task execution speed
- Worktree operations
- Git operations
- Multi-instance coordination
"""

import pytest
import subprocess
from pathlib import Path
import tempfile
import shutil

from benchmark import PerformanceBenchmark, MemoryProfiler, CPUProfiler
from worktree import WorktreeManager, WorktreeConfig, WorktreePattern
from multi_instance import MultiInstanceManager, InstanceConfig
from tech_lead import TechLeadSystem, TaskPlanner, PlanningStrategy


class TestAgentPerformance:
    """Performance benchmarks for agent operations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup benchmark environment"""
        self.benchmark = PerformanceBenchmark(suite_name="Agent Performance")

        # Create temp repository
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()

        subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=self.repo_path,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=self.repo_path,
            check=True,
        )

        # Initial commit
        (self.repo_path / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=self.repo_path,
            check=True,
        )

        yield

        # Cleanup
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.benchmark.print_summary()
        self.benchmark.save_results("agent_performance.json")

    def test_worktree_creation_performance(self):
        """Benchmark worktree creation speed"""

        manager = WorktreeManager(repository_path=self.repo_path)

        def create_worktree():
            config = WorktreeConfig(
                feature="perf-test",
                pattern=WorktreePattern.PARALLEL,
                base_branch="master",
                agent_name="perf_agent",
            )
            worktree = manager.create_worktree(config)
            manager.remove_worktree(worktree.name)

        # Benchmark single worktree creation
        self.benchmark.benchmark(
            func=create_worktree,
            name="Single Worktree Creation",
            iterations=1,
            warmup=1,
        )

        # Benchmark batch worktree creation
        def create_multiple_worktrees(count=5):
            worktrees = []
            for i in range(count):
                config = WorktreeConfig(
                    feature=f"feature-{i}",
                    pattern=WorktreePattern.PARALLEL,
                    base_branch="master",
                    agent_name=f"agent_{i}",
                )
                worktrees.append(manager.create_worktree(config))

            for wt in worktrees:
                manager.remove_worktree(wt.name)

        self.benchmark.benchmark(
            func=lambda: create_multiple_worktrees(5),
            name="Batch Worktree Creation (5)",
            iterations=1,
        )

        self.benchmark.benchmark(
            func=lambda: create_multiple_worktrees(10),
            name="Batch Worktree Creation (10)",
            iterations=1,
        )

    def test_git_operations_performance(self):
        """Benchmark Git operations"""

        manager = WorktreeManager(repository_path=self.repo_path)
        config = WorktreeConfig(
            feature="git-perf",
            pattern=WorktreePattern.PARALLEL,
            base_branch="master",
            agent_name="git_agent",
        )
        worktree = manager.create_worktree(config)

        def small_commit():
            """Commit a small file"""
            test_file = worktree.path / "small.txt"
            test_file.write_text("Small content")
            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Small commit"],
                cwd=worktree.path,
                check=True,
            )

        def large_commit():
            """Commit a large file"""
            test_file = worktree.path / "large.txt"
            test_file.write_text("X" * 1024 * 100)  # 100KB
            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Large commit"],
                cwd=worktree.path,
                check=True,
            )

        def many_files_commit():
            """Commit many files"""
            for i in range(50):
                (worktree.path / f"file_{i}.txt").write_text(f"Content {i}")
            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Many files"],
                cwd=worktree.path,
                check=True,
            )

        # Benchmark different commit scenarios
        self.benchmark.benchmark(
            func=small_commit, name="Small File Commit", iterations=1
        )

        self.benchmark.benchmark(
            func=large_commit, name="Large File Commit (100KB)", iterations=1
        )

        self.benchmark.benchmark(
            func=many_files_commit, name="Many Files Commit (50)", iterations=1
        )

        # Cleanup
        manager.remove_worktree(worktree.name)

    def test_task_planning_performance(self):
        """Benchmark task planning operations"""

        planner = TaskPlanner()

        def simple_feature_plan():
            """Plan a simple feature"""
            return planner.create_feature_plan(
                feature_name="Simple Feature",
                feature_description="A simple CRUD feature",
                strategy=PlanningStrategy.FEATURE_FIRST,
                estimated_complexity="low",
            )

        def complex_feature_plan():
            """Plan a complex feature"""
            return planner.create_feature_plan(
                feature_name="Complex Feature",
                feature_description="Complex multi-service authentication system",
                strategy=PlanningStrategy.DEPENDENCY_FIRST,
                estimated_complexity="high",
            )

        # Benchmark planning strategies
        self.benchmark.benchmark(
            func=simple_feature_plan,
            name="Simple Feature Planning",
            iterations=10,
            warmup=2,
        )

        self.benchmark.benchmark(
            func=complex_feature_plan,
            name="Complex Feature Planning",
            iterations=10,
            warmup=2,
        )

        # Compare planning strategies
        strategies = {
            "Feature-First": lambda: planner.create_feature_plan(
                "Test",
                "Test feature",
                PlanningStrategy.FEATURE_FIRST,
                "medium",
            ),
            "Dependency-First": lambda: planner.create_feature_plan(
                "Test",
                "Test feature",
                PlanningStrategy.DEPENDENCY_FIRST,
                "medium",
            ),
            "Test-Driven": lambda: planner.create_feature_plan(
                "Test",
                "Test feature",
                PlanningStrategy.TEST_DRIVEN,
                "medium",
            ),
            "Iterative": lambda: planner.create_feature_plan(
                "Test",
                "Test feature",
                PlanningStrategy.ITERATIVE,
                "medium",
            ),
        }

        self.benchmark.compare(strategies, iterations=5, warmup=1)

    def test_multi_instance_coordination_performance(self):
        """Benchmark multi-instance coordination"""

        manager = MultiInstanceManager()

        # Create test instances
        instances = []
        for i in range(1, 11):  # 10 instances
            instance = InstanceConfig(
                instance_id=i,
                name=f"Instance-{i}",
                capabilities=["backend", "frontend"],
                status="active",
                max_concurrent_tasks=3,
            )
            instances.append(instance)

        def register_instances():
            """Register all instances"""
            for instance in instances:
                manager.register_instance(instance)

        def create_and_assign_tasks(task_count=10):
            """Create and assign tasks"""
            for i in range(task_count):
                manager.create_task(
                    description=f"Task {i}",
                    priority="medium",
                    estimated_hours=5.0,
                    required_skills=["backend"],
                )

            manager.auto_assign_tasks()

        # Benchmark instance registration
        self.benchmark.benchmark(
            func=register_instances,
            name="Register 10 Instances",
            iterations=1,
        )

        # Benchmark task assignment
        self.benchmark.benchmark(
            func=lambda: create_and_assign_tasks(10),
            name="Create & Assign 10 Tasks",
            iterations=1,
        )

        self.benchmark.benchmark(
            func=lambda: create_and_assign_tasks(50),
            name="Create & Assign 50 Tasks",
            iterations=1,
        )

        self.benchmark.benchmark(
            func=lambda: create_and_assign_tasks(100),
            name="Create & Assign 100 Tasks",
            iterations=1,
        )

    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load"""

        manager = MultiInstanceManager()

        with MemoryProfiler.track_memory() as memory_stats:
            # Register many instances
            for i in range(50):
                instance = InstanceConfig(
                    instance_id=i,
                    name=f"Instance-{i}",
                    capabilities=["backend"],
                    status="active",
                    max_concurrent_tasks=2,
                )
                manager.register_instance(instance)

            # Create many tasks
            for i in range(200):
                manager.create_task(
                    description=f"Task {i}",
                    priority="medium",
                    estimated_hours=5.0,
                    required_skills=["backend"],
                )

            # Assign tasks
            manager.auto_assign_tasks()

        print(f"\nMemory Usage Test:")
        print(f"  Start: {memory_stats['start_mb']:.2f} MB")
        print(f"  End: {memory_stats['end_mb']:.2f} MB")
        print(f"  Delta: {memory_stats['delta_mb']:.2f} MB")

        # Assert reasonable memory usage
        assert (
            memory_stats["delta_mb"] < 500
        ), "Memory usage should stay under 500MB"

    def test_cpu_usage_efficiency(self):
        """Test CPU efficiency"""

        planner = TaskPlanner()

        with CPUProfiler.track_cpu() as cpu_stats:
            # CPU-intensive task planning
            for _ in range(100):
                planner.create_feature_plan(
                    feature_name="Test Feature",
                    feature_description="Complex feature",
                    strategy=PlanningStrategy.DEPENDENCY_FIRST,
                    estimated_complexity="high",
                )

        print(f"\nCPU Usage Test:")
        print(f"  Duration: {cpu_stats['duration']:.2f}s")
        print(f"  CPU: {cpu_stats['cpu_percent']:.1f}%")

    def test_concurrent_operations_performance(self):
        """Test performance under concurrent operations"""

        import concurrent.futures

        manager = WorktreeManager(repository_path=self.repo_path)

        def create_and_work_on_worktree(index):
            """Create worktree and do some work"""
            config = WorktreeConfig(
                feature=f"concurrent-{index}",
                pattern=WorktreePattern.PARALLEL,
                base_branch="master",
                agent_name=f"agent_{index}",
            )

            worktree = manager.create_worktree(config)

            # Do some work
            test_file = worktree.path / "work.txt"
            test_file.write_text(f"Work from agent {index}")

            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Work {index}"],
                cwd=worktree.path,
                check=True,
            )

            return worktree.name

        def concurrent_worktrees(worker_count):
            """Create multiple worktrees concurrently"""
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=worker_count
            ) as executor:
                futures = [
                    executor.submit(create_and_work_on_worktree, i)
                    for i in range(worker_count)
                ]

                worktree_names = [f.result() for f in futures]

            # Cleanup
            for name in worktree_names:
                manager.remove_worktree(name)

        # Benchmark concurrent operations
        self.benchmark.benchmark(
            func=lambda: concurrent_worktrees(5),
            name="5 Concurrent Worktrees",
            iterations=1,
        )

        self.benchmark.benchmark(
            func=lambda: concurrent_worktrees(10),
            name="10 Concurrent Worktrees",
            iterations=1,
        )

    def test_scalability_limits(self):
        """Test system scalability limits"""

        manager = MultiInstanceManager()

        # Test with increasing load
        for instance_count in [10, 50, 100]:
            for i in range(instance_count):
                instance = InstanceConfig(
                    instance_id=i,
                    name=f"Scale-Instance-{i}",
                    capabilities=["backend"],
                    status="active",
                    max_concurrent_tasks=2,
                )
                manager.register_instance(instance)

            task_count = instance_count * 5

            self.benchmark.benchmark(
                func=lambda: [
                    manager.create_task(
                        description=f"Task {i}",
                        priority="medium",
                        estimated_hours=5.0,
                        required_skills=["backend"],
                    )
                    for i in range(task_count)
                ],
                name=f"Scale Test: {instance_count} instances, {task_count} tasks",
                iterations=1,
            )

            # Reset for next iteration
            manager = MultiInstanceManager()


@pytest.mark.performance
@pytest.mark.slow
class TestEndToEndPerformance:
    """End-to-end performance scenarios"""

    def test_complete_workflow_performance(self):
        """Test complete development workflow performance"""

        benchmark = PerformanceBenchmark(suite_name="E2E Workflow Performance")

        # Simulate complete workflow
        def complete_workflow():
            # 1. Task planning
            planner = TaskPlanner()
            tasks = planner.create_feature_plan(
                feature_name="User Authentication",
                feature_description="OAuth 2.0 authentication",
                strategy=PlanningStrategy.FEATURE_FIRST,
                estimated_complexity="medium",
            )

            # 2. Instance management
            manager = MultiInstanceManager()
            for i in range(3):
                instance = InstanceConfig(
                    instance_id=i,
                    name=f"Agent-{i}",
                    capabilities=["backend", "frontend"],
                    status="active",
                    max_concurrent_tasks=2,
                )
                manager.register_instance(instance)

            # 3. Task assignment
            for task in tasks:
                manager.create_task(
                    description=task.title,
                    priority=task.priority,
                    estimated_hours=task.estimated_hours,
                    required_skills=task.required_skills,
                )

            manager.auto_assign_tasks()

        benchmark.benchmark(
            func=complete_workflow,
            name="Complete E2E Workflow",
            iterations=5,
            warmup=1,
        )

        benchmark.print_summary()
        benchmark.save_results("e2e_workflow_performance.json")
