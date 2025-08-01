from typing import Dict, Optional, Any
from sqlmodel import Session, select, and_
from datetime import datetime
import logging
from enum import Enum
import uuid

from models import (
    Volunteer,
    SkillVerification,
    Badge,
    UserBadge,
    AnalyticsEvent,
    Application,
)

logger = logging.getLogger(__name__)


class VerificationMethod(str, Enum):
    """Available skill verification methods"""

    ASSESSMENT_TEST = "assessment_test"
    PORTFOLIO_REVIEW = "portfolio_review"
    PEER_ENDORSEMENT = "peer_endorsement"
    CERTIFICATE_UPLOAD = "certificate_upload"
    PRACTICAL_DEMONSTRATION = "practical_demonstration"
    INTERVIEW_ASSESSMENT = "interview_assessment"
    WORK_SAMPLE = "work_sample"
    COMMUNITY_VALIDATION = "community_validation"


class VerificationStatus(str, Enum):
    """Verification status options"""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CHALLENGED = "challenged"


class BadgeType(str, Enum):
    """Types of badges that can be earned"""

    SKILL_MASTERY = "skill_mastery"
    EXPERIENCE_LEVEL = "experience_level"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    RELIABILITY = "reliability"
    EXPERTISE_RECOGNITION = "expertise_recognition"
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    SPECIAL_RECOGNITION = "special_recognition"


