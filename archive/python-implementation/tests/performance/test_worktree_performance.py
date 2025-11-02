"""
Performance Benchmarks: Worktree Operations

Specialized benchmarks for worktree operations:
- Pattern-specific performance
- Branch operations
- Merge performance
- Cleanup efficiency
"""

import pytest
import subprocess
from pathlib import Path
import tempfile
import shutil
import time

from benchmark import PerformanceBenchmark, PerformanceMonitor
from worktree import WorktreeManager, WorktreeConfig, WorktreePattern


class TestWorktreePerformance:
    """Performance benchmarks for worktree operations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup benchmark environment"""
        self.benchmark = PerformanceBenchmark(suite_name="Worktree Performance")

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

        # Initial commit with some files
        (self.repo_path / "README.md").write_text("# Test Project")
        (self.repo_path / "src").mkdir()
        (self.repo_path / "src" / "main.py").write_text("# Main file")
        subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=self.repo_path,
            check=True,
        )

        self.manager = WorktreeManager(repository_path=self.repo_path)

        yield

        # Cleanup
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.benchmark.print_summary()
        self.benchmark.save_results("worktree_performance.json")

    def test_pattern_creation_performance(self):
        """Benchmark creation time for different patterns"""

        patterns = {
            "Competition": WorktreePattern.COMPETITION,
            "Parallel": WorktreePattern.PARALLEL,
            "A/B Test": WorktreePattern.AB_TEST,
            "Role-Based": WorktreePattern.ROLE_BASED,
            "Branch Tree": WorktreePattern.BRANCH_TREE,
        }

        for name, pattern in patterns.items():

            def create_pattern_worktree():
                config = WorktreeConfig(
                    feature=f"perf-{name.lower().replace(' ', '-')}",
                    pattern=pattern,
                    base_branch="master",
                    agent_name=f"{name}_agent",
                )
                worktree = self.manager.create_worktree(config)
                self.manager.remove_worktree(worktree.name)

            self.benchmark.benchmark(
                func=create_pattern_worktree,
                name=f"{name} Pattern Creation",
                iterations=1,
            )

    def test_competition_pattern_performance(self):
        """Benchmark competition pattern with multiple competitors"""

        def competition_2_agents():
            worktrees = self.manager.create_competition_worktrees(
                feature="sort-algo",
                agents=["agent1", "agent2"],
                max_competitors=2,
            )
            for wt in worktrees:
                self.manager.remove_worktree(wt.name)

        def competition_5_agents():
            worktrees = self.manager.create_competition_worktrees(
                feature="sort-algo",
                agents=["agent1", "agent2", "agent3", "agent4", "agent5"],
                max_competitors=5,
            )
            for wt in worktrees:
                self.manager.remove_worktree(wt.name)

        def competition_10_agents():
            worktrees = self.manager.create_competition_worktrees(
                feature="sort-algo",
                agents=[f"agent{i}" for i in range(10)],
                max_competitors=10,
            )
            for wt in worktrees:
                self.manager.remove_worktree(wt.name)

        # Benchmark different competition sizes
        self.benchmark.benchmark(
            func=competition_2_agents,
            name="Competition: 2 Agents",
            iterations=1,
        )

        self.benchmark.benchmark(
            func=competition_5_agents,
            name="Competition: 5 Agents",
            iterations=1,
        )

        self.benchmark.benchmark(
            func=competition_10_agents,
            name="Competition: 10 Agents",
            iterations=1,
        )

    def test_file_operations_in_worktree(self):
        """Benchmark file operations within worktrees"""

        config = WorktreeConfig(
            feature="file-ops",
            pattern=WorktreePattern.PARALLEL,
            base_branch="master",
            agent_name="file_agent",
        )
        worktree = self.manager.create_worktree(config)

        def write_small_files(count=10):
            """Write many small files"""
            for i in range(count):
                (worktree.path / f"file_{i}.txt").write_text(f"Content {i}")

        def write_large_file():
            """Write one large file"""
            (worktree.path / "large.txt").write_text("X" * 1024 * 1024)  # 1MB

        def modify_existing_files(count=10):
            """Modify existing files"""
            for i in range(count):
                path = worktree.path / f"file_{i}.txt"
                if path.exists():
                    content = path.read_text()
                    path.write_text(content + "\nModified")

        # Benchmark different file operations
        self.benchmark.benchmark(
            func=lambda: write_small_files(10),
            name="Write 10 Small Files",
            iterations=10,
            warmup=2,
        )

        self.benchmark.benchmark(
            func=lambda: write_small_files(100),
            name="Write 100 Small Files",
            iterations=5,
        )

        self.benchmark.benchmark(
            func=write_large_file, name="Write 1MB File", iterations=5
        )

        # Create files first
        write_small_files(10)

        self.benchmark.benchmark(
            func=lambda: modify_existing_files(10),
            name="Modify 10 Files",
            iterations=10,
            warmup=2,
        )

        # Cleanup
        self.manager.remove_worktree(worktree.name)

    def test_branch_operations_performance(self):
        """Benchmark branch-related operations"""

        config = WorktreeConfig(
            feature="branch-ops",
            pattern=WorktreePattern.PARALLEL,
            base_branch="master",
            agent_name="branch_agent",
        )
        worktree = self.manager.create_worktree(config)

        def create_commit():
            """Create a commit"""
            test_file = worktree.path / f"commit_{time.time()}.txt"
            test_file.write_text("Test content")
            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Test commit"],
                cwd=worktree.path,
                check=True,
            )

        def create_multiple_commits(count=5):
            """Create multiple commits"""
            for _ in range(count):
                create_commit()

        def check_branch_status():
            """Check branch status"""
            subprocess.run(
                ["git", "status"], cwd=worktree.path, capture_output=True
            )

        def get_branch_diff():
            """Get diff from base branch"""
            subprocess.run(
                ["git", "diff", "master"],
                cwd=worktree.path,
                capture_output=True,
            )

        # Benchmark branch operations
        self.benchmark.benchmark(
            func=create_commit, name="Single Commit", iterations=10, warmup=2
        )

        self.benchmark.benchmark(
            func=lambda: create_multiple_commits(5),
            name="5 Sequential Commits",
            iterations=3,
        )

        self.benchmark.benchmark(
            func=check_branch_status,
            name="Git Status Check",
            iterations=100,
            warmup=10,
        )

        self.benchmark.benchmark(
            func=get_branch_diff,
            name="Git Diff from Base",
            iterations=50,
            warmup=5,
        )

        # Cleanup
        self.manager.remove_worktree(worktree.name)

    def test_worktree_cleanup_performance(self):
        """Benchmark worktree cleanup operations"""

        # Create many worktrees
        worktree_names = []
        for i in range(20):
            config = WorktreeConfig(
                feature=f"cleanup-test-{i}",
                pattern=WorktreePattern.PARALLEL,
                base_branch="master",
                agent_name=f"cleanup_agent_{i}",
            )
            worktree = self.manager.create_worktree(config)
            worktree_names.append(worktree.name)

        def cleanup_single():
            """Cleanup one worktree"""
            if worktree_names:
                name = worktree_names.pop()
                self.manager.remove_worktree(name)

        def cleanup_batch(count=5):
            """Cleanup multiple worktrees"""
            for _ in range(min(count, len(worktree_names))):
                cleanup_single()

        # Benchmark cleanup operations
        self.benchmark.benchmark(
            func=cleanup_single, name="Single Worktree Cleanup", iterations=5
        )

        self.benchmark.benchmark(
            func=lambda: cleanup_batch(5),
            name="Batch Cleanup (5 worktrees)",
            iterations=2,
        )

        # Cleanup remaining
        for name in worktree_names:
            self.manager.remove_worktree(name)

    def test_merge_performance(self):
        """Benchmark merge operations"""

        # Create base worktree
        config = WorktreeConfig(
            feature="merge-source",
            pattern=WorktreePattern.PARALLEL,
            base_branch="master",
            agent_name="merge_agent",
        )
        worktree = self.manager.create_worktree(config)

        # Create some commits
        for i in range(10):
            test_file = worktree.path / f"file_{i}.txt"
            test_file.write_text(f"Content {i}")

        subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add files"],
            cwd=worktree.path,
            check=True,
        )

        def simple_merge():
            """Perform a simple merge"""
            # Create a new branch from master
            test_branch = "test-merge-target"
            subprocess.run(
                ["git", "checkout", "-b", test_branch],
                cwd=self.repo_path,
                check=True,
            )

            # Merge the worktree branch
            subprocess.run(
                ["git", "merge", "--no-ff", worktree.branch, "-m", "Merge test"],
                cwd=self.repo_path,
                check=True,
            )

            # Checkout back to master
            subprocess.run(
                ["git", "checkout", "master"], cwd=self.repo_path, check=True
            )

            # Delete test branch
            subprocess.run(
                ["git", "branch", "-D", test_branch],
                cwd=self.repo_path,
                check=True,
            )

        self.benchmark.benchmark(
            func=simple_merge, name="Simple Merge (10 files)", iterations=3
        )

        # Cleanup
        self.manager.remove_worktree(worktree.name)

    def test_concurrent_worktree_access(self):
        """Test performance with concurrent worktree access"""

        import concurrent.futures

        # Create multiple worktrees
        worktrees = []
        for i in range(5):
            config = WorktreeConfig(
                feature=f"concurrent-{i}",
                pattern=WorktreePattern.PARALLEL,
                base_branch="master",
                agent_name=f"concurrent_agent_{i}",
            )
            worktrees.append(self.manager.create_worktree(config))

        def work_on_worktree(worktree):
            """Perform work on a worktree"""
            # Write files
            for i in range(10):
                (worktree.path / f"work_{i}.txt").write_text(f"Work {i}")

            # Commit
            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Concurrent work"],
                cwd=worktree.path,
                check=True,
            )

        def concurrent_work():
            """Execute work concurrently on all worktrees"""
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(work_on_worktree, wt) for wt in worktrees
                ]
                concurrent.futures.wait(futures)

        self.benchmark.benchmark(
            func=concurrent_work,
            name="Concurrent Work (5 worktrees)",
            iterations=1,
        )

        # Cleanup
        for wt in worktrees:
            self.manager.remove_worktree(wt.name)

    def test_worktree_monitoring_overhead(self):
        """Test overhead of continuous monitoring"""

        monitor = PerformanceMonitor(interval=0.1)

        config = WorktreeConfig(
            feature="monitoring-test",
            pattern=WorktreePattern.PARALLEL,
            base_branch="master",
            agent_name="monitoring_agent",
        )

        with monitor.monitor() as metrics:
            # Create worktree
            worktree = self.manager.create_worktree(config)

            # Do work
            for i in range(50):
                (worktree.path / f"file_{i}.txt").write_text(f"Content {i}")

            subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Monitoring test"],
                cwd=worktree.path,
                check=True,
            )

            # Cleanup
            self.manager.remove_worktree(worktree.name)

        summary = monitor.get_summary()

        print(f"\nMonitoring Summary:")
        print(f"  Duration: {summary['duration']:.2f}s")
        print(f"  Samples: {summary['samples']}")
        print(f"  Avg Memory: {summary['memory']['avg_mb']:.2f} MB")
        print(f"  Max Memory: {summary['memory']['max_mb']:.2f} MB")
        print(f"  Avg CPU: {summary['cpu']['avg_percent']:.1f}%")
        print(f"  Max CPU: {summary['cpu']['max_percent']:.1f}%")

    def test_worktree_pattern_comparison(self):
        """Compare performance across different patterns"""

        patterns = {
            "Competition (2)": lambda: self.manager.create_competition_worktrees(
                "comp-test", ["a1", "a2"], 2
            ),
            "Parallel": lambda: self.manager.create_worktree(
                WorktreeConfig(
                    "parallel-test",
                    WorktreePattern.PARALLEL,
                    "master",
                    "parallel_agent",
                )
            ),
            "A/B Test": lambda: self.manager.create_worktree(
                WorktreeConfig(
                    "ab-test",
                    WorktreePattern.AB_TEST,
                    "master",
                    "ab_agent",
                )
            ),
            "Role-Based": lambda: self.manager.create_worktree(
                WorktreeConfig(
                    "role-test",
                    WorktreePattern.ROLE_BASED,
                    "master",
                    "role_agent",
                )
            ),
            "Branch Tree": lambda: self.manager.create_worktree(
                WorktreeConfig(
                    "tree-test",
                    WorktreePattern.BRANCH_TREE,
                    "master",
                    "tree_agent",
                )
            ),
        }

        # Clean up worktrees after each test
        def clean_wrapper(name, func):
            def wrapped():
                result = func()
                if isinstance(result, list):
                    for wt in result:
                        self.manager.remove_worktree(wt.name)
                else:
                    self.manager.remove_worktree(result.name)

            return wrapped

        patterns_cleaned = {
            name: clean_wrapper(name, func) for name, func in patterns.items()
        }

        self.benchmark.compare(patterns_cleaned, iterations=1)


@pytest.mark.performance
@pytest.mark.slow
class TestWorktreeScaling:
    """Test worktree scalability"""

    def test_many_worktrees_performance(self):
        """Test system with many worktrees"""

        benchmark = PerformanceBenchmark(suite_name="Worktree Scaling")

        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=repo_path, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo_path,
            check=True,
        )

        (repo_path / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], cwd=repo_path, check=True
        )

        manager = WorktreeManager(repository_path=repo_path)

        # Test with increasing number of worktrees
        for count in [10, 25, 50]:

            def create_many_worktrees(n):
                worktrees = []
                for i in range(n):
                    config = WorktreeConfig(
                        feature=f"scale-{i}",
                        pattern=WorktreePattern.PARALLEL,
                        base_branch="master",
                        agent_name=f"agent_{i}",
                    )
                    worktrees.append(manager.create_worktree(config))

                # Cleanup
                for wt in worktrees:
                    manager.remove_worktree(wt.name)

            benchmark.benchmark(
                func=lambda: create_many_worktrees(count),
                name=f"Create & Cleanup {count} Worktrees",
                iterations=1,
            )

        shutil.rmtree(temp_dir, ignore_errors=True)

        benchmark.print_summary()
        benchmark.save_results("worktree_scaling.json")
