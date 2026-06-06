"""Mindset test agent."""

import logging
from datetime import datetime
from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    MindsetTestResult,
    MindsetAnswer,
    MindsetScores,
    Mindset,
)
from src.utils.test_data import get_mindset_scenarios
from src.utils.scoring_logic import calculate_mindset_scores


logger = logging.getLogger(__name__)


class MindsetTestAgent(BaseAgent):
    """Agent for administering mindset test."""

    def __init__(self):
        """Initialize mindset test agent."""
        super().__init__(AgentType.MINDSET)
        self.scenarios = get_mindset_scenarios()

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute mindset test.

        Args:
            payload: Contains session_id and optionally user_answers

        Returns:
            AgentResponse with test progress or result
        """
        try:
            session_id = payload.get("session_id")
            user_answers = payload.get("user_answers", {})

            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            if not user_answers:
                return await self._get_test_scenarios(session_id)
            else:
                return await self._score_test(session_id, user_answers)

        except Exception as e:
            return await self.handle_error(e, "Mindset test execution failed")

    async def _get_test_scenarios(self, session_id: str) -> AgentResponse:
        """Get mindset test scenarios.

        Args:
            session_id: Session identifier

        Returns:
            AgentResponse with scenarios
        """
        try:
            scenarios_data = []
            for scenario in self.scenarios:
                scenarios_data.append({
                    "scenario_id": scenario.scenario_id,
                    "scenario": scenario.scenario,
                    "question": scenario.question,
                    "options": scenario.options,
                })

            self.log_info(f"Generated {len(scenarios_data)} mindset scenarios for session {session_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "test_id": f"MS_{datetime.utcnow().timestamp()}",
                    "total_scenarios": len(scenarios_data),
                    "scenarios": scenarios_data,
                    "message": "Mindset scenarios loaded. Please select the best answer for each scenario.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to get test scenarios")

    async def _score_test(self, session_id: str, user_answers: Dict[str, str]) -> AgentResponse:
        """Score the mindset test.

        Args:
            session_id: Session identifier
            user_answers: Dict mapping scenario_id -> user_answer

        Returns:
            AgentResponse with test result
        """
        try:
            start_time = datetime.utcnow()
            answered_scenarios = []

            # Calculate mindset scores
            mindset_scores_dict = calculate_mindset_scores(user_answers)

            # Create MindsetScores object
            mindset_scores = MindsetScores(
                future_focused=mindset_scores_dict["future_focused"],
                self_responsibility=mindset_scores_dict["self_responsibility"],
                kindness=mindset_scores_dict["kindness"],
                listening_skill=mindset_scores_dict["listening_skill"],
                inclusivity=mindset_scores_dict["inclusivity"],
                collaboration=mindset_scores_dict["collaboration"],
                total_score=mindset_scores_dict["total_score"],
            )

            # Build scenario answers
            for scenario in self.scenarios:
                sid = scenario.scenario_id
                user_answer = user_answers.get(sid, "")

                answered_scenarios.append(
                    MindsetAnswer(
                        scenario_id=sid,
                        user_answer=user_answer,
                        score=15 if user_answer.upper() == scenario.correct_answer.upper() else 10,
                        scoring_rationale=f"Answer: {user_answer}",
                        mindset_scores={},  # Will be populated based on scoring pattern
                    )
                )

            total_score = mindset_scores.total_score
            passed = total_score >= 60  # 60点以上で合格
            qualifies_for_secondary = passed  # マインドセット60点以上で2次進出

            end_time = datetime.utcnow()
            time_spent = int((end_time - start_time).total_seconds())

            result = MindsetTestResult(
                test_id=f"MS_{start_time.timestamp()}",
                session_id=session_id,
                test_agent=AgentType.MINDSET,
                score=total_score,
                total_points=100,
                passed=passed,
                start_time=start_time,
                end_time=end_time,
                time_spent_seconds=time_spent,
                scenarios=answered_scenarios,
                mindset_scores=mindset_scores,
                passes_secondary_test=qualifies_for_secondary,
            )

            self.log_info(
                f"Mindset test scored for session {session_id}: "
                f"total_score={total_score}, passed={passed}, "
                f"qualifies_for_secondary={qualifies_for_secondary}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "test_result": result.model_dump(mode="json"),
                    "total_score": total_score,
                    "mindset_scores": {
                        "future_focused": mindset_scores.future_focused,
                        "self_responsibility": mindset_scores.self_responsibility,
                        "kindness": mindset_scores.kindness,
                        "listening_skill": mindset_scores.listening_skill,
                        "inclusivity": mindset_scores.inclusivity,
                        "collaboration": mindset_scores.collaboration,
                    },
                    "passed": passed,
                    "qualifies_for_secondary": qualifies_for_secondary,
                    "message": f"Mindset test completed. Total score: {total_score}/100. "
                    f"Qualifies for secondary test: {qualifies_for_secondary}",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to score mindset test")
