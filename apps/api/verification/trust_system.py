from typing import List, Dict, Optional, Any, Tuple
from sqlmodel import Session, select, and_, or_, func
from datetime import datetime, timedelta
import json
import logging
from enum import Enum
import hashlib

from models import (
    User, Organisation, Opportunity, Application, Review, 
    AnalyticsEvent, Badge, UserBadge
)

logger = logging.getLogger(__name__)


class TrustLevel(str, Enum):
    """Organization trust levels"""
    UNVERIFIED = "unverified"
    BASIC = "basic"
    VERIFIED = "verified"
    PREMIUM = "premium"
    GOLD = "gold"
    PLATINUM = "platinum"


class VerificationBadge(str, Enum):
    """Types of verification badges organizations can earn"""
    REGISTERED_NONPROFIT = "registered_nonprofit"
    TAX_EXEMPT_STATUS = "tax_exempt_status"
    FINANCIAL_TRANSPARENCY = "financial_transparency"
    LEADERSHIP_VERIFIED = "leadership_verified"
    IMPACT_DOCUMENTED = "impact_documented"
    VOLUNTEER_ENDORSED = "volunteer_endorsed"
    COMMUNITY_RECOGNIZED = "community_recognized"
    LONG_STANDING = "long_standing"
    HIGH_ENGAGEMENT = "high_engagement"
    EXCELLENCE_AWARD = "excellence_award"


class TrustFactor(str, Enum):
    """Factors that contribute to trust score"""
    REGISTRATION_STATUS = "registration_status"
    FINANCIAL_TRANSPARENCY = "financial_transparency"
    VOLUNTEER_FEEDBACK = "volunteer_feedback"
    COMMUNITY_IMPACT = "community_impact"
    LEADERSHIP_CREDIBILITY = "leadership_credibility"
    OPERATIONAL_HISTORY = "operational_history"
    EXTERNAL_ENDORSEMENTS = "external_endorsements"
    PLATFORM_ENGAGEMENT = "platform_engagement"
    COMPLIANCE_RECORD = "compliance_record"
    INNOVATION_LEADERSHIP = "innovation_leadership"


