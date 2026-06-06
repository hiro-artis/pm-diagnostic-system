"""Test orchestrator agent - manages overall test flow."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.models.schemas import (
    AgentType,
    AgentResponse,
    TestPhase,
    TestStatus,
    SessionInfo,
)
from src.storage.session_manager import SessionManager
from src.storage.result_store import ResultStore


logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrates the entire test flow and coordinates other agents."""

    def __init__(self):
        """Initialize orchestrator agent."""
        super().__init__(AgentType.ORCHESTRATOR)
        self.session_manager = SessionManager()
        self.result_store = ResultStore()

    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute orchestrator logic based on action.

        Args:
            payload: Input containing action and parameters

        Returns:
            AgentResponse with execution result
        """
        try:
            action = payload.get("action")

            if action == "start_primary_test":
                return await self._start_primary_test(payload)
            elif action == "check_primary_results":
                return await self._check_primary_results(payload)
            elif action == "start_secondary_test":
                return await self._start_secondary_test(payload)
            elif action == "finalize":
                return await self._finalize_test(payload)
            else:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message=f"Unknown action: {action}",
                )
        except Exception as e:
            return await self.handle_error(e, "Orchestrator execution failed")

    async def _start_primary_test(self, payload: Dict[str, Any]) -> AgentResponse:
        """Start primary test (1次テスト).

        Args:
            payload: Contains user_id and optional test config

        Returns:
            AgentResponse with session info and first test agent
        """
        try:
            user_id = payload.get("user_id")
            if not user_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="user_id is required",
                )

            # Create new session
            session = self.session_manager.create_session(user_id)

            # Update session status to in progress
            self.session_manager.update_session_status(
                session.session_id,
                TestStatus.IN_PROGRESS,
                AgentType.BASIC_KNOWLEDGE,
            )

            self.log_info(f"Started primary test for user {user_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session.session_id,
                    "user_id": user_id,
                    "next_action": "run_basic_knowledge_test",
                    "message": "Primary test started. Beginning with basic knowledge test.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to start primary test")

    async def _check_primary_results(self, payload: Dict[str, Any]) -> AgentResponse:
        """Check if all primary tests passed and determine next action.

        Args:
            payload: Contains session_id

        Returns:
            AgentResponse with verdict and next action
        """
        try:
            session_id = payload.get("session_id")
            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            # Get all results for this session
            all_results = self.result_store.get_all_session_results(session_id)

            # Check if all primary tests completed
            tests_completed = {
                "basic_knowledge": all_results["basic_knowledge"] is not None,
                "office_migration": all_results["office_migration"] is not None,
                "mindset": all_results["mindset"] is not None,
            }

            if not all(tests_completed.values()):
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="Not all primary tests completed",
                )

            # Check if all passed
            basic_passed = all_results["basic_knowledge"].passed if all_results["basic_knowledge"] else False
            office_passed = all_results["office_migration"].passed if all_results["office_migration"] else False
            mindset_passed = all_results["mindset"].passed if all_results["mindset"] else False

            all_passed = basic_passed and office_passed and mindset_passed

            # Check if qualifies for secondary test (mindset >= 60)
            mindset_score = all_results["mindset"].score if all_results["mindset"] else 0
            qualifies_for_secondary = mindset_score >= 60

            self.log_info(
                f"Primary test check: all_passed={all_passed}, "
                f"qualifies_for_secondary={qualifies_for_secondary}"
            )

            if all_passed and qualifies_for_secondary:
                next_action = "start_secondary_test"
            elif all_passed:
                next_action = "finalize"
            else:
                next_action = "schedule_retake"

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "all_passed": all_passed,
                    "qualifies_for_secondary": qualifies_for_secondary,
                    "scores": {
                        "basic_knowledge": all_results["basic_knowledge"].score if all_results["basic_knowledge"] else 0,
                        "office_migration": all_results["office_migration"].score if all_results["office_migration"] else 0,
                        "mindset": mindset_score,
                    },
                    "next_action": next_action,
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to check primary results")

    async def _start_secondary_test(self, payload: Dict[str, Any]) -> AgentResponse:
        """Start secondary test (2次テスト - face-to-face interview).

        Args:
            payload: Contains session_id

        Returns:
            AgentResponse with next test agent
        """
        try:
            session_id = payload.get("session_id")
            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            # Advance to secondary test phase
            if not self.session_manager.advance_to_secondary_test(session_id):
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="Failed to advance to secondary test",
                )

            # Update session with mindset interview agent
            self.session_manager.update_session_status(
                session_id,
                TestStatus.IN_PROGRESS,
                AgentType.MINDSET_INTERVIEW,
            )

            self.log_info(f"Started secondary test for session {session_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "next_action": "run_mindset_interview",
                    "message": "Congratulations! You qualified for the secondary test. "
                    "We will now conduct a face-to-face interview to verify your mindset.",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to start secondary test")

    async def _finalize_test(self, payload: Dict[str, Any]) -> AgentResponse:
        """Finalize test and generate final assessment.

        Args:
            payload: Contains session_id

        Returns:
            AgentResponse with final assessment
        """
        try:
            session_id = payload.get("session_id")
            if not session_id:
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="session_id is required",
                )

            # Mark test as completed
            if not self.session_manager.complete_test(session_id):
                return AgentResponse(
                    agent_type=self.agent_type,
                    status="error",
                    error_message="Failed to complete test",
                )

            # TODO: Generate final assessment (will be implemented in comprehensive scorer)
            # For now, return completion status

            self.log_info(f"Finalized test for session {session_id}")

            return AgentResponse(
                agent_type=self.agent_type,
                status="success",
                result={
                    "session_id": session_id,
                    "next_action": "generate_final_report",
                    "message": "Test completed. Generating final assessment...",
                },
            )
        except Exception as e:
            return await self.handle_error(e, "Failed to finalize test")

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get current session information.

        Args:
            session_id: Session identifier

        Returns:
            SessionInfo if found, None otherwise
        """
        return self.session_manager.get_session(session_id)

    def is_session_active(self, session_id: str) -> bool:
        """Check if session is still active (not expired).

        Args:
            session_id: Session identifier

        Returns:
            True if active, False if expired or not found
        """
        if self.session_manager.is_session_expired(session_id):
            self.log_info(f"Session {session_id} has expired")
            return False
        return True
