import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from apps.api.services.unified_seeding_service import UnifiedSeedingService
from apps.api.models import User

@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.seeding
@pytest.mark.slow
def test_idempotent_seed(session, monkeypatch):
    monkeypatch.setattr("apps.api.services.unified_seeding_service.get_session", lambda: iter([session]))
    seeder = UnifiedSeedingService()
    first = seeder.seed_all_data(clear_existing=True)
    users_first = len(session.exec(select(User)).all())
    second = seeder.seed_all_data(clear_existing=False)
    users_second = len(session.exec(select(User)).all())
    assert users_first == users_second
    assert second["status"] == "skipped"
