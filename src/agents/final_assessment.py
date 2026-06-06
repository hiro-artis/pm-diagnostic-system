"""Final assessment agent - generates final evaluation report."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    FinalAssessment,
    MindsetScores,
)


logger = logging.getLogger(__name__)


class FinalAssessmentAgent(BaseAgent):
    """Agent for generating final assessment and recommendation."""

    def __init__(self):
        """Initialize final assessment agent."""
        super().__init__(AgentType.ORCHESTRATOR)  # Use generic type

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute final assessment.

        Args:
            payload: Contains all test results (primary and optional secondary)

        Returns:
            AgentResponse with final assessment
        """
        try:
            session_id = payload.get("session_id")
            user_id = payload.get("user_id")
            primary_results = payload.get("primary_results", {})
            secondary_results = payload.get("secondary_results")

            if not session_id or not user_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id and user_id are required",
                )

            # Generate final assessment
            assessment = self._generate_assessment(
                session_id,
                user_id,
                primary_results,
                secondary_results,
            )

            self.log_info(
                f"Final assessment generated for session {session_id}: "
                f"grade={assessment.grade_level}, total_score={assessment.total_score}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "assessment": assessment.model_dump(mode="json"),
                    "grade_level": assessment.grade_level,
                    "total_score": assessment.total_score,
                    "message": f"Assessment complete. Grade: {assessment.grade_level}. {assessment.summary}",
                },
            )

        except Exception as e:
            return await self.handle_error(e, "Final assessment generation failed")

    def _generate_assessment(
        self,
        session_id: str,
        user_id: str,
        primary_results: Dict[str, Any],
        secondary_results: Optional[Dict[str, Any]] = None,
    ) -> FinalAssessment:
        """Generate final assessment based on all test results.

        Args:
            session_id: Session identifier
            user_id: User identifier
            primary_results: Primary test results
            secondary_results: Secondary test results (optional)

        Returns:
            FinalAssessment object
        """
        # Extract scores
        basic_knowledge_score = primary_results.get("basic_knowledge_score", 0)
        office_migration_score = primary_results.get("office_migration_score", 0)
        mindset_score = primary_results.get("mindset_score", 0)
        interview_score = secondary_results.get("score", 0) if secondary_results else None

        # Calculate total score
        if interview_score is not None:
            # Both primary and secondary: weight them
            total_score = (
                basic_knowledge_score * 0.2 +
                office_migration_score * 0.2 +
                mindset_score * 0.3 +
                interview_score * 0.3
            )
            secondary_test_conducted = True
        else:
            # Primary only
            total_score = (
                basic_knowledge_score * 0.25 +
                office_migration_score * 0.25 +
                mindset_score * 0.5
            )
            secondary_test_conducted = False

        # Determine grade level
        grade_level = self._determine_grade(total_score, mindset_score)

        # Extract and convert mindset breakdown
        mindset_breakdown_dict = primary_results.get("mindset_breakdown", {})
        mindset_breakdown = self._build_mindset_scores(mindset_breakdown_dict)

        # Generate strengths and development areas
        strengths, development_areas = self._analyze_mindsets(mindset_breakdown_dict)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            grade_level,
            mindset_breakdown_dict,
            interview_score,
        )

        # Generate summary
        summary = self._generate_summary(grade_level, total_score)

        return FinalAssessment(
            session_id=session_id,
            user_id=user_id,
            test_date=datetime.utcnow(),
            basic_knowledge_score=basic_knowledge_score,
            office_migration_score=office_migration_score,
            mindset_score=mindset_score,
            interview_score=interview_score,
            total_score=total_score,
            mindset_breakdown=mindset_breakdown,
            grade_level=grade_level,
            summary=summary,
            strengths=strengths,
            development_areas=development_areas,
            recommendations=recommendations,
            primary_test_completed=True,
            secondary_test_completed=secondary_test_conducted,
            secondary_test_conducted=secondary_test_conducted,
        )

    def _build_mindset_scores(self, mindset_breakdown_dict: Dict[str, int]) -> MindsetScores:
        """Build MindsetScores object from dictionary.

        Args:
            mindset_breakdown_dict: Dictionary of mindset scores

        Returns:
            MindsetScores object
        """
        if not mindset_breakdown_dict:
            return MindsetScores(
                future_focused=0,
                self_responsibility=0,
                kindness=0,
                listening_skill=0,
                inclusivity=0,
                collaboration=0,
                total_score=0,
            )

        # Calculate total score if not present
        scores = mindset_breakdown_dict.copy()
        if "total_score" not in scores:
            mindset_values = [
                v for k, v in scores.items()
                if k in [
                    "future_focused",
                    "self_responsibility",
                    "kindness",
                    "listening_skill",
                    "inclusivity",
                    "collaboration",
                ]
            ]
            if mindset_values:
                scores["total_score"] = sum(mindset_values) // len(mindset_values)
            else:
                scores["total_score"] = 0

        return MindsetScores(
            future_focused=scores.get("future_focused", 0),
            self_responsibility=scores.get("self_responsibility", 0),
            kindness=scores.get("kindness", 0),
            listening_skill=scores.get("listening_skill", 0),
            inclusivity=scores.get("inclusivity", 0),
            collaboration=scores.get("collaboration", 0),
            total_score=scores.get("total_score", 0),
        )

    def _determine_grade(self, total_score: float, mindset_score: int) -> str:
        """Determine grade level based on scores.

        Args:
            total_score: Total combined score
            mindset_score: Mindset test score

        Returns:
            Grade level (A/B/C/再検査)
        """
        # マインドセットが重視されるため、スコアが低い場合は下げる
        if mindset_score < 60:
            return "再検査"  # Below mindset threshold

        if total_score >= 80:
            return "A"
        elif total_score >= 70:
            return "B"
        elif total_score >= 60:
            return "C"
        else:
            return "再検査"

    def _analyze_mindsets(self, mindset_breakdown: Dict[str, int]) -> tuple:
        """Analyze mindset scores to identify strengths and development areas.

        Args:
            mindset_breakdown: Dict of mindset scores

        Returns:
            Tuple of (strengths, development_areas) lists
        """
        strengths = []
        development_areas = []

        # Analyze each mindset
        mindset_labels = {
            "future_focused": "未来志向",
            "self_responsibility": "自責",
            "kindness": "優しさ",
            "listening_skill": "聴く力",
            "inclusivity": "置いてきぼりにしない",
            "collaboration": "一人で進まない",
        }

        for key, label in mindset_labels.items():
            score = mindset_breakdown.get(key, 0)

            if score >= 80:
                strengths.append(f"{label}（{score}点）- 高い評価")
            elif score >= 60:
                strengths.append(f"{label}（{score}点）- 標準的")
            else:
                development_areas.append(f"{label}（{score}点）- 今後の改善が望ましい")

        # Ensure we have at least some output
        if not strengths:
            strengths = ["各項目で基礎的な水準を達成"]
        if not development_areas:
            development_areas = ["全項目で適切な水準に達しています"]

        return strengths, development_areas

    def _generate_recommendations(
        self,
        grade_level: str,
        mindset_breakdown: Dict[str, int],
        interview_score: Optional[int] = None,
    ) -> list:
        """Generate recommendations based on assessment results.

        Args:
            grade_level: Final grade level
            mindset_breakdown: Mindset scores
            interview_score: Interview score (if available)

        Returns:
            List of recommendations
        """
        recommendations = []

        if grade_level == "A":
            recommendations.append("PM適性が高いと評価されました。プロジェクトマネジャーとしての責任を積極的に担い、さらなる経験を積むことをお勧めします。")
            recommendations.append("特に強みのある領域を活かしながら、弱みの改善にも取り組んでください。")

        elif grade_level == "B":
            recommendations.append("PM適性があります。今後の実務経験を通じて、さらにマインドセットを高めることをお勧めします。")
            weak_areas = [k for k, v in mindset_breakdown.items() if v < 70]
            if weak_areas:
                recommendations.append(f"特に以下のマインドセットの強化に注力してください: {', '.join(weak_areas)}")

        elif grade_level == "C":
            recommendations.append("PM適性の基礎はありますが、今後の成長の余地があります。")
            recommendations.append("メンタリングプログラムやPM研修の参加をお勧めします。")
            recommendations.append("実務経験を通じて、特にマインドセットの強化に取り組んでください。")

        elif grade_level == "再検査":
            recommendations.append("PM適性について、さらなる検証が必要です。")
            recommendations.append("再検査の実施をお勧めします。（実施可能日時: 1週間後）")
            if interview_score is None:
                recommendations.append("特にマインドセットの向上に注力し、その後の再検査での確認をお勧めします。")

        return recommendations

    def _generate_summary(self, grade_level: str, total_score: float) -> str:
        """Generate assessment summary.

        Args:
            grade_level: Final grade level
            total_score: Total score

        Returns:
            Summary text
        """
        summaries = {
            "A": f"総合スコア {total_score:.1f}/100。PM適性が高く、プロジェクト推進リーダーとしての活躍が期待できます。",
            "B": f"総合スコア {total_score:.1f}/100。PM適性があります。経験を通じたさらなる成長が期待できます。",
            "C": f"総合スコア {total_score:.1f}/100。PM適性の基礎がありますが、成長の余地があります。",
            "再検査": f"総合スコア {total_score:.1f}/100。PM適性について再検査をお勧めします。",
        }
        return summaries.get(grade_level, "評価処理中...")
