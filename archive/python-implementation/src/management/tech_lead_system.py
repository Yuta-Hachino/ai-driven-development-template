"""
Tech Lead System

Acts as a technical lead coordinating multiple Claude Code instances.
Provides task planning, assignment, progress tracking, and bottleneck detection.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task lifecycle status"""
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressMetric(Enum):
    """Progress tracking metrics"""
    COMPLETION_RATE = "completion_rate"
    VELOCITY = "velocity"
    CYCLE_TIME = "cycle_time"
    BLOCKED_TIME = "blocked_time"
    QUALITY_SCORE = "quality_score"


@dataclass
class TaskBreakdown:
    """Individual task in a breakdown"""
    task_id: str
    title: str
    description: str
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    priority: int = 5
    status: TaskStatus = TaskStatus.PLANNED
    assigned_to: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    blocked_reason: Optional[str] = None
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class TaskPlan:
    """High-level feature plan broken down into tasks"""
    plan_id: str
    feature_name: str
    description: str
    created_at: str
    created_by: str
    tasks: List[TaskBreakdown] = field(default_factory=list)
    total_estimated_hours: float = 0.0
    status: str = "active"
    completion_percentage: float = 0.0


@dataclass
class ProgressReport:
    """Progress report for tracking development"""
    report_id: str
    generated_at: str
    overall_completion: float
    tasks_completed: int
    tasks_in_progress: int
    tasks_blocked: int
    total_tasks: int
    velocity: float  # tasks per day
    estimated_completion_date: Optional[str]
    instance_performance: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BottleneckDetection:
    """Detected bottleneck in development process"""
    bottleneck_id: str
    detected_at: str
    bottleneck_type: str  # task_blocked, instance_overloaded, dependency_chain, skill_gap
    severity: str  # low, medium, high, critical
    affected_tasks: List[str]
    affected_instances: List[int]
    description: str
    suggested_actions: List[str]
    resolved: bool = False


