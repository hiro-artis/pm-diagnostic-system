"""Comprehensive scorer agent for essay grading and final assessment."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    OfficeMigrationTestResult,
    OfficeMigrationAnswer,
)


logger = logging.getLogger(__name__)


class ComprehensiveScorerAgent(BaseAgent):
    """Agent for comprehensive scoring including essay grading."""

    def __init__(self):
        """Initialize comprehensive scorer agent."""
        super().__init__(AgentType.COMPREHENSIVE_SCORER)

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute comprehensive scoring.

        Args:
            payload: Contains scoring request with essay answers

        Returns:
            AgentResponse with scoring result
        """
        try:
            action = payload.get("action")

            if action == "score_essay":
                return await self._score_essay(payload)
            elif action == "score_office_migration":
                return await self._score_office_migration(payload)
            else:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message=f"Unknown action: {action}",
                )

        except Exception as e:
            return await self.handle_error(e, "Comprehensive scoring failed")

    async def _score_essay(self, payload: Dict[str, Any]) -> AgentResponse:
        """Score essay questions.

        Args:
            payload: Contains question_id, essay_text, and evaluation_criteria

        Returns:
            AgentResponse with scoring result
        """
        try:
            question_id = payload.get("question_id")
            essay_text = payload.get("essay_text", "")
            evaluation_criteria = payload.get("evaluation_criteria", {})

            if not question_id or not essay_text:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="question_id and essay_text are required",
                )

            # Score using rule-based logic
            score = self._calculate_essay_score(question_id, essay_text, evaluation_criteria)

            self.log_info(f"Essay scored for question {question_id}: score={score}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "question_id": question_id,
                    "score": score,
                    "scoring_rationale": f"Essay evaluated based on criteria: {list(evaluation_criteria.keys())}",
                },
            )

        except Exception as e:
            return await self.handle_error(e, "Failed to score essay")

    async def _score_office_migration(self, payload: Dict[str, Any]) -> AgentResponse:
        """Complete office migration test scoring.

        Args:
            payload: Contains test_result and essay_answers

        Returns:
            AgentResponse with updated test result
        """
        try:
            test_result_dict = payload.get("test_result")
            essay_answers = payload.get("essay_answers", {})

            if not test_result_dict:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="test_result is required",
                )

            # Convert dict to OfficeMigrationTestResult
            test_result = OfficeMigrationTestResult(**test_result_dict)

            # Score essays
            essay_score = 0
            for i, (question_id, essay_text) in enumerate(essay_answers.items()):
                q_score = self._calculate_essay_score(
                    question_id,
                    essay_text,
                    self._get_essay_criteria(question_id),
                )
                essay_score += q_score

                # Update question answer with score
                for answer in test_result.questions:
                    if answer.question_id == question_id:
                        answer.score = q_score
                        break

            # Update test result
            test_result.essay_score = essay_score
            test_result.score = test_result.mc_score + essay_score
            test_result.passed = test_result.score >= 65

            self.log_info(
                f"Office migration test final score: "
                f"mc={test_result.mc_score}, essay={essay_score}, total={test_result.score}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "test_result": test_result.model_dump(mode="json"),
                    "mc_score": test_result.mc_score,
                    "essay_score": essay_score,
                    "total_score": test_result.score,
                    "passed": test_result.passed,
                    "message": f"Office migration test final score: "
                    f"MC {test_result.mc_score}/25 + Essay {essay_score}/75 = {test_result.score}/100",
                },
            )

        except Exception as e:
            return await self.handle_error(e, "Failed to score office migration")

    def _calculate_essay_score(
        self,
        question_id: str,
        essay_text: str,
        evaluation_criteria: Dict[str, Any],
    ) -> int:
        """Calculate essay score based on content analysis.

        Args:
            question_id: Question identifier
            essay_text: Essay text from user
            evaluation_criteria: Criteria for evaluation

        Returns:
            Score (0-25)
        """
        if not essay_text or len(essay_text.strip()) < 50:
            return 5  # Minimal score for very short answers

        # Basic scoring logic (to be enhanced with Claude API in future)
        score = 0

        # Word count check (10 points)
        word_count = len(essay_text.split())
        if 200 <= word_count <= 300:
            score += 10
        elif 150 <= word_count <= 350:
            score += 8
        elif word_count >= 100:
            score += 6
        else:
            score += 3

        # Content keywords check (15 points)
        # Different criteria for each question
        if question_id == "OM-ES-001":
            score += self._check_es001_content(essay_text)
        elif question_id == "OM-ES-002":
            score += self._check_es002_content(essay_text)
        elif question_id == "OM-ES-003":
            score += self._check_es003_content(essay_text)

        return min(25, max(0, score))

    def _check_es001_content(self, essay_text: str) -> int:
        """Check ES-001 essay for key concepts.

        Evaluates: リスク認識、対応策、コミュニケーション
        """
        score = 0
        text_lower = essay_text.lower()

        # Risk recognition (5 points)
        risk_keywords = ["リスク", "課題", "懸念", "問題"]
        if any(k in text_lower for k in risk_keywords):
            score += 3

        # Response strategy (5 points)
        strategy_keywords = ["対応", "工夫", "スケジュール", "配置"]
        if any(k in text_lower for k in strategy_keywords):
            score += 4

        # Communication (5 points)
        comm_keywords = ["コミュニケーション", "説明", "相談", "理解"]
        if any(k in text_lower for k in comm_keywords):
            score += 4

        return score

    def _check_es002_content(self, essay_text: str) -> int:
        """Check ES-002 essay for key concepts.

        Evaluates: 自責、マルチステークホルダー対応、意思決定の透明性
        """
        score = 0
        text_lower = essay_text.lower()

        # Self-responsibility (5 points)
        responsibility_keywords = ["判断", "決定", "主体", "責任"]
        if any(k in text_lower for k in responsibility_keywords):
            score += 3

        # Multi-stakeholder (5 points)
        stakeholder_keywords = ["関係者", "部門", "立場", "調整"]
        if any(k in text_lower for k in stakeholder_keywords):
            score += 4

        # Transparency (5 points)
        transparency_keywords = ["説明", "理由", "基準", "根拠"]
        if any(k in text_lower for k in transparency_keywords):
            score += 4

        return score

    def _check_es003_content(self, essay_text: str) -> int:
        """Check ES-003 essay for key concepts.

        Evaluates: 優しさ、聴く力、前向きな施策
        """
        score = 0
        text_lower = essay_text.lower()

        # Kindness (5 points)
        kindness_keywords = ["不安", "懸念", "配慮", "理解"]
        if any(k in text_lower for k in kindness_keywords):
            score += 3

        # Listening (5 points)
        listening_keywords = ["聴く", "声", "意見", "フィードバック"]
        if any(k in text_lower for k in listening_keywords):
            score += 4

        # Positive initiatives (5 points)
        initiative_keywords = ["施策", "活動", "機会", "協力"]
        if any(k in text_lower for k in initiative_keywords):
            score += 4

        return score

    def _get_essay_criteria(self, question_id: str) -> Dict[str, Any]:
        """Get evaluation criteria for an essay question.

        Args:
            question_id: Question identifier

        Returns:
            Evaluation criteria dictionary
        """
        criteria_map = {
            "OM-ES-001": {
                "リスク認識": {"max_score": 5},
                "対応策の実現性": {"max_score": 10},
                "コミュニケーション": {"max_score": 10},
            },
            "OM-ES-002": {
                "自責の姿勢": {"max_score": 5},
                "マルチステークホルダー対応": {"max_score": 10},
                "意思決定の透明性": {"max_score": 10},
            },
            "OM-ES-003": {
                "相手への優しさ": {"max_score": 5},
                "聴く力": {"max_score": 10},
                "前向きな施策": {"max_score": 10},
            },
        }
        return criteria_map.get(question_id, {})
