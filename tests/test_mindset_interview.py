"""Tests for mindset interview agent."""

import pytest
from src.agents.mindset_interview import MindsetInterviewAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    return MindsetInterviewAgent()


@pytest.mark.asyncio
async def test_get_interview_questions(agent):
    """Test getting interview questions."""
    response = await agent.execute({
        "action": "get_questions",
        "session_id": "test_session_001",
        "primary_mindset_scores": {
            "future_focused": 75,
            "self_responsibility": 55,
            "kindness": 70,
            "listening_skill": 50,
            "inclusivity": 60,
            "collaboration": 80,
        },
    })

    assert response.status == "success"
    assert "questions" in response.result
    assert response.result["total_questions"] > 0
    assert len(response.result["focus_areas"]) > 0  # Should identify weak areas


@pytest.mark.asyncio
async def test_get_interview_questions_all_strong(agent):
    """Test when all mindsets are strong."""
    response = await agent.execute({
        "action": "get_questions",
        "session_id": "test_session_002",
        "primary_mindset_scores": {
            "future_focused": 85,
            "self_responsibility": 80,
            "kindness": 90,
            "listening_skill": 85,
            "inclusivity": 88,
            "collaboration": 82,
        },
    })

    assert response.status == "success"
    assert "questions" in response.result
    assert response.result["total_questions"] > 0
    # Focus areas should be empty or minimal
    assert len(response.result["focus_areas"]) == 0


@pytest.mark.asyncio
async def test_score_interview(agent):
    """Test scoring interview responses."""
    response = await agent.execute({
        "action": "score_interview",
        "session_id": "test_session_003",
        "primary_mindset_result": {
            "future_focused": 70,
            "self_responsibility": 65,
            "kindness": 75,
            "listening_skill": 60,
            "inclusivity": 70,
            "collaboration": 75,
        },
        "interview_responses": {
            "1": "プロジェクト推進の際、長期的な視点から判断を変えた経験があります。当初の短期的な利益ではなく、3年後の顧客満足度を重視する戦略に切り替えました。",
            "2": "困難な状況では、自分の責任として問題を解決しました。チーム全体に説明し、一緒に改善案を探りました。",
            "3": "相手の意見と異なる場合、相手の立場を理解することに注力しました。聴く姿勢を大切にしています。",
        },
    })

    assert response.status == "success"
    assert "test_result" in response.result
    assert response.result["total_score"] >= 0
    assert "revised_mindset_scores" in response.result


@pytest.mark.asyncio
async def test_score_interview_weak_responses(agent):
    """Test scoring with weak responses."""
    response = await agent.execute({
        "action": "score_interview",
        "session_id": "test_session_004",
        "primary_mindset_result": {
            "future_focused": 50,
            "self_responsibility": 55,
            "kindness": 50,
            "listening_skill": 45,
            "inclusivity": 50,
            "collaboration": 55,
        },
        "interview_responses": {
            "1": "特に経験はありません。",
            "2": "わかりません。",
            "3": "通常通り進めるだけです。",
        },
    })

    assert response.status == "success"
    assert response.result["total_score"] >= 0


@pytest.mark.asyncio
async def test_missing_session_id(agent):
    """Test error handling when session_id is missing."""
    response = await agent.execute({
        "action": "get_questions",
    })

    assert response.status == "error"
    assert "session_id is required" in response.error_message


@pytest.mark.asyncio
async def test_unknown_action(agent):
    """Test error handling for unknown action."""
    response = await agent.execute({
        "action": "unknown_action",
        "session_id": "test_session_005",
    })

    assert response.status == "error"
    assert "Unknown action" in response.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
