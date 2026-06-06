"""Tests for orchestrator agent."""

import pytest
import asyncio
from src.agents.orchestrator import OrchestratorAgent
from src.models.schemas import TestStatus


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return OrchestratorAgent()


@pytest.mark.asyncio
async def test_start_primary_test(orchestrator):
    """Test starting a primary test."""
    response = await orchestrator.execute({
        "action": "start_primary_test",
        "user_id": "test_user_001",
    })

    assert response.status == "success"
    assert "session_id" in response.result
    assert response.result["next_action"] == "run_basic_knowledge_test"


@pytest.mark.asyncio
async def test_start_primary_test_missing_user_id(orchestrator):
    """Test starting a primary test without user_id."""
    response = await orchestrator.execute({
        "action": "start_primary_test",
    })

    assert response.status == "error"
    assert "user_id is required" in response.error_message


@pytest.mark.asyncio
async def test_get_session_info(orchestrator):
    """Test retrieving session info."""
    # Start a test first
    start_response = await orchestrator.execute({
        "action": "start_primary_test",
        "user_id": "test_user_002",
    })

    session_id = start_response.result["session_id"]

    # Get session info
    session = orchestrator.get_session_info(session_id)

    assert session is not None
    assert session.session_id == session_id
    assert session.user_id == "test_user_002"
    assert session.status == TestStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_unknown_action(orchestrator):
    """Test unknown action."""
    response = await orchestrator.execute({
        "action": "unknown_action",
    })

    assert response.status == "error"
    assert "Unknown action" in response.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
