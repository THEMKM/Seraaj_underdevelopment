"""
Divine Password Utilities for Seraaj
Centralized password hashing to end the duplication sins
Compatible with both passlib (main JWT) and raw bcrypt (demo scripts)
"""

from passlib.context import CryptContext


# Sacred password context - matches auth/jwt.py configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password using passlib/bcrypt - THE SINGLE SOURCE OF TRUTH

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Note: This replaces all 8 duplicate implementations across the codebase
    Compatible with existing JWT auth system
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against its hash - matches JWT auth interface

    Args:
        plain_password: Plain text password
        hashed_password: Previously hashed password

    Returns:
        True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


# Legacy compatibility function for demo scripts
def verify_password_hash(password: str, hashed: str) -> bool:
    """Legacy compatibility - delegates to verify_password"""
    return verify_password(password, hashed)
