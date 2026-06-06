"""Tests for comprehensive scorer agent."""

import pytest
from src.agents.comprehensive_scorer import ComprehensiveScorerAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    return ComprehensiveScorerAgent()


@pytest.mark.asyncio
async def test_score_essay_good_quality(agent):
    """Test scoring a good quality essay."""
    response = await agent.execute({
        "action": "score_essay",
        "question_id": "OM-ES-001",
        "essay_text": """リスク分析：営業部の不在によるスケジュール遅延、企画部の繁忙により移転後の立ち上げ負荷。
対応策：営業部の事前説明会を開催し、代理人を指定。企画部への段階的なサポート体制を用意。
コミュニケーション：各部門の責任者と個別に懸念を聴取し、スケジュール調整を提案。
什器納期遅延への対応として、一部は代替品で一時対応し、段階的に正規品への交換を進める。""",
        "evaluation_criteria": {
            "リスク認識": {"max_score": 5},
            "対応策の実現性": {"max_score": 10},
            "コミュニケーション": {"max_score": 10},
        },
    })

    assert response.status == "success"
    assert "score" in response.result
    assert 0 <= response.result["score"] <= 25


@pytest.mark.asyncio
async def test_score_essay_poor_quality(agent):
    """Test scoring a poor quality essay."""
    response = await agent.execute({
        "action": "score_essay",
        "question_id": "OM-ES-001",
        "essay_text": "対応が必要です。",  # Very short
        "evaluation_criteria": {
            "リスク認識": {"max_score": 5},
            "対応策の実現性": {"max_score": 10},
            "コミュニケーション": {"max_score": 10},
        },
    })

    assert response.status == "success"
    assert response.result["score"] < 15


@pytest.mark.asyncio
async def test_score_office_migration_complete(agent):
    """Test scoring complete office migration test."""
    test_result = {
        "test_id": "OM_test123",
        "session_id": "session123",
        "test_agent": "office_migration_test",
        "score": 25,
        "total_points": 100,
        "passed": False,
        "start_time": "2026-06-06T10:00:00",
        "end_time": "2026-06-06T10:30:00",
        "time_spent_seconds": 1800,
        "mc_score": 25,
        "essay_score": 0,
        "questions": [
            {
                "question_id": "OM-MC-001",
                "answer_text": "",
                "user_answer": "C",
                "score": 5,
            },
            {
                "question_id": "OM-MC-002",
                "answer_text": "",
                "user_answer": "C",
                "score": 5,
            },
            {
                "question_id": "OM-MC-003",
                "answer_text": "",
                "user_answer": "B",
                "score": 5,
            },
            {
                "question_id": "OM-MC-004",
                "answer_text": "",
                "user_answer": "C",
                "score": 5,
            },
            {
                "question_id": "OM-MC-005",
                "answer_text": "",
                "user_answer": "B",
                "score": 5,
            },
            {
                "question_id": "OM-ES-001",
                "answer_text": "長めの回答テキスト。リスク分析と対応策を含めた内容。",
                "score": 0,
            },
            {
                "question_id": "OM-ES-002",
                "answer_text": "判断プロセスと検討事項についての記述。",
                "score": 0,
            },
            {
                "question_id": "OM-ES-003",
                "answer_text": "施策の具体的な内容について説明している。",
                "score": 0,
            },
        ],
    }

    essay_answers = {
        "OM-ES-001": "リスク分析と対応策の詳細な説明。",
        "OM-ES-002": "判断プロセスと複数の選択肢の検討。",
        "OM-ES-003": "メンバー不安への対応と具体的な施策。",
    }

    response = await agent.execute({
        "action": "score_office_migration",
        "test_result": test_result,
        "essay_answers": essay_answers,
    })

    assert response.status == "success"
    assert "test_result" in response.result
    assert response.result["essay_score"] > 0
    assert response.result["total_score"] > 25


@pytest.mark.asyncio
async def test_missing_required_fields(agent):
    """Test error handling for missing required fields."""
    response = await agent.execute({
        "action": "score_essay",
        # Missing question_id
        "essay_text": "Some essay text",
    })

    assert response.status == "error"


@pytest.mark.asyncio
async def test_unknown_action(agent):
    """Test error handling for unknown action."""
    response = await agent.execute({
        "action": "unknown_action",
    })

    assert response.status == "error"
    assert "Unknown action" in response.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
