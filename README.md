# Autonomous Development Repository System

> Enterprise-grade autonomous development system powered by Google ADK, Git Worktrees, and AI agents

[![CI/CD](https://github.com/your-org/autonomous-dev-system/workflows/CI/badge.svg)](https://github.com/your-org/autonomous-dev-system/actions)
[![Security Scan](https://github.com/your-org/autonomous-dev-system/workflows/Security/badge.svg)](https://github.com/your-org/autonomous-dev-system/security)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The Autonomous Development Repository System is a cutting-edge platform that combines:

- **Google ADK (Agent Development Kit)** - Multi-agent framework for autonomous development
- **Git Worktree Patterns** - 5 parallel development patterns for optimal collaboration
- **Enterprise Security** - Zero-trust architecture with comprehensive security controls

### Key Features

- ✅ **Fully Autonomous Development** - AI agents handle development, testing, and deployment
- ✅ **P2P Coordination** - Decentralized architecture using GitHub as communication layer (Phase 6)
- ✅ **Free Default Setup** - $0/month with GitHub Pages dashboard and GitHub Actions
- ✅ **Multi-Instance Coordination** - Multiple Claude Code instances working in parallel
- ✅ **Multi-Pattern Worktrees** - Competition, Parallel, A/B Testing, Role-based, Branch Tree
- ✅ **Enterprise Security** - gVisor sandboxing, encryption, MFA, RBAC, audit logging
- ✅ **Intelligent Evaluation** - Automated code quality, performance, and security assessment
- ✅ **Self-Healing System** - Automatic failure detection and recovery
- ✅ **Project Memory** - Shared knowledge base and context preservation
- ✅ **Tech Lead Management** - Intelligent task planning and assignment
- ✅ **Auto-Documentation** - Keep documentation in sync with code
- ✅ **Flexible Deployment** - GitHub Pages, Cloud Run, VPS, Lambda, or Kubernetes
- ✅ **Comprehensive Testing** - 90%+ test coverage with security scanning

## Quick Start

### Prerequisites

- Python 3.11+
- Git 2.35+
- Docker (optional)
- GCP Account (for cloud deployment)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-org/autonomous-dev-system.git
cd autonomous-dev-system
```

2. **Run initialization script**

```bash
./scripts/init-project.sh
```

3. **Activate virtual environment**

```bash
source venv/bin/activate
```

4. **Configure environment**

```bash
# Edit configuration files in config/
# - config/agents.yaml
# - config/security.yaml
# - config/worktree.yaml
```

5. **Run tests**

```bash
pytest
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Autonomous Dev System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Multi-Instance Coordination Layer             │  │
│  │  • Task Distribution  • Load Balancing  • Messaging   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Development   │  │  Management   │  │   Security    │   │
│  │    Agents     │  │    Agents     │  │    Agents     │   │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤   │
│  │ • Frontend    │  │ • Approval    │  │ • Encryption  │   │
│  │ • Backend     │  │ • Security    │  │ • Auth/MFA    │   │
│  │ • Algorithm   │  │ • Integration │  │ • Audit Log   │   │
│  │ • DevOps      │  │ • Monitoring  │  │ • Compliance  │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Autonomous Intelligence Layer                  │  │
│  │ • Tech Lead System  • Self-Healing  • Auto-Docs       │  │
│  │ • Project Memory    • Notifications • Bottleneck Det. │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                    Worktree Management                        │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │Competition  │  Parallel   │  A/B Test   │ Role-Based  │ │
│  │ Resolution  │ Development │             │Specialization│ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      Infrastructure                           │
│          GCP • Kubernetes • Docker • GitHub Actions          │
└─────────────────────────────────────────────────────────────┘
```

### Agent Types

#### Development Agents

- **Frontend Agent** - UI/UX, React, TypeScript, Accessibility
- **Backend Agent** - API, Database, Performance, Scalability
- **Algorithm Agent** - Optimization, Data Structures, Complexity
- **DevOps Agent** - CI/CD, Infrastructure, Monitoring

#### Management Agents

- **Approval Agent** - Code review and PR approval decisions
- **Security Agent** - Vulnerability scanning and security audits
- **Integration Agent** - Conflict resolution and continuous integration
- **Monitoring Agent** - System health and performance monitoring

## Worktree Development Patterns

### 1. Competition Resolution

Multiple agents solve the same problem independently, best solution wins.

### 2. Parallel Development

Different features developed simultaneously by specialized agents.

### 3. A/B Testing

Two implementation variants tested and compared.

### 4. Role-Based Specialization

Agents work on specialized areas and coordinate.

### 5. Branch Tree Exploration

Exploratory development with intelligent pruning.

## Security Features

### Zero-Trust Architecture

- ✅ No implicit trust, verify all access
- ✅ Continuous authentication and authorization
- ✅ Least privilege principle
- ✅ Assume breach mentality

### Multi-Layer Defense

- **Network Layer**: Firewall, DDoS protection, VPN
- **Application Layer**: WAF, API Gateway, Rate limiting
- **Data Layer**: AES-256-GCM encryption, Audit logs

### Container Security (gVisor)

All agents run in gVisor sandboxed containers for enhanced security.

## Phase 2.5 Features - Multi-Instance Collaboration

### Multi-Instance Coordination

Coordinate multiple Claude Code instances working in parallel:

```python
from src.parallel_execution import MultiInstanceManager, InstanceConfig

manager = MultiInstanceManager()

# Register instances
instance = InstanceConfig(
    instance_id=1,
    name="Frontend-Specialist",
    capabilities=["frontend", "ui", "react"],
    status="active",
    max_concurrent_tasks=2
)
manager.register_instance(instance)

# Auto-assign tasks with skill matching and load balancing
assignments = manager.auto_assign_tasks()
```

### Project Memory System

Preserve and share knowledge across instances:

```python
from src.memory import ProjectMemory, KnowledgeType

memory = ProjectMemory(project_root=".")

# Record architectural decision
memory.record_decision(
    title="Use PostgreSQL",
    decision="Adopt PostgreSQL for primary database",
    rationale="Strong ACID compliance and JSON support",
    decided_by="tech_lead",
    alternatives=["MySQL", "MongoDB"]
)

# Search knowledge base
results = memory.search_entries(query="database", limit=10)
```

### Tech Lead Management

Intelligent task planning and coordination:

```python
from src.management import TechLeadSystem, TaskPlanner, PlanningStrategy

planner = TaskPlanner()
tech_lead = TechLeadSystem(project_root=".")

# Create task plan with multiple strategies
tasks = planner.create_feature_plan(
    feature_name="User Authentication",
    feature_description="OAuth 2.0 authentication",
    strategy=PlanningStrategy.FEATURE_FIRST,
    estimated_complexity="medium"
)

# Track progress
report = tech_lead.generate_progress_report()
print(f"Completion: {report.overall_completion}%")
```

### Notification Hub

Multi-channel alerting and monitoring:

```python
from src.monitoring import NotificationHub, NotificationPriority

hub = NotificationHub(project_root=".")

# Send notification
hub.send_notification(
    title="Build Failed",
    message="CI/CD pipeline failed with 3 errors",
    priority=NotificationPriority.HIGH,
    channels=["github_issue", "console"]
)

# Create alert rules
hub.create_alert_rule(
    name="High blocked tasks",
    condition="tasks_blocked > 3",
    priority=NotificationPriority.HIGH,
    channels=["github_issue"]
)
```

### Auto-Documentation

Keep documentation synchronized with code:

```python
from src.documentation import AutoDocumenter

documenter = AutoDocumenter(project_root=".")

# Generate API docs from code
documenter.generate_api_documentation()

# Generate changelog from git commits
documenter.generate_changelog()

# Update README
documenter.update_readme()
```

## Configuration Files

### `config/agents.yaml`

Defines agent configurations, models, specializations, and resource limits.

### `config/security.yaml`

Security settings including encryption, authentication, RBAC, and audit policies.

### `config/worktree.yaml`

Worktree patterns, evaluation criteria, and resource management settings.

### `config/parallel_execution.yaml`

Multi-instance coordination, task distribution, and resource management.

### `config/alerting_rules.yaml`

Alert rules, notification channels, and escalation policies.

## Usage Examples

### Creating an Agent

```python
from src.agents import FrontendAgent, AgentConfig

config = AgentConfig(
    name="ui_specialist",
    model="claude-3-opus",
    specialization=["React", "TypeScript"]
)

agent = FrontendAgent(config)
result = await agent.execute("Create login component")
```

### Managing Worktrees

```python
from src.worktree import WorktreeManager

manager = WorktreeManager("/path/to/repo")

# Create competition worktrees
worktrees = manager.create_competition_worktrees(
    feature="api-optimization",
    agents=["backend_agent", "algorithm_agent"]
)
```

### Security Operations

```python
from src.security import DataEncryption, SecretManager, AuditLogger

# Encrypt sensitive data
encryption = DataEncryption()
ciphertext = encryption.encrypt_data("sensitive info")

# Manage secrets
secrets = SecretManager()
secrets.create_secret("api_key", "secret_value_123")

# Audit logging
audit = AuditLogger()
audit.log_event(
    event_type=EventType.DATA_ACCESS,
    actor="user123",
    resource="database",
    action="read",
    result=EventResult.SUCCESS
)
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
pytest tests/test_agents.py
pytest tests/test_worktree.py
pytest tests/test_security.py
```

### With Coverage

```bash
pytest --cov=src --cov-report=html
```

## Deployment

The system supports two deployment architectures:

### **Option 1: P2P Architecture (Phase 6) - Recommended ✨**

Fully decentralized coordination using GitHub as the communication layer. No central server required!

**Features:**
- ✅ **$0/month** - Free GitHub Pages dashboard (default)
- ✅ **Fully Decentralized** - GitHub handles all coordination
- ✅ **Scalable** - 1-5 parallel instances via GitHub Actions
- ✅ **Simple** - No Kubernetes or server management
- ✅ **Optional Upgrades** - Deploy dynamic dashboard to Cloud Run, VPS, or Lambda

**Quick Start:**
```bash
# 1. Set up GitHub Actions secrets
# GITHUB_TOKEN with repo access

# 2. Create issue with 'autonomous-dev' label
# 3. Instances auto-coordinate via P2P

# 4. Deploy dashboard (choose one):
python scripts/deploy_dashboard.py
# Options:
# 1. GitHub Pages (FREE, default)
# 2. Google Cloud Run ($0-10/month)
# 3. VPS/Sakura ($4-25/month)
# 4. AWS Lambda ($0-5/month)
```

**See detailed documentation:** [docs/P2P_ARCHITECTURE.md](docs/P2P_ARCHITECTURE.md)

---

### **Option 2: Centralized Kubernetes (Phase 5)**

Traditional centralized architecture with Kubernetes orchestration.

**When to use:**
- Enterprise deployments requiring centralized control
- Need for >5 parallel instances
- Existing Kubernetes infrastructure

#### Local Docker

```bash
docker build -f docker/Dockerfile -t autonomous-dev:latest .
docker run autonomous-dev:latest
```

#### Kubernetes (GKE)

```bash
kubectl apply -f k8s/production/
```

#### Cloud Run

```bash
gcloud run deploy autonomous-dev \
  --image gcr.io/project/autonomous-dev:latest \
  --platform managed
```

## Project Structure

```
.
├── config/                      # Configuration files
│   ├── agents.yaml
│   ├── security.yaml
│   ├── worktree.yaml
│   ├── parallel_execution.yaml  # Phase 2.5
│   └── alerting_rules.yaml      # Phase 2.5
├── src/                        # Source code
│   ├── agents/                 # Agent implementations
│   ├── worktree/               # Worktree management
│   ├── security/               # Security modules
│   ├── autonomous/             # Self-healing (Phase 2)
│   ├── parallel_execution/     # Multi-instance (Phase 2.5)
│   ├── memory/                 # Project memory (Phase 2.5)
│   ├── management/             # Tech lead system (Phase 2.5)
│   ├── monitoring/             # Notifications (Phase 2.5)
│   ├── documentation/          # Auto-docs (Phase 2.5)
│   └── p2p/                    # P2P coordination (Phase 6)
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── scripts/                   # Utility scripts
│   └── deploy_dashboard.py     # Dashboard deployment selector (Phase 6)
├── docker/                    # Docker configuration
├── k8s/                       # Kubernetes manifests (Phase 5)
│   └── production/             # Production configs
├── deployments/               # Optional deployments (Phase 6)
│   ├── cloudrun/              # Google Cloud Run
│   ├── vps/                   # VPS deployment
│   └── lambda/                # AWS Lambda
├── dashboard/                 # GitHub Pages dashboard (Phase 6)
│   └── index.html             # Default free dashboard
├── frontend/                  # Real-time UI (Phase 7)
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── types/             # TypeScript types
│   │   └── pages/             # Page components
│   ├── package.json
│   └── vite.config.ts
├── backend/                   # FastAPI backend (Phase 7)
│   ├── api/
│   │   └── gateway.py         # WebSocket & REST API
│   └── requirements.txt
├── docs/                      # Documentation
│   ├── P2P_ARCHITECTURE.md    # P2P architecture guide (Phase 6)
│   ├── PHASE7_REALTIME_UI.md  # Real-time UI guide (Phase 7)
│   ├── COMPLIANCE_GOVERNANCE.md
│   └── COST_OPTIMIZATION.md
└── .github/workflows/         # CI/CD pipelines
    ├── ci.yml
    ├── security.yml
    └── p2p-autonomous-dev.yml  # P2P coordination workflow (Phase 6)
```

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/autonomous-dev-system/issues)
- **Documentation**: See specification files in the repository

---

**Built with ❤️ for autonomous software development**