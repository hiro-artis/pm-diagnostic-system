"""Office migration test agent."""

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
from src.utils.test_data import (
    get_office_migration_mc_questions,
    get_office_migration_essay_questions,
)


logger = logging.getLogger(__name__)


class OfficeMigrationTestAgent(BaseAgent):
    """Agent for administering office migration test."""

    def __init__(self):
        """Initialize office migration test agent."""
        super().__init__(AgentType.OFFICE_MIGRATION)
        self.mc_questions = get_office_migration_mc_questions()
        self.essay_questions = get_office_migration_essay_questions()

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute office migration test.

        Args:
            payload: Contains session_id, stage (mc|essay|final), and user_answers

        Returns:
            AgentResponse with test progress or result
        """
        try:
            session_id = payload.get("session_id")
            stage = payload.get("stage", "mc")  # mc, essay, or final
            user_answers = payload.get("user_answers", {})

            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            if stage == "mc" and not user_answers:
                return await self._get_mc_questions(session_id)
            elif stage == "essay" and not user_answers:
                return await self._get_essay_questions(session_id)
            elif stage == "final":
                return await self._score_test(session_id, user_answers)
            else:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message=f"Unknown stage: {stage}",
                )

        except Exception as e:
            return await self.handle_error(e, "Office migration test execution failed")

    async def _get_mc_questions(self, session_id: str) -> AgentResponse:
        """Get multiple choice questions.

        Args:
            session_id: Session identifier

        Returns:
            AgentResponse with MC questions
        """
        try:
            questions_data = []
            for q in self.mc_questions:
                questions_data.append({
                    "question_id": q.question_id,
                    "question": q.question,
                    "options": q.options,
                })

            self.log_info(f"Generated MC questions for session {session_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "stage": "mc",
                    "total_questions": len(questions_data),
                    "questions": questions_data,
                    "message": "Multiple choice questions loaded. Please answer all questions.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to get MC questions")

    async def _get_essay_questions(self, session_id: str) -> AgentResponse:
        """Get essay questions.

        Args:
            session_id: Session identifier

        Returns:
            AgentResponse with essay questions
        """
        try:
            questions_data = []
            for q in self.essay_questions:
                questions_data.append({
                    "question_id": q.question_id,
                    "question": q.question,
                    "word_count_min": q.word_count_min,
                    "word_count_max": q.word_count_max,
                })

            self.log_info(f"Generated essay questions for session {session_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "stage": "essay",
                    "total_questions": len(questions_data),
                    "questions": questions_data,
                    "message": "Essay questions loaded. Please write your answers carefully.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to get essay questions")

    async def _score_test(
        self,
        session_id: str,
        user_answers: Dict[str, Any],
    ) -> AgentResponse:
        """Score the test based on user answers.

        Args:
            session_id: Session identifier
            user_answers: Dict with mc_answers and essay_answers

        Returns:
            AgentResponse with test result
        """
        try:
            start_time = datetime.utcnow()
            answered_questions = []

            # Score MC questions
            mc_answers = user_answers.get("mc_answers", {})
            mc_score = 0

            for question in self.mc_questions:
                qid = question.question_id
                user_answer = mc_answers.get(qid)

                if not user_answer:
                    self.log_info(f"MC question {qid} not answered")
                    continue

                is_correct = user_answer.upper() == question.correct_answer.upper()
                score = question.score_per_question if is_correct else 0
                mc_score += score

                answered_questions.append(
                    OfficeMigrationAnswer(
                        question_id=qid,
                        answer_text="",
                        user_answer=user_answer,
                        score=score,
                    )
                )

            # Essay answers - will be scored by comprehensive scorer
            # For now, store answers for later processing
            essay_answers = user_answers.get("essay_answers", {})
            essay_score = 0  # Will be set by comprehensive scorer

            for question in self.essay_questions:
                qid = question.question_id
                user_answer = essay_answers.get(qid, "")

                answered_questions.append(
                    OfficeMigrationAnswer(
                        question_id=qid,
                        answer_text=user_answer,
                        score=0,  # Will be set by comprehensive scorer
                        scoring_rationale="Pending comprehensive scorer evaluation",
                    )
                )

            total_score = mc_score + essay_score
            passed = total_score >= 65

            end_time = datetime.utcnow()
            time_spent = int((end_time - start_time).total_seconds())

            result = OfficeMigrationTestResult(
                test_id=f"OM_{start_time.timestamp()}",
                session_id=session_id,
                test_agent=AgentType.OFFICE_MIGRATION,
                score=total_score,
                total_points=100,
                passed=passed,
                start_time=start_time,
                end_time=end_time,
                time_spent_seconds=time_spent,
                mc_score=mc_score,
                essay_score=essay_score,
                questions=answered_questions,
            )

            self.log_info(
                f"Test completed for session {session_id}: "
                f"mc_score={mc_score}, essay_score={essay_score}, total={total_score}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "test_result": result.model_dump(mode="json"),
                    "mc_score": mc_score,
                    "essay_score": essay_score,
                    "total_score": total_score,
                    "passed": passed,
                    "message": f"Office migration test completed. "
                    f"MC: {mc_score}/25, Essay: {essay_score}/75, Total: {total_score}/100. "
                    f"Essay answers pending comprehensive scorer evaluation.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to score test")
