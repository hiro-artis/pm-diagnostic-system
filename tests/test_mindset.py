"""Tests for mindset test agent."""

import pytest
from src.agents.mindset_test import MindsetTestAgent
from src.utils.scoring_logic import calculate_mindset_scores


@pytest.fixture
def agent():
    """Create agent instance."""
    return MindsetTestAgent()


@pytest.mark.asyncio
async def test_get_scenarios(agent):
    """Test getting mindset scenarios."""
    response = await agent.execute({
        "session_id": "test_session_001",
    })

    assert response.status == "success"
    assert "scenarios" in response.result
    assert len(response.result["scenarios"]) == 6


@pytest.mark.asyncio
async def test_score_test_all_correct(agent):
    """Test scoring with all correct answers."""
    user_answers = {
        "MS-S01": "C",  # Correct
        "MS-S02": "C",  # Correct
        "MS-S03": "C",  # Correct
        "MS-S04": "B",  # Correct
        "MS-S05": "C",  # Correct
        "MS-S06": "C",  # Correct
    }

    response = await agent.execute({
        "session_id": "test_session_002",
        "user_answers": user_answers,
    })

    assert response.status == "success"
    assert response.result["total_score"] >= 90  # Very high score
    assert response.result["passed"] is True
    assert response.result["qualifies_for_secondary"] is True


@pytest.mark.asyncio
async def test_score_test_mixed_answers(agent):
    """Test scoring with mixed correct and incorrect answers."""
    user_answers = {
        "MS-S01": "C",  # Correct
        "MS-S02": "A",  # Incorrect
        "MS-S03": "C",  # Correct
        "MS-S04": "B",  # Correct
        "MS-S05": "A",  # Incorrect
        "MS-S06": "C",  # Correct
    }

    response = await agent.execute({
        "session_id": "test_session_003",
        "user_answers": user_answers,
    })

    assert response.status == "success"
    assert response.result["total_score"] > 0
    assert "mindset_scores" in response.result


@pytest.mark.asyncio
async def test_score_calculation():
    """Test mindset score calculation logic."""
    user_answers = {
        "MS-S01": "C",
        "MS-S02": "C",
        "MS-S03": "C",
        "MS-S04": "B",  # Correct answer for scenario 4
        "MS-S05": "C",
        "MS-S06": "C",
    }

    scores = calculate_mindset_scores(user_answers)

    assert "total_score" in scores
    assert "future_focused" in scores
    assert "self_responsibility" in scores
    assert "kindness" in scores
    assert "listening_skill" in scores
    assert "inclusivity" in scores
    assert "collaboration" in scores

    # All scores should be 0-100
    for score in scores.values():
        assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_qualifies_for_secondary_test(agent):
    """Test qualification for secondary test."""
    # High score - qualifies
    high_score_answers = {
        "MS-S01": "C",
        "MS-S02": "C",
        "MS-S03": "C",
        "MS-S04": "C",
        "MS-S05": "C",
        "MS-S06": "C",
    }

    response = await agent.execute({
        "session_id": "test_session_004",
        "user_answers": high_score_answers,
    })

    assert response.result["qualifies_for_secondary"] is True

    # Low score - does not qualify
    low_score_answers = {
        "MS-S01": "A",
        "MS-S02": "A",
        "MS-S03": "A",
        "MS-S04": "A",
        "MS-S05": "A",
        "MS-S06": "A",
    }

    response = await agent.execute({
        "session_id": "test_session_005",
        "user_answers": low_score_answers,
    })

    assert response.result["qualifies_for_secondary"] is False


@pytest.mark.asyncio
async def test_missing_session_id(agent):
    """Test error handling when session_id is missing."""
    response = await agent.execute({})

    assert response.status == "error"
    assert "session_id is required" in response.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