class TechLeadSystem:
    """
    Tech Lead System for coordinating multiple Claude Code instances.

    Acts as a technical lead that:
    - Creates detailed task plans from feature requests
    - Assigns tasks to appropriate instances
    - Tracks progress and identifies bottlenecks
    - Provides recommendations and adjustments
    - Generates status reports
    """

    def __init__(self, project_root: str, config: Optional[Dict] = None):
        """
        Initialize Tech Lead System.

        Args:
            project_root: Root directory of the project
            config: Optional configuration dictionary
        """
        self.project_root = Path(project_root)
        self.config = config or {}

        # Storage paths
        self.management_dir = self.project_root / "docs" / "management"
        self.management_dir.mkdir(parents=True, exist_ok=True)

        self.plans_file = self.management_dir / "task_plans.json"
        self.progress_file = self.management_dir / "progress_reports.json"
        self.bottlenecks_file = self.management_dir / "bottlenecks.json"

        # State
        self.plans: Dict[str, TaskPlan] = {}
        self.bottlenecks: Dict[str, BottleneckDetection] = {}

        # Load existing data
        self._load_plans()
        self._load_bottlenecks()

        logger.info(f"Tech Lead System initialized with {len(self.plans)} active plans")

    def create_task_plan(
        self,
        feature_name: str,
        description: str,
        created_by: str,
        tasks: List[TaskBreakdown]
    ) -> TaskPlan:
        """
        Create a new task plan for a feature.

        Args:
            feature_name: Name of the feature
            description: Detailed description
            created_by: Creator (human or instance ID)
            tasks: List of task breakdowns

        Returns:
            Created TaskPlan
        """
        plan_id = f"plan_{int(datetime.now().timestamp())}"
        total_hours = sum(task.estimated_hours for task in tasks)

        plan = TaskPlan(
            plan_id=plan_id,
            feature_name=feature_name,
            description=description,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            tasks=tasks,
            total_estimated_hours=total_hours,
            status="active",
            completion_percentage=0.0
        )

        self.plans[plan_id] = plan
        self._save_plans()

        logger.info(f"Created task plan {plan_id} for {feature_name} with {len(tasks)} tasks")
        return plan

    def assign_task(
        self,
        plan_id: str,
        task_id: str,
        instance_id: int
    ) -> bool:
        """
        Assign a task to a Claude Code instance.

        Args:
            plan_id: Plan ID
            task_id: Task ID within the plan
            instance_id: Instance to assign to

        Returns:
            True if successful
        """
        if plan_id not in self.plans:
            logger.error(f"Plan {plan_id} not found")
            return False

        plan = self.plans[plan_id]
        task = next((t for t in plan.tasks if t.task_id == task_id), None)

        if not task:
            logger.error(f"Task {task_id} not found in plan {plan_id}")
            return False

        # Check dependencies
        if not self._check_dependencies(plan, task):
            logger.warning(f"Task {task_id} has unmet dependencies")
            return False

        task.assigned_to = instance_id
        task.status = TaskStatus.ASSIGNED

        self._save_plans()
        logger.info(f"Assigned task {task_id} to instance {instance_id}")
        return True

    def start_task(self, plan_id: str, task_id: str) -> bool:
        """Mark a task as in progress."""
        if plan_id not in self.plans:
            return False

        plan = self.plans[plan_id]
        task = next((t for t in plan.tasks if t.task_id == task_id), None)

        if not task or task.status != TaskStatus.ASSIGNED:
            return False

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()

        self._save_plans()
        logger.info(f"Started task {task_id}")
        return True

    def complete_task(self, plan_id: str, task_id: str) -> bool:
        """Mark a task as completed."""
        if plan_id not in self.plans:
            return False

        plan = self.plans[plan_id]
        task = next((t for t in plan.tasks if t.task_id == task_id), None)

        if not task or task.status != TaskStatus.IN_PROGRESS:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()

        # Update plan completion percentage
        completed_tasks = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
        plan.completion_percentage = (completed_tasks / len(plan.tasks)) * 100

        self._save_plans()
        logger.info(f"Completed task {task_id}")
        return True

    def block_task(self, plan_id: str, task_id: str, reason: str) -> bool:
        """Mark a task as blocked with a reason."""
        if plan_id not in self.plans:
            return False

        plan = self.plans[plan_id]
        task = next((t for t in plan.tasks if t.task_id == task_id), None)

        if not task:
            return False

        task.status = TaskStatus.BLOCKED
        task.blocked_reason = reason

        # Create bottleneck detection
        self._detect_bottleneck_from_blocked_task(plan, task)

        self._save_plans()
        logger.warning(f"Task {task_id} blocked: {reason}")
        return True

    def generate_progress_report(self) -> ProgressReport:
        """
        Generate comprehensive progress report.

        Returns:
            ProgressReport with current status
        """
        all_tasks = []
        for plan in self.plans.values():
            if plan.status == "active":
                all_tasks.extend(plan.tasks)

        total_tasks = len(all_tasks)
        tasks_completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
        tasks_in_progress = sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS)
        tasks_blocked = sum(1 for t in all_tasks if t.status == TaskStatus.BLOCKED)

        overall_completion = (tasks_completed / total_tasks * 100) if total_tasks > 0 else 0.0

        # Calculate velocity (tasks completed per day)
        velocity = self._calculate_velocity(all_tasks)

        # Estimate completion date
        remaining_tasks = total_tasks - tasks_completed
        estimated_days = remaining_tasks / velocity if velocity > 0 else None
        estimated_completion = None
        if estimated_days:
            estimated_completion = (datetime.now() + timedelta(days=estimated_days)).isoformat()

        # Instance performance
        instance_performance = self._calculate_instance_performance(all_tasks)

        # Identify bottlenecks
        bottleneck_descriptions = [
            f"{b.bottleneck_type}: {b.description}"
            for b in self.bottlenecks.values()
            if not b.resolved
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(all_tasks, instance_performance)

        report = ProgressReport(
            report_id=f"report_{int(datetime.now().timestamp())}",
            generated_at=datetime.now().isoformat(),
            overall_completion=overall_completion,
            tasks_completed=tasks_completed,
            tasks_in_progress=tasks_in_progress,
            tasks_blocked=tasks_blocked,
            total_tasks=total_tasks,
            velocity=velocity,
            estimated_completion_date=estimated_completion,
            instance_performance=instance_performance,
            bottlenecks=bottleneck_descriptions,
            recommendations=recommendations
        )

        self._save_progress_report(report)
        logger.info(f"Generated progress report: {overall_completion:.1f}% complete")
        return report

    def detect_bottlenecks(self) -> List[BottleneckDetection]:
        """
        Detect current bottlenecks in the development process.

        Returns:
            List of detected bottlenecks
        """
        bottlenecks = []

        # Check for blocked tasks
        for plan in self.plans.values():
            if plan.status != "active":
                continue

            blocked_tasks = [t for t in plan.tasks if t.status == TaskStatus.BLOCKED]
            if blocked_tasks:
                bottleneck = self._create_blocked_task_bottleneck(plan, blocked_tasks)
                bottlenecks.append(bottleneck)

        # Check for overloaded instances
        instance_workload = defaultdict(int)
        for plan in self.plans.values():
            for task in plan.tasks:
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                    if task.assigned_to:
                        instance_workload[task.assigned_to] += 1

        for instance_id, workload in instance_workload.items():
            if workload > self.config.get("max_concurrent_tasks_per_instance", 3):
                bottleneck = self._create_overload_bottleneck(instance_id, workload)
                bottlenecks.append(bottleneck)

        # Check for long dependency chains
        for plan in self.plans.values():
            long_chains = self._find_long_dependency_chains(plan)
            if long_chains:
                bottleneck = self._create_dependency_chain_bottleneck(plan, long_chains)
                bottlenecks.append(bottleneck)

        # Save detected bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks[bottleneck.bottleneck_id] = bottleneck
        self._save_bottlenecks()

        return [b for b in self.bottlenecks.values() if not b.resolved]

    def _check_dependencies(self, plan: TaskPlan, task: TaskBreakdown) -> bool:
        """Check if all task dependencies are met."""
        for dep_id in task.dependencies:
            dep_task = next((t for t in plan.tasks if t.task_id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def _calculate_velocity(self, tasks: List[TaskBreakdown]) -> float:
        """Calculate development velocity (tasks per day)."""
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED and t.completed_at]

        if len(completed_tasks) < 2:
            return 0.0

        # Calculate average time between completions
        completion_times = [datetime.fromisoformat(t.completed_at) for t in completed_tasks]
        completion_times.sort()

        time_span = (completion_times[-1] - completion_times[0]).days
        if time_span == 0:
            time_span = 1

        velocity = len(completed_tasks) / time_span
        return round(velocity, 2)

    def _calculate_instance_performance(
        self,
        tasks: List[TaskBreakdown]
    ) -> Dict[int, Dict[str, Any]]:
        """Calculate performance metrics for each instance."""
        instance_stats = defaultdict(lambda: {
            "tasks_completed": 0,
            "tasks_in_progress": 0,
            "tasks_blocked": 0,
            "avg_completion_time_hours": 0.0,
            "quality_score": 0.0
        })

        for task in tasks:
            if not task.assigned_to:
                continue

            instance_id = task.assigned_to

            if task.status == TaskStatus.COMPLETED:
                instance_stats[instance_id]["tasks_completed"] += 1

                # Calculate completion time
                if task.started_at and task.completed_at:
                    start = datetime.fromisoformat(task.started_at)
                    end = datetime.fromisoformat(task.completed_at)
                    hours = (end - start).total_seconds() / 3600
                    current_avg = instance_stats[instance_id]["avg_completion_time_hours"]
                    count = instance_stats[instance_id]["tasks_completed"]
                    instance_stats[instance_id]["avg_completion_time_hours"] = (
                        (current_avg * (count - 1) + hours) / count
                    )

            elif task.status == TaskStatus.IN_PROGRESS:
                instance_stats[instance_id]["tasks_in_progress"] += 1

            elif task.status == TaskStatus.BLOCKED:
                instance_stats[instance_id]["tasks_blocked"] += 1

        return dict(instance_stats)

    def _generate_recommendations(
        self,
        tasks: List[TaskBreakdown],
        instance_performance: Dict[int, Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on current state."""
        recommendations = []

        # Check for unassigned tasks
        unassigned = [t for t in tasks if t.status == TaskStatus.PLANNED]
        if unassigned:
            recommendations.append(
                f"Assign {len(unassigned)} pending tasks to available instances"
            )

        # Check for blocked tasks
        blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        if blocked:
            recommendations.append(
                f"Resolve {len(blocked)} blocked tasks to maintain velocity"
            )

        # Check for overloaded instances
        for instance_id, stats in instance_performance.items():
            in_progress = stats["tasks_in_progress"]
            if in_progress > 3:
                recommendations.append(
                    f"Instance {instance_id} has {in_progress} concurrent tasks - consider redistribution"
                )

        # Check for underutilized instances
        for instance_id, stats in instance_performance.items():
            if stats["tasks_in_progress"] == 0 and stats["tasks_completed"] > 0:
                recommendations.append(
                    f"Instance {instance_id} is idle - assign new tasks"
                )

        return recommendations

    def _detect_bottleneck_from_blocked_task(
        self,
        plan: TaskPlan,
        task: TaskBreakdown
    ) -> None:
        """Create bottleneck detection for a blocked task."""
        bottleneck_id = f"bottleneck_{int(datetime.now().timestamp())}"

        bottleneck = BottleneckDetection(
            bottleneck_id=bottleneck_id,
            detected_at=datetime.now().isoformat(),
            bottleneck_type="task_blocked",
            severity="medium",
            affected_tasks=[task.task_id],
            affected_instances=[task.assigned_to] if task.assigned_to else [],
            description=f"Task '{task.title}' is blocked: {task.blocked_reason}",
            suggested_actions=[
                "Review blocking reason",
                "Provide necessary resources or information",
                "Consider reassigning if persistent"
            ]
        )

        self.bottlenecks[bottleneck_id] = bottleneck
        self._save_bottlenecks()

    def _create_blocked_task_bottleneck(
        self,
        plan: TaskPlan,
        blocked_tasks: List[TaskBreakdown]
    ) -> BottleneckDetection:
        """Create bottleneck for multiple blocked tasks."""
        bottleneck_id = f"bottleneck_{int(datetime.now().timestamp())}"

        return BottleneckDetection(
            bottleneck_id=bottleneck_id,
            detected_at=datetime.now().isoformat(),
            bottleneck_type="task_blocked",
            severity="high" if len(blocked_tasks) > 2 else "medium",
            affected_tasks=[t.task_id for t in blocked_tasks],
            affected_instances=[t.assigned_to for t in blocked_tasks if t.assigned_to],
            description=f"{len(blocked_tasks)} tasks blocked in plan {plan.plan_id}",
            suggested_actions=[
                "Review and resolve blocking issues",
                "Reassign tasks if possible",
                "Update dependencies"
            ]
        )

    def _create_overload_bottleneck(
        self,
        instance_id: int,
        workload: int
    ) -> BottleneckDetection:
        """Create bottleneck for overloaded instance."""
        bottleneck_id = f"bottleneck_{int(datetime.now().timestamp())}"

        return BottleneckDetection(
            bottleneck_id=bottleneck_id,
            detected_at=datetime.now().isoformat(),
            bottleneck_type="instance_overloaded",
            severity="medium",
            affected_tasks=[],
            affected_instances=[instance_id],
            description=f"Instance {instance_id} has {workload} concurrent tasks",
            suggested_actions=[
                "Redistribute some tasks to other instances",
                "Prioritize critical tasks",
                "Consider increasing instance capacity"
            ]
        )

    def _find_long_dependency_chains(self, plan: TaskPlan) -> List[List[str]]:
        """Find long chains of task dependencies."""
        chains = []
        max_chain_length = self.config.get("max_dependency_chain", 5)

        def build_chain(task_id: str, current_chain: List[str]) -> List[str]:
            task = next((t for t in plan.tasks if t.task_id == task_id), None)
            if not task or not task.dependencies:
                return current_chain

            longest = current_chain
            for dep_id in task.dependencies:
                chain = build_chain(dep_id, current_chain + [dep_id])
                if len(chain) > len(longest):
                    longest = chain

            return longest

        for task in plan.tasks:
            chain = build_chain(task.task_id, [task.task_id])
            if len(chain) > max_chain_length:
                chains.append(chain)

        return chains

    def _create_dependency_chain_bottleneck(
        self,
        plan: TaskPlan,
        chains: List[List[str]]
    ) -> BottleneckDetection:
        """Create bottleneck for long dependency chains."""
        bottleneck_id = f"bottleneck_{int(datetime.now().timestamp())}"

        longest_chain = max(chains, key=len)

        return BottleneckDetection(
            bottleneck_id=bottleneck_id,
            detected_at=datetime.now().isoformat(),
            bottleneck_type="dependency_chain",
            severity="medium",
            affected_tasks=longest_chain,
            affected_instances=[],
            description=f"Long dependency chain detected ({len(longest_chain)} tasks)",
            suggested_actions=[
                "Review if tasks can be parallelized",
                "Consider breaking down complex tasks",
                "Identify critical path"
            ]
        )

    def _load_plans(self) -> None:
        """Load task plans from file."""
        if not self.plans_file.exists():
            return

        try:
            with open(self.plans_file, 'r') as f:
                data = json.load(f)
                for plan_id, plan_data in data.items():
                    # Convert tasks
                    tasks = [
                        TaskBreakdown(
                            **{**task_data, 'status': TaskStatus(task_data['status'])}
                        )
                        for task_data in plan_data['tasks']
                    ]
                    plan_data['tasks'] = tasks
                    self.plans[plan_id] = TaskPlan(**plan_data)
        except Exception as e:
            logger.error(f"Error loading plans: {e}")

    def _save_plans(self) -> None:
        """Save task plans to file."""
        try:
            data = {}
            for plan_id, plan in self.plans.items():
                plan_dict = asdict(plan)
                # Convert enums to strings
                plan_dict['tasks'] = [
                    {**task, 'status': task['status'].value}
                    for task in plan_dict['tasks']
                ]
                data[plan_id] = plan_dict

            with open(self.plans_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving plans: {e}")

    def _load_bottlenecks(self) -> None:
        """Load bottlenecks from file."""
        if not self.bottlenecks_file.exists():
            return

        try:
            with open(self.bottlenecks_file, 'r') as f:
                data = json.load(f)
                self.bottlenecks = {
                    k: BottleneckDetection(**v)
                    for k, v in data.items()
                }
        except Exception as e:
            logger.error(f"Error loading bottlenecks: {e}")

    def _save_bottlenecks(self) -> None:
        """Save bottlenecks to file."""
        try:
            data = {k: asdict(v) for k, v in self.bottlenecks.items()}
            with open(self.bottlenecks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving bottlenecks: {e}")

    def _save_progress_report(self, report: ProgressReport) -> None:
        """Save progress report to file."""
        try:
            reports = []
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    reports = json.load(f)

            reports.append(asdict(report))

            # Keep only last 100 reports
            reports = reports[-100:]

            with open(self.progress_file, 'w') as f:
                json.dump(reports, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress report: {e}")
