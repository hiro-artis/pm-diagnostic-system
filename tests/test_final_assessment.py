"""Tests for final assessment agent."""

import pytest
from src.agents.final_assessment import FinalAssessmentAgent


@pytest.fixture
def agent():
    """Create agent instance."""
    return FinalAssessmentAgent()


@pytest.mark.asyncio
async def test_generate_assessment_grade_a(agent):
    """Test generating assessment with Grade A."""
    response = await agent.execute({
        "session_id": "test_session_001",
        "user_id": "test_user_001",
        "primary_results": {
            "basic_knowledge_score": 95,
            "office_migration_score": 88,
            "mindset_score": 85,
            "mindset_breakdown": {
                "future_focused": 88,
                "self_responsibility": 85,
                "kindness": 82,
                "listening_skill": 87,
                "inclusivity": 86,
                "collaboration": 84,
            },
        },
    })

    assert response.status == "success"
    assert response.result["grade_level"] == "A"
    assert response.result["total_score"] >= 80


@pytest.mark.asyncio
async def test_generate_assessment_grade_b(agent):
    """Test generating assessment with Grade B."""
    response = await agent.execute({
        "session_id": "test_session_002",
        "user_id": "test_user_002",
        "primary_results": {
            "basic_knowledge_score": 78,
            "office_migration_score": 72,
            "mindset_score": 75,
            "mindset_breakdown": {
                "future_focused": 75,
                "self_responsibility": 70,
                "kindness": 78,
                "listening_skill": 72,
                "inclusivity": 76,
                "collaboration": 74,
            },
        },
    })

    assert response.status == "success"
    assert response.result["grade_level"] == "B"


@pytest.mark.asyncio
async def test_generate_assessment_grade_c(agent):
    """Test generating assessment with Grade C."""
    response = await agent.execute({
        "session_id": "test_session_003",
        "user_id": "test_user_003",
        "primary_results": {
            "basic_knowledge_score": 65,
            "office_migration_score": 62,
            "mindset_score": 65,
            "mindset_breakdown": {
                "future_focused": 62,
                "self_responsibility": 65,
                "kindness": 60,
                "listening_skill": 68,
                "inclusivity": 64,
                "collaboration": 66,
            },
        },
    })

    assert response.status == "success"
    assert response.result["grade_level"] == "C"


@pytest.mark.asyncio
async def test_generate_assessment_with_secondary_test(agent):
    """Test generating assessment with secondary test results."""
    response = await agent.execute({
        "session_id": "test_session_004",
        "user_id": "test_user_004",
        "primary_results": {
            "basic_knowledge_score": 80,
            "office_migration_score": 75,
            "mindset_score": 72,
            "mindset_breakdown": {
                "future_focused": 70,
                "self_responsibility": 75,
                "kindness": 72,
                "listening_skill": 68,
                "inclusivity": 74,
                "collaboration": 72,
            },
        },
        "secondary_results": {
            "score": 78,
        },
    })

    assert response.status == "success"
    assert response.result["assessment"]["secondary_test_conducted"] is True
    assert response.result["assessment"]["interview_score"] == 78


@pytest.mark.asyncio
async def test_generate_assessment_low_mindset(agent):
    """Test generating assessment with low mindset score."""
    response = await agent.execute({
        "session_id": "test_session_005",
        "user_id": "test_user_005",
        "primary_results": {
            "basic_knowledge_score": 85,
            "office_migration_score": 80,
            "mindset_score": 55,  # Below 60 threshold
            "mindset_breakdown": {
                "future_focused": 50,
                "self_responsibility": 55,
                "kindness": 58,
                "listening_skill": 52,
                "inclusivity": 56,
                "collaboration": 54,
            },
        },
    })

    assert response.status == "success"
    assert response.result["grade_level"] == "再検査"  # Below mindset threshold


@pytest.mark.asyncio
async def test_missing_required_fields(agent):
    """Test error handling for missing required fields."""
    response = await agent.execute({
        # Missing user_id
        "session_id": "test_session_006",
        "primary_results": {},
    })

    assert response.status == "error"
    assert "user_id is required" in response.error_message


@pytest.mark.asyncio
async def test_assessment_contains_strengths_and_areas(agent):
    """Test that assessment includes strengths and development areas."""
    response = await agent.execute({
        "session_id": "test_session_007",
        "user_id": "test_user_007",
        "primary_results": {
            "basic_knowledge_score": 75,
            "office_migration_score": 70,
            "mindset_score": 72,
            "mindset_breakdown": {
                "future_focused": 80,  # Strength
                "self_responsibility": 65,  # Development
                "kindness": 75,
                "listening_skill": 70,
                "inclusivity": 72,
                "collaboration": 68,
            },
        },
    })

    assert response.status == "success"
    assessment = response.result["assessment"]
    assert "strengths" in assessment
    assert "development_areas" in assessment
    assert len(assessment["strengths"]) > 0
    assert len(assessment["development_areas"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
