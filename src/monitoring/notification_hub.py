"""
Notification Hub

Centralized notification and alerting system for autonomous development.
Supports multiple channels: GitHub Issues, Slack, Email, Webhooks.
"""

import json
import logging
import smtplib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification delivery channels"""
    GITHUB_ISSUE = "github_issue"
    GITHUB_COMMENT = "github_comment"
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CONSOLE = "console"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Notification:
    """Notification message"""
    notification_id: str
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    sent_to: List[str] = field(default_factory=list)
    failed_channels: List[str] = field(default_factory=list)


@dataclass
class AlertRule:
    """Alert rule for triggering notifications"""
    rule_id: str
    name: str
    condition: str  # Python expression
    priority: NotificationPriority
    channels: List[NotificationChannel]
    cooldown_minutes: int = 30
    enabled: bool = True
    last_triggered: Optional[str] = None


class NotificationHub:
    """
    Centralized notification hub for autonomous development system.

    Features:
    - Multi-channel notification delivery
    - Alert rules with conditions
    - Rate limiting and cooldowns
    - Notification history
    - Failed delivery retry
    """

    def __init__(self, project_root: str, config: Optional[Dict] = None):
        """
        Initialize Notification Hub.

        Args:
            project_root: Root directory of the project
            config: Optional configuration dictionary
        """
        self.project_root = Path(project_root)
        self.config = config or {}

        # Storage paths
        self.monitoring_dir = self.project_root / "docs" / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)

        self.notifications_file = self.monitoring_dir / "notifications.jsonl"
        self.rules_file = self.monitoring_dir / "alert_rules.json"

        # State
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_history: List[Notification] = []

        # Channel handlers
        self.channel_handlers: Dict[NotificationChannel, Callable] = {
            NotificationChannel.GITHUB_ISSUE: self._send_github_issue,
            NotificationChannel.GITHUB_COMMENT: self._send_github_comment,
            NotificationChannel.SLACK: self._send_slack,
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.WEBHOOK: self._send_webhook,
            NotificationChannel.CONSOLE: self._send_console,
        }

        # Load existing data
        self._load_alert_rules()
        self._load_notification_history()

        logger.info(f"Notification Hub initialized with {len(self.alert_rules)} alert rules")

    def send_notification(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Send a notification through specified channels.

        Args:
            title: Notification title
            message: Notification message
            priority: Priority level
            channels: List of channels to use (default: console)
            metadata: Additional metadata

        Returns:
            Created Notification object
        """
        if channels is None:
            channels = [NotificationChannel.CONSOLE]

        notification_id = f"notif_{int(datetime.now().timestamp())}"

        notification = Notification(
            notification_id=notification_id,
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        # Send through each channel
        for channel in channels:
            try:
                handler = self.channel_handlers.get(channel)
                if handler:
                    success = handler(notification)
                    if success:
                        notification.sent_to.append(channel.value)
                    else:
                        notification.failed_channels.append(channel.value)
                else:
                    logger.warning(f"No handler for channel: {channel}")
                    notification.failed_channels.append(channel.value)
            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {e}")
                notification.failed_channels.append(channel.value)

        # Save to history
        self.notification_history.append(notification)
        self._save_notification(notification)

        logger.info(f"Sent notification '{title}' via {len(notification.sent_to)} channels")
        return notification

    def create_alert_rule(
        self,
        name: str,
        condition: str,
        priority: NotificationPriority,
        channels: List[NotificationChannel],
        cooldown_minutes: int = 30
    ) -> AlertRule:
        """
        Create a new alert rule.

        Args:
            name: Rule name
            condition: Python expression (e.g., "tasks_blocked > 3")
            priority: Alert priority
            channels: Notification channels
            cooldown_minutes: Minimum time between alerts

        Returns:
            Created AlertRule
        """
        rule_id = f"rule_{int(datetime.now().timestamp())}"

        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            condition=condition,
            priority=priority,
            channels=channels,
            cooldown_minutes=cooldown_minutes,
            enabled=True
        )

        self.alert_rules[rule_id] = rule
        self._save_alert_rules()

        logger.info(f"Created alert rule: {name}")
        return rule

    def evaluate_alert_rules(self, context: Dict[str, Any]) -> List[Notification]:
        """
        Evaluate all alert rules against current context.

        Args:
            context: Dictionary of variables for condition evaluation

        Returns:
            List of triggered notifications
        """
        triggered_notifications = []

        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            # Check cooldown
            if rule.last_triggered:
                last_trigger_time = datetime.fromisoformat(rule.last_triggered)
                cooldown_end = last_trigger_time + timedelta(minutes=rule.cooldown_minutes)
                if datetime.now() < cooldown_end:
                    continue

            # Evaluate condition
            try:
                # Create safe evaluation environment
                safe_context = {k: v for k, v in context.items() if not k.startswith('_')}
                condition_met = eval(rule.condition, {"__builtins__": {}}, safe_context)

                if condition_met:
                    # Trigger notification
                    notification = self.send_notification(
                        title=f"Alert: {rule.name}",
                        message=f"Alert condition met: {rule.condition}\n\nContext: {json.dumps(safe_context, indent=2)}",
                        priority=rule.priority,
                        channels=rule.channels,
                        metadata={
                            "rule_id": rule.rule_id,
                            "condition": rule.condition,
                            "context": safe_context
                        }
                    )

                    # Update last triggered time
                    rule.last_triggered = datetime.now().isoformat()
                    self._save_alert_rules()

                    triggered_notifications.append(notification)
                    logger.info(f"Alert rule '{rule.name}' triggered")

            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.name}': {e}")

        return triggered_notifications

    def get_notification_history(
        self,
        limit: int = 50,
        priority: Optional[NotificationPriority] = None,
        channel: Optional[NotificationChannel] = None
    ) -> List[Notification]:
        """
        Get notification history with filters.

        Args:
            limit: Maximum number of notifications to return
            priority: Filter by priority
            channel: Filter by channel

        Returns:
            List of notifications
        """
        filtered = self.notification_history

        if priority:
            filtered = [n for n in filtered if n.priority == priority]

        if channel:
            filtered = [n for n in filtered if channel in n.channels]

        # Sort by created_at descending
        filtered.sort(key=lambda n: n.created_at, reverse=True)

        return filtered[:limit]

    def _send_github_issue(self, notification: Notification) -> bool:
        """Send notification as GitHub issue."""
        try:
            # Use gh CLI to create issue
            labels = self._get_github_labels(notification.priority)

            cmd = [
                "gh", "issue", "create",
                "--title", notification.title,
                "--body", notification.message,
                "--label", labels
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Created GitHub issue for notification: {notification.title}")
                return True
            else:
                logger.error(f"Failed to create GitHub issue: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return False

    def _send_github_comment(self, notification: Notification) -> bool:
        """Send notification as GitHub comment."""
        try:
            # Requires issue number in metadata
            issue_number = notification.metadata.get('issue_number')
            if not issue_number:
                logger.warning("No issue_number in metadata for GitHub comment")
                return False

            cmd = [
                "gh", "issue", "comment", str(issue_number),
                "--body", f"### {notification.title}\n\n{notification.message}"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Posted GitHub comment on issue #{issue_number}")
                return True
            else:
                logger.error(f"Failed to post GitHub comment: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error posting GitHub comment: {e}")
            return False

    def _send_slack(self, notification: Notification) -> bool:
        """Send notification to Slack."""
        try:
            webhook_url = self.config.get('slack_webhook_url')
            if not webhook_url:
                logger.warning("No Slack webhook URL configured")
                return False

            # Create Slack message
            color = self._get_slack_color(notification.priority)
            payload = {
                "attachments": [{
                    "color": color,
                    "title": notification.title,
                    "text": notification.message,
                    "footer": "Autonomous Development System",
                    "ts": int(datetime.now().timestamp())
                }]
            }

            # Send via curl (simple approach)
            import urllib.request
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info("Sent notification to Slack")
                    return True
                else:
                    logger.error(f"Slack API returned status {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False

    def _send_email(self, notification: Notification) -> bool:
        """Send notification via email."""
        try:
            smtp_config = self.config.get('email', {})
            if not smtp_config:
                logger.warning("No email configuration provided")
                return False

            # Create email
            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_address')
            msg['To'] = smtp_config.get('to_address')
            msg['Subject'] = f"[{notification.priority.value.upper()}] {notification.title}"

            body = f"{notification.message}\n\n---\nAutonomous Development System\n{notification.created_at}"
            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(smtp_config['smtp_host'], smtp_config.get('smtp_port', 587)) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()

                if smtp_config.get('username') and smtp_config.get('password'):
                    server.login(smtp_config['username'], smtp_config['password'])

                server.send_message(msg)

            logger.info("Sent notification via email")
            return True

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    def _send_webhook(self, notification: Notification) -> bool:
        """Send notification to webhook."""
        try:
            webhook_url = notification.metadata.get('webhook_url') or self.config.get('webhook_url')
            if not webhook_url:
                logger.warning("No webhook URL provided")
                return False

            payload = {
                "notification_id": notification.notification_id,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority.value,
                "created_at": notification.created_at,
                "metadata": notification.metadata
            }

            import urllib.request
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info("Sent notification to webhook")
                    return True
                else:
                    logger.error(f"Webhook returned status {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            return False

    def _send_console(self, notification: Notification) -> bool:
        """Send notification to console (log)."""
        priority_emoji = {
            NotificationPriority.LOW: "ℹ️",
            NotificationPriority.MEDIUM: "⚠️",
            NotificationPriority.HIGH: "🚨",
            NotificationPriority.CRITICAL: "🔴"
        }

        emoji = priority_emoji.get(notification.priority, "📢")
        print(f"\n{emoji} {notification.title}")
        print(f"Priority: {notification.priority.value}")
        print(f"Message: {notification.message}")
        print(f"Time: {notification.created_at}\n")

        return True

    def _get_github_labels(self, priority: NotificationPriority) -> str:
        """Get GitHub labels based on priority."""
        label_map = {
            NotificationPriority.LOW: "notification,low-priority",
            NotificationPriority.MEDIUM: "notification,medium-priority",
            NotificationPriority.HIGH: "notification,high-priority",
            NotificationPriority.CRITICAL: "notification,critical"
        }
        return label_map.get(priority, "notification")

    def _get_slack_color(self, priority: NotificationPriority) -> str:
        """Get Slack attachment color based on priority."""
        color_map = {
            NotificationPriority.LOW: "#36a64f",  # Green
            NotificationPriority.MEDIUM: "#ff9900",  # Orange
            NotificationPriority.HIGH: "#ff0000",  # Red
            NotificationPriority.CRITICAL: "#8b0000"  # Dark red
        }
        return color_map.get(priority, "#808080")

    def _load_alert_rules(self) -> None:
        """Load alert rules from file."""
        if not self.rules_file.exists():
            # Create default rules
            self._create_default_rules()
            return

        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                for rule_id, rule_data in data.items():
                    # Convert enums
                    rule_data['priority'] = NotificationPriority(rule_data['priority'])
                    rule_data['channels'] = [
                        NotificationChannel(ch) for ch in rule_data['channels']
                    ]
                    self.alert_rules[rule_id] = AlertRule(**rule_data)
        except Exception as e:
            logger.error(f"Error loading alert rules: {e}")

    def _save_alert_rules(self) -> None:
        """Save alert rules to file."""
        try:
            data = {}
            for rule_id, rule in self.alert_rules.items():
                rule_dict = asdict(rule)
                # Convert enums to strings
                rule_dict['priority'] = rule_dict['priority'].value
                rule_dict['channels'] = [ch.value for ch in rule.channels]
                data[rule_id] = rule_dict

            with open(self.rules_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving alert rules: {e}")

    def _load_notification_history(self) -> None:
        """Load notification history from file."""
        if not self.notifications_file.exists():
            return

        try:
            with open(self.notifications_file, 'r') as f:
                for line in f:
                    if line.strip():
                        notif_data = json.loads(line)
                        # Convert enums
                        notif_data['priority'] = NotificationPriority(notif_data['priority'])
                        notif_data['channels'] = [
                            NotificationChannel(ch) for ch in notif_data['channels']
                        ]
                        self.notification_history.append(Notification(**notif_data))

            # Keep only last 1000 notifications in memory
            self.notification_history = self.notification_history[-1000:]
        except Exception as e:
            logger.error(f"Error loading notification history: {e}")

    def _save_notification(self, notification: Notification) -> None:
        """Append notification to history file."""
        try:
            notif_dict = asdict(notification)
            # Convert enums to strings
            notif_dict['priority'] = notif_dict['priority'].value
            notif_dict['channels'] = [ch.value for ch in notification.channels]

            with open(self.notifications_file, 'a') as f:
                f.write(json.dumps(notif_dict) + '\n')
        except Exception as e:
            logger.error(f"Error saving notification: {e}")

    def _create_default_rules(self) -> None:
        """Create default alert rules."""
        # Rule 1: Too many blocked tasks
        self.create_alert_rule(
            name="High number of blocked tasks",
            condition="tasks_blocked > 3",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.GITHUB_ISSUE, NotificationChannel.CONSOLE],
            cooldown_minutes=60
        )

        # Rule 2: Instance overloaded
        self.create_alert_rule(
            name="Instance overloaded",
            condition="max_instance_workload > 5",
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.CONSOLE],
            cooldown_minutes=30
        )

        # Rule 3: Low velocity
        self.create_alert_rule(
            name="Low development velocity",
            condition="velocity < 1.0 and total_tasks > 10",
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.CONSOLE],
            cooldown_minutes=120
        )

        # Rule 4: CI/CD failure
        self.create_alert_rule(
            name="CI/CD pipeline failure",
            condition="ci_status == 'failed'",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.GITHUB_ISSUE, NotificationChannel.CONSOLE],
            cooldown_minutes=15
        )

        logger.info("Created default alert rules")
