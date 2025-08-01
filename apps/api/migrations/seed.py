"""Simple seed for development"""

# ruff: noqa: E402

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))  # noqa: E402

from auth.password_utils import hash_password
from database import create_db_and_tables, get_session
from models import (
    User,
    UserRole,
    UserStatus,
    Organisation,
    TeamSizeRange,
    OrganizationType,
    Volunteer,
    Opportunity,
    OpportunityState,
)


def seed():
    create_db_and_tables()
    session = next(get_session())
    session.query(Opportunity).delete()
    session.query(Organisation).delete()
    session.query(Volunteer).delete()
    session.query(User).delete()
    session.commit()

    vol_user = User(
        email="volunteer@example.com",
        hashed_password=hash_password("Demo123!"),
        first_name="Demo",
        last_name="Volunteer",
        role=UserRole.VOLUNTEER,
        status=UserStatus.ACTIVE,
        is_verified=True,
        email_verified=True,
        login_count=1,
        language_preference="en",
        theme_preference="light",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    org_user = User(
        email="org@example.com",
        hashed_password=hash_password("Demo123!"),
        first_name="Demo",
        last_name="Org",
        role=UserRole.ORGANIZATION,
        status=UserStatus.ACTIVE,
        is_verified=True,
        email_verified=True,
        login_count=1,
        language_preference="en",
        theme_preference="light",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add_all([vol_user, org_user])
    session.commit()

    volunteer = Volunteer(user_id=vol_user.id, full_name="Demo Volunteer")
    organisation = Organisation(
        user_id=org_user.id,
        name="Demo Org",
        email="org@example.com",
        team_size=TeamSizeRange.SMALL,
        organization_type=OrganizationType.NGO,
    )
    session.add_all([volunteer, organisation])
    session.commit()

    opportunity = Opportunity(
        org_id=organisation.id,
        title="Demo Opportunity",
        description="Demo",
        state=OpportunityState.ACTIVE,
    )
    session.add(opportunity)
    session.commit()
    session.close()


if __name__ == "__main__":
    seed()