class OrganizationTrustSystem:
    """Advanced trust and verification system for organizations"""
    
    def __init__(self):
        # Trust score weights for different factors
        self.trust_weights = {
            TrustFactor.REGISTRATION_STATUS: 0.20,
            TrustFactor.FINANCIAL_TRANSPARENCY: 0.15,
            TrustFactor.VOLUNTEER_FEEDBACK: 0.15,
            TrustFactor.COMMUNITY_IMPACT: 0.12,
            TrustFactor.LEADERSHIP_CREDIBILITY: 0.10,
            TrustFactor.OPERATIONAL_HISTORY: 0.08,
            TrustFactor.EXTERNAL_ENDORSEMENTS: 0.08,
            TrustFactor.PLATFORM_ENGAGEMENT: 0.07,
            TrustFactor.COMPLIANCE_RECORD: 0.03,
            TrustFactor.INNOVATION_LEADERSHIP: 0.02
        }
        
        # Trust level thresholds
        self.trust_thresholds = {
            TrustLevel.UNVERIFIED: 0.0,
            TrustLevel.BASIC: 0.3,
            TrustLevel.VERIFIED: 0.6,
            TrustLevel.PREMIUM: 0.75,
            TrustLevel.GOLD: 0.85,
            TrustLevel.PLATINUM: 0.95
        }
        
        # Badge criteria and requirements
        self.badge_criteria = self._initialize_badge_criteria()
    
    def _initialize_badge_criteria(self) -> Dict[str, Dict]:
        """Initialize verification badge criteria"""
        return {
            VerificationBadge.REGISTERED_NONPROFIT.value: {
                "name": "Registered Nonprofit",
                "description": "Officially registered as a nonprofit organization",
                "criteria": {
                    "registration_documents": True,
                    "legal_status_verified": True,
                    "registration_date_min_months": 6
                },
                "trust_boost": 0.15,
                "auto_verifiable": True
            },
            VerificationBadge.TAX_EXEMPT_STATUS.value: {
                "name": "Tax Exempt",
                "description": "Recognized tax-exempt status by relevant authorities",
                "criteria": {
                    "tax_exempt_certificate": True,
                    "annual_filings_current": True
                },
                "trust_boost": 0.12,
                "auto_verifiable": True
            },
            VerificationBadge.FINANCIAL_TRANSPARENCY.value: {
                "name": "Financial Transparency",
                "description": "Publicly available financial reports and transparency",
                "criteria": {
                    "annual_reports_published": 2,
                    "financial_statements_current": True,
                    "expense_ratios_disclosed": True
                },
                "trust_boost": 0.10,
                "auto_verifiable": False
            },
            VerificationBadge.LEADERSHIP_VERIFIED.value: {
                "name": "Leadership Verified",
                "description": "Organization leadership credentials verified",
                "criteria": {
                    "leadership_bios_complete": True,
                    "background_checks_completed": True,
                    "references_verified": 3
                },
                "trust_boost": 0.08,
                "auto_verifiable": False
            },
            VerificationBadge.IMPACT_DOCUMENTED.value: {
                "name": "Impact Documented",
                "description": "Clear documentation of community impact and outcomes",
                "criteria": {
                    "impact_reports_published": 2,
                    "beneficiary_testimonials": 10,
                    "measurable_outcomes": True
                },
                "trust_boost": 0.08,
                "auto_verifiable": False
            },
            VerificationBadge.VOLUNTEER_ENDORSED.value: {
                "name": "Volunteer Endorsed",
                "description": "Highly rated by volunteers with consistent positive feedback",
                "criteria": {
                    "min_volunteer_reviews": 25,
                    "min_average_rating": 4.5,
                    "volunteer_retention_rate": 0.8
                },
                "trust_boost": 0.10,
                "auto_verifiable": True
            },
            VerificationBadge.COMMUNITY_RECOGNIZED.value: {
                "name": "Community Recognized",
                "description": "Recognized by community leaders and partner organizations",
                "criteria": {
                    "community_endorsements": 5,
                    "media_mentions": 3,
                    "partnership_agreements": 2
                },
                "trust_boost": 0.06,
                "auto_verifiable": False
            },
            VerificationBadge.LONG_STANDING.value: {
                "name": "Long Standing",
                "description": "Established organization with proven track record",
                "criteria": {
                    "years_in_operation": 5,
                    "platform_tenure_months": 12,
                    "consistent_activity": True
                },
                "trust_boost": 0.05,
                "auto_verifiable": True
            },
            VerificationBadge.HIGH_ENGAGEMENT.value: {
                "name": "High Engagement",
                "description": "Actively engages with volunteers and maintains high activity",
                "criteria": {
                    "opportunities_posted_yearly": 12,
                    "volunteer_response_rate": 0.9,
                    "platform_activity_score": 0.8
                },
                "trust_boost": 0.05,
                "auto_verifiable": True
            },
            VerificationBadge.EXCELLENCE_AWARD.value: {
                "name": "Excellence Award",
                "description": "Recognized for outstanding contribution to the community",
                "criteria": {
                    "external_awards": 1,
                    "exceptional_impact_score": 0.95,
                    "volunteer_satisfaction": 0.95
                },
                "trust_boost": 0.15,
                "auto_verifiable": False
            }
        }
    
    async def calculate_trust_score(
        self,
        session: Session,
        organization_id: int
    ) -> Dict[str, Any]:
        """Calculate comprehensive trust score for an organization"""
        
        organization = session.get(Organisation, organization_id)
        if not organization:
            raise ValueError("Organization not found")
        
        trust_factors = {}
        
        # 1. Registration Status (20%)
        trust_factors[TrustFactor.REGISTRATION_STATUS] = self._evaluate_registration_status(
            session, organization
        )
        
        # 2. Financial Transparency (15%)
        trust_factors[TrustFactor.FINANCIAL_TRANSPARENCY] = self._evaluate_financial_transparency(
            session, organization
        )
        
        # 3. Volunteer Feedback (15%)
        trust_factors[TrustFactor.VOLUNTEER_FEEDBACK] = await self._evaluate_volunteer_feedback(
            session, organization_id
        )
        
        # 4. Community Impact (12%)
        trust_factors[TrustFactor.COMMUNITY_IMPACT] = self._evaluate_community_impact(
            session, organization
        )
        
        # 5. Leadership Credibility (10%)
        trust_factors[TrustFactor.LEADERSHIP_CREDIBILITY] = self._evaluate_leadership_credibility(
            session, organization
        )
        
        # 6. Operational History (8%)
        trust_factors[TrustFactor.OPERATIONAL_HISTORY] = self._evaluate_operational_history(
            session, organization
        )
        
        # 7. External Endorsements (8%)
        trust_factors[TrustFactor.EXTERNAL_ENDORSEMENTS] = self._evaluate_external_endorsements(
            session, organization
        )
        
        # 8. Platform Engagement (7%)
        trust_factors[TrustFactor.PLATFORM_ENGAGEMENT] = await self._evaluate_platform_engagement(
            session, organization_id
        )
        
        # 9. Compliance Record (3%)
        trust_factors[TrustFactor.COMPLIANCE_RECORD] = self._evaluate_compliance_record(
            session, organization
        )
        
        # 10. Innovation Leadership (2%)
        trust_factors[TrustFactor.INNOVATION_LEADERSHIP] = self._evaluate_innovation_leadership(
            session, organization
        )
        
        # Calculate weighted trust score
        total_score = sum(
            trust_factors[factor] * self.trust_weights[factor]
            for factor in trust_factors.keys()
        )
        
        # Apply badge bonuses
        badge_bonus = await self._calculate_badge_bonus(session, organization_id)
        final_score = min(total_score + badge_bonus, 1.0)
        
        # Determine trust level
        trust_level = self._determine_trust_level(final_score)
        
        # Update organization trust score
        organization.trust_score = final_score
        organization.trust_level = trust_level.value
        organization.trust_last_updated = datetime.now(datetime.timezone.utc)
        
        session.add(organization)
        session.commit()
        
        # Log trust calculation
        await self._log_trust_calculation(
            session, organization_id, trust_factors, final_score, trust_level
        )
        
        return {
            "organization_id": organization_id,
            "trust_score": round(final_score, 3),
            "trust_level": trust_level.value,
            "trust_factors": {factor.value: round(score, 3) for factor, score in trust_factors.items()},
            "badge_bonus": round(badge_bonus, 3),
            "calculated_at": datetime.now(datetime.timezone.utc).isoformat()
        }
    
    def _evaluate_registration_status(self, session: Session, organization: Organisation) -> float:
        """Evaluate organization registration and legal status"""
        score = 0.0
        
        # Basic registration
        if organization.verified:
            score += 0.4
        
        # Registration age (older = more trust)
        if organization.created_at:
            age_months = (datetime.now(datetime.timezone.utc) - organization.created_at).days / 30
            if age_months >= 12:
                score += 0.3
            elif age_months >= 6:
                score += 0.2
            else:
                score += 0.1
        
        # Legal documentation
        metadata = organization.metadata or {}
        if metadata.get("legal_documents_verified"):
            score += 0.2
        
        if metadata.get("tax_id_verified"):
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_financial_transparency(self, session: Session, organization: Organisation) -> float:
        """Evaluate financial transparency and reporting"""
        score = 0.0
        metadata = organization.metadata or {}
        
        # Annual reports published
        annual_reports = metadata.get("annual_reports_count", 0)
        if annual_reports >= 3:
            score += 0.4
        elif annual_reports >= 2:
            score += 0.3
        elif annual_reports >= 1:
            score += 0.2
        
        # Financial statements current
        if metadata.get("financial_statements_current"):
            score += 0.3
        
        # Expense ratios disclosed
        if metadata.get("expense_ratios_public"):
            score += 0.2
        
        # Third-party financial rating
        financial_rating = metadata.get("third_party_rating", 0)
        if financial_rating >= 4:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _evaluate_volunteer_feedback(self, session: Session, organization_id: int) -> float:
        """Evaluate volunteer feedback and satisfaction"""
        
        # Get organization reviews
        reviews = session.exec(
            select(Review).where(Review.organisation_id == organization_id)
        ).all()
        
        if not reviews:
            return 0.3  # Neutral score for no reviews
        
        # Calculate average rating
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        rating_score = (avg_rating - 1) / 4  # Normalize 1-5 to 0-1
        
        # Review count bonus
        review_count_bonus = min(len(reviews) / 50, 0.2)  # Up to 20% bonus for 50+ reviews
        
        # Recent reviews weight more
        recent_threshold = datetime.now(datetime.timezone.utc) - timedelta(days=90)
        recent_reviews = [r for r in reviews if r.created_at >= recent_threshold]
        
        if recent_reviews:
            recent_avg = sum(r.rating for r in recent_reviews) / len(recent_reviews)
            recent_score = (recent_avg - 1) / 4
            # Weight: 70% all-time, 30% recent
            final_score = (rating_score * 0.7) + (recent_score * 0.3)
        else:
            final_score = rating_score
        
        return min(final_score + review_count_bonus, 1.0)
    
    def _evaluate_community_impact(self, session: Session, organization: Organisation) -> float:
        """Evaluate documented community impact"""
        score = 0.0
        metadata = organization.metadata or {}
        
        # Impact reports published
        impact_reports = metadata.get("impact_reports_count", 0)
        if impact_reports >= 3:
            score += 0.3
        elif impact_reports >= 2:
            score += 0.2
        elif impact_reports >= 1:
            score += 0.1
        
        # Beneficiaries served
        beneficiaries = metadata.get("beneficiaries_served", 0)
        if beneficiaries >= 1000:
            score += 0.3
        elif beneficiaries >= 500:
            score += 0.2
        elif beneficiaries >= 100:
            score += 0.1
        
        # Measurable outcomes documented
        if metadata.get("measurable_outcomes"):
            score += 0.2
        
        # Third-party impact verification
        if metadata.get("impact_verified_external"):
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_leadership_credibility(self, session: Session, organization: Organisation) -> float:
        """Evaluate leadership team credibility"""
        score = 0.0
        metadata = organization.metadata or {}
        
        # Leadership bios complete
        if metadata.get("leadership_bios_complete"):
            score += 0.3
        
        # Background checks completed
        if metadata.get("background_checks_completed"):
            score += 0.3
        
        # Professional references verified
        references = metadata.get("verified_references", 0)
        if references >= 5:
            score += 0.2
        elif references >= 3:
            score += 0.1
        
        # Leadership experience
        leadership_experience = metadata.get("avg_leadership_experience_years", 0)
        if leadership_experience >= 10:
            score += 0.2
        elif leadership_experience >= 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_operational_history(self, session: Session, organization: Organisation) -> float:
        """Evaluate operational history and consistency"""
        score = 0.0
        
        # Organization age
        if organization.created_at:
            age_years = (datetime.now(datetime.timezone.utc) - organization.created_at).days / 365
            if age_years >= 10:
                score += 0.4
            elif age_years >= 5:
                score += 0.3
            elif age_years >= 2:
                score += 0.2
            else:
                score += 0.1
        
        # Platform tenure
        age_months = (datetime.now(datetime.timezone.utc) - organization.created_at).days / 30 if organization.created_at else 0
        if age_months >= 24:
            score += 0.3
        elif age_months >= 12:
            score += 0.2
        elif age_months >= 6:
            score += 0.1
        
        # Consistent activity
        metadata = organization.metadata or {}
        if metadata.get("consistent_monthly_activity"):
            score += 0.2
        
        # Growth trajectory
        if metadata.get("positive_growth_trend"):
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_external_endorsements(self, session: Session, organization: Organisation) -> float:
        """Evaluate external endorsements and partnerships"""
        score = 0.0
        metadata = organization.metadata or {}
        
        # Community endorsements
        endorsements = metadata.get("community_endorsements", 0)
        if endorsements >= 10:
            score += 0.3
        elif endorsements >= 5:
            score += 0.2
        elif endorsements >= 2:
            score += 0.1
        
        # Media mentions
        media_mentions = metadata.get("media_mentions", 0)
        if media_mentions >= 10:
            score += 0.2
        elif media_mentions >= 5:
            score += 0.15
        elif media_mentions >= 2:
            score += 0.1
        
        # Partnership agreements
        partnerships = metadata.get("verified_partnerships", 0)
        if partnerships >= 5:
            score += 0.2
        elif partnerships >= 3:
            score += 0.15
        elif partnerships >= 1:
            score += 0.1
        
        # Awards and recognition
        awards = metadata.get("external_awards", 0)
        if awards >= 3:
            score += 0.3
        elif awards >= 1:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _evaluate_platform_engagement(self, session: Session, organization_id: int) -> float:
        """Evaluate platform engagement and activity"""
        
        # Get opportunities posted in last 12 months
        year_ago = datetime.now(datetime.timezone.utc) - timedelta(days=365)
        opportunities = session.exec(
            select(Opportunity).where(
                and_(
                    Opportunity.org_id == organization_id,
                    Opportunity.created_at >= year_ago
                )
            )
        ).all()
        
        score = 0.0
        
        # Opportunity posting frequency
        opp_count = len(opportunities)
        if opp_count >= 24:
            score += 0.3
        elif opp_count >= 12:
            score += 0.2
        elif opp_count >= 6:
            score += 0.1
        
        # Application response rate
        applications = session.exec(
            select(Application).join(Opportunity, Application.opp_id == Opportunity.id)
            .where(Opportunity.org_id == organization_id)
        ).all()
        
        if applications:
            responded_count = len([a for a in applications if a.status not in ['submitted', 'draft']])
            response_rate = responded_count / len(applications)
            
            if response_rate >= 0.9:
                score += 0.3
            elif response_rate >= 0.7:
                score += 0.2
            elif response_rate >= 0.5:
                score += 0.1
        
        # Profile completeness
        organization = session.get(Organisation, organization_id)
        if organization and organization.profile_completed:
            score += 0.2
        
        # Recent activity
        recent_activity = session.exec(
            select(AnalyticsEvent).where(
                and_(
                    AnalyticsEvent.user_id == organization.user_id,
                    AnalyticsEvent.timestamp >= datetime.now(datetime.timezone.utc) - timedelta(days=30)
                )
            )
        ).all()
        
        if len(recent_activity) >= 20:
            score += 0.2
        elif len(recent_activity) >= 10:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_compliance_record(self, session: Session, organization: Organisation) -> float:
        """Evaluate compliance and policy adherence"""
        score = 1.0  # Start with perfect score
        metadata = organization.metadata or {}
        
        # Deduct for policy violations
        policy_violations = metadata.get("policy_violations", 0)
        score -= policy_violations * 0.2
        
        # Deduct for complaints
        complaints = metadata.get("formal_complaints", 0)
        score -= complaints * 0.1
        
        # Deduct for suspended periods
        if metadata.get("account_suspended_days", 0) > 0:
            score -= 0.3
        
        return max(score, 0.0)
    
    def _evaluate_innovation_leadership(self, session: Session, organization: Organisation) -> float:
        """Evaluate innovation and thought leadership"""
        score = 0.0
        metadata = organization.metadata or {}
        
        # Innovative programs
        if metadata.get("innovative_programs_count", 0) >= 2:
            score += 0.4
        elif metadata.get("innovative_programs_count", 0) >= 1:
            score += 0.2
        
        # Thought leadership content
        if metadata.get("thought_leadership_articles", 0) >= 5:
            score += 0.3
        elif metadata.get("thought_leadership_articles", 0) >= 2:
            score += 0.2
        
        # Industry recognition
        if metadata.get("industry_recognition"):
            score += 0.3
        
        return min(score, 1.0)
    
    async def _calculate_badge_bonus(self, session: Session, organization_id: int) -> float:
        """Calculate trust bonus from earned badges"""
        
        # Get organization's badges
        user_badges = session.exec(
            select(UserBadge, Badge)
            .join(Badge, UserBadge.badge_id == Badge.id)
            .join(User, UserBadge.user_id == User.id)
            .join(Organisation, User.id == Organisation.user_id)
            .where(Organisation.id == organization_id)
        ).all()
        
        total_bonus = 0.0
        
        for user_badge, badge in user_badges:
            if badge.code in self.badge_criteria:
                badge_info = self.badge_criteria[badge.code]
                total_bonus += badge_info.get("trust_boost", 0)
        
        return min(total_bonus, 0.3)  # Cap at 30% bonus
    
    def _determine_trust_level(self, trust_score: float) -> TrustLevel:
        """Determine trust level based on score"""
        
        for level in reversed(list(TrustLevel)):
            if trust_score >= self.trust_thresholds[level]:
                return level
        
        return TrustLevel.UNVERIFIED
    
    async def check_badge_eligibility(
        self,
        session: Session,
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """Check which badges an organization is eligible for"""
        
        organization = session.get(Organisation, organization_id)
        if not organization:
            raise ValueError("Organization not found")
        
        # Get current badges
        current_badges = session.exec(
            select(UserBadge.badge_code)
            .where(UserBadge.user_id == organization.user_id)
        ).all()
        
        current_badge_codes = set(badge_code for badge_code, in current_badges)
        
        eligible_badges = []
        
        for badge_code, badge_info in self.badge_criteria.items():
            if badge_code in current_badge_codes:
                continue  # Already has this badge
            
            if await self._meets_badge_criteria(session, organization, badge_info["criteria"]):
                eligible_badges.append({
                    "badge_code": badge_code,
                    "name": badge_info["name"],
                    "description": badge_info["description"],
                    "trust_boost": badge_info["trust_boost"],
                    "auto_verifiable": badge_info["auto_verifiable"]
                })
        
        return eligible_badges
    
    async def _meets_badge_criteria(
        self,
        session: Session,
        organization: Organisation,
        criteria: Dict[str, Any]
    ) -> bool:
        """Check if organization meets specific badge criteria"""
        
        metadata = organization.metadata or {}
        
        # Check each criterion
        for criterion, required_value in criteria.items():
            
            if criterion == "registration_documents":
                if not metadata.get("registration_verified"):
                    return False
            
            elif criterion == "legal_status_verified":
                if not metadata.get("legal_status_verified"):
                    return False
            
            elif criterion == "registration_date_min_months":
                if organization.created_at:
                    months = (datetime.now(datetime.timezone.utc) - organization.created_at).days / 30
                    if months < required_value:
                        return False
                else:
                    return False
            
            elif criterion == "min_volunteer_reviews":
                review_count = session.exec(
                    select(func.count(Review.id)).where(Review.organisation_id == organization.id)
                ).first()
                if review_count < required_value:
                    return False
            
            elif criterion == "min_average_rating":
                avg_rating = session.exec(
                    select(func.avg(Review.rating)).where(Review.organisation_id == organization.id)
                ).first()
                if not avg_rating or avg_rating < required_value:
                    return False
            
            elif criterion == "years_in_operation":
                if organization.created_at:
                    years = (datetime.now(datetime.timezone.utc) - organization.created_at).days / 365
                    if years < required_value:
                        return False
                else:
                    return False
            
            # Add more criteria checks as needed
            
        return True
    
    async def award_verification_badge(
        self,
        session: Session,
        organization_id: int,
        badge_code: str,
        awarded_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Award a verification badge to an organization"""
        
        organization = session.get(Organisation, organization_id)
        if not organization:
            raise ValueError("Organization not found")
        
        if badge_code not in self.badge_criteria:
            raise ValueError(f"Unknown badge: {badge_code}")
        
        badge_info = self.badge_criteria[badge_code]
        
        # Create or get badge
        badge = session.exec(
            select(Badge).where(Badge.code == badge_code)
        ).first()
        
        if not badge:
            badge = Badge(
                code=badge_code,
                name=badge_info["name"],
                description=badge_info["description"],
                badge_type="verification",
                rarity="common",
                points_value=int(badge_info["trust_boost"] * 100)
            )
            session.add(badge)
            session.commit()
            session.refresh(badge)
        
        # Check if already awarded
        existing_badge = session.exec(
            select(UserBadge).where(
                and_(
                    UserBadge.user_id == organization.user_id,
                    UserBadge.badge_code == badge_code
                )
            )
        ).first()
        
        if existing_badge:
            raise ValueError("Badge already awarded")
        
        # Award badge
        user_badge = UserBadge(
            user_id=organization.user_id,
            badge_id=badge.id,
            badge_code=badge_code,
            earned_at=datetime.now(datetime.timezone.utc),
            evidence_data={
                "organization_id": organization_id,
                "awarded_by": awarded_by,
                "verification_type": "trust_system"
            }
        )
        
        session.add(user_badge)
        session.commit()
        
        # Recalculate trust score
        await self.calculate_trust_score(session, organization_id)
        
        # Log badge award
        await self._log_trust_event(
            session, "badge_awarded", organization_id, 
            {"badge_code": badge_code, "awarded_by": awarded_by}
        )
        
        logger.info(f"Verification badge '{badge_code}' awarded to organization {organization_id}")
        
        return {
            "badge_code": badge_code,
            "name": badge_info["name"],
            "description": badge_info["description"],
            "awarded_at": user_badge.earned_at.isoformat(),
            "trust_boost": badge_info["trust_boost"]
        }
    
    async def _log_trust_calculation(
        self,
        session: Session,
        organization_id: int,
        trust_factors: Dict[TrustFactor, float],
        final_score: float,
        trust_level: TrustLevel
    ):
        """Log trust score calculation for auditing"""
        
        try:
            event = AnalyticsEvent(
                event_type="trust_score_calculated",
                user_id=None,  # System event
                data={
                    "organization_id": organization_id,
                    "trust_factors": {factor.value: score for factor, score in trust_factors.items()},
                    "final_score": final_score,
                    "trust_level": trust_level.value,
                    "timestamp": datetime.now(datetime.timezone.utc).isoformat()
                }
            )
            
            session.add(event)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error logging trust calculation: {e}")
    
    async def _log_trust_event(
        self,
        session: Session,
        event_type: str,
        organization_id: int,
        event_data: Dict[str, Any]
    ):
        """Log trust-related events"""
        
        try:
            event = AnalyticsEvent(
                event_type=f"trust_{event_type}",
                user_id=None,
                data={
                    "organization_id": organization_id,
                    **event_data,
                    "timestamp": datetime.now(datetime.timezone.utc).isoformat()
                }
            )
            
            session.add(event)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error logging trust event: {e}")
    
    def get_trust_system_stats(self, session: Session) -> Dict[str, Any]:
        """Get trust system statistics"""
        
        # Organization distribution by trust level
        trust_distribution = session.exec(
            select(Organisation.trust_level, func.count(Organisation.id))
            .group_by(Organisation.trust_level)
        ).all()
        
        # Average trust score
        avg_trust_score = session.exec(
            select(func.avg(Organisation.trust_score))
        ).first()
        
        # Badge distribution
        badge_distribution = session.exec(
            select(Badge.code, func.count(UserBadge.id))
            .join(UserBadge, Badge.id == UserBadge.badge_id)
            .where(Badge.badge_type == "verification")
            .group_by(Badge.code)
        ).all()
        
        return {
            "trust_level_distribution": dict(trust_distribution),
            "average_trust_score": round(float(avg_trust_score or 0), 3),
            "badge_distribution": dict(badge_distribution),
            "trust_weights": {factor.value: weight for factor, weight in self.trust_weights.items()},
            "trust_thresholds": {level.value: threshold for level, threshold in self.trust_thresholds.items()}
        }


# Global trust system instance
trust_system = OrganizationTrustSystem()