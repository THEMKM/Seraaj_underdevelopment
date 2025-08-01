from typing import List, Dict, Optional, Any
from sqlmodel import Session, select, and_
from datetime import datetime
import logging

from models import Volunteer, Organisation, Opportunity, Application, AnalyticsEvent
from models.opportunity import OpportunityState, TimeCommitmentType
from models.volunteer import AvailabilityType

logger = logging.getLogger(__name__)


class MatchingEngine:
    """ML-powered matching engine for volunteers and opportunities"""

    def __init__(self):
        # Feature weights (can be learned/adjusted over time)
        self.feature_weights = {
            "skill_match": 0.25,
            "location_match": 0.20,
            "availability_match": 0.15,
            "experience_match": 0.15,
            "cause_match": 0.10,
            "time_commitment_match": 0.10,
            "rating_boost": 0.05,
        }

        # Learning parameters
        self.learning_rate = 0.01
        self.decay_factor = 0.95

    def rule_based_opportunities(
        self, session: Session, volunteer_id: int, limit: int = 10
    ) -> List[Dict[str, float]]:
        """Return top opportunity matches using a simple rule-based algorithm."""

        volunteer = session.get(Volunteer, volunteer_id)
        if not volunteer:
            return []

        opportunities = session.exec(
            select(Opportunity).where(Opportunity.state == OpportunityState.ACTIVE)
        ).all()

        matches: List[Dict[str, float]] = []
        for opp in opportunities:
            score = self._rule_based_score(volunteer, opp)
            matches.append({"id": opp.id, "title": opp.title, "score": round(score * 100, 2)})

        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:limit]

    def _rule_based_score(self, volunteer: Volunteer, opportunity: Opportunity) -> float:
        """Calculate rule-based score between volunteer and opportunity."""

        # Skill overlap
        if opportunity.skills_required:
            overlap = len(set(volunteer.skills or []).intersection(opportunity.skills_required))
            skill_score = overlap / len(opportunity.skills_required)
        else:
            skill_score = 0.0

        # Location match
        if opportunity.remote_allowed:
            location_score = 1.0
        elif volunteer.country and opportunity.country and volunteer.country.lower() == opportunity.country.lower():
            if volunteer.location and opportunity.location and volunteer.location.lower() == opportunity.location.lower():
                location_score = 1.0
            else:
                location_score = 0.5
        else:
            location_score = 0.0

        # Availability match
        if volunteer.availability == opportunity.time_commitment_type:
            availability_score = 1.0
        elif (
            volunteer.availability == AvailabilityType.FLEXIBLE
            or opportunity.time_commitment_type == TimeCommitmentType.FLEXIBLE
        ):
            availability_score = 0.8
        else:
            availability_score = 0.5

        return (skill_score + location_score + availability_score) / 3

    async def find_matches(
        self,
        session: Session,
        volunteer_id: Optional[int] = None,
        opportunity_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find matches for a volunteer or opportunity"""

        if volunteer_id:
            return await self._find_opportunities_for_volunteer(
                session, volunteer_id, limit
            )
        elif opportunity_id:
            return await self._find_volunteers_for_opportunity(
                session, opportunity_id, limit
            )
        else:
            raise ValueError("Must specify either volunteer_id or opportunity_id")

    async def _find_opportunities_for_volunteer(
        self, session: Session, volunteer_id: int, limit: int
    ) -> List[Dict[str, Any]]:
        """Find best matching opportunities for a volunteer"""

        # Get volunteer profile
        volunteer = session.get(Volunteer, volunteer_id)
        if not volunteer:
            return []

        # Get active opportunities
        opportunities = session.exec(
            select(Opportunity).where(
                and_(
                    Opportunity.state == "active",
                    Opportunity.application_deadline
                    > datetime.now(datetime.timezone.utc),
                )
            )
        ).all()

        if not opportunities:
            return []

        # Calculate match scores
        matches = []
        for opportunity in opportunities:
            # Skip if already applied
            existing_application = session.exec(
                select(Application).where(
                    and_(
                        Application.volunteer_id == volunteer_id,
                        Application.opportunity_id == opportunity.id,
                    )
                )
            ).first()

            if existing_application:
                continue

            score = await self._calculate_opportunity_match_score(
                session, volunteer, opportunity
            )

            if score > 0.3:  # Minimum threshold
                matches.append(
                    {
                        "opportunity_id": opportunity.id,
                        "opportunity_title": opportunity.title,
                        "organization_name": await self._get_organization_name(
                            session, opportunity.org_id
                        ),
                        "match_score": round(score * 100, 2),
                        "match_reasons": await self._get_match_reasons(
                            session, volunteer, opportunity, score
                        ),
                        "opportunity_data": {
                            "country": opportunity.country,
                            "city": opportunity.city,
                            "causes": opportunity.causes,
                            "skills_required": opportunity.skills_required,
                            "time_commitment": opportunity.time_commitment,
                            "urgency": opportunity.urgency.value,
                            "remote_allowed": opportunity.remote_allowed,
                        },
                    }
                )

        # Sort by match score and return top matches
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:limit]

    async def _find_volunteers_for_opportunity(
        self, session: Session, opportunity_id: int, limit: int
    ) -> List[Dict[str, Any]]:
        """Find best matching volunteers for an opportunity"""

        # Get opportunity details
        opportunity = session.get(Opportunity, opportunity_id)
        if not opportunity:
            return []

        # Get active volunteers
        volunteers = session.exec(
            select(Volunteer).where(
                and_(Volunteer.available == True, Volunteer.profile_completed == True)
            )
        ).all()

        if not volunteers:
            return []

        # Calculate match scores
        matches = []
        for volunteer in volunteers:
            # Skip if already applied
            existing_application = session.exec(
                select(Application).where(
                    and_(
                        Application.volunteer_id == volunteer.id,
                        Application.opportunity_id == opportunity_id,
                    )
                )
            ).first()

            if existing_application:
                continue

            score = await self._calculate_volunteer_match_score(
                session, volunteer, opportunity
            )

            if score > 0.3:  # Minimum threshold
                matches.append(
                    {
                        "volunteer_id": volunteer.id,
                        "volunteer_name": volunteer.full_name,
                        "match_score": round(score * 100, 2),
                        "match_reasons": await self._get_volunteer_match_reasons(
                            session, volunteer, opportunity, score
                        ),
                        "volunteer_data": {
                            "country": volunteer.country,
                            "city": volunteer.city,
                            "skills": volunteer.skills,
                            "experience_level": volunteer.experience_level.value,
                            "availability": volunteer.availability.value,
                            "rating": volunteer.rating,
                            "verified": volunteer.verified,
                        },
                    }
                )

        # Sort by match score and return top matches
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:limit]

    async def _calculate_opportunity_match_score(
        self, session: Session, volunteer: Volunteer, opportunity: Opportunity
    ) -> float:
        """Calculate match score between volunteer and opportunity"""

        scores = {}

        # 1. Skill matching
        scores["skill_match"] = self._calculate_skill_match(
            volunteer.skills, opportunity.skills_required
        )

        # 2. Location matching
        scores["location_match"] = self._calculate_location_match(
            volunteer.country,
            volunteer.city,
            opportunity.country,
            opportunity.city,
            opportunity.remote_allowed,
        )

        # 3. Availability matching
        scores["availability_match"] = self._calculate_availability_match(
            volunteer.availability, opportunity.time_commitment_type
        )

        # 4. Experience matching
        scores["experience_match"] = self._calculate_experience_match(
            volunteer.experience_level, opportunity.experience_required
        )

        # 5. Cause alignment
        scores["cause_match"] = self._calculate_cause_match(
            volunteer.preferred_causes, opportunity.causes
        )

        # 6. Time commitment match
        scores["time_commitment_match"] = self._calculate_time_commitment_match(
            volunteer.time_availability, opportunity.time_commitment
        )

        # 7. Rating boost
        scores["rating_boost"] = min(volunteer.rating / 5.0, 1.0)

        # Calculate weighted score
        total_score = sum(
            scores[feature] * self.feature_weights[feature] for feature in scores.keys()
        )

        # Apply personalization based on volunteer's history
        personalization_boost = await self._calculate_personalization_boost(
            session, volunteer.user_id, opportunity
        )

        final_score = min(total_score + personalization_boost, 1.0)

        # Log match calculation for learning
        await self._log_match_calculation(
            session, volunteer.id, opportunity.id, scores, final_score
        )

        return final_score

    async def _calculate_volunteer_match_score(
        self, session: Session, volunteer: Volunteer, opportunity: Opportunity
    ) -> float:
        """Calculate match score - same logic as opportunity matching"""
        return await self._calculate_opportunity_match_score(
            session, volunteer, opportunity
        )

    def _calculate_skill_match(
        self, volunteer_skills: List[str], required_skills: List[str]
    ) -> float:
        """Calculate skill matching score"""
        if not required_skills:
            return 0.5  # Neutral if no skills required

        if not volunteer_skills:
            return 0.0

        # Convert to sets for easier comparison
        vol_skills = set(skill.lower().strip() for skill in volunteer_skills)
        req_skills = set(skill.lower().strip() for skill in required_skills)

        # Calculate intersection
        matching_skills = vol_skills.intersection(req_skills)

        # Score based on percentage of required skills matched
        if not req_skills:
            return 0.5

        match_ratio = len(matching_skills) / len(req_skills)

        # Bonus for having additional relevant skills
        additional_relevant = vol_skills - req_skills
        bonus = min(len(additional_relevant) * 0.1, 0.3)

        return min(match_ratio + bonus, 1.0)

    def _calculate_location_match(
        self,
        vol_country: str,
        vol_city: Optional[str],
        opp_country: str,
        opp_city: Optional[str],
        remote_allowed: bool,
    ) -> float:
        """Calculate location matching score"""
        if remote_allowed:
            return 1.0  # Perfect match if remote work is allowed

        if vol_country.lower() != opp_country.lower():
            return 0.0  # Different countries, no match

        if not vol_city or not opp_city:
            return 0.7  # Same country, city unknown

        if vol_city.lower() == opp_city.lower():
            return 1.0  # Same city, perfect match

        return 0.5  # Same country, different city

    def _calculate_availability_match(
        self, volunteer_availability, opportunity_time_commitment
    ) -> float:
        """Calculate availability matching score"""
        # Simplified matching logic
        availability_scores = {
            ("flexible", "flexible"): 1.0,
            ("flexible", "part_time"): 0.9,
            ("flexible", "full_time"): 0.7,
            ("part_time", "flexible"): 0.8,
            ("part_time", "part_time"): 1.0,
            ("part_time", "full_time"): 0.3,
            ("full_time", "flexible"): 0.9,
            ("full_time", "part_time"): 0.6,
            ("full_time", "full_time"): 1.0,
        }

        key = (
            volunteer_availability.value if volunteer_availability else "flexible",
            (
                opportunity_time_commitment.value
                if opportunity_time_commitment
                else "flexible"
            ),
        )

        return availability_scores.get(key, 0.5)

    def _calculate_experience_match(
        self, volunteer_experience, required_experience
    ) -> float:
        """Calculate experience level matching"""
        if not required_experience:
            return 0.8  # Good match if no specific experience required

        experience_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4,
        }

        vol_level = experience_levels.get(
            volunteer_experience.value if volunteer_experience else "beginner", 1
        )
        req_level = experience_levels.get(
            required_experience.value if required_experience else "beginner", 1
        )

        # Perfect match if levels are equal
        if vol_level == req_level:
            return 1.0

        # Good match if volunteer has higher experience
        if vol_level > req_level:
            return max(0.8 - (vol_level - req_level) * 0.1, 0.5)

        # Lower match if volunteer has less experience
        return max(0.6 - (req_level - vol_level) * 0.2, 0.1)

    def _calculate_cause_match(
        self, volunteer_causes: List[str], opportunity_causes: List[str]
    ) -> float:
        """Calculate cause alignment score"""
        if not opportunity_causes or not volunteer_causes:
            return 0.5  # Neutral if causes not specified

        vol_causes = set(cause.lower().strip() for cause in volunteer_causes)
        opp_causes = set(cause.lower().strip() for cause in opportunity_causes)

        intersection = vol_causes.intersection(opp_causes)
        union = vol_causes.union(opp_causes)

        if not union:
            return 0.5

        # Jaccard similarity
        return len(intersection) / len(union)

    def _calculate_time_commitment_match(
        self, volunteer_time: Optional[int], opportunity_time: Optional[int]
    ) -> float:
        """Calculate time commitment matching"""
        if not volunteer_time or not opportunity_time:
            return 0.6  # Neutral if time not specified

        # Calculate ratio (smaller/larger to get value <= 1)
        ratio = min(volunteer_time, opportunity_time) / max(
            volunteer_time, opportunity_time
        )

        return ratio

    async def _calculate_personalization_boost(
        self, session: Session, user_id: int, opportunity: Opportunity
    ) -> float:
        """Calculate personalization boost based on user history"""

        boost = 0.0

        # Get user's application history
        applications = session.exec(
            select(Application)
            .join(Volunteer, Application.volunteer_id == Volunteer.id)
            .where(Volunteer.user_id == user_id)
        ).all()

        if not applications:
            return boost

        # Analyze successful applications
        successful_apps = [
            app for app in applications if app.status in ["accepted", "completed"]
        ]

        if successful_apps:
            # Get opportunities from successful applications
            successful_opportunities = []
            for app in successful_apps:
                opp = session.get(Opportunity, app.opportunity_id)
                if opp:
                    successful_opportunities.append(opp)

            # Boost based on similar patterns
            for past_opp in successful_opportunities:
                # Similar causes
                if set(past_opp.causes).intersection(set(opportunity.causes)):
                    boost += 0.05

                # Similar location
                if past_opp.country == opportunity.country:
                    boost += 0.03

                # Similar organization type or size
                if past_opp.urgency == opportunity.urgency:
                    boost += 0.02

        # Penalize if user has rejected similar opportunities
        rejected_apps = [app for app in applications if app.status == "rejected"]
        for app in rejected_apps:
            past_opp = session.get(Opportunity, app.opportunity_id)
            if past_opp and set(past_opp.causes).intersection(set(opportunity.causes)):
                boost -= 0.02

        return max(min(boost, 0.2), -0.1)  # Cap boost between -0.1 and 0.2

    async def _get_match_reasons(
        self,
        session: Session,
        volunteer: Volunteer,
        opportunity: Opportunity,
        total_score: float,
    ) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []

        # Skill matches
        matching_skills = set(volunteer.skills).intersection(
            set(opportunity.skills_required)
        )
        if matching_skills:
            reasons.append(f"Skills match: {', '.join(list(matching_skills)[:3])}")

        # Location match
        if opportunity.remote_allowed:
            reasons.append("Remote work available")
        elif volunteer.country == opportunity.country:
            if volunteer.city == opportunity.city:
                reasons.append("Same city")
            else:
                reasons.append("Same country")

        # Experience match
        if volunteer.experience_level and opportunity.experience_required:
            if (
                volunteer.experience_level.value
                == opportunity.experience_required.value
            ):
                reasons.append("Perfect experience match")
            elif (
                volunteer.experience_level.value > opportunity.experience_required.value
            ):
                reasons.append("Experienced candidate")

        # Cause alignment
        matching_causes = set(volunteer.preferred_causes).intersection(
            set(opportunity.causes)
        )
        if matching_causes:
            reasons.append(f"Shared interest in {list(matching_causes)[0]}")

        # High rating
        if volunteer.rating >= 4.5:
            reasons.append("Highly rated volunteer")

        # Availability
        if volunteer.available:
            reasons.append("Currently available")

        return reasons[:4]  # Return top 4 reasons

    async def _get_volunteer_match_reasons(
        self,
        session: Session,
        volunteer: Volunteer,
        opportunity: Opportunity,
        total_score: float,
    ) -> List[str]:
        """Generate match reasons from organization perspective"""
        return await self._get_match_reasons(
            session, volunteer, opportunity, total_score
        )

    async def _get_organization_name(self, session: Session, org_id: int) -> str:
        """Get organization name"""
        org = session.get(Organisation, org_id)
        return org.name if org else "Unknown Organization"

    async def _log_match_calculation(
        self,
        session: Session,
        volunteer_id: int,
        opportunity_id: int,
        feature_scores: Dict[str, float],
        final_score: float,
    ):
        """Log match calculation for learning purposes"""
        try:
            # Create analytics event
            event = AnalyticsEvent(
                event_type="match_calculated",
                user_id=None,  # System event
                data={
                    "volunteer_id": volunteer_id,
                    "opportunity_id": opportunity_id,
                    "feature_scores": feature_scores,
                    "final_score": final_score,
                    "feature_weights": self.feature_weights,
                },
            )

            session.add(event)
            session.commit()
        except Exception as e:
            logger.error(f"Error logging match calculation: {e}")

    async def learn_from_feedback(
        self,
        session: Session,
        volunteer_id: int,
        opportunity_id: int,
        feedback_type: str,  # 'applied', 'rejected', 'accepted', 'completed'
        feedback_score: Optional[float] = None,
    ):
        """Learn from user feedback to improve matching"""

        try:
            # Get the original match calculation
            match_event = session.exec(
                select(AnalyticsEvent).where(
                    and_(
                        AnalyticsEvent.event_type == "match_calculated",
                        AnalyticsEvent.data.op("->>")(["volunteer_id"])
                        == str(volunteer_id),
                        AnalyticsEvent.data.op("->>")(["opportunity_id"])
                        == str(opportunity_id),
                    )
                )
            ).first()

            if not match_event:
                return

            # Extract original scores
            original_data = match_event.data
            feature_scores = original_data.get("feature_scores", {})
            predicted_score = original_data.get("final_score", 0.5)

            # Determine actual outcome score
            outcome_scores = {
                "applied": 0.8,  # User applied - good match
                "rejected": 0.2,  # User rejected - poor match
                "accepted": 0.9,  # Organization accepted - great match
                "completed": 1.0,  # Successfully completed - perfect match
            }

            actual_score = outcome_scores.get(feedback_type, 0.5)
            if feedback_score:
                actual_score = feedback_score

            # Calculate prediction error
            error = actual_score - predicted_score

            # Update feature weights based on error
            for feature, score in feature_scores.items():
                if feature in self.feature_weights:
                    # Increase weight if feature contributed to correct prediction
                    # Decrease weight if feature led to incorrect prediction
                    contribution = score * self.feature_weights[feature]
                    weight_adjustment = self.learning_rate * error * contribution

                    self.feature_weights[feature] += weight_adjustment

                    # Keep weights positive and normalized
                    self.feature_weights[feature] = max(
                        0.01, self.feature_weights[feature]
                    )

            # Normalize weights to sum to 1
            total_weight = sum(self.feature_weights.values())
            for feature in self.feature_weights:
                self.feature_weights[feature] /= total_weight

            # Log learning event
            learning_event = AnalyticsEvent(
                event_type="matching_learned",
                user_id=None,
                data={
                    "volunteer_id": volunteer_id,
                    "opportunity_id": opportunity_id,
                    "feedback_type": feedback_type,
                    "predicted_score": predicted_score,
                    "actual_score": actual_score,
                    "error": error,
                    "updated_weights": self.feature_weights.copy(),
                },
            )

            session.add(learning_event)
            session.commit()

            logger.info(f"Updated matching weights based on {feedback_type} feedback")

        except Exception as e:
            logger.error(f"Error in learning from feedback: {e}")

    def get_feature_weights(self) -> Dict[str, float]:
        """Get current feature weights"""
        return self.feature_weights.copy()

    def update_feature_weights(self, new_weights: Dict[str, float]):
        """Update feature weights (for admin configuration)"""
        # Validate weights
        if not all(w >= 0 for w in new_weights.values()):
            raise ValueError("All weights must be non-negative")

        # Normalize weights
        total = sum(new_weights.values())
        if total > 0:
            for feature in new_weights:
                new_weights[feature] /= total

        self.feature_weights.update(new_weights)


# Global matching engine instance
matching_engine = MatchingEngine()
