"""Basic knowledge test agent."""

import random
import logging
from datetime import datetime
from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    BasicKnowledgeTestResult,
    BasicKnowledgeAnswer,
)
from src.utils.test_data import get_basic_knowledge_questions


logger = logging.getLogger(__name__)


class BasicKnowledgeTestAgent(BaseAgent):
    """Agent for administering basic knowledge test."""

    def __init__(self):
        """Initialize basic knowledge test agent."""
        super().__init__(AgentType.BASIC_KNOWLEDGE)
        self.questions = get_basic_knowledge_questions()

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute basic knowledge test.

        Args:
            payload: Contains session_id and optionally selected question IDs

        Returns:
            AgentResponse with test result
        """
        try:
            session_id = payload.get("session_id")
            user_answers = payload.get("user_answers", {})  # Dict[question_id, answer]

            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            if not user_answers:
                # Return questions for the user to answer
                return await self._get_test_questions(session_id)

            # Score the test
            return await self._score_test(session_id, user_answers)

        except Exception as e:
            return await self.handle_error(e, "Basic knowledge test execution failed")

    async def _get_test_questions(self, session_id: str) -> AgentResponse:
        """Get test questions (shuffled).

        Args:
            session_id: Session identifier

        Returns:
            AgentResponse with questions
        """
        try:
            # Shuffle and select all questions
            shuffled = self.questions.copy()
            random.shuffle(shuffled)

            questions_data = []
            for q in shuffled:
                questions_data.append({
                    "question_id": q.question_id,
                    "question": q.question,
                    "options": q.options,
                })

            self.log_info(f"Generated test with {len(questions_data)} questions for session {session_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "test_id": f"BK_{datetime.utcnow().timestamp()}",
                    "total_questions": len(questions_data),
                    "questions": questions_data,
                    "message": "Basic knowledge test questions loaded. Please answer all questions.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to get test questions")

    async def _score_test(self, session_id: str, user_answers: Dict[str, str]) -> AgentResponse:
        """Score the test based on user answers.

        Args:
            session_id: Session identifier
            user_answers: Dict of question_id -> user_answer

        Returns:
            AgentResponse with test result
        """
        try:
            start_time = datetime.utcnow()
            answered_questions = []
            correct_count = 0

            for question in self.questions:
                qid = question.question_id
                user_answer = user_answers.get(qid)

                if not user_answer:
                    self.log_info(f"Question {qid} not answered")
                    continue

                is_correct = user_answer.upper() == question.correct_answer.upper()
                if is_correct:
                    correct_count += 1

                answered_questions.append(
                    BasicKnowledgeAnswer(
                        question_id=qid,
                        user_answer=user_answer,
                        is_correct=is_correct,
                        score=10 if is_correct else 0,
                    )
                )

            total_score = correct_count * 10
            passed = total_score >= 70  # 70% threshold

            end_time = datetime.utcnow()
            time_spent = int((end_time - start_time).total_seconds())

            result = BasicKnowledgeTestResult(
                test_id=f"BK_{start_time.timestamp()}",
                session_id=session_id,
                test_agent=AgentType.BASIC_KNOWLEDGE,
                score=total_score,
                total_points=100,
                passed=passed,
                start_time=start_time,
                end_time=end_time,
                time_spent_seconds=time_spent,
                questions=answered_questions,
                total_questions=len(self.questions),
                correct_answers=correct_count,
            )

            self.log_info(
                f"Test scored for session {session_id}: "
                f"score={total_score}, passed={passed}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "test_result": result.model_dump(mode="json"),
                    "score": total_score,
                    "correct_answers": correct_count,
                    "total_questions": len(self.questions),
                    "passed": passed,
                    "message": f"Basic knowledge test completed. Score: {total_score}/100",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to score test")
