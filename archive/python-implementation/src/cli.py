"""
CLI Entry Point

Command-line interface for the autonomous development system.
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
except ImportError:
    # Fallback if rich/click not installed
    click = None
    Console = None
    Table = None
    Progress = None

from agents import (
    FrontendAgent,
    BackendAgent,
    AlgorithmAgent,
    AgentConfig,
    AgentType,
)
from worktree import WorktreeManager, DevelopmentPattern
from security import AuditLogger, EventType, EventResult
from utils import setup_logging


# Setup console
console = Console() if Console else None


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║   Autonomous Development Repository System            ║
║   Enterprise AI-Powered Development Platform          ║
╚═══════════════════════════════════════════════════════╝
    """
    if console:
        console.print(banner, style="bold cyan")
    else:
        print(banner)


if click:
    @click.group()
    @click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
    @click.option('--config', '-c', type=click.Path(exists=True), help='Config file path')
    def cli(verbose, config):
        """Autonomous Development System CLI"""
        # Setup logging
        level = "DEBUG" if verbose else "INFO"
        setup_logging(level=level, log_file="logs/autonomous-dev.log")

        print_banner()


    @cli.command()
    @click.argument('task')
    @click.option('--agent', '-a', default='backend', help='Agent type to use')
    @click.option('--model', '-m', default='claude-3-opus', help='AI model to use')
    def execute(task, agent, model):
        """Execute a development task with an agent"""
        console.print(f"\n[bold green]Executing task:[/bold green] {task}")
        console.print(f"[cyan]Agent:[/cyan] {agent}")
        console.print(f"[cyan]Model:[/cyan] {model}")

        # Create agent config
        config = AgentConfig(
            name=f"{agent}_agent",
            agent_type=AgentType.LLM,
            model=model,
        )

        # Select agent type
        if agent == 'frontend':
            agent_instance = FrontendAgent(config)
        elif agent == 'backend':
            agent_instance = BackendAgent(config)
        elif agent == 'algorithm':
            agent_instance = AlgorithmAgent(config)
        else:
            console.print(f"[red]Unknown agent type: {agent}[/red]")
            sys.exit(1)

        # Execute task
        async def run():
            with Progress() as progress:
                task_progress = progress.add_task(
                    f"[cyan]Processing with {agent} agent...",
                    total=100
                )

                result = await agent_instance.execute(task)

                progress.update(task_progress, completed=100)

                if result.success:
                    console.print("\n[bold green]✓ Task completed successfully![/bold green]")
                    console.print("\n[bold]Result:[/bold]")
                    console.print(result.output)
                else:
                    console.print("\n[bold red]✗ Task failed[/bold red]")
                    console.print(f"[red]Error: {result.error}[/red]")

                console.print(f"\n[dim]Execution time: {result.execution_time:.2f}s[/dim]")

        asyncio.run(run())


    @cli.command()
    @click.argument('feature')
    @click.option('--pattern', '-p', default='parallel', help='Worktree pattern')
    @click.option('--agents', '-a', multiple=True, help='Agents to use')
    def worktree(feature, pattern, agents):
        """Create and manage worktrees"""
        console.print(f"\n[bold green]Creating worktree for feature:[/bold green] {feature}")
        console.print(f"[cyan]Pattern:[/cyan] {pattern}")

        # Get repository path
        repo_path = Path.cwd()
        manager = WorktreeManager(str(repo_path))

        # Create worktrees based on pattern
        try:
            pattern_enum = DevelopmentPattern(pattern)

            if pattern_enum == DevelopmentPattern.COMPETITION:
                agents_list = list(agents) or ['backend', 'algorithm', 'frontend']
                worktrees = manager.create_competition_worktrees(
                    feature=feature,
                    agents=agents_list
                )
                console.print(f"[green]Created {len(worktrees)} competition worktrees[/green]")

            elif pattern_enum == DevelopmentPattern.PARALLEL:
                features = [feature]
                agent_map = {feature: agents[0] if agents else 'backend'}
                worktrees = manager.create_parallel_worktrees(
                    features=features,
                    agent_assignments=agent_map
                )
                console.print(f"[green]Created {len(worktrees)} parallel worktrees[/green]")

            # Display worktrees
            table = Table(title="Created Worktrees")
            table.add_column("Name", style="cyan")
            table.add_column("Path", style="green")
            table.add_column("Pattern", style="yellow")

            for wt in worktrees:
                table.add_row(wt.name, wt.path, wt.pattern.value)

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


    @cli.command()
    def status():
        """Show system status"""
        console.print("\n[bold]System Status[/bold]\n")

        # Worktree stats
        repo_path = Path.cwd()
        manager = WorktreeManager(str(repo_path))
        metrics = manager.get_metrics()

        console.print(f"[cyan]Total Worktrees:[/cyan] {metrics['total_worktrees']}")
        console.print(f"[cyan]Active Patterns:[/cyan]")

        for pattern, count in metrics.get('patterns', {}).items():
            console.print(f"  • {pattern}: {count}")

        console.print()


    @cli.command()
    @click.argument('log_file', type=click.Path(exists=True))
    def analyze(log_file):
        """Analyze CI/CD failure logs"""
        from autonomous import FailureAnalyzer

        console.print(f"\n[bold]Analyzing failure log:[/bold] {log_file}")

        # Read log file
        with open(log_file, 'r') as f:
            log_content = f.read()

        # Analyze
        analyzer = FailureAnalyzer()
        report = analyzer.analyze_log(log_content)

        # Display report
        console.print(f"\n[bold]{report.title}[/bold]")
        console.print(f"[yellow]Type:[/yellow] {report.failure_type.value}")
        console.print(f"[yellow]Severity:[/yellow] {report.severity.value}")
        console.print(f"[yellow]Auto-fixable:[/yellow] {report.auto_fixable}")

        if report.affected_files:
            console.print(f"\n[bold]Affected Files ({len(report.affected_files)}):[/bold]")
            for file in report.affected_files[:5]:
                console.print(f"  • {file}")

        if report.suggested_fixes:
            console.print(f"\n[bold]Suggested Fixes:[/bold]")
            for i, fix in enumerate(report.suggested_fixes, 1):
                console.print(f"  {i}. {fix}")


    @cli.command()
    @click.argument('log_file', type=click.Path(exists=True))
    @click.option('--dry-run', is_flag=True, help='Analyze only, do not apply fixes')
    def heal(log_file, dry_run):
        """Automatically heal CI/CD failures"""
        from autonomous import FailureAnalyzer, AutoHealer

        console.print(f"\n[bold]Auto-healing from log:[/bold] {log_file}")

        # Read and analyze
        with open(log_file, 'r') as f:
            log_content = f.read()

        analyzer = FailureAnalyzer()
        report = analyzer.analyze_log(log_content)

        console.print(f"\n[yellow]Failure:[/yellow] {report.failure_type.value}")
        console.print(f"[yellow]Auto-fixable:[/yellow] {report.auto_fixable}")

        if not report.auto_fixable:
            console.print("\n[red]This failure requires manual intervention[/red]")
            sys.exit(1)

        if dry_run:
            console.print("\n[cyan]Dry run - no changes will be made[/cyan]")
            return

        # Heal
        repo_path = Path.cwd()
        healer = AutoHealer(str(repo_path))

        async def run_heal():
            with Progress() as progress:
                task = progress.add_task("[cyan]Applying fixes...", total=100)

                result = await healer.heal(report)

                progress.update(task, completed=100)

                if result.success:
                    console.print("\n[bold green]✓ Healing successful![/bold green]")
                    console.print(f"\n[bold]Actions taken:[/bold]")
                    for action in result.actions_taken:
                        console.print(f"  • {action}")

                    if result.files_modified:
                        console.print(f"\n[bold]Files modified ({len(result.files_modified)}):[/bold]")
                        for file in result.files_modified[:10]:
                            console.print(f"  • {file}")
                else:
                    console.print("\n[bold red]✗ Healing failed[/bold red]")
                    console.print(f"[red]Error: {result.error_message}[/red]")

        asyncio.run(run_heal())


    @cli.command()
    def version():
        """Show version information"""
        console.print("\n[bold]Autonomous Development System[/bold]")
        console.print("Version: [cyan]0.1.0[/cyan]")
        console.print("Python: [cyan]" + sys.version.split()[0] + "[/cyan]")


else:
    # Fallback if click not installed
    def cli():
        print_banner()
        print("\nError: click and rich packages required")
        print("Install with: pip install click rich")
        sys.exit(1)


def main():
    """Main entry point"""
    if click:
        cli()
    else:
        print("Error: click package not installed")
        print("Install with: pip install click rich")
        sys.exit(1)


if __name__ == '__main__':
    main()
