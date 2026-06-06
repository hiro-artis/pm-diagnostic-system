"""End-to-end integration tests for complete diagnostic flow."""

import pytest
from src.agents.primary_test_orchestrator import PrimaryTestOrchestratorAgent
from src.agents.secondary_test_orchestrator import SecondaryTestOrchestratorAgent


# Sample test data
BASIC_KNOWLEDGE_ANSWERS = {
    "BK-001": "B", "BK-002": "D", "BK-003": "A", "BK-004": "B",
    "BK-005": "D", "BK-006": "B", "BK-007": "C", "BK-008": "B",
    "BK-009": "C", "BK-010": "D",
}

OFFICE_MIGRATION_MC_ANSWERS = {
    "OM-MC-001": "C", "OM-MC-002": "C", "OM-MC-003": "B",
    "OM-MC-004": "C", "OM-MC-005": "B",
}

OFFICE_MIGRATION_ESSAY_ANSWERS = {
    "OM-ES-001": """リスク分析：営業部の不在によるスケジュール遅延、企画部の繁忙により移転後の立ち上げ負荷。
対応策：営業部の事前説明会を開催し、代理人を指定。企画部への段階的なサポート体制を用意。
コミュニケーション：各部門の責任者と個別に懸念を聴取し、スケジュール調整を提案。""",
    "OM-ES-002": """判断プロセス：各部門の要望を詳しく聴取し、電気系統欠陥の影響範囲を明確化。
複数選択肢：1) 予定通り移転+部分的稼働 2) 5日延期+完全稼働
推奨案：予定日に営業部のみ移転し、IT関連は3日後に段階的移転。""",
    "OM-ES-003": """メンバーの不安解消のため、個別対話を重視し、プレビュー見学会を開催。
交流機会の創出として、ランチ会やチームビルディング実施。
プライバシー保護の具体的な工夫説明と、移転後の段階的フォローアップを実施。""",
}

MINDSET_ANSWERS = {
    "MS-S01": "C", "MS-S02": "C", "MS-S03": "C",
    "MS-S04": "B", "MS-S05": "C", "MS-S06": "C",  # MS-S04 correct answer is B
}

INTERVIEW_RESPONSES = {
    "1": "プロジェクト推進の際、長期的な視点から判断を変えた経験があります。",
    "2": "困難な状況では、自分の責任として問題解決に取り組みました。",
    "3": "チームメンバーの不安に丁寧に向き合うことを大切にしています。",
    "4": "相手の意見を真摯に理解しようとする姿勢を大切にしています。",
}


@pytest.fixture
def primary_orchestrator():
    """Create primary orchestrator instance."""
    return PrimaryTestOrchestratorAgent()


@pytest.fixture
def secondary_orchestrator():
    """Create secondary orchestrator instance."""
    return SecondaryTestOrchestratorAgent()


@pytest.mark.asyncio
async def test_complete_flow_primary_only(primary_orchestrator, secondary_orchestrator):
    """Test complete flow with primary test only (no secondary)."""
    # Run primary test
    primary_result = await primary_orchestrator.run_complete_primary_test(
        user_id="test_user_e2e_001",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS,
    )

    assert primary_result.status == "success"
    assert primary_result.result["passed"] is True
    assert primary_result.result["qualifies_for_secondary"] is True

    # Generate final assessment (primary only)
    session_id = primary_result.result["session_id"]
    primary_scores = primary_result.result["scores"]

    assessment_result = await secondary_orchestrator.generate_final_assessment(
        session_id=session_id,
        user_id="test_user_e2e_001",
        primary_results={
            "basic_knowledge_score": primary_scores["basic_knowledge"],
            "office_migration_score": primary_scores["office_migration"],
            "mindset_score": primary_scores["mindset"],
            "mindset_breakdown": {
                "future_focused": 85,
                "self_responsibility": 82,
                "kindness": 80,
                "listening_skill": 83,
                "inclusivity": 84,
                "collaboration": 81,
            },
        },
    )

    assert assessment_result.status == "success"
    assert "grade_level" in assessment_result.result
    assert assessment_result.result["grade_level"] in ["A", "B", "C", "再検査"]


