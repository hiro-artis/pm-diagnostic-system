"""Orchestrator for primary test flow (1次テスト制御)."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from src.agents.orchestrator import OrchestratorAgent
from src.agents.basic_knowledge_test import BasicKnowledgeTestAgent
from src.agents.office_migration_test import OfficeMigrationTestAgent
from src.agents.mindset_test import MindsetTestAgent
from src.agents.comprehensive_scorer import ComprehensiveScorerAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    TestStatus,
    PrimaryTestResults,
)
from src.storage.result_store import ResultStore
from src.storage.session_manager import SessionManager


logger = logging.getLogger(__name__)


class PrimaryTestOrchestratorAgent:
    """Orchestrates the entire primary test flow."""

    def __init__(self):
        """Initialize primary test orchestrator."""
        self.orchestrator = OrchestratorAgent()
        self.basic_knowledge = BasicKnowledgeTestAgent()
        self.office_migration = OfficeMigrationTestAgent()
        self.mindset = MindsetTestAgent()
        self.scorer = ComprehensiveScorerAgent()
        self.session_manager = SessionManager()
        self.result_store = ResultStore()

    async def run_complete_primary_test(
        self,
        user_id: str,
        basic_answers: Dict[str, str],
        office_mc_answers: Dict[str, str],
        office_essay_answers: Dict[str, str],
        mindset_answers: Dict[str, str],
    ) -> AgentResponse:
        """Run complete primary test flow.

        Args:
            user_id: User identifier
            basic_answers: Basic knowledge answers
            office_mc_answers: Office migration MC answers
            office_essay_answers: Office migration essay answers
            mindset_answers: Mindset scenario answers

        Returns:
            AgentResponse with primary test results
        """
        try:
            logger.info(f"Starting primary test for user {user_id}")

            # 1. Start test session
            start_response = await self.orchestrator.execute({
                "action": "start_primary_test",
                "user_id": user_id,
            })

            if start_response.status != "success":
                return start_response

            session_id = start_response.result["session_id"]
            logger.info(f"Session created: {session_id}")

            # 2. Run basic knowledge test
            logger.info("Running basic knowledge test...")
            bk_response = await self.basic_knowledge.execute({
                "session_id": session_id,
                "user_answers": basic_answers,
            })

            if bk_response.status != "success":
                return bk_response

            bk_result = bk_response.result["test_result"]
            self.result_store.save_test_result(session_id, bk_result)
            logger.info(f"Basic knowledge test completed: score={bk_result['score']}")

            # 3. Run office migration test
            logger.info("Running office migration test...")
            essay_response = await self.office_migration.execute({
                "session_id": session_id,
                "stage": "final",
                "user_answers": {
                    "mc_answers": office_mc_answers,
                    "essay_answers": office_essay_answers,
                },
            })

            if essay_response.status != "success":
                return essay_response

            om_result_dict = essay_response.result["test_result"]
            # Score essays using comprehensive scorer
            scorer_response = await self.scorer.execute({
                "action": "score_office_migration",
                "test_result": om_result_dict,
                "essay_answers": office_essay_answers,
            })

            if scorer_response.status != "success":
                return scorer_response

            om_result = scorer_response.result["test_result"]
            self.result_store.save_test_result(session_id, om_result)
            logger.info(f"Office migration test completed: score={om_result['score']}")

            # 4. Run mindset test
            logger.info("Running mindset test...")
            ms_response = await self.mindset.execute({
                "session_id": session_id,
                "user_answers": mindset_answers,
            })

            if ms_response.status != "success":
                return ms_response

            ms_result = ms_response.result["test_result"]
            self.result_store.save_test_result(session_id, ms_result)
            logger.info(f"Mindset test completed: score={ms_result['score']}")

            # 5. Check primary test results and determine next action
            logger.info("Checking primary test results...")
            check_response = await self.orchestrator.execute({
                "action": "check_primary_results",
                "session_id": session_id,
            })

            if check_response.status != "success":
                return check_response

            results_check = check_response.result
            logger.info(
                f"Primary test check: all_passed={results_check['all_passed']}, "
                f"qualifies_for_secondary={results_check['qualifies_for_secondary']}"
            )

            return AgentResponse(
                agent_type=AgentType.ORCHESTRATOR,
                status="success",
                result={
                    "session_id": session_id,
                    "user_id": user_id,
                    "scores": {
                        "basic_knowledge": bk_result["score"],
                        "office_migration": om_result["score"],
                        "mindset": ms_result["score"],
                    },
                    "passed": results_check["all_passed"],
                    "qualifies_for_secondary": results_check["qualifies_for_secondary"],
                    "message": f"Primary test completed. "
                    f"Basic Knowledge: {bk_result['score']}/100, "
                    f"Office Migration: {om_result['score']}/100, "
                    f"Mindset: {ms_result['score']}/100. "
                    f"Qualifies for secondary test: {results_check['qualifies_for_secondary']}",
                },
            )

        except Exception as e:
            logger.error(f"Primary test flow failed: {str(e)}")
            return AgentResponse(
                agent_type=AgentType.ORCHESTRATOR,
                status="error",
                error_message=f"Primary test execution failed: {str(e)}",
            )
