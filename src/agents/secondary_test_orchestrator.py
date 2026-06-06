"""Orchestrator for secondary test flow (2次テスト制御)."""

import logging
from typing import Any, Dict

from src.agents.mindset_interview import MindsetInterviewAgent
from src.agents.final_assessment import FinalAssessmentAgent
from src.models.schemas import AgentType, AgentResponse
from src.storage.result_store import ResultStore
from src.storage.session_manager import SessionManager


logger = logging.getLogger(__name__)


class SecondaryTestOrchestratorAgent:
    """Orchestrates the secondary test (2次テスト) flow."""

    def __init__(self):
        """Initialize secondary test orchestrator."""
        self.interview = MindsetInterviewAgent()
        self.assessor = FinalAssessmentAgent()
        self.session_manager = SessionManager()
        self.result_store = ResultStore()

    async def run_complete_secondary_test(
        self,
        session_id: str,
        primary_mindset_scores: Dict[str, int],
        interview_responses: Dict[str, str],
    ) -> AgentResponse:
        """Run complete secondary test flow.

        Args:
            session_id: Session identifier
            primary_mindset_scores: Primary test mindset scores
            interview_responses: Interview responses from user

        Returns:
            AgentResponse with secondary test results
        """
        try:
            logger.info(f"Starting secondary test for session {session_id}")

            # 1. Get interview questions
            logger.info("Loading interview questions...")
            questions_response = await self.interview.execute({
                "action": "get_questions",
                "session_id": session_id,
                "primary_mindset_scores": primary_mindset_scores,
            })

            if questions_response.status != "success":
                return questions_response

            # 2. Score interview
            logger.info("Scoring interview responses...")
            score_response = await self.interview.execute({
                "action": "score_interview",
                "session_id": session_id,
                "primary_mindset_result": primary_mindset_scores,
                "interview_responses": interview_responses,
            })

            if score_response.status != "success":
                return score_response

            interview_result = score_response.result["test_result"]
            self.result_store.save_test_result(session_id, **interview_result)
            logger.info(f"Interview test completed: score={interview_result['score']}")

            return AgentResponse(
                agent_type=AgentType.ORCHESTRATOR,
                status="success",
                result={
                    "session_id": session_id,
                    "interview_result": interview_result,
                    "interview_score": score_response.result["total_score"],
                    "revised_mindset_scores": score_response.result["revised_mindset_scores"],
                    "next_action": "generate_final_assessment",
                    "message": "Secondary test completed successfully.",
                },
            )

        except Exception as e:
            logger.error(f"Secondary test flow failed: {str(e)}")
            return AgentResponse(
                agent_type=AgentType.ORCHESTRATOR,
                status="error",
                error_message=f"Secondary test execution failed: {str(e)}",
            )

    async def generate_final_assessment(
        self,
        session_id: str,
        user_id: str,
        primary_results: Dict[str, Any],
        secondary_results: Dict[str, Any] = None,
    ) -> AgentResponse:
        """Generate final assessment combining primary and secondary results.

        Args:
            session_id: Session identifier
            user_id: User identifier
            primary_results: Primary test results
            secondary_results: Secondary test results (optional)

        Returns:
            AgentResponse with final assessment
        """
        try:
            logger.info(f"Generating final assessment for session {session_id}")

            # Generate assessment
            assessment_response = await self.assessor.execute({
                "session_id": session_id,
                "user_id": user_id,
                "primary_results": primary_results,
                "secondary_results": secondary_results,
            })

            if assessment_response.status != "success":
                return assessment_response

            assessment = assessment_response.result["assessment"]

            # Save assessment
            self.result_store.save_final_assessment(session_id, **assessment)

            # Mark session as complete
            self.session_manager.complete_test(session_id)

            logger.info(
                f"Final assessment completed: "
                f"grade={assessment['grade_level']}, score={assessment['total_score']}"
            )

            return AgentResponse(
                agent_type=AgentType.ORCHESTRATOR,
                status="success",
                result={
                    "session_id": session_id,
                    "user_id": user_id,
                    "assessment": assessment,
                    "grade_level": assessment["grade_level"],
                    "total_score": assessment["total_score"],
                    "message": assessment_response.result["message"],
                },
            )

        except Exception as e:
            logger.error(f"Final assessment generation failed: {str(e)}")
            return AgentResponse(
                agent_type=AgentType.ORCHESTRATOR,
                status="error",
                error_message=f"Final assessment generation failed: {str(e)}",
            )
