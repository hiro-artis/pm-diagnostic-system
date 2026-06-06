"""Mindset interview agent for secondary test (2次テスト)."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    MindsetInterviewResult,
    InterviewQuestion,
    InterviewResponse,
    MindsetScores,
    Mindset,
    MindsetTestResult,
)


logger = logging.getLogger(__name__)


class MindsetInterviewAgent(BaseAgent):
    """Agent for conducting mindset verification interview (2次テスト)."""

    def __init__(self):
        """Initialize mindset interview agent."""
        super().__init__(AgentType.MINDSET_INTERVIEW)
        self.interview_questions = self._load_interview_questions()

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute mindset interview.

        Args:
            payload: Contains session_id, primary_test_results, and interview_responses

        Returns:
            AgentResponse with interview result
        """
        try:
            action = payload.get("action", "get_questions")

            if action == "get_questions":
                return await self._get_interview_questions(payload)
            elif action == "score_interview":
                return await self._score_interview(payload)
            else:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message=f"Unknown action: {action}",
                )

        except Exception as e:
            return await self.handle_error(e, "Mindset interview execution failed")

    async def _get_interview_questions(self, payload: Dict[str, Any]) -> AgentResponse:
        """Get interview questions based on primary test results.

        Args:
            payload: Contains session_id and primary_mindset_scores

        Returns:
            AgentResponse with interview questions
        """
        try:
            session_id = payload.get("session_id")
            primary_mindset_scores = payload.get("primary_mindset_scores", {})

            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            # Identify weak mindsets (score < 70)
            weak_mindsets = [
                mindset for mindset, score in primary_mindset_scores.items()
                if score < 70
            ]

            # Select questions focusing on weak mindsets
            selected_questions = self._select_questions(weak_mindsets)

            questions_data = []
            for i, q in enumerate(selected_questions, 1):
                questions_data.append({
                    "question_number": i,
                    "question_text": q["question"],
                    "question_type": q["type"],
                    "evaluated_mindsets": q["evaluated_mindsets"],
                })

            self.log_info(
                f"Generated {len(questions_data)} interview questions for session {session_id}. "
                f"Focus areas: {weak_mindsets}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "total_questions": len(questions_data),
                    "focus_areas": weak_mindsets,
                    "questions": questions_data,
                    "message": "Interview questions loaded. Please answer thoughtfully.",
                },
            )

        except Exception as e:
            return await self.handle_error(e, "Failed to get interview questions")

    async def _score_interview(self, payload: Dict[str, Any]) -> AgentResponse:
        """Score the interview and generate results.

        Args:
            payload: Contains session_id, primary_results, and interview_responses

        Returns:
            AgentResponse with interview result
        """
        try:
            session_id = payload.get("session_id")
            primary_mindset_result = payload.get("primary_mindset_result", {})
            interview_responses = payload.get("interview_responses", {})

            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            start_time = datetime.utcnow()

            # Score each response
            scored_responses = []
            revised_mindset_scores = {
                Mindset.FUTURE_FOCUSED: primary_mindset_result.get("future_focused", 0),
                Mindset.SELF_RESPONSIBILITY: primary_mindset_result.get("self_responsibility", 0),
                Mindset.KINDNESS: primary_mindset_result.get("kindness", 0),
                Mindset.LISTENING_SKILL: primary_mindset_result.get("listening_skill", 0),
                Mindset.INCLUSIVITY: primary_mindset_result.get("inclusivity", 0),
                Mindset.COLLABORATION: primary_mindset_result.get("collaboration", 0),
            }

            for question_num, response_text in interview_responses.items():
                # Score the response based on content analysis
                mindset_scores = self._analyze_response(response_text)

                scored_responses.append({
                    "question_number": int(question_num),
                    "response_text": response_text,
                    "evaluated_mindsets": mindset_scores,
                    "consistency_with_primary": self._check_consistency(
                        question_num,
                        mindset_scores,
                        primary_mindset_result,
                    ),
                    "notes": "",
                })

                # Update revised mindset scores
                for mindset, score in mindset_scores.items():
                    # Blend primary and interview scores (60% primary, 40% interview)
                    revised_mindset_scores[mindset] = int(
                        revised_mindset_scores[mindset] * 0.6 + score * 0.4
                    )

            # Calculate final mindset scores
            mindset_scores_obj = MindsetScores(
                future_focused=revised_mindset_scores[Mindset.FUTURE_FOCUSED],
                self_responsibility=revised_mindset_scores[Mindset.SELF_RESPONSIBILITY],
                kindness=revised_mindset_scores[Mindset.KINDNESS],
                listening_skill=revised_mindset_scores[Mindset.LISTENING_SKILL],
                inclusivity=revised_mindset_scores[Mindset.INCLUSIVITY],
                collaboration=revised_mindset_scores[Mindset.COLLABORATION],
                total_score=int(sum(revised_mindset_scores.values()) / len(revised_mindset_scores)),
            )

            end_time = datetime.utcnow()
            time_spent = int((end_time - start_time).total_seconds())

            result = MindsetInterviewResult(
                test_id=f"INT_{start_time.timestamp()}",
                session_id=session_id,
                test_agent=AgentType.MINDSET_INTERVIEW,
                score=mindset_scores_obj.total_score,
                total_points=100,
                passed=True,  # Always pass if interview conducted
                start_time=start_time,
                end_time=end_time,
                time_spent_seconds=time_spent,
                interview_questions=[],  # Populated from questions
                responses=scored_responses,  # type: ignore
                revised_mindset_scores=mindset_scores_obj,
                consistency_rating="moderate",  # To be refined
            )

            self.log_info(
                f"Interview completed for session {session_id}: "
                f"final_score={mindset_scores_obj.total_score}"
            )

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "test_result": result.model_dump(mode="json"),
                    "revised_mindset_scores": {
                        "future_focused": mindset_scores_obj.future_focused,
                        "self_responsibility": mindset_scores_obj.self_responsibility,
                        "kindness": mindset_scores_obj.kindness,
                        "listening_skill": mindset_scores_obj.listening_skill,
                        "inclusivity": mindset_scores_obj.inclusivity,
                        "collaboration": mindset_scores_obj.collaboration,
                    },
                    "total_score": mindset_scores_obj.total_score,
                    "message": f"Interview completed. Final mindset score: {mindset_scores_obj.total_score}/100",
                },
            )

        except Exception as e:
            return await self.handle_error(e, "Failed to score interview")

    def _load_interview_questions(self) -> List[Dict[str, Any]]:
        """Load interview question templates.

        Returns:
            List of interview question templates
        """
        return [
            # Open-ended questions
            {
                "question": "過去にプロジェクトを進める中で、長期的な視点から判断を変えた経験はありますか？その時どのような点を重視しましたか？",
                "type": "open",
                "evaluated_mindsets": {Mindset.FUTURE_FOCUSED: 4},
            },
            {
                "question": "困難な状況で、自分の責任として問題を解決した経験を教えてください。その時の考え方や行動を詳しく説明してください。",
                "type": "open",
                "evaluated_mindsets": {Mindset.SELF_RESPONSIBILITY: 4},
            },
            {
                "question": "チームメンバーが不安や悩みを抱えていた時、あなたはどのように対応しましたか？相手の気持ちにどう向き合いましたか？",
                "type": "open",
                "evaluated_mindsets": {Mindset.KINDNESS: 4},
            },
            {
                "question": "相手の意見と異なる場合、相手の意見をどのように理解しようとしましたか？具体的な例を挙げて説明してください。",
                "type": "open",
                "evaluated_mindsets": {Mindset.LISTENING_SKILL: 4},
            },
            {
                "question": "プロジェクトで意見が合わないメンバーがいた時、そのメンバーをどのように進行に巻き込みましたか？",
                "type": "open",
                "evaluated_mindsets": {Mindset.INCLUSIVITY: 4},
            },
            {
                "question": "重要な決定の際に、一人で決めずに他の人の力を借りた経験があれば教えてください。誰にどのように相談しましたか？",
                "type": "open",
                "evaluated_mindsets": {Mindset.COLLABORATION: 4},
            },
            # Deep-dive questions
            {
                "question": "その時の判断について、もし別の視点があったらどう考えていましたか？",
                "type": "deep_dive",
                "evaluated_mindsets": {Mindset.FUTURE_FOCUSED: 3},
            },
            {
                "question": "その状況で、あなた自身の行動で改善できた点はありましたか？",
                "type": "deep_dive",
                "evaluated_mindsets": {Mindset.SELF_RESPONSIBILITY: 3},
            },
            # Verification questions
            {
                "question": "1次テストのシナリオ3で、あなたはCを選びました。なぜそう考えたのか、実務ではどのように対応していますか？",
                "type": "verification",
                "evaluated_mindsets": {Mindset.KINDNESS: 3, Mindset.INCLUSIVITY: 3},
            },
            {
                "question": "現在のプロジェクトや業務で、あなたが実践しているこれらのマインドセットの具体例があれば教えてください。",
                "type": "verification",
                "evaluated_mindsets": {
                    Mindset.FUTURE_FOCUSED: 2,
                    Mindset.SELF_RESPONSIBILITY: 2,
                    Mindset.COLLABORATION: 2,
                },
            },
        ]

    def _select_questions(self, weak_mindsets: List[str]) -> List[Dict[str, Any]]:
        """Select interview questions based on weak mindsets.

        Args:
            weak_mindsets: List of mindsets scoring below 70

        Returns:
            Selected interview questions
        """
        all_questions = self.interview_questions
        selected = []

        # First, select open questions for weak mindsets
        for q in all_questions:
            if q["type"] == "open":
                for mindset_key in q["evaluated_mindsets"].keys():
                    if mindset_key in weak_mindsets and len(selected) < 5:
                        selected.append(q)
                        break

        # Add verification questions
        verification_q = [q for q in all_questions if q["type"] == "verification"]
        selected.extend(verification_q[:2])

        # Ensure at least 5 questions
        if len(selected) < 5:
            for q in all_questions:
                if q not in selected and len(selected) < 5:
                    selected.append(q)

        return selected[:6]  # Maximum 6 questions

    def _analyze_response(self, response_text: str) -> Dict[str, int]:
        """Analyze interview response for mindset indicators.

        Args:
            response_text: User's response text

        Returns:
            Dict of mindset scores (0-100)
        """
        text_lower = response_text.lower()

        mindset_scores = {
            Mindset.FUTURE_FOCUSED: 50,
            Mindset.SELF_RESPONSIBILITY: 50,
            Mindset.KINDNESS: 50,
            Mindset.LISTENING_SKILL: 50,
            Mindset.INCLUSIVITY: 50,
            Mindset.COLLABORATION: 50,
        }

        # Keyword-based scoring (simple heuristic)
        future_keywords = ["長期", "将来", "展望", "視点", "戦略"]
        if any(k in text_lower for k in future_keywords):
            mindset_scores[Mindset.FUTURE_FOCUSED] = min(100, 50 + 25)

        responsibility_keywords = ["自分", "主体", "判断", "責任", "行動"]
        if any(k in text_lower for k in responsibility_keywords):
            mindset_scores[Mindset.SELF_RESPONSIBILITY] = min(100, 50 + 25)

        kindness_keywords = ["理解", "配慮", "心", "気持ち", "寄り添"]
        if any(k in text_lower for k in kindness_keywords):
            mindset_scores[Mindset.KINDNESS] = min(100, 50 + 25)

        listening_keywords = ["聴く", "聞く", "声", "意見", "相手"]
        if any(k in text_lower for k in listening_keywords):
            mindset_scores[Mindset.LISTENING_SKILL] = min(100, 50 + 25)

        inclusivity_keywords = ["巻き込む", "一緒", "全員", "参加", "含める"]
        if any(k in text_lower for k in inclusivity_keywords):
            mindset_scores[Mindset.INCLUSIVITY] = min(100, 50 + 25)

        collaboration_keywords = ["相談", "協力", "力", "チーム", "連携"]
        if any(k in text_lower for k in collaboration_keywords):
            mindset_scores[Mindset.COLLABORATION] = min(100, 50 + 25)

        return mindset_scores

    def _check_consistency(
        self,
        question_num: str,
        interview_scores: Dict[str, int],
        primary_scores: Dict[str, int],
    ) -> str:
        """Check consistency between primary and interview scores.

        Args:
            question_num: Question number
            interview_scores: Interview response scores
            primary_scores: Primary test mindset scores

        Returns:
            Consistency rating (consistent/improved/declined/unclear)
        """
        if not interview_scores or not primary_scores:
            return "unclear"

        interview_avg = sum(interview_scores.values()) / len(interview_scores) if interview_scores else 0
        primary_avg = sum(primary_scores.values()) / len(primary_scores) if primary_scores else 0

        diff = interview_avg - primary_avg
        if abs(diff) < 10:
            return "consistent"
        elif diff > 10:
            return "improved"
        elif diff < -10:
            return "declined"
        else:
            return "unclear"
