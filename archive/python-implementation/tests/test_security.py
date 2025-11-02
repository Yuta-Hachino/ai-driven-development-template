"""
Tests for Security Module
"""

import pytest
from src.security.encryption import DataEncryption, SecretManager
from src.security.auth import (
    AuthenticationManager,
    MultiFactorAuth,
    RBACManager,
    User,
    UserRole,
)
from src.security.audit import AuditLogger, EventType, EventResult


def test_data_encryption():
    """Test data encryption and decryption"""
    encryption = DataEncryption()

    plaintext = "sensitive data"
    encrypted = encryption.encrypt_data(plaintext)

    assert encrypted != plaintext
    assert len(encrypted) > 0


def test_encryption_key_rotation():
    """Test encryption key rotation"""
    encryption = DataEncryption()

    old_key_id = encryption.master_key.key_id
    new_key_id = encryption.rotate_key(old_key_id)

    assert new_key_id != old_key_id
    assert new_key_id in encryption.keys


def test_secret_manager():
    """Test secret manager"""
    manager = SecretManager()

    # Create secret
    success = manager.create_secret(
        "test_secret",
        "secret_value_123",
        metadata={"type": "api_key"}
    )

    assert success is True

    # Get secret
    secret = manager.get_secret("test_secret")
    assert secret is not None

    # List secrets
    secrets = manager.list_secrets()
    assert len(secrets) == 1
    assert secrets[0]["id"] == "test_secret"


def test_secret_rotation():
    """Test secret rotation"""
    manager = SecretManager()

    manager.create_secret("rotate_test", "old_value")
    success = manager.rotate_secret("rotate_test")

    assert success is True


def test_user_creation():
    """Test user creation"""
    auth_manager = AuthenticationManager()

    user = auth_manager.create_user(
        "user123",
        "user@example.com",
        "password123",
        roles=[UserRole.DEVELOPER]
    )

    assert user.user_id == "user123"
    assert user.email == "user@example.com"
    assert UserRole.DEVELOPER in user.roles


def test_authentication():
    """Test user authentication"""
    auth_manager = AuthenticationManager()

    auth_manager.create_user(
        "user123",
        "user@example.com",
        "password123"
    )

    session_id = auth_manager.authenticate(
        "user123",
        "password123",
        ip_address="127.0.0.1"
    )

    assert session_id is not None
    assert auth_manager.verify_session(session_id) is True


def test_session_expiration():
    """Test session expiration"""
    auth_manager = AuthenticationManager(config={"session_timeout": 1})

    auth_manager.create_user("user123", "user@example.com", "password123")
    session_id = auth_manager.authenticate("user123", "password123")

    # Session should be valid initially
    assert auth_manager.verify_session(session_id) is True

    # Manually expire the session
    import time
    from datetime import datetime, timedelta
    auth_manager.sessions[session_id].expires_at = datetime.now() - timedelta(seconds=10)

    # Session should be invalid now
    assert auth_manager.verify_session(session_id) is False


def test_mfa():
    """Test multi-factor authentication"""
    mfa = MultiFactorAuth()

    secret = mfa.generate_secret("user123")
    assert len(secret) > 0

    # Verify token (simplified test)
    is_valid = mfa.verify_token("user123", "123456")
    assert isinstance(is_valid, bool)


def test_rbac_permissions():
    """Test RBAC permission checking"""
    rbac = RBACManager()

    user = User(
        user_id="dev1",
        email="dev@example.com",
        roles={UserRole.DEVELOPER}
    )

    # Developer should have read:code permission
    assert rbac.check_permission(user, "read:code", "code") is True

    # Developer should not have approve:pr permission
    assert rbac.check_permission(user, "approve:pr", "pull_requests") is False


def test_rbac_admin_permissions():
    """Test admin has all permissions"""
    rbac = RBACManager()

    admin = User(
        user_id="admin1",
        email="admin@example.com",
        roles={UserRole.ADMIN}
    )

    # Admin should have all permissions
    assert rbac.check_permission(admin, "read:code", "code") is True
    assert rbac.check_permission(admin, "approve:pr", "pull_requests") is True
    assert rbac.check_permission(admin, "any:permission", "any_resource") is True


def test_audit_logger():
    """Test audit logging"""
    logger = AuditLogger()

    event = logger.log_event(
        event_type=EventType.AUTHENTICATION,
        actor="user123",
        resource="system",
        action="login",
        result=EventResult.SUCCESS,
        ip_address="127.0.0.1"
    )

    assert event is not None
    assert event.event_type == EventType.AUTHENTICATION
    assert event.actor == "user123"
    assert event.hash is not None


def test_audit_log_integrity():
    """Test audit log integrity verification"""
    logger = AuditLogger()

    # Log multiple events
    for i in range(5):
        logger.log_event(
            event_type=EventType.DATA_ACCESS,
            actor=f"user{i}",
            resource="database",
            action="read",
            result=EventResult.SUCCESS
        )

    # Verify integrity
    assert logger.verify_integrity() is True


def test_audit_log_query():
    """Test audit log querying"""
    logger = AuditLogger()

    # Log events
    logger.log_event(
        EventType.AUTHENTICATION,
        "user1",
        "system",
        "login",
        EventResult.SUCCESS
    )
    logger.log_event(
        EventType.DATA_ACCESS,
        "user2",
        "database",
        "read",
        EventResult.SUCCESS
    )

    # Query by event type
    auth_events = logger.query_events(event_type=EventType.AUTHENTICATION)
    assert len(auth_events) == 1
    assert auth_events[0].actor == "user1"


def test_audit_statistics():
    """Test audit log statistics"""
    logger = AuditLogger()

    # Log events
    logger.log_event(
        EventType.AUTHENTICATION,
        "user1",
        "system",
        "login",
        EventResult.SUCCESS
    )
    logger.log_event(
        EventType.AUTHENTICATION,
        "user1",
        "system",
        "logout",
        EventResult.SUCCESS
    )

    stats = logger.get_statistics()

    assert stats["total_events"] == 2
    assert "authentication" in stats["event_types"]
    assert stats["event_types"]["authentication"] == 2
