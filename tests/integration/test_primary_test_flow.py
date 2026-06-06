"""Integration tests for primary test flow."""

import pytest
from src.agents.primary_test_orchestrator import PrimaryTestOrchestratorAgent


@pytest.fixture
def orchestrator():
    """Create primary test orchestrator instance."""
    return PrimaryTestOrchestratorAgent()


# Sample test data
BASIC_KNOWLEDGE_ANSWERS_PASS = {
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

OFFICE_MIGRATION_MC_ANSWERS_PASS = {
    "OM-MC-001": "C",
    "OM-MC-002": "C",
    "OM-MC-003": "B",
    "OM-MC-004": "C",
    "OM-MC-005": "B",
}

OFFICE_MIGRATION_ESSAY_ANSWERS = {
    "OM-ES-001": """リスク分析：営業部の不在によるスケジュール遅延、企画部の繁忙により移転後の立ち上げ負荷。
対応策：営業部の事前説明会を開催し、代理人を指定。企画部への段階的なサポート体制を用意。
コミュニケーション：各部門の責任者と個別に懸念を聴取し、スケジュール調整を提案。
什器納期遅延への対応として、一部は代替品で一時対応し、段階的に正規品への交換を進める。""",
    "OM-ES-002": """状況分析：経営層、営業部、IT部門の利益が相反している。
判断プロセス：各部門の要望を詳しく聴取し、電気系統欠陥の影響範囲を明確化。
選択肢検討：
1) 予定通り移転＋部分的稼働（IT部門と相談で最小限の稼働）
2) 5日延期＋完全稼働（経営層への説得）
推奨案：予定日に営業部のみ移転し、IT関連は3日後に段階的移転。
関係者への説明：各立場の懸念を認め、スケジュール調整の必要性を経営層に報告。""",
    "OM-ES-003": """不安への向き合い：メンバーの心理的な距離感への懸念を理解し、個別対話を重視。
施策案：
1) 新配置前のプレビュー見学会開催
2) 交流機会の意図的創出（ランチ会、チームビルディング）
3) プライバシー保護の具体的な工夫説明（パーティション、ルール明記）
4) 移転後2週間のフォローアップ確認
長期支援：部門間協力体制の段階的構築を、メンバーの声を聴きながら進める。""",
}

MINDSET_ANSWERS_PASS = {
    "MS-S01": "C",
    "MS-S02": "C",
    "MS-S03": "C",
    "MS-S04": "C",
    "MS-S05": "C",
    "MS-S06": "C",
}

MINDSET_ANSWERS_FAIL = {
    "MS-S01": "A",
    "MS-S02": "A",
    "MS-S03": "A",
    "MS-S04": "A",
    "MS-S05": "A",
    "MS-S06": "A",
}


@pytest.mark.asyncio
async def test_primary_test_flow_all_pass(orchestrator):
    """Test complete primary test flow with all tests passing."""
    response = await orchestrator.run_complete_primary_test(
        user_id="test_user_001",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS_PASS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS_PASS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS_PASS,
    )

    assert response.status == "success"
    assert response.result["passed"] is True
    assert response.result["qualifies_for_secondary"] is True
    assert response.result["scores"]["basic_knowledge"] >= 70
    assert response.result["scores"]["office_migration"] >= 65
    assert response.result["scores"]["mindset"] >= 60


@pytest.mark.asyncio
async def test_primary_test_flow_mindset_fail(orchestrator):
    """Test primary test flow with mindset test failing."""
    response = await orchestrator.run_complete_primary_test(
        user_id="test_user_002",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS_PASS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS_PASS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS_FAIL,
    )

    assert response.status == "success"
    assert response.result["qualifies_for_secondary"] is False
    assert response.result["scores"]["mindset"] < 60


@pytest.mark.asyncio
async def test_primary_test_flow_session_created(orchestrator):
    """Test that session is properly created during test flow."""
    response = await orchestrator.run_complete_primary_test(
        user_id="test_user_003",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS_PASS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS_PASS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS_PASS,
    )

    assert response.status == "success"
    assert "session_id" in response.result

    # Verify session exists
    session_id = response.result["session_id"]
    session = orchestrator.session_manager.get_session(session_id)
    assert session is not None
    assert session.user_id == "test_user_003"


@pytest.mark.asyncio
async def test_primary_test_flow_results_stored(orchestrator):
    """Test that all test results are properly stored."""
    response = await orchestrator.run_complete_primary_test(
        user_id="test_user_004",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS_PASS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS_PASS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS_PASS,
    )

    assert response.status == "success"
    session_id = response.result["session_id"]

    # Verify all results are stored
    all_results = orchestrator.result_store.get_all_session_results(session_id)
    assert all_results["basic_knowledge"] is not None
    assert all_results["office_migration"] is not None
    assert all_results["mindset"] is not None


@pytest.mark.asyncio
async def test_primary_test_score_calculation(orchestrator):
    """Test that scores are calculated correctly."""
    response = await orchestrator.run_complete_primary_test(
        user_id="test_user_005",
        basic_answers=BASIC_KNOWLEDGE_ANSWERS_PASS,
        office_mc_answers=OFFICE_MIGRATION_MC_ANSWERS_PASS,
        office_essay_answers=OFFICE_MIGRATION_ESSAY_ANSWERS,
        mindset_answers=MINDSET_ANSWERS_PASS,
    )

    assert response.status == "success"

    # Verify scores are within expected ranges
    scores = response.result["scores"]
    assert 0 <= scores["basic_knowledge"] <= 100
    assert 0 <= scores["office_migration"] <= 100
    assert 0 <= scores["mindset"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