class SkillVerificationEngine:
    """Advanced skill verification and badge management system"""

    def __init__(self):
        # Verification scoring weights
        self.verification_weights = {
            VerificationMethod.ASSESSMENT_TEST: 0.25,
            VerificationMethod.PORTFOLIO_REVIEW: 0.20,
            VerificationMethod.PEER_ENDORSEMENT: 0.15,
            VerificationMethod.CERTIFICATE_UPLOAD: 0.15,
            VerificationMethod.PRACTICAL_DEMONSTRATION: 0.10,
            VerificationMethod.INTERVIEW_ASSESSMENT: 0.08,
            VerificationMethod.WORK_SAMPLE: 0.05,
            VerificationMethod.COMMUNITY_VALIDATION: 0.02,
        }

        # Minimum scores for verification levels
        self.verification_thresholds = {
            "basic": 0.3,
            "intermediate": 0.6,
            "advanced": 0.8,
            "expert": 0.95,
        }

        # Badge criteria definitions
        self.badge_criteria = self._initialize_badge_criteria()

    def _initialize_badge_criteria(self) -> Dict[str, Dict]:
        """Initialize badge earning criteria"""
        return {
            "skill_master": {
                "type": BadgeType.SKILL_MASTERY,
                "name": "Skill Master",
                "description": "Achieved expert-level verification in a skill",
                "criteria": {
                    "min_verification_score": 0.9,
                    "required_methods": [
                        VerificationMethod.ASSESSMENT_TEST,
                        VerificationMethod.PORTFOLIO_REVIEW,
                    ],
                    "peer_endorsements": 3,
                },
                "rarity": "rare",
                "points": 100,
            },
            "multi_skilled": {
                "type": BadgeType.SKILL_MASTERY,
                "name": "Multi-Skilled Professional",
                "description": "Verified in 5+ different skills",
                "criteria": {"verified_skills_count": 5, "min_avg_score": 0.7},
                "rarity": "uncommon",
                "points": 75,
            },
            "reliable_volunteer": {
                "type": BadgeType.RELIABILITY,
                "name": "Reliable Volunteer",
                "description": "Consistently delivers high-quality work",
                "criteria": {
                    "completed_applications": 10,
                    "min_average_rating": 4.5,
                    "completion_rate": 0.9,
                },
                "rarity": "common",
                "points": 50,
            },
            "community_champion": {
                "type": BadgeType.COMMUNITY_CONTRIBUTION,
                "name": "Community Champion",
                "description": "Active community contributor and mentor",
                "criteria": {
                    "peer_endorsements_given": 20,
                    "community_hours": 100,
                    "mentorship_sessions": 5,
                },
                "rarity": "rare",
                "points": 120,
            },
            "expert_recognized": {
                "type": BadgeType.EXPERTISE_RECOGNITION,
                "name": "Expert Recognized",
                "description": "Recognized as an expert by organizations",
                "criteria": {
                    "organization_endorsements": 3,
                    "expert_level_verifications": 2,
                    "min_experience_years": 5,
                },
                "rarity": "legendary",
                "points": 200,
            },
            "quick_learner": {
                "type": BadgeType.ACHIEVEMENT,
                "name": "Quick Learner",
                "description": "Rapidly acquired and verified new skills",
                "criteria": {
                    "skills_verified_30_days": 3,
                    "assessment_completion_time": "fast",
                },
                "rarity": "uncommon",
                "points": 60,
            },
            "veteran_volunteer": {
                "type": BadgeType.MILESTONE,
                "name": "Veteran Volunteer",
                "description": "Long-standing community member",
                "criteria": {
                    "platform_tenure_months": 24,
                    "total_volunteer_hours": 500,
                    "active_months_ratio": 0.8,
                },
                "rarity": "rare",
                "points": 150,
            },
        }

    async def initiate_skill_verification(
        self,
        session: Session,
        volunteer_id: int,
        skill_name: str,
        verification_method: VerificationMethod,
        evidence_data: Dict[str, Any],
        requested_by: int,
    ) -> SkillVerification:
        """Start a new skill verification process"""

        # Check if verification already exists for this skill
        existing_verification = session.exec(
            select(SkillVerification).where(
                and_(
                    SkillVerification.volunteer_id == volunteer_id,
                    SkillVerification.skill_name == skill_name,
                    SkillVerification.status.in_(
                        [VerificationStatus.PENDING, VerificationStatus.IN_REVIEW]
                    ),
                )
            )
        ).first()

        if existing_verification:
            raise ValueError(
                f"Active verification already exists for skill: {skill_name}"
            )

        # Create verification record
        verification = SkillVerification(
            volunteer_id=volunteer_id,
            skill_name=skill_name,
            verification_method=verification_method,
            evidence_data=evidence_data,
            status=VerificationStatus.PENDING,
            requested_by=requested_by,
            verification_id=str(uuid.uuid4()),
        )

        session.add(verification)
        session.commit()
        session.refresh(verification)

        # Log verification initiation
        await self._log_verification_event(
            session,
            verification.id,
            "verification_initiated",
            {"method": verification_method.value, "skill": skill_name},
        )

        # Auto-process certain verification types
        if verification_method in [
            VerificationMethod.CERTIFICATE_UPLOAD,
            VerificationMethod.WORK_SAMPLE,
        ]:
            await self._auto_process_verification(session, verification)

        logger.info(
            f"Skill verification initiated: {skill_name} for volunteer {volunteer_id}"
        )
        return verification

    async def _auto_process_verification(
        self, session: Session, verification: SkillVerification
    ):
        """Automatically process certain types of verifications"""

        if verification.verification_method == VerificationMethod.CERTIFICATE_UPLOAD:
            # Basic certificate validation
            score = await self._validate_certificate(verification.evidence_data)

        elif verification.verification_method == VerificationMethod.WORK_SAMPLE:
            # Basic work sample validation
            score = await self._validate_work_sample(verification.evidence_data)

        else:
            return  # Manual processing required

        # Update verification with auto-calculated score
        verification.verification_score = score
        verification.status = (
            VerificationStatus.VERIFIED if score >= 0.7 else VerificationStatus.REJECTED
        )
        verification.verified_at = datetime.now(datetime.timezone.utc)
        verification.verified_by = None  # System verification

        session.add(verification)
        session.commit()

        if verification.status == VerificationStatus.VERIFIED:
            await self._update_volunteer_skills(session, verification)
            await self._check_badge_eligibility(session, verification.volunteer_id)

    async def _validate_certificate(self, evidence_data: Dict) -> float:
        """Validate uploaded certificate"""
        score = 0.5  # Base score

        # Check certificate details
        if evidence_data.get("issuing_organization"):
            score += 0.2

        if evidence_data.get("issue_date"):
            # Recent certificates get higher scores
            issue_date = datetime.fromisoformat(evidence_data["issue_date"])
            months_old = (datetime.now(datetime.timezone.utc) - issue_date).days / 30
            if months_old <= 12:
                score += 0.2
            elif months_old <= 36:
                score += 0.1

        if evidence_data.get("verification_url"):
            score += 0.1

        return min(score, 1.0)

    async def _validate_work_sample(self, evidence_data: Dict) -> float:
        """Validate work sample submission"""
        score = 0.4  # Base score

        # Check work sample completeness
        if evidence_data.get("description"):
            score += 0.1

        if evidence_data.get("technologies_used"):
            score += 0.1

        if evidence_data.get("project_duration"):
            score += 0.1

        if evidence_data.get("outcomes_achieved"):
            score += 0.1

        if evidence_data.get("file_attachments"):
            file_count = len(evidence_data["file_attachments"])
            score += min(file_count * 0.05, 0.2)

        return min(score, 1.0)

    async def process_peer_endorsement(
        self,
        session: Session,
        verification_id: int,
        endorser_id: int,
        endorsement_data: Dict[str, Any],
    ) -> bool:
        """Process a peer endorsement for skill verification"""

        verification = session.get(SkillVerification, verification_id)
        if not verification:
            raise ValueError("Verification not found")

        # Verify endorser is qualified to endorse this skill
        endorser_volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == endorser_id)
        ).first()

        if not endorser_volunteer:
            raise ValueError("Endorser must be a verified volunteer")

        # Check if endorser has this skill verified
        endorser_verification = session.exec(
            select(SkillVerification).where(
                and_(
                    SkillVerification.volunteer_id == endorser_volunteer.id,
                    SkillVerification.skill_name == verification.skill_name,
                    SkillVerification.status == VerificationStatus.VERIFIED,
                )
            )
        ).first()

        if not endorser_verification:
            raise ValueError("Endorser must have verified expertise in this skill")

        # Add endorsement to verification
        endorsements = verification.peer_endorsements or []

        # Check if already endorsed
        existing_endorsement = next(
            (e for e in endorsements if e.get("endorser_id") == endorser_id), None
        )

        if existing_endorsement:
            raise ValueError("You have already endorsed this verification")

        endorsement = {
            "endorser_id": endorser_id,
            "endorser_name": endorser_volunteer.full_name,
            "endorsement_score": endorsement_data.get("score", 0.8),
            "comments": endorsement_data.get("comments", ""),
            "endorsed_at": datetime.now(datetime.timezone.utc).isoformat(),
            "endorser_skill_level": endorser_verification.verification_level,
        }

        endorsements.append(endorsement)
        verification.peer_endorsements = endorsements
        verification.updated_at = datetime.now(datetime.timezone.utc)

        session.add(verification)
        session.commit()

        # Check if enough endorsements to complete verification
        await self._check_endorsement_completion(session, verification)

        return True

    async def _check_endorsement_completion(
        self, session: Session, verification: SkillVerification
    ):
        """Check if peer endorsement verification is complete"""

        if verification.verification_method != VerificationMethod.PEER_ENDORSEMENT:
            return

        endorsements = verification.peer_endorsements or []

        # Need at least 3 endorsements
        if len(endorsements) < 3:
            return

        # Calculate average endorsement score
        total_score = sum(e.get("endorsement_score", 0) for e in endorsements)
        avg_score = total_score / len(endorsements)

        # Weight by endorser skill levels
        weighted_score = 0
        total_weight = 0

        for endorsement in endorsements:
            endorser_level = endorsement.get("endorser_skill_level", "basic")
            weight = {
                "basic": 0.5,
                "intermediate": 0.7,
                "advanced": 0.9,
                "expert": 1.0,
            }.get(endorser_level, 0.5)

            weighted_score += endorsement.get("endorsement_score", 0) * weight
            total_weight += weight

        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = avg_score

        # Complete verification
        verification.verification_score = final_score
        verification.status = (
            VerificationStatus.VERIFIED
            if final_score >= 0.7
            else VerificationStatus.REJECTED
        )
        verification.verified_at = datetime.now(datetime.timezone.utc)

        session.add(verification)
        session.commit()

        if verification.status == VerificationStatus.VERIFIED:
            await self._update_volunteer_skills(session, verification)
            await self._check_badge_eligibility(session, verification.volunteer_id)

    async def complete_assessment_test(
        self, session: Session, verification_id: int, test_results: Dict[str, Any]
    ) -> bool:
        """Complete skill assessment test"""

        verification = session.get(SkillVerification, verification_id)
        if not verification:
            raise ValueError("Verification not found")

        if verification.verification_method != VerificationMethod.ASSESSMENT_TEST:
            raise ValueError("Not an assessment test verification")

        # Calculate test score
        score = self._calculate_assessment_score(test_results)

        # Update verification
        verification.verification_score = score
        verification.assessment_results = test_results
        verification.status = (
            VerificationStatus.VERIFIED if score >= 0.6 else VerificationStatus.REJECTED
        )
        verification.verified_at = datetime.now(datetime.timezone.utc)

        session.add(verification)
        session.commit()

        if verification.status == VerificationStatus.VERIFIED:
            await self._update_volunteer_skills(session, verification)
            await self._check_badge_eligibility(session, verification.volunteer_id)

        return verification.status == VerificationStatus.VERIFIED

    def _calculate_assessment_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate score from assessment test results"""

        correct_answers = test_results.get("correct_answers", 0)
        total_questions = test_results.get("total_questions", 1)
        time_taken = test_results.get("time_taken_minutes", 60)
        time_limit = test_results.get("time_limit_minutes", 60)

        # Base accuracy score
        accuracy_score = correct_answers / total_questions

        # Time bonus (up to 10% extra for completing quickly)
        time_efficiency = min(time_limit / max(time_taken, 1), 1.5)
        time_bonus = (time_efficiency - 1) * 0.2

        # Difficulty bonus
        difficulty_level = test_results.get("difficulty_level", "intermediate")
        difficulty_multiplier = {
            "basic": 0.8,
            "intermediate": 1.0,
            "advanced": 1.2,
            "expert": 1.5,
        }.get(difficulty_level, 1.0)

        final_score = (accuracy_score + time_bonus) * difficulty_multiplier
        return min(final_score, 1.0)

    async def _update_volunteer_skills(
        self, session: Session, verification: SkillVerification
    ):
        """Update volunteer's skill list with verified skill"""

        volunteer = session.get(Volunteer, verification.volunteer_id)
        if not volunteer:
            return

        # Determine skill level based on verification score
        skill_level = self._determine_skill_level(verification.verification_score)

        # Update or add skill
        skills = volunteer.skills or []
        skill_updated = False

        for i, skill in enumerate(skills):
            if isinstance(skill, dict) and skill.get("name") == verification.skill_name:
                # Update existing skill with higher level
                current_level_value = {
                    "basic": 1,
                    "intermediate": 2,
                    "advanced": 3,
                    "expert": 4,
                }.get(skill.get("level", "basic"), 1)
                new_level_value = {
                    "basic": 1,
                    "intermediate": 2,
                    "advanced": 3,
                    "expert": 4,
                }.get(skill_level, 1)

                if new_level_value > current_level_value:
                    skills[i] = {
                        "name": verification.skill_name,
                        "level": skill_level,
                        "verified": True,
                        "verification_date": datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                        "verification_score": verification.verification_score,
                    }
                skill_updated = True
                break

        if not skill_updated:
            # Add new skill
            skills.append(
                {
                    "name": verification.skill_name,
                    "level": skill_level,
                    "verified": True,
                    "verification_date": datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                    "verification_score": verification.verification_score,
                }
            )

        volunteer.skills = skills
        volunteer.updated_at = datetime.now(datetime.timezone.utc)

        # Update verification level
        verification.verification_level = skill_level

        session.add(volunteer)
        session.add(verification)
        session.commit()

    def _determine_skill_level(self, score: float) -> str:
        """Determine skill level based on verification score"""
        if score >= self.verification_thresholds["expert"]:
            return "expert"
        elif score >= self.verification_thresholds["advanced"]:
            return "advanced"
        elif score >= self.verification_thresholds["intermediate"]:
            return "intermediate"
        else:
            return "basic"

    async def _check_badge_eligibility(self, session: Session, volunteer_id: int):
        """Check if volunteer is eligible for any new badges"""

        volunteer = session.get(Volunteer, volunteer_id)
        if not volunteer:
            return

        # Get volunteer's current badges
        current_badges = session.exec(
            select(UserBadge).where(UserBadge.user_id == volunteer.user_id)
        ).all()

        current_badge_codes = {badge.badge_code for badge in current_badges}

        # Check each badge criteria
        for badge_code, criteria in self.badge_criteria.items():
            if badge_code in current_badge_codes:
                continue  # Already has this badge

            if await self._meets_badge_criteria(session, volunteer, criteria):
                await self._award_badge(session, volunteer, badge_code, criteria)

    async def _meets_badge_criteria(
        self, session: Session, volunteer: Volunteer, criteria: Dict[str, Any]
    ) -> bool:
        """Check if volunteer meets badge criteria"""

        badge_criteria = criteria["criteria"]

        # Check verification score requirement
        if "min_verification_score" in badge_criteria:
            verifications = session.exec(
                select(SkillVerification).where(
                    and_(
                        SkillVerification.volunteer_id == volunteer.id,
                        SkillVerification.status == VerificationStatus.VERIFIED,
                        SkillVerification.verification_score
                        >= badge_criteria["min_verification_score"],
                    )
                )
            ).all()

            if not verifications:
                return False

        # Check required verification methods
        if "required_methods" in badge_criteria:
            required_methods = badge_criteria["required_methods"]
            volunteer_methods = session.exec(
                select(SkillVerification.verification_method)
                .where(
                    and_(
                        SkillVerification.volunteer_id == volunteer.id,
                        SkillVerification.status == VerificationStatus.VERIFIED,
                    )
                )
                .distinct()
            ).all()

            volunteer_method_set = {method.value for method in volunteer_methods}
            required_method_set = {method.value for method in required_methods}

            if not required_method_set.issubset(volunteer_method_set):
                return False

        # Check verified skills count
        if "verified_skills_count" in badge_criteria:
            verified_skills = session.exec(
                select(func.count(SkillVerification.id.distinct())).where(
                    and_(
                        SkillVerification.volunteer_id == volunteer.id,
                        SkillVerification.status == VerificationStatus.VERIFIED,
                    )
                )
            ).first()

            if verified_skills < badge_criteria["verified_skills_count"]:
                return False

        # Check completed applications
        if "completed_applications" in badge_criteria:
            completed_apps = session.exec(
                select(func.count(Application.id)).where(
                    and_(
                        Application.volunteer_id == volunteer.id,
                        Application.status == "completed",
                    )
                )
            ).first()

            if completed_apps < badge_criteria["completed_applications"]:
                return False

        # Check average rating
        if "min_average_rating" in badge_criteria:
            if volunteer.rating < badge_criteria["min_average_rating"]:
                return False

        # Check peer endorsements given
        if "peer_endorsements_given" in badge_criteria:
            endorsements_given = session.exec(
                select(func.count(SkillVerification.id)).where(
                    SkillVerification.peer_endorsements.op("@>")(
                        [{"endorser_id": volunteer.user_id}]
                    )
                )
            ).first()

            if endorsements_given < badge_criteria["peer_endorsements_given"]:
                return False

        return True

    async def _award_badge(
        self,
        session: Session,
        volunteer: Volunteer,
        badge_code: str,
        badge_info: Dict[str, Any],
    ):
        """Award a badge to a volunteer"""

        # Create badge if it doesn't exist
        badge = session.exec(select(Badge).where(Badge.code == badge_code)).first()

        if not badge:
            badge = Badge(
                code=badge_code,
                name=badge_info["name"],
                description=badge_info["description"],
                badge_type=badge_info["type"],
                rarity=badge_info["rarity"],
                points_value=badge_info["points"],
            )
            session.add(badge)
            session.commit()
            session.refresh(badge)

        # Award badge to user
        user_badge = UserBadge(
            user_id=volunteer.user_id,
            badge_id=badge.id,
            badge_code=badge_code,
            earned_at=datetime.now(datetime.timezone.utc),
            evidence_data={
                "volunteer_id": volunteer.id,
                "award_reason": "Automatic award based on criteria",
            },
        )

        session.add(user_badge)
        session.commit()

        # Log badge award
        await self._log_verification_event(
            session,
            None,
            "badge_awarded",
            {
                "badge_code": badge_code,
                "badge_name": badge_info["name"],
                "volunteer_id": volunteer.id,
                "user_id": volunteer.user_id,
            },
        )

        logger.info(f"Badge '{badge_code}' awarded to volunteer {volunteer.id}")

    async def _log_verification_event(
        self,
        session: Session,
        verification_id: Optional[int],
        event_type: str,
        event_data: Dict[str, Any],
    ):
        """Log verification-related events for analytics"""

        try:
            event = AnalyticsEvent(
                event_type=f"verification_{event_type}",
                user_id=event_data.get("user_id"),
                data={
                    **event_data,
                    "verification_id": verification_id,
                    "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                },
            )

            session.add(event)
            session.commit()

        except Exception as e:
            logger.error(f"Error logging verification event: {e}")

    async def get_verification_statistics(
        self, session: Session, volunteer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get verification statistics"""

        base_query = select(SkillVerification)

        if volunteer_id:
            base_query = base_query.where(
                SkillVerification.volunteer_id == volunteer_id
            )

        # Total verifications
        total_verifications = session.exec(
            select(func.count(SkillVerification.id))
        ).first()

        # Verifications by status
        status_stats = session.exec(
            select(SkillVerification.status, func.count(SkillVerification.id)).group_by(
                SkillVerification.status
            )
        ).all()

        # Verifications by method
        method_stats = session.exec(
            select(
                SkillVerification.verification_method, func.count(SkillVerification.id)
            ).group_by(SkillVerification.verification_method)
        ).all()

        # Average verification scores
        avg_scores = session.exec(
            select(
                SkillVerification.verification_method,
                func.avg(SkillVerification.verification_score),
            )
            .where(SkillVerification.verification_score.is_not(None))
            .group_by(SkillVerification.verification_method)
        ).all()

        return {
            "total_verifications": total_verifications,
            "status_breakdown": dict(status_stats),
            "method_breakdown": dict(method_stats),
            "average_scores_by_method": {
                method.value: round(float(score), 3) for method, score in avg_scores
            },
            "verification_weights": self.verification_weights,
            "badge_criteria_count": len(self.badge_criteria),
        }


# Global verification engine instance
verification_engine = SkillVerificationEngine()


from sqlmodel import func
