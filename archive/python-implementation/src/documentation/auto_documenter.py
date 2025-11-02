"""
Auto Documenter

Automatically generates and updates project documentation based on code changes,
project memory, and development progress.
"""

import ast
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger(__name__)


class DocumentationType(Enum):
    """Types of documentation to generate"""
    API_REFERENCE = "api_reference"
    USER_GUIDE = "user_guide"
    ARCHITECTURE = "architecture"
    CHANGELOG = "changelog"
    README = "readme"
    CONTRIBUTING = "contributing"
    DEPLOYMENT = "deployment"


@dataclass
class CodeAnalysis:
    """Analysis of code structure"""
    file_path: str
    module_name: str
    classes: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    complexity_score: int = 0


@dataclass
class DocumentationUpdate:
    """Documentation update record"""
    update_id: str
    doc_type: DocumentationType
    file_path: str
    changes: List[str]
    updated_at: str
    triggered_by: str  # commit hash, issue, manual
    automated: bool = True


class AutoDocumenter:
    """
    Automatic documentation generator and updater.

    Features:
    - Code-to-documentation synchronization
    - API reference generation from docstrings
    - Changelog generation from git commits
    - Architecture diagram updates
    - User guide generation
    """

    def __init__(self, project_root: str, config: Optional[Dict] = None):
        """
        Initialize Auto Documenter.

        Args:
            project_root: Root directory of the project
            config: Optional configuration
        """
        self.project_root = Path(project_root)
        self.config = config or {}

        # Documentation paths
        self.docs_dir = self.project_root / "docs"
        self.docs_dir.mkdir(exist_ok=True)

        self.api_docs_dir = self.docs_dir / "api"
        self.api_docs_dir.mkdir(exist_ok=True)

        self.user_docs_dir = self.docs_dir / "guides"
        self.user_docs_dir.mkdir(exist_ok=True)

        # Source paths
        self.src_dir = self.project_root / "src"

        # Update history
        self.updates_file = self.docs_dir / "documentation_updates.json"
        self.updates: List[DocumentationUpdate] = []
        self._load_updates()

        logger.info("Auto Documenter initialized")

    def generate_api_documentation(
        self,
        module_path: Optional[str] = None
    ) -> List[Path]:
        """
        Generate API documentation from code.

        Args:
            module_path: Specific module to document (default: all)

        Returns:
            List of generated documentation files
        """
        generated_files = []

        if module_path:
            modules = [Path(module_path)]
        else:
            # Find all Python files in src/
            modules = list(self.src_dir.rglob("*.py"))

        for module_file in modules:
            if module_file.name.startswith("__") and module_file.name != "__init__.py":
                continue

            try:
                analysis = self._analyze_python_file(module_file)
                doc_file = self._generate_api_doc_file(analysis)
                if doc_file:
                    generated_files.append(doc_file)
            except Exception as e:
                logger.error(f"Error documenting {module_file}: {e}")

        # Generate API index
        index_file = self._generate_api_index(generated_files)
        if index_file:
            generated_files.append(index_file)

        logger.info(f"Generated API documentation for {len(generated_files)} modules")
        return generated_files

    def generate_changelog(
        self,
        since_commit: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Path:
        """
        Generate changelog from git commits.

        Args:
            since_commit: Generate changelog since this commit
            output_file: Output file path (default: docs/CHANGELOG.md)

        Returns:
            Path to generated changelog
        """
        import subprocess

        if output_file is None:
            output_file = self.docs_dir / "CHANGELOG.md"
        else:
            output_file = Path(output_file)

        # Get git log
        cmd = ["git", "log", "--pretty=format:%H|||%an|||%ad|||%s|||%b", "--date=short"]
        if since_commit:
            cmd.append(f"{since_commit}..HEAD")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Git log failed: {result.stderr}")
                return output_file

            # Parse commits
            commits = self._parse_git_log(result.stdout)

            # Group by type
            grouped = self._group_commits_by_type(commits)

            # Generate markdown
            changelog_md = self._generate_changelog_markdown(grouped)

            # Write to file
            with open(output_file, 'w') as f:
                f.write(changelog_md)

            logger.info(f"Generated changelog with {len(commits)} commits")
            return output_file

        except Exception as e:
            logger.error(f"Error generating changelog: {e}")
            return output_file

    def update_readme(
        self,
        sections: Optional[Dict[str, str]] = None
    ) -> Path:
        """
        Update README.md with current project information.

        Args:
            sections: Dictionary of sections to update

        Returns:
            Path to updated README
        """
        readme_path = self.project_root / "README.md"

        # Read existing README if it exists
        existing_content = ""
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                existing_content = f.read()

        # Generate or update sections
        if sections is None:
            sections = self._generate_default_readme_sections()

        # Merge with existing content
        updated_content = self._merge_readme_sections(existing_content, sections)

        # Write updated README
        with open(readme_path, 'w') as f:
            f.write(updated_content)

        logger.info("Updated README.md")
        return readme_path

    def generate_architecture_doc(self) -> Path:
        """
        Generate architecture documentation.

        Returns:
            Path to architecture doc
        """
        arch_file = self.docs_dir / "ARCHITECTURE.md"

        # Analyze project structure
        structure = self._analyze_project_structure()

        # Generate markdown
        content = self._generate_architecture_markdown(structure)

        # Write to file
        with open(arch_file, 'w') as f:
            f.write(content)

        logger.info("Generated architecture documentation")
        return arch_file

    def sync_documentation(self) -> Dict[str, List[Path]]:
        """
        Synchronize all documentation with current codebase.

        Returns:
            Dictionary of updated documentation by type
        """
        results = {}

        # API documentation
        results['api'] = self.generate_api_documentation()

        # Changelog
        results['changelog'] = [self.generate_changelog()]

        # Architecture
        results['architecture'] = [self.generate_architecture_doc()]

        # README
        results['readme'] = [self.update_readme()]

        logger.info(f"Synchronized documentation: {sum(len(v) for v in results.values())} files updated")
        return results

    def _analyze_python_file(self, file_path: Path) -> CodeAnalysis:
        """Analyze a Python file and extract documentation information."""
        with open(file_path, 'r') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return CodeAnalysis(
                file_path=str(file_path),
                module_name=file_path.stem
            )

        analysis = CodeAnalysis(
            file_path=str(file_path),
            module_name=file_path.stem,
            docstring=ast.get_docstring(tree)
        )

        # Extract classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': [],
                    'bases': [self._get_node_name(base) for base in node.bases]
                }

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            'name': item.name,
                            'docstring': ast.get_docstring(item),
                            'args': [arg.arg for arg in item.args.args],
                            'returns': self._get_annotation_name(item.returns) if item.returns else None
                        }
                        class_info['methods'].append(method_info)

                analysis.classes.append(class_info)

            elif isinstance(node, ast.FunctionDef) and not any(
                isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
            ):
                func_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'args': [arg.arg for arg in node.args.args],
                    'returns': self._get_annotation_name(node.returns) if node.returns else None
                }
                analysis.functions.append(func_info)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis.imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    analysis.imports.append(node.module)

        return analysis

    def _generate_api_doc_file(self, analysis: CodeAnalysis) -> Optional[Path]:
        """Generate API documentation file from code analysis."""
        # Create module documentation
        doc_content = f"# {analysis.module_name}\n\n"

        if analysis.docstring:
            doc_content += f"{analysis.docstring}\n\n"

        # Classes
        if analysis.classes:
            doc_content += "## Classes\n\n"
            for cls in analysis.classes:
                doc_content += f"### {cls['name']}\n\n"
                if cls['docstring']:
                    doc_content += f"{cls['docstring']}\n\n"

                if cls['bases']:
                    doc_content += f"**Inherits from**: {', '.join(cls['bases'])}\n\n"

                # Methods
                if cls['methods']:
                    doc_content += "#### Methods\n\n"
                    for method in cls['methods']:
                        args_str = ', '.join(method['args'])
                        returns_str = f" -> {method['returns']}" if method['returns'] else ""
                        doc_content += f"##### `{method['name']}({args_str}){returns_str}`\n\n"
                        if method['docstring']:
                            doc_content += f"{method['docstring']}\n\n"

        # Functions
        if analysis.functions:
            doc_content += "## Functions\n\n"
            for func in analysis.functions:
                args_str = ', '.join(func['args'])
                returns_str = f" -> {func['returns']}" if func['returns'] else ""
                doc_content += f"### `{func['name']}({args_str}){returns_str}`\n\n"
                if func['docstring']:
                    doc_content += f"{func['docstring']}\n\n"

        # Write to file
        doc_file = self.api_docs_dir / f"{analysis.module_name}.md"
        with open(doc_file, 'w') as f:
            f.write(doc_content)

        return doc_file

    def _generate_api_index(self, doc_files: List[Path]) -> Path:
        """Generate API documentation index."""
        index_content = "# API Reference\n\n"
        index_content += "This documentation is automatically generated from the codebase.\n\n"

        # Group by directory
        by_dir: Dict[str, List[Path]] = {}
        for doc_file in doc_files:
            relative = doc_file.relative_to(self.api_docs_dir)
            dir_name = str(relative.parent) if relative.parent != Path('.') else 'root'
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(doc_file)

        # Generate index
        for dir_name in sorted(by_dir.keys()):
            if dir_name != 'root':
                index_content += f"## {dir_name}\n\n"

            for doc_file in sorted(by_dir[dir_name]):
                module_name = doc_file.stem
                relative_path = doc_file.relative_to(self.api_docs_dir)
                index_content += f"- [{module_name}]({relative_path})\n"

            index_content += "\n"

        index_file = self.api_docs_dir / "index.md"
        with open(index_file, 'w') as f:
            f.write(index_content)

        return index_file

    def _parse_git_log(self, log_output: str) -> List[Dict[str, str]]:
        """Parse git log output into commit dictionaries."""
        commits = []
        for line in log_output.strip().split('\n'):
            if not line:
                continue

            parts = line.split('|||')
            if len(parts) >= 4:
                commits.append({
                    'hash': parts[0],
                    'author': parts[1],
                    'date': parts[2],
                    'subject': parts[3],
                    'body': parts[4] if len(parts) > 4 else ''
                })

        return commits

    def _group_commits_by_type(
        self,
        commits: List[Dict[str, str]]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Group commits by type (feat, fix, docs, etc.)."""
        grouped = {
            'features': [],
            'fixes': [],
            'docs': [],
            'refactor': [],
            'test': [],
            'chore': [],
            'other': []
        }

        for commit in commits:
            subject = commit['subject']

            if subject.startswith('feat'):
                grouped['features'].append(commit)
            elif subject.startswith('fix'):
                grouped['fixes'].append(commit)
            elif subject.startswith('docs'):
                grouped['docs'].append(commit)
            elif subject.startswith('refactor'):
                grouped['refactor'].append(commit)
            elif subject.startswith('test'):
                grouped['test'].append(commit)
            elif subject.startswith('chore'):
                grouped['chore'].append(commit)
            else:
                grouped['other'].append(commit)

        return grouped

    def _generate_changelog_markdown(
        self,
        grouped_commits: Dict[str, List[Dict[str, str]]]
    ) -> str:
        """Generate changelog markdown from grouped commits."""
        changelog = "# Changelog\n\n"
        changelog += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        type_titles = {
            'features': '## ✨ Features',
            'fixes': '## 🐛 Bug Fixes',
            'docs': '## 📚 Documentation',
            'refactor': '## ♻️ Refactoring',
            'test': '## ✅ Tests',
            'chore': '## 🔧 Chores',
            'other': '## 📝 Other Changes'
        }

        for commit_type, title in type_titles.items():
            commits = grouped_commits.get(commit_type, [])
            if commits:
                changelog += f"{title}\n\n"
                for commit in commits:
                    # Remove type prefix from subject
                    subject = re.sub(r'^(feat|fix|docs|refactor|test|chore)(\([^\)]+\))?: ', '', commit['subject'])
                    changelog += f"- {subject} ({commit['hash'][:7]})\n"
                    if commit['body']:
                        changelog += f"  {commit['body']}\n"
                changelog += "\n"

        return changelog

    def _generate_default_readme_sections(self) -> Dict[str, str]:
        """Generate default README sections."""
        sections = {}

        # Project name and description
        sections['header'] = f"# {self.project_root.name}\n\n"
        sections['description'] = "Autonomous Development Repository System\n\n"

        # Quick start
        sections['quick_start'] = """## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development
python src/cli.py
```

"""

        # Features
        sections['features'] = """## Features

- Multi-agent development framework
- Git worktree patterns
- Enterprise security
- Autonomous self-healing
- Multi-instance coordination

"""

        return sections

    def _merge_readme_sections(
        self,
        existing: str,
        new_sections: Dict[str, str]
    ) -> str:
        """Merge new sections with existing README content."""
        # For simplicity, replace entire content
        # In production, this would intelligently merge sections
        content = ""
        for section in new_sections.values():
            content += section

        return content

    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure for architecture documentation."""
        structure = {
            'modules': [],
            'agents': [],
            'worktrees': [],
            'security': [],
            'monitoring': []
        }

        # Scan directories
        for subdir in ['agents', 'worktree', 'security', 'parallel_execution', 'monitoring']:
            dir_path = self.src_dir / subdir
            if dir_path.exists():
                files = list(dir_path.glob("*.py"))
                structure[subdir] = [f.stem for f in files if not f.name.startswith('__')]

        return structure

    def _generate_architecture_markdown(self, structure: Dict[str, Any]) -> str:
        """Generate architecture documentation markdown."""
        content = "# Architecture\n\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        content += """## Overview

This project implements an autonomous development system with multiple components:

"""

        # Component breakdown
        for component, modules in structure.items():
            if modules:
                content += f"### {component.title()}\n\n"
                for module in modules:
                    content += f"- `{module}`\n"
                content += "\n"

        return content

    def _get_node_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        return "Unknown"

    def _get_annotation_name(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get annotation name from AST node."""
        if node is None:
            return None
        return self._get_node_name(node)

    def _load_updates(self) -> None:
        """Load documentation update history."""
        if not self.updates_file.exists():
            return

        try:
            with open(self.updates_file, 'r') as f:
                data = json.load(f)
                for update_data in data:
                    update_data['doc_type'] = DocumentationType(update_data['doc_type'])
                    self.updates.append(DocumentationUpdate(**update_data))
        except Exception as e:
            logger.error(f"Error loading updates: {e}")

    def _save_update(self, update: DocumentationUpdate) -> None:
        """Save documentation update to history."""
        self.updates.append(update)

        try:
            # Save all updates
            data = []
            for u in self.updates:
                u_dict = {
                    'update_id': u.update_id,
                    'doc_type': u.doc_type.value,
                    'file_path': u.file_path,
                    'changes': u.changes,
                    'updated_at': u.updated_at,
                    'triggered_by': u.triggered_by,
                    'automated': u.automated
                }
                data.append(u_dict)

            with open(self.updates_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving update: {e}")
