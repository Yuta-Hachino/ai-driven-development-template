"""
Task Planner

Provides intelligent task planning and breakdown strategies.
Converts high-level feature requests into actionable task plans.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

from .tech_lead_system import TaskBreakdown, TaskPlan

logger = logging.getLogger(__name__)


class PlanningStrategy(Enum):
    """Task planning strategies"""
    WATERFALL = "waterfall"  # Sequential phases
    AGILE = "agile"  # Iterative sprints
    FEATURE_FIRST = "feature_first"  # Feature-driven
    TEST_DRIVEN = "test_driven"  # TDD approach
    RISK_DRIVEN = "risk_driven"  # Riskiest first


class TaskDependency(Enum):
    """Types of task dependencies"""
    FINISH_TO_START = "finish_to_start"  # Task B starts after A finishes
    START_TO_START = "start_to_start"  # Task B starts when A starts
    FINISH_TO_FINISH = "finish_to_finish"  # Task B finishes when A finishes
    START_TO_FINISH = "start_to_finish"  # Task B finishes when A starts


@dataclass
class TaskTemplate:
    """Template for common task types"""
    template_id: str
    name: str
    description: str
    estimated_hours: float
    required_skills: List[str]
    acceptance_criteria: List[str]
    dependencies_template: List[str] = field(default_factory=list)
    category: str = "general"


class TaskPlanner:
    """
    Intelligent task planner for breaking down features into tasks.

    Provides:
    - Multiple planning strategies
    - Task templates for common patterns
    - Dependency management
    - Estimation support
    - Skill matching
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Task Planner.

        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.templates = self._initialize_templates()

    def create_feature_plan(
        self,
        feature_name: str,
        feature_description: str,
        strategy: PlanningStrategy = PlanningStrategy.FEATURE_FIRST,
        estimated_complexity: str = "medium"
    ) -> List[TaskBreakdown]:
        """
        Create a task breakdown for a feature.

        Args:
            feature_name: Name of the feature
            feature_description: Detailed description
            strategy: Planning strategy to use
            estimated_complexity: low, medium, high, very_high

        Returns:
            List of TaskBreakdown objects
        """
        if strategy == PlanningStrategy.WATERFALL:
            return self._plan_waterfall(feature_name, feature_description, estimated_complexity)
        elif strategy == PlanningStrategy.AGILE:
            return self._plan_agile(feature_name, feature_description, estimated_complexity)
        elif strategy == PlanningStrategy.FEATURE_FIRST:
            return self._plan_feature_first(feature_name, feature_description, estimated_complexity)
        elif strategy == PlanningStrategy.TEST_DRIVEN:
            return self._plan_test_driven(feature_name, feature_description, estimated_complexity)
        elif strategy == PlanningStrategy.RISK_DRIVEN:
            return self._plan_risk_driven(feature_name, feature_description, estimated_complexity)
        else:
            return self._plan_feature_first(feature_name, feature_description, estimated_complexity)

    def _plan_waterfall(
        self,
        feature_name: str,
        description: str,
        complexity: str
    ) -> List[TaskBreakdown]:
        """Waterfall planning: Requirements -> Design -> Implementation -> Test -> Deploy"""
        tasks = []
        base_id = feature_name.lower().replace(" ", "-")

        # Phase 1: Requirements
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-req",
            title=f"Requirements Analysis for {feature_name}",
            description=f"Gather and document requirements for {description}",
            estimated_hours=self._estimate_hours("requirements", complexity),
            required_skills=["requirements", "documentation"],
            priority=10,
            acceptance_criteria=[
                "Requirements documented in docs/requirements/",
                "Acceptance criteria defined",
                "Edge cases identified"
            ]
        ))

        # Phase 2: Design
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-design",
            title=f"Design {feature_name}",
            description=f"Create technical design and architecture for {description}",
            estimated_hours=self._estimate_hours("design", complexity),
            dependencies=[f"{base_id}-req"],
            required_skills=["architecture", "design"],
            priority=9,
            acceptance_criteria=[
                "Architecture diagram created",
                "API contracts defined",
                "Database schema designed (if applicable)"
            ]
        ))

        # Phase 3: Implementation
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-impl",
            title=f"Implement {feature_name}",
            description=f"Implement the feature: {description}",
            estimated_hours=self._estimate_hours("implementation", complexity),
            dependencies=[f"{base_id}-design"],
            required_skills=["backend", "frontend", "database"],
            priority=8,
            acceptance_criteria=[
                "Code implemented according to design",
                "Code passes linting and type checks",
                "Self-documented with docstrings"
            ]
        ))

        # Phase 4: Testing
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-test",
            title=f"Test {feature_name}",
            description=f"Write comprehensive tests for {description}",
            estimated_hours=self._estimate_hours("testing", complexity),
            dependencies=[f"{base_id}-impl"],
            required_skills=["testing", "qa"],
            priority=7,
            acceptance_criteria=[
                "Unit tests with >90% coverage",
                "Integration tests pass",
                "Edge cases covered"
            ]
        ))

        # Phase 5: Documentation
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-docs",
            title=f"Document {feature_name}",
            description=f"Create user and developer documentation for {description}",
            estimated_hours=self._estimate_hours("documentation", complexity),
            dependencies=[f"{base_id}-test"],
            required_skills=["documentation"],
            priority=6,
            acceptance_criteria=[
                "User guide created",
                "API documentation updated",
                "Code examples provided"
            ]
        ))

        return tasks

    def _plan_agile(
        self,
        feature_name: str,
        description: str,
        complexity: str
    ) -> List[TaskBreakdown]:
        """Agile planning: Iterative sprints with MVP approach"""
        tasks = []
        base_id = feature_name.lower().replace(" ", "-")

        # Sprint 1: MVP
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-mvp",
            title=f"Build MVP for {feature_name}",
            description=f"Create minimal viable version of {description}",
            estimated_hours=self._estimate_hours("mvp", complexity),
            required_skills=["backend", "frontend"],
            priority=10,
            acceptance_criteria=[
                "Core functionality works",
                "Basic tests pass",
                "Deployable state"
            ]
        ))

        # Sprint 2: Core Features
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-core",
            title=f"Add Core Features to {feature_name}",
            description=f"Implement core features for {description}",
            estimated_hours=self._estimate_hours("core_features", complexity),
            dependencies=[f"{base_id}-mvp"],
            required_skills=["backend", "frontend"],
            priority=9,
            acceptance_criteria=[
                "All core features implemented",
                "Test coverage >80%",
                "Performance acceptable"
            ]
        ))

        # Sprint 3: Polish & Refinement
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-polish",
            title=f"Polish {feature_name}",
            description=f"Refine UX, performance, and error handling for {description}",
            estimated_hours=self._estimate_hours("polish", complexity),
            dependencies=[f"{base_id}-core"],
            required_skills=["frontend", "ux"],
            priority=7,
            acceptance_criteria=[
                "UX improved based on feedback",
                "Error handling comprehensive",
                "Performance optimized"
            ]
        ))

        return tasks

    def _plan_feature_first(
        self,
        feature_name: str,
        description: str,
        complexity: str
    ) -> List[TaskBreakdown]:
        """Feature-first planning: Break down by feature components"""
        tasks = []
        base_id = feature_name.lower().replace(" ", "-")

        # Backend implementation
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-backend",
            title=f"Backend for {feature_name}",
            description=f"Implement backend logic for {description}",
            estimated_hours=self._estimate_hours("backend", complexity),
            required_skills=["backend", "database", "api"],
            priority=10,
            acceptance_criteria=[
                "API endpoints implemented",
                "Business logic complete",
                "Database models created",
                "Unit tests pass"
            ]
        ))

        # Frontend implementation
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-frontend",
            title=f"Frontend for {feature_name}",
            description=f"Implement UI components for {description}",
            estimated_hours=self._estimate_hours("frontend", complexity),
            dependencies=[f"{base_id}-backend"],
            required_skills=["frontend", "ui", "ux"],
            priority=9,
            acceptance_criteria=[
                "UI components implemented",
                "Connected to backend APIs",
                "Responsive design",
                "Component tests pass"
            ]
        ))

        # Integration
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-integration",
            title=f"Integration for {feature_name}",
            description=f"Integrate and test end-to-end {description}",
            estimated_hours=self._estimate_hours("integration", complexity),
            dependencies=[f"{base_id}-backend", f"{base_id}-frontend"],
            required_skills=["testing", "integration"],
            priority=8,
            acceptance_criteria=[
                "End-to-end tests pass",
                "Error handling verified",
                "Performance acceptable"
            ]
        ))

        return tasks

    def _plan_test_driven(
        self,
        feature_name: str,
        description: str,
        complexity: str
    ) -> List[TaskBreakdown]:
        """TDD planning: Tests first, then implementation"""
        tasks = []
        base_id = feature_name.lower().replace(" ", "-")

        # Write tests first
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-tests",
            title=f"Write Tests for {feature_name}",
            description=f"Define test cases for {description}",
            estimated_hours=self._estimate_hours("tests_first", complexity),
            required_skills=["testing", "tdd"],
            priority=10,
            acceptance_criteria=[
                "Test cases defined",
                "Unit tests written (failing)",
                "Integration tests written (failing)",
                "Test coverage plan created"
            ]
        ))

        # Implementation to make tests pass
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-impl-tdd",
            title=f"Implement {feature_name} (TDD)",
            description=f"Implement feature to make tests pass: {description}",
            estimated_hours=self._estimate_hours("implementation_tdd", complexity),
            dependencies=[f"{base_id}-tests"],
            required_skills=["backend", "frontend", "tdd"],
            priority=9,
            acceptance_criteria=[
                "All tests pass",
                "Code coverage >90%",
                "No unnecessary code (YAGNI principle)"
            ]
        ))

        # Refactoring
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-refactor",
            title=f"Refactor {feature_name}",
            description=f"Refactor while keeping tests green: {description}",
            estimated_hours=self._estimate_hours("refactoring", complexity),
            dependencies=[f"{base_id}-impl-tdd"],
            required_skills=["refactoring", "clean_code"],
            priority=7,
            acceptance_criteria=[
                "Code follows best practices",
                "All tests still pass",
                "Complexity reduced",
                "Documentation updated"
            ]
        ))

        return tasks

    def _plan_risk_driven(
        self,
        feature_name: str,
        description: str,
        complexity: str
    ) -> List[TaskBreakdown]:
        """Risk-driven planning: Tackle risky parts first"""
        tasks = []
        base_id = feature_name.lower().replace(" ", "-")

        # Prototype/Spike for risky parts
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-spike",
            title=f"Spike: High-Risk Parts of {feature_name}",
            description=f"Prototype and validate risky aspects of {description}",
            estimated_hours=self._estimate_hours("spike", complexity),
            required_skills=["prototyping", "research"],
            priority=10,
            acceptance_criteria=[
                "Technical feasibility validated",
                "Risk mitigation strategies identified",
                "Proof of concept created"
            ]
        ))

        # Implement validated approach
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-impl-validated",
            title=f"Implement Validated Approach for {feature_name}",
            description=f"Implement using validated approach: {description}",
            estimated_hours=self._estimate_hours("implementation", complexity),
            dependencies=[f"{base_id}-spike"],
            required_skills=["backend", "frontend"],
            priority=9,
            acceptance_criteria=[
                "Implementation matches validated approach",
                "Tests pass",
                "Performance metrics met"
            ]
        ))

        # Low-risk polish
        tasks.append(TaskBreakdown(
            task_id=f"{base_id}-polish-low-risk",
            title=f"Polish Low-Risk Parts of {feature_name}",
            description=f"Complete low-risk portions: {description}",
            estimated_hours=self._estimate_hours("polish", complexity),
            dependencies=[f"{base_id}-impl-validated"],
            required_skills=["frontend", "ux"],
            priority=6,
            acceptance_criteria=[
                "UI polished",
                "Documentation complete",
                "Edge cases handled"
            ]
        ))

        return tasks

    def _estimate_hours(self, task_type: str, complexity: str) -> float:
        """
        Estimate hours for a task based on type and complexity.

        Args:
            task_type: Type of task
            complexity: low, medium, high, very_high

        Returns:
            Estimated hours
        """
        # Base hours by task type
        base_hours = {
            "requirements": 4,
            "design": 6,
            "implementation": 16,
            "testing": 8,
            "documentation": 4,
            "mvp": 12,
            "core_features": 20,
            "polish": 8,
            "backend": 12,
            "frontend": 10,
            "integration": 6,
            "tests_first": 8,
            "implementation_tdd": 12,
            "refactoring": 6,
            "spike": 8,
        }

        # Complexity multipliers
        complexity_multiplier = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "very_high": 2.5
        }

        base = base_hours.get(task_type, 8)
        multiplier = complexity_multiplier.get(complexity, 1.0)

        return round(base * multiplier, 1)

    def _initialize_templates(self) -> Dict[str, TaskTemplate]:
        """Initialize common task templates."""
        templates = {}

        # Backend API template
        templates["backend_api"] = TaskTemplate(
            template_id="backend_api",
            name="Backend API Implementation",
            description="Implement RESTful API endpoints",
            estimated_hours=12.0,
            required_skills=["backend", "api", "database"],
            acceptance_criteria=[
                "API endpoints implemented",
                "Request/response validation",
                "Error handling complete",
                "API documentation updated",
                "Unit tests pass"
            ],
            category="backend"
        )

        # Frontend component template
        templates["frontend_component"] = TaskTemplate(
            template_id="frontend_component",
            name="Frontend Component",
            description="Implement UI component",
            estimated_hours=8.0,
            required_skills=["frontend", "ui", "css"],
            acceptance_criteria=[
                "Component implemented",
                "Responsive design",
                "Accessible (WCAG 2.1)",
                "Component tests pass"
            ],
            category="frontend"
        )

        # Database migration template
        templates["database_migration"] = TaskTemplate(
            template_id="database_migration",
            name="Database Migration",
            description="Create and apply database migration",
            estimated_hours=4.0,
            required_skills=["database", "sql"],
            acceptance_criteria=[
                "Migration script created",
                "Up and down migrations tested",
                "Data integrity verified",
                "Rollback plan documented"
            ],
            category="database"
        )

        # Testing template
        templates["comprehensive_testing"] = TaskTemplate(
            template_id="comprehensive_testing",
            name="Comprehensive Testing",
            description="Write unit, integration, and e2e tests",
            estimated_hours=10.0,
            required_skills=["testing", "qa"],
            acceptance_criteria=[
                "Unit tests >90% coverage",
                "Integration tests pass",
                "E2E tests for critical paths",
                "Edge cases covered"
            ],
            category="testing"
        )

        # Documentation template
        templates["feature_documentation"] = TaskTemplate(
            template_id="feature_documentation",
            name="Feature Documentation",
            description="Create user and developer documentation",
            estimated_hours=6.0,
            required_skills=["documentation", "technical_writing"],
            acceptance_criteria=[
                "User guide created",
                "API documentation updated",
                "Code examples provided",
                "Architecture diagrams included"
            ],
            category="documentation"
        )

        # Security audit template
        templates["security_audit"] = TaskTemplate(
            template_id="security_audit",
            name="Security Audit",
            description="Perform security review and fixes",
            estimated_hours=8.0,
            required_skills=["security", "audit"],
            acceptance_criteria=[
                "Security scan completed",
                "Vulnerabilities addressed",
                "Authentication/authorization verified",
                "Input validation checked"
            ],
            category="security"
        )

        return templates

    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """Get a task template by ID."""
        return self.templates.get(template_id)

    def list_templates(self, category: Optional[str] = None) -> List[TaskTemplate]:
        """
        List available templates.

        Args:
            category: Optional category filter

        Returns:
            List of templates
        """
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
