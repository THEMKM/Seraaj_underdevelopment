import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from apps.api.services.unified_seeding_service import UnifiedSeedingService

@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_seed_all(session, monkeypatch):
    # Patch get_session to use in-memory session
    monkeypatch.setattr("apps.api.services.unified_seeding_service.get_session", lambda: iter([session]))
    seeder = UnifiedSeedingService()
    results = seeder.seed_all_data(clear_existing=True)
    assert results["total_volunteers"] >= 15
    assert results["total_organizations"] >= 3
    assert results["opportunities"] >= 30
