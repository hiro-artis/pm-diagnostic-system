"""Base agent class for all diagnostic agents."""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import logging

from src.models.schemas import AgentType, AgentMessage, AgentResponse


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, agent_type: AgentType):
        """Initialize base agent.

        Args:
            agent_type: Type of agent (from AgentType enum)
        """
        self.agent_type = agent_type
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> AgentResponse:
        """Execute agent's main logic.

        Args:
            payload: Input data for the agent

        Returns:
            AgentResponse with result or error
        """
        pass

    async def send_message(
        self,
        to_agent: Optional[AgentType],
        message_type: str,
        payload: Dict[str, Any],
        priority: str = "normal",
    ) -> AgentMessage:
        """Send message to another agent.

        Args:
            to_agent: Target agent type
            message_type: Type of message
            payload: Message payload
            priority: Message priority (high/normal/low)

        Returns:
            AgentMessage sent
        """
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_type,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            priority=priority,
        )
        logger.info(
            f"Agent {self.agent_type} sending message to {to_agent}: {message_type}"
        )
        return message

    async def handle_error(
        self,
        error: Exception,
        context: str = "",
    ) -> AgentResponse:
        """Handle agent errors gracefully.

        Args:
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            AgentResponse with error information
        """
        error_message = f"{context}: {str(error)}" if context else str(error)
        logger.error(f"Agent {self.agent_type} error: {error_message}")

        return AgentResponse(
            agent_type=self.agent_type,
            status="error",
            error_message=error_message,
        )

    def log_info(self, message: str) -> None:
        """Log info message."""
        logger.info(f"[{self.agent_type}] {message}")

    def log_error(self, message: str) -> None:
        """Log error message."""
        logger.error(f"[{self.agent_type}] {message}")

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        logger.debug(f"[{self.agent_type}] {message}")
