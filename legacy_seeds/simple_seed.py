"""
Simple database seeding for testing authentication and basic functionality
"""

import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from database import get_session, create_db_and_tables
from models import User, UserStatus
from models.user import UserRole
from auth.password_utils import hash_password


def create_mock_accounts():
    """Create essential mock accounts for testing"""
    print("Creating mock accounts...")

    session = next(get_session())

    try:
        # Clear existing users
        session.query(User).delete()
        session.commit()

        # Create mock accounts
        accounts = [
            {
                "email": "admin@seraaj.com",
                "password": "admin123",
                "first_name": "System",
                "last_name": "Administrator",
                "role": UserRole.ADMIN,
            },
            {
                "email": "volunteer1@demo.com",
                "password": "vol123",
                "first_name": "Fatima",
                "last_name": "Al-Zahra",
                "role": UserRole.VOLUNTEER,
            },
            {
                "email": "volunteer2@demo.com",
                "password": "vol123",
                "first_name": "Ahmed",
                "last_name": "Hassan",
                "role": UserRole.VOLUNTEER,
            },
            {
                "email": "org1@demo.com",
                "password": "org123",
                "first_name": "Organization",
                "last_name": "Manager",
                "role": UserRole.ORGANIZATION,
            },
        ]

        for account in accounts:
            user = User(
                email=account["email"],
                hashed_password=hash_password(account["password"]),
                first_name=account["first_name"],
                last_name=account["last_name"],
                role=account["role"],
                status=UserStatus.ACTIVE,
                is_verified=True,
                created_at=datetime.now(datetime.timezone.utc),
            )
            session.add(user)

        session.commit()
        print(f"Created {len(accounts)} mock accounts")

        print("\nLogin Credentials:")
        for account in accounts:
            print(
                f"  {account['email']} | {account['password']} | {account['role'].value}"
            )

    except Exception as e:
        print(f"Error creating accounts: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def main():
    """Main seeding function"""
    print("Simple Database Seeding for Seraaj v2")
    print("Creating essential mock accounts for testing...")

    # Ensure database tables exist
    create_db_and_tables()

    # Create mock accounts
    create_mock_accounts()

    print("\nSimple seeding completed!")
    print("You can now test authentication with the created accounts.")


if __name__ == "__main__":
    main()
