from sqlmodel import Session, select, func
from models import AnalyticsEvent, AnalyticsEventCreate, User, Opportunity, Application

class AnalyticsService:
    """Service for recording events and retrieving analytics metrics."""

    def record_event(self, session: Session, event: AnalyticsEventCreate) -> AnalyticsEvent:
        event_model = AnalyticsEvent(**event.model_dump())
        session.add(event_model)
        session.commit()
        session.refresh(event_model)
        return event_model

    def get_platform_counts(self, session: Session) -> dict:
        return {
            "total_users": session.exec(select(func.count(User.id))).first() or 0,
            "total_opportunities": session.exec(select(func.count(Opportunity.id))).first() or 0,
            "total_applications": session.exec(select(func.count(Application.id))).first() or 0,
            "total_events": session.exec(select(func.count(AnalyticsEvent.id))).first() or 0,
        }
