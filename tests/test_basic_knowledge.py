"""Tests for basic knowledge test agent."""

import pytest
from src.agents.basic_knowledge_test import BasicKnowledgeTestAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    return BasicKnowledgeTestAgent()


@pytest.mark.asyncio
async def test_get_test_questions(agent):
    """Test getting test questions."""
    response = await agent.execute({
        "action": "get_questions",
        "session_id": "test_session_001",
    })

    assert response.status == "success"
    assert "questions" in response.result
    assert len(response.result["questions"]) > 0
    assert response.result["total_questions"] == 10


@pytest.mark.asyncio
async def test_score_test_all_correct(agent):
    """Test scoring with all correct answers."""
    # First get questions
    get_response = await agent.execute({
        "action": "get_questions",
        "session_id": "test_session_002",
    })

    # Score test with all correct answers
    user_answers = {
        "BK-001": "B",
        "BK-002": "D",
        "BK-003": "A",
        "BK-004": "B",
        "BK-005": "D",
        "BK-006": "B",
        "BK-007": "C",
        "BK-008": "B",
        "BK-009": "C",
        "BK-010": "D",
    }

    response = await agent.execute({
        "action": "score_test",
        "session_id": "test_session_002",
        "user_answers": user_answers,
    })

    assert response.status == "success"
    assert response.result["score"] == 100
    assert response.result["passed"] is True


@pytest.mark.asyncio
async def test_score_test_partial_correct(agent):
    """Test scoring with partial correct answers."""
    user_answers = {
        "BK-001": "B",
        "BK-002": "D",
        "BK-003": "A",
        "BK-004": "B",
        "BK-005": "D",
        "BK-006": "A",  # Wrong
        "BK-007": "A",  # Wrong
        "BK-008": "B",
        "BK-009": "C",
        "BK-010": "D",
    }

    response = await agent.execute({
        "action": "score_test",
        "session_id": "test_session_003",
        "user_answers": user_answers,
    })

    assert response.status == "success"
    assert response.result["score"] == 80  # 8 correct = 80 points
    assert response.result["passed"] is True


@pytest.mark.asyncio
async def test_score_test_below_threshold(agent):
    """Test scoring below passing threshold."""
    user_answers = {
        "BK-001": "B",
        "BK-002": "D",
        "BK-003": "A",
        "BK-004": "A",  # Wrong
        "BK-005": "A",  # Wrong
        "BK-006": "A",  # Wrong
        "BK-007": "A",  # Wrong
        "BK-008": "B",
        "BK-009": "C",
        "BK-010": "D",
    }

    response = await agent.execute({
        "action": "score_test",
        "session_id": "test_session_004",
        "user_answers": user_answers,
    })

    assert response.status == "success"
    assert response.result["score"] == 60  # 6 correct = 60 points
    assert response.result["passed"] is False


@pytest.mark.asyncio
async def test_missing_session_id(agent):
    """Test error handling when session_id is missing."""
    response = await agent.execute({})

    assert response.status == "error"
    assert "session_id is required" in response.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
