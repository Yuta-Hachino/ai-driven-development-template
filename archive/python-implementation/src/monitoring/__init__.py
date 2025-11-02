"""
Monitoring Module

Provides notification hub and monitoring capabilities for autonomous development.
Enables real-time alerts, metrics collection, and system health tracking.
"""

from .notification_hub import (
    NotificationHub,
    Notification,
    NotificationChannel,
    NotificationPriority,
    AlertRule,
)

__all__ = [
    "NotificationHub",
    "Notification",
    "NotificationChannel",
    "NotificationPriority",
    "AlertRule",
]

__version__ = "0.1.0"
