"""Session management for diagnostic tests."""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import logging

from src.models.schemas import SessionInfo, TestStatus, TestPhase, AgentType


logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions and their state."""

    def __init__(self, storage_path: str = "data/sessions"):
        """Initialize session manager.

        Args:
            storage_path: Path to store session data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_session(
        self,
        user_id: str,
        timeout_seconds: int = 3600,
    ) -> SessionInfo:
        """Create a new session.

        Args:
            user_id: User identifier
            timeout_seconds: Session timeout in seconds

        Returns:
            SessionInfo with new session
        """
        session_id = str(uuid.uuid4())
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            timeout_seconds=timeout_seconds,
            status=TestStatus.NOT_STARTED,
            current_phase=TestPhase.PRIMARY,
        )

        self._save_session(session)
        logger.info(f"Created session {session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionInfo if found, None otherwise
        """
        session_file = self.storage_path / f"{session_id}.json"

        if not session_file.exists():
            logger.warning(f"Session {session_id} not found")
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionInfo(**data)
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None

    def update_session(self, session: SessionInfo) -> bool:
        """Update session information.

        Args:
            session: Updated SessionInfo

        Returns:
            True if successful, False otherwise
        """
        try:
            self._save_session(session)
            logger.info(f"Updated session {session.session_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            return False

    def update_session_status(
        self,
        session_id: str,
        status: TestStatus,
        current_test_agent: Optional[AgentType] = None,
    ) -> bool:
        """Update session status.

        Args:
            session_id: Session identifier
            status: New status
            current_test_agent: Current test agent (optional)

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = status
        if current_test_agent:
            session.current_test_agent = current_test_agent

        if status == TestStatus.IN_PROGRESS and not session.started_at:
            session.started_at = datetime.utcnow()
        elif status == TestStatus.COMPLETED:
            session.ended_at = datetime.utcnow()

        return self.update_session(session)

    def advance_to_secondary_test(self, session_id: str) -> bool:
        """Advance session to secondary test phase.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.current_phase = TestPhase.SECONDARY
        return self.update_session(session)

    def complete_test(self, session_id: str) -> bool:
        """Mark test as completed.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = TestStatus.COMPLETED
        session.current_phase = TestPhase.COMPLETED
        session.ended_at = datetime.utcnow()
        return self.update_session(session)

    def is_session_expired(self, session_id: str) -> bool:
        """Check if session has expired.

        Args:
            session_id: Session identifier

        Returns:
            True if expired, False otherwise
        """
        session = self.get_session(session_id)
        if not session or not session.started_at:
            return False

        elapsed = datetime.utcnow() - session.started_at
        return elapsed.total_seconds() > session.timeout_seconds

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from storage.

        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_file in self.storage_path.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = SessionInfo(**data)

                if self.is_session_expired(session.session_id):
                    session_file.unlink()
                    count += 1
                    logger.info(f"Cleaned up expired session {session.session_id}")
            except Exception as e:
                logger.error(f"Error cleaning session {session_file}: {str(e)}")

        return count

    def _save_session(self, session: SessionInfo) -> None:
        """Internal method to save session to disk.

        Args:
            session: SessionInfo to save
        """
        session_file = self.storage_path / f"{session.session_id}.json"
        data = session.model_dump(mode="json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
