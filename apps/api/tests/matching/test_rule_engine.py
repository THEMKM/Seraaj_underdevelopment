import asyncio
from datetime import date, timedelta

from sqlmodel import Session

from models import (
    User,
    UserRole,
    Volunteer,
    Organisation,
    Opportunity,
    OpportunityState,
    TimeCommitmentType,
)
from models.volunteer import AvailabilityType
from ml.matching_engine import matching_engine


def _create_user(session: Session, role: UserRole) -> User:
    user = User(
        email=f"{role}@test.com",
        hashed_password="x",
        first_name="T",
        last_name="U",
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _create_volunteer(session: Session, user: User) -> Volunteer:
    volunteer = Volunteer(
        user_id=user.id,
        full_name="Tester",
        skills=["python", "design"],
        country="CountryA",
        location="CityA",
        availability=AvailabilityType.FULL_TIME,
    )
    session.add(volunteer)
    session.commit()
    session.refresh(volunteer)
    return volunteer


def _create_org(session: Session, user: User) -> Organisation:
    org = Organisation(user_id=user.id, name="Org", email="org@test.com")
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


def _create_opportunity(
    session: Session,
    org: Organisation,
    title: str,
    skills: list[str],
    country: str,
    city: str,
    remote: bool,
    commitment: TimeCommitmentType,
) -> Opportunity:
    opp = Opportunity(
        org_id=org.id,
        title=title,
        description="d",
        skills_required=skills,
        country=country,
        location=city,
        remote_allowed=remote,
        time_commitment_type=commitment,
        state=OpportunityState.ACTIVE,
        application_deadline=date.today() + timedelta(days=10),
    )
    session.add(opp)
    session.commit()
    session.refresh(opp)
    return opp


def test_rule_based_order(session: Session):
    vol_user = _create_user(session, UserRole.VOLUNTEER)
    volunteer = _create_volunteer(session, vol_user)
    org_user = _create_user(session, UserRole.ORGANIZATION)
    org = _create_org(session, org_user)

    opp1 = _create_opportunity(
        session,
        org,
        "Perfect Match",
        ["python"],
        "CountryA",
        "CityA",
        False,
        TimeCommitmentType.FULL_TIME,
    )
    opp2 = _create_opportunity(
        session,
        org,
        "Partial Match",
        ["python"],
        "CountryA",
        "CityB",
        False,
        TimeCommitmentType.PART_TIME,
    )
    opp3 = _create_opportunity(
        session,
        org,
        "Remote",
        ["marketing"],
        "CountryB",
        "CityZ",
        True,
        TimeCommitmentType.WEEKLY,
    )

    matches = matching_engine.rule_based_opportunities(session, volunteer.id, limit=3)
    ids = [m["id"] for m in matches]
    assert ids[0] == opp1.id
    assert len(matches) == 3


def test_rule_based_runtime(session: Session, performance_timer):
    vol_user = _create_user(session, UserRole.VOLUNTEER)
    volunteer = _create_volunteer(session, vol_user)
    org_user = _create_user(session, UserRole.ORGANIZATION)
    org = _create_org(session, org_user)

    for i in range(1000):
        _create_opportunity(
            session,
            org,
            f"Opp {i}",
            ["python" if i % 2 == 0 else "design"],
            "CountryA",
            "CityA",
            False,
            TimeCommitmentType.FULL_TIME,
        )

    performance_timer.start()
    matching_engine.rule_based_opportunities(session, volunteer.id, limit=5)
    performance_timer.stop()
    assert performance_timer.elapsed < 0.1
