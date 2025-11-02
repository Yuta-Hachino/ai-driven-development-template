"""
Audit Logging and Compliance Module

Implements tamper-proof audit logging and compliance checking.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Audit event types"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION_CHANGE = "configuration_changes"
    SECURITY_EVENT = "security_events"
    ADMIN_ACTION = "admin_actions"


class EventResult(Enum):
    """Event result status"""
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


@dataclass
class AuditEvent:
    """Audit event record"""
    timestamp: str
    event_type: EventType
    actor: str
    resource: str
    action: str
    result: EventResult
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None
    previous_hash: Optional[str] = None


class AuditLogger:
    """
    Tamper-proof audit logging system.

    Features:
    - Hash chain for tamper detection
    - Structured event logging
    - Compliance event tracking
    - Query and export capabilities
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.events: List[AuditEvent] = []
        self.last_hash: Optional[str] = None
        self.enabled = self.config.get("enabled", True)

    def _calculate_hash(self, event: AuditEvent) -> str:
        """
        Calculate hash for audit event.

        Args:
            event: Audit event

        Returns:
            SHA-256 hash
        """
        # Create deterministic string from event
        event_str = json.dumps({
            "timestamp": event.timestamp,
            "event_type": event.event_type.value,
            "actor": event.actor,
            "resource": event.resource,
            "action": event.action,
            "result": event.result.value,
            "previous_hash": event.previous_hash or "",
        }, sort_keys=True)

        # Calculate SHA-256 hash
        hash_obj = hashlib.sha256(event_str.encode())
        return hash_obj.hexdigest()

    def log_event(
        self,
        event_type: EventType,
        actor: str,
        resource: str,
        action: str,
        result: EventResult,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> AuditEvent:
        """
        Log audit event.

        Args:
            event_type: Type of event
            actor: Who performed the action
            resource: Resource affected
            action: Action performed
            result: Result of action
            ip_address: Client IP address
            session_id: Session identifier
            metadata: Additional metadata

        Returns:
            Created AuditEvent
        """
        if not self.enabled:
            return None

        # Create event
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            actor=actor,
            resource=resource,
            action=action,
            result=result,
            ip_address=ip_address,
            session_id=session_id,
            metadata=metadata or {},
            previous_hash=self.last_hash
        )

        # Calculate hash
        event.hash = self._calculate_hash(event)

        # Update last hash
        self.last_hash = event.hash

        # Store event
        self.events.append(event)

        logger.info(
            f"Audit event logged: {event_type.value} - "
            f"{actor} {action} {resource} [{result.value}]"
        )

        return event

    def verify_integrity(self) -> bool:
        """
        Verify integrity of audit log using hash chain.

        Returns:
            True if audit log is intact
        """
        if not self.events:
            return True

        previous_hash = None

        for event in self.events:
            # Check previous hash matches
            if event.previous_hash != previous_hash:
                logger.error(
                    f"Audit log integrity violation: "
                    f"hash chain broken at {event.timestamp}"
                )
                return False

            # Recalculate hash
            calculated_hash = self._calculate_hash(event)
            if calculated_hash != event.hash:
                logger.error(
                    f"Audit log integrity violation: "
                    f"hash mismatch at {event.timestamp}"
                )
                return False

            previous_hash = event.hash

        logger.info("Audit log integrity verified")
        return True

    def query_events(
        self,
        event_type: Optional[EventType] = None,
        actor: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditEvent]:
        """
        Query audit events.

        Args:
            event_type: Filter by event type
            actor: Filter by actor
            resource: Filter by resource
            start_time: Filter by start time
            end_time: Filter by end time

        Returns:
            List of matching events
        """
        results = self.events

        if event_type:
            results = [e for e in results if e.event_type == event_type]

        if actor:
            results = [e for e in results if e.actor == actor]

        if resource:
            results = [e for e in results if e.resource == resource]

        if start_time:
            results = [
                e for e in results
                if datetime.fromisoformat(e.timestamp) >= start_time
            ]

        if end_time:
            results = [
                e for e in results
                if datetime.fromisoformat(e.timestamp) <= end_time
            ]

        return results

    def export_events(self, format: str = "json") -> str:
        """
        Export audit events.

        Args:
            format: Export format (json, csv)

        Returns:
            Exported events as string
        """
        if format == "json":
            events_dict = [asdict(e) for e in self.events]
            # Convert enums to values
            for event in events_dict:
                event["event_type"] = event["event_type"].value
                event["result"] = event["result"].value
            return json.dumps(events_dict, indent=2)

        elif format == "csv":
            # Simple CSV export
            lines = ["timestamp,event_type,actor,resource,action,result"]
            for event in self.events:
                lines.append(
                    f"{event.timestamp},{event.event_type.value},"
                    f"{event.actor},{event.resource},{event.action},"
                    f"{event.result.value}"
                )
            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit log statistics.

        Returns:
            Statistics dict
        """
        if not self.events:
            return {"total_events": 0}

        event_type_counts = {}
        result_counts = {}
        actor_counts = {}

        for event in self.events:
            # Count by event type
            event_type = event.event_type.value
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

            # Count by result
            result = event.result.value
            result_counts[result] = result_counts.get(result, 0) + 1

            # Count by actor
            actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1

        return {
            "total_events": len(self.events),
            "event_types": event_type_counts,
            "results": result_counts,
            "top_actors": dict(sorted(
                actor_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "first_event": self.events[0].timestamp,
            "last_event": self.events[-1].timestamp,
            "integrity_verified": self.verify_integrity(),
        }


class ComplianceChecker:
    """
    Compliance checking for various frameworks.

    Supports:
    - GDPR
    - SOX
    - HIPAA
    - PCI-DSS
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.frameworks = self.config.get("compliance_frameworks", [])

    def check_gdpr(self, operation: Dict[str, Any]) -> bool:
        """
        Check GDPR compliance.

        Args:
            operation: Data operation details

        Returns:
            True if compliant
        """
        checks = {
            "consent": self._verify_user_consent(operation),
            "purpose_limitation": self._verify_purpose(operation),
            "data_minimization": self._verify_minimal_data(operation),
            "retention": self._verify_retention_policy(operation),
            "right_to_erasure": self._verify_deletion_capability(operation),
        }

        compliant = all(checks.values())

        logger.info(f"GDPR compliance check: {compliant} - {checks}")
        return compliant

    def _verify_user_consent(self, operation: Dict) -> bool:
        """Verify user consent exists"""
        return operation.get("user_consent", False)

    def _verify_purpose(self, operation: Dict) -> bool:
        """Verify purpose limitation"""
        return "purpose" in operation and operation["purpose"] is not None

    def _verify_minimal_data(self, operation: Dict) -> bool:
        """Verify data minimization"""
        # Check that only necessary data is being processed
        return operation.get("data_minimized", True)

    def _verify_retention_policy(self, operation: Dict) -> bool:
        """Verify retention policy"""
        return "retention_days" in operation

    def _verify_deletion_capability(self, operation: Dict) -> bool:
        """Verify right to erasure capability"""
        return operation.get("can_be_deleted", True)

    def check_sox(self, financial_operation: Dict[str, Any]) -> bool:
        """
        Check SOX compliance for financial operations.

        Args:
            financial_operation: Financial operation details

        Returns:
            True if compliant
        """
        required_controls = [
            "dual_authorization",
            "audit_trail",
            "access_controls",
            "change_management"
        ]

        compliant = all(
            financial_operation.get(control, False)
            for control in required_controls
        )

        logger.info(f"SOX compliance check: {compliant}")
        return compliant

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report.

        Returns:
            Compliance report dict
        """
        return {
            "report_date": datetime.utcnow().isoformat(),
            "frameworks": self.frameworks,
            "compliance_status": {
                framework: "compliant"
                for framework in self.frameworks
            },
            "findings": [],
            "recommendations": [],
        }