@pytest.mark.asyncio
async def test_complete_flow_with_secondary(primary_orchestrator, secondary_orchestrator):
    """Test complete flow including secondary test (interview)."""
    # Run primary test
    primary_result = await primary_orchestrator.run_complete_primary_test(
        user_id="test_user_e2e_002",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS,
    )

    assert primary_result.status == "success"
    session_id = primary_result.result["session_id"]
    primary_mindset_scores = {
        "future_focused": 85,
        "self_responsibility": 82,
        "kindness": 80,
        "listening_skill": 83,
        "inclusivity": 84,
        "collaboration": 81,
    }

    # Run secondary test (interview)
    secondary_result = await secondary_orchestrator.run_complete_secondary_test(
        session_id=session_id,
        primary_mindset_scores=primary_mindset_scores,
        interview_responses=INTERVIEW_RESPONSES,
    )

    assert secondary_result.status == "success"
    assert secondary_result.result["interview_score"] >= 0

    # Generate final assessment with secondary results
    primary_scores = primary_result.result["scores"]
    assessment_result = await secondary_orchestrator.generate_final_assessment(
        session_id=session_id,
        user_id="test_user_e2e_002",
        primary_results={
            "basic_knowledge_score": primary_scores["basic_knowledge"],
            "office_migration_score": primary_scores["office_migration"],
            "mindset_score": primary_scores["mindset"],
            "mindset_breakdown": primary_mindset_scores,
        },
        secondary_results={"score": secondary_result.result["interview_score"]},
    )

    assert assessment_result.status == "success"
    assessment = assessment_result.result["assessment"]
    assert assessment["secondary_test_conducted"] is True
    assert assessment["interview_score"] is not None


@pytest.mark.asyncio
async def test_complete_flow_low_mindset(primary_orchestrator):
    """Test flow when mindset score is below secondary threshold."""
    # Create answers with low mindset score
    low_mindset_answers = {
        "MS-S01": "A", "MS-S02": "A", "MS-S03": "A",
        "MS-S04": "A", "MS-S05": "A", "MS-S06": "A",
    }

    primary_result = await primary_orchestrator.run_complete_primary_test(
        user_id="test_user_e2e_003",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=low_mindset_answers,
    )

    assert primary_result.status == "success"
    assert primary_result.result["qualifies_for_secondary"] is False


@pytest.mark.asyncio
async def test_data_persistence(primary_orchestrator, secondary_orchestrator):
    """Test that all data is properly persisted throughout flow."""
    # Run primary test
    primary_result = await primary_orchestrator.run_complete_primary_test(
        user_id="test_user_e2e_004",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS,
    )

    session_id = primary_result.result["session_id"]

    # Verify session exists
    session = primary_orchestrator.session_manager.get_session(session_id)
    assert session is not None
    assert session.user_id == "test_user_e2e_004"

    # Verify all results are stored
    all_results = primary_orchestrator.result_store.get_all_session_results(session_id)
    assert all_results["basic_knowledge"] is not None
    assert all_results["office_migration"] is not None
    assert all_results["mindset"] is not None


@pytest.mark.asyncio
async def test_multiple_users_parallel(primary_orchestrator):
    """Test handling multiple users in parallel (simulated)."""
    import asyncio

    # Create test tasks for 3 users
    tasks = [
        primary_orchestrator.run_complete_primary_test(
            user_id=f"test_user_parallel_{i}",
            basic_answers=BASIC_KNOWLEDGE_ANSWERS,
            office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS,
            office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
            mindset_answers=MINDSET_ANSWERS,
        )
        for i in range(3)
    ]

    # Run in parallel
    results = await asyncio.gather(*tasks)

    # Verify all completed successfully
    for result in results:
        assert result.status == "success"
        assert result.result["session_id"] is not None


@pytest.mark.asyncio
async def test_assessment_report_quality(primary_orchestrator, secondary_orchestrator):
    """Test that final assessment report is comprehensive and meaningful."""
    primary_result = await primary_orchestrator.run_complete_primary_test(
        user_id="test_user_e2e_005",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS,
    )

    session_id = primary_result.result["session_id"]
    primary_scores = primary_result.result["scores"]

    assessment_result = await secondary_orchestrator.generate_final_assessment(
        session_id=session_id,
        user_id="test_user_e2e_005",
        primary_results={
            "basic_knowledge_score": primary_scores["basic_knowledge"],
            "office_migration_score": primary_scores["office_migration"],
            "mindset_score": primary_scores["mindset"],
            "mindset_breakdown": {
                "future_focused": 75,
                "self_responsibility": 72,
                "kindness": 78,
                "listening_skill": 70,
                "inclusivity": 76,
                "collaboration": 74,
            },
        },
    )

    assert assessment_result.status == "success"
    assessment = assessment_result.result["assessment"]

    # Verify comprehensive report
    assert assessment["total_score"] > 0
    assert assessment["grade_level"] is not None
    assert assessment["summary"] is not None and len(assessment["summary"]) > 0
    assert len(assessment["strengths"]) > 0
    assert len(assessment["development_areas"]) > 0
    assert len(assessment["recommendations"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
