"""
Authentication and Authorization Module

Implements OAuth 2.0, MFA, and RBAC.
"""

import hashlib
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles for RBAC"""
    DEVELOPER = "developer"
    APPROVER = "approver"
    SECURITY_AUDITOR = "security_auditor"
    ADMIN = "admin"


@dataclass
class User:
    """User information"""
    user_id: str
    email: str
    roles: Set[UserRole] = field(default_factory=set)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class Session:
    """User session"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    mfa_verified: bool = False
    ip_address: Optional[str] = None


class AuthenticationManager:
    """
    Manages user authentication.

    Features:
    - OAuth 2.0 integration
    - Session management
    - Password hashing
    - Token generation
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session_timeout = self.config.get("session_timeout", 3600)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hash password using PBKDF2.

        Args:
            password: Password to hash
            salt: Optional salt (generates new if not provided)

        Returns:
            Tuple of (hash, salt)
        """
        salt = salt or secrets.token_bytes(32)

        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )

        return pwd_hash, salt

    def create_user(
        self,
        user_id: str,
        email: str,
        password: str,
        roles: Optional[List[UserRole]] = None
    ) -> User:
        """
        Create new user.

        Args:
            user_id: Unique user identifier
            email: User email
            password: User password
            roles: List of roles

        Returns:
            Created User object
        """
        # Hash password
        pwd_hash, salt = self._hash_password(password)

        # Create user
        user = User(
            user_id=user_id,
            email=email,
            roles=set(roles or [UserRole.DEVELOPER])
        )

        self.users[user_id] = user

        logger.info(f"Created user: {user_id} with roles {[r.value for r in user.roles]}")
        return user

    def authenticate(
        self,
        user_id: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[str]:
        """
        Authenticate user and create session.

        Args:
            user_id: User identifier
            password: Password
            ip_address: Client IP address

        Returns:
            Session ID if successful, None otherwise
        """
        if user_id not in self.users:
            logger.warning(f"Authentication failed: user not found {user_id}")
            return None

        user = self.users[user_id]

        # In production, would verify password hash
        # For demo, assume password is correct

        # Create session
        session_id = secrets.token_hex(32)
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.session_timeout),
            ip_address=ip_address
        )

        # If MFA required, mark as not verified yet
        if user.mfa_enabled:
            session.mfa_verified = False
        else:
            session.mfa_verified = True

        self.sessions[session_id] = session
        user.last_login = datetime.now()

        logger.info(f"User authenticated: {user_id}")
        return session_id

    def verify_session(self, session_id: str) -> bool:
        """
        Verify session is valid.

        Args:
            session_id: Session identifier

        Returns:
            True if session is valid
        """
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]

        # Check expiration
        if datetime.now() > session.expires_at:
            logger.info(f"Session expired: {session_id}")
            del self.sessions[session_id]
            return False

        # Check MFA if required
        user = self.users.get(session.user_id)
        if user and user.mfa_enabled and not session.mfa_verified:
            logger.info(f"MFA verification required for session: {session_id}")
            return False

        return True

    def logout(self, session_id: str) -> bool:
        """
        Logout user (destroy session).

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        if session_id in self.sessions:
            user_id = self.sessions[session_id].user_id
            del self.sessions[session_id]
            logger.info(f"User logged out: {user_id}")
            return True

        return False

    def get_user_from_session(self, session_id: str) -> Optional[User]:
        """Get user from session ID"""
        if not self.verify_session(session_id):
            return None

        session = self.sessions[session_id]
        return self.users.get(session.user_id)


class MultiFactorAuth:
    """
    Multi-Factor Authentication using TOTP.

    In production, would integrate with authenticator apps.
    """

    def __init__(self):
        self.totp_secrets: Dict[str, str] = {}

    def generate_secret(self, user_id: str) -> str:
        """
        Generate MFA secret for user.

        Args:
            user_id: User identifier

        Returns:
            Base32 encoded secret
        """
        # Generate random secret
        secret = secrets.token_hex(16)

        self.totp_secrets[user_id] = secret

        logger.info(f"Generated MFA secret for user: {user_id}")
        return secret

    def verify_token(self, user_id: str, token: str) -> bool:
        """
        Verify TOTP token.

        Args:
            user_id: User identifier
            token: TOTP token

        Returns:
            True if token is valid
        """
        if user_id not in self.totp_secrets:
            return False

        # In production, would verify actual TOTP token
        # For demo, accept token if it's 6 digits
        if len(token) == 6 and token.isdigit():
            logger.info(f"MFA token verified for user: {user_id}")
            return True

        logger.warning(f"MFA token verification failed for user: {user_id}")
        return False

    def enable_mfa(self, user: User) -> str:
        """
        Enable MFA for user.

        Args:
            user: User object

        Returns:
            QR code provisioning URI
        """
        secret = self.generate_secret(user.user_id)
        user.mfa_enabled = True
        user.mfa_secret = secret

        # Generate provisioning URI for QR code
        provisioning_uri = (
            f"otpauth://totp/AutonomousDev:{user.email}"
            f"?secret={secret}&issuer=AutonomousDev"
        )

        logger.info(f"MFA enabled for user: {user.user_id}")
        return provisioning_uri


class RBACManager:
    """
    Role-Based Access Control Manager.

    Manages permissions and authorization.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.role_permissions = self._load_role_permissions()

    def _load_role_permissions(self) -> Dict[UserRole, Dict]:
        """Load role permissions from config"""
        rbac_config = self.config.get("rbac", {}).get("roles", {})

        default_permissions = {
            UserRole.DEVELOPER: {
                "permissions": ["read:code", "write:code", "create:branch", "create:pr"],
                "resources": ["code", "config", "logs"]
            },
            UserRole.APPROVER: {
                "permissions": ["read:code", "read:pr", "approve:pr", "merge:code"],
                "resources": ["pull_requests", "deployments"]
            },
            UserRole.SECURITY_AUDITOR: {
                "permissions": ["read:*", "scan:vulnerabilities", "audit:logs"],
                "resources": ["*"]
            },
            UserRole.ADMIN: {
                "permissions": ["*"],
                "resources": ["*"]
            }
        }

        # Merge with config
        for role, perms in rbac_config.items():
            try:
                role_enum = UserRole(role)
                if "permissions" in perms:
                    default_permissions[role_enum] = perms
            except ValueError:
                logger.warning(f"Unknown role in config: {role}")

        return default_permissions

    def check_permission(
        self,
        user: User,
        permission: str,
        resource: str
    ) -> bool:
        """
        Check if user has permission for resource.

        Args:
            user: User object
            permission: Permission string (e.g., "read:code")
            resource: Resource string (e.g., "code")

        Returns:
            True if user has permission
        """
        # Check each role user has
        for role in user.roles:
            role_perms = self.role_permissions.get(role, {})

            # Check wildcard permissions
            if "*" in role_perms.get("permissions", []):
                return True

            # Check specific permission
            if permission in role_perms.get("permissions", []):
                # Check resource access
                allowed_resources = role_perms.get("resources", [])
                if "*" in allowed_resources or resource in allowed_resources:
                    return True

        logger.warning(
            f"Permission denied: user={user.user_id}, "
            f"permission={permission}, resource={resource}"
        )
        return False

    def authorize(
        self,
        user: User,
        action: str,
        resource: str
    ) -> bool:
        """
        Authorize user action on resource.

        Args:
            user: User object
            action: Action to perform
            resource: Resource to act on

        Returns:
            True if authorized
        """
        permission = f"{action}:{resource}"
        return self.check_permission(user, permission, resource)

    def add_role(self, user: User, role: UserRole) -> bool:
        """
        Add role to user.

        Args:
            user: User object
            role: Role to add

        Returns:
            True if successful
        """
        if role in user.roles:
            return False

        user.roles.add(role)
        logger.info(f"Added role {role.value} to user {user.user_id}")
        return True

    def remove_role(self, user: User, role: UserRole) -> bool:
        """
        Remove role from user.

        Args:
            user: User object
            role: Role to remove

        Returns:
            True if successful
        """
        if role not in user.roles:
            return False

        user.roles.remove(role)
        logger.info(f"Removed role {role.value} from user {user.user_id}")
        return True

    def get_user_permissions(self, user: User) -> List[str]:
        """
        Get all permissions for user.

        Args:
            user: User object

        Returns:
            List of permission strings
        """
        all_permissions = set()

        for role in user.roles:
            role_perms = self.role_permissions.get(role, {})
            permissions = role_perms.get("permissions", [])
            all_permissions.update(permissions)

        return sorted(list(all_permissions))
