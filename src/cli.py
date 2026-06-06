"""Command-line interface for PM diagnostic system."""

import asyncio
import logging
from typing import Dict

from src.agents.primary_test_orchestrator import PrimaryTestOrchestratorAgent
from src.agents.secondary_test_orchestrator import SecondaryTestOrchestratorAgent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PMDiagnosticCLI:
    """CLI interface for PM diagnostic system."""

    def __init__(self):
        """Initialize CLI."""
        self.primary_orchestrator = PrimaryTestOrchestratorAgent()
        self.secondary_orchestrator = SecondaryTestOrchestratorAgent()

    async def run(self):
        """Run the CLI interface."""
        print("\n" + "=" * 70)
        print("  PM協会テスト診断システムへようこそ")
        print("=" * 70)
        print("\nこのシステムでは、以下の3つのテストを実施します：")
        print("  1. PM基礎知識テスト（10問）")
        print("  2. オフィス移転実務テスト（MC5問 + 記述式3問）")
        print("  3. マインドセット検証（6シナリオ）")
        print("\n所要時間：約60-90分")
        print("=" * 70 + "\n")

        # Get user info
        user_id = input("ユーザーID（メールアドレス推奨）を入力してください: ").strip()
        if not user_id:
            print("ユーザーIDが入力されていません。終了します。")
            return

        print(f"\n{user_id} さん、テストを開始します。\n")

        # Run primary test
        print("【1次テスト開始】\n")
        primary_result = await self._run_primary_test()

        if primary_result is None:
            print("1次テストがキャンセルされました。")
            return

        session_id = primary_result.get("session_id")
        user_scores = primary_result.get("scores", {})

        print("\n" + "=" * 70)
        print("【1次テスト結果】")
        print("=" * 70)
        print(f"PM基礎知識：{user_scores.get('basic_knowledge', 0)}/100")
        print(f"オフィス移転：{user_scores.get('office_migration', 0)}/100")
        print(f"マインドセット：{user_scores.get('mindset', 0)}/100")

        qualifies_for_secondary = primary_result.get("qualifies_for_secondary", False)

        if not primary_result.get("passed"):
            print("\n【判定】：1次テスト不合格")
            print("1週間後に再検査を受けることをお勧めします。")
            return

        if qualifies_for_secondary:
            print("\n【判定】：1次テスト合格 → 2次テスト進出")
            print("\n2次テスト（マインドセット面接）を実施します。")
            await self._run_secondary_test(session_id, user_id, user_scores)
        else:
            print("\n【判定】：1次テスト合格（2次テストなし）")
            print("\nテスト完了です。最終レポートを生成しています...\n")
            await self._generate_final_report(
                session_id,
                user_id,
                {
                    "basic_knowledge_score": user_scores.get("basic_knowledge", 0),
                    "office_migration_score": user_scores.get("office_migration", 0),
                    "mindset_score": user_scores.get("mindset", 0),
                    "mindset_breakdown": primary_result.get("mindset_breakdown", {}),
                },
            )

    async def _run_primary_test(self) -> Dict:
        """Run primary test."""
        try:
            # Collect answers
            basic_answers = await self._collect_basic_knowledge_answers()
            office_mc_answers = await self._collect_office_migration_mc_answers()
            office_essay_answers = await self._collect_office_migration_essay_answers()
            mindset_answers = await self._collect_mindset_answers()

            # Run primary test
            result = await self.primary_orchestrator.run_complete_primary_test(
                user_id="cli_user",
                basic_answers=basic_answers,
                office_mc_answers=office_mc_answers,
                office_essay_answers=office_essay_answers,
                mindset_answers=mindset_answers,
            )

            if result.status == "success":
                return result.result
            else:
                print(f"エラー: {result.error_message}")
                return None

        except Exception as e:
            logger.error(f"Primary test failed: {str(e)}")
            print(f"テスト実行中にエラーが発生しました: {str(e)}")
            return None

    async def _run_secondary_test(
        self,
        session_id: str,
        user_id: str,
        primary_scores: Dict,
    ):
        """Run secondary test (interview)."""
        try:
            print("\n" + "=" * 70)
            print("【2次テスト（マインドセット面接）】")
            print("=" * 70)
            print("\n以下の質問に、あなたの経験や考えに基づいてお答えください。")
            print("（各質問に対して、3-5文程度でお答えください）\n")

            # Collect interview responses
            interview_responses = await self._collect_interview_responses()

            # Run secondary test
            result = await self.secondary_orchestrator.run_complete_secondary_test(
                session_id=session_id,
                primary_mindset_scores=primary_scores.get("mindset_breakdown", {}),
                interview_responses=interview_responses,
            )

            if result.status == "success":
                interview_result = result.result.get("interview_result", {})
                revised_scores = result.result.get("revised_mindset_scores", {})

                print("\n" + "=" * 70)
                print("【2次テスト（面接）結果】")
                print("=" * 70)
                print(f"面接スコア：{result.result.get('interview_score', 0)}/100")
                print("\n修正後のマインドセット別スコア：")
                for key, value in revised_scores.items():
                    print(f"  {key}: {value}点")

                # Generate final assessment
                await self._generate_final_report(
                    session_id,
                    user_id,
                    {
                        "basic_knowledge_score": primary_scores.get("basic_knowledge", 0),
                        "office_migration_score": primary_scores.get("office_migration", 0),
                        "mindset_score": primary_scores.get("mindset", 0),
                        "mindset_breakdown": revised_scores,
                    },
                    secondary_results={"score": result.result.get("interview_score", 0)},
                )
            else:
                print(f"エラー: {result.error_message}")

        except Exception as e:
            logger.error(f"Secondary test failed: {str(e)}")
            print(f"2次テスト実行中にエラーが発生しました: {str(e)}")

    async def _generate_final_report(
        self,
        session_id: str,
        user_id: str,
        primary_results: Dict,
        secondary_results: Dict = None,
    ):
        """Generate final assessment report."""
        try:
            result = await self.secondary_orchestrator.generate_final_assessment(
                session_id=session_id,
                user_id=user_id,
                primary_results=primary_results,
                secondary_results=secondary_results,
            )

            if result.status == "success":
                assessment = result.result.get("assessment", {})

                print("\n" + "=" * 70)
                print("【最終評価レポート】")
                print("=" * 70)
                print(f"\n総合スコア: {assessment.get('total_score', 0):.1f}/100")
                print(f"評価等級: {assessment.get('grade_level', 'N/A')}")
                print(f"\nサマリー:\n{assessment.get('summary', 'N/A')}")

                if assessment.get('strengths'):
                    print("\n【強み】")
                    for strength in assessment['strengths']:
                        print(f"  • {strength}")

                if assessment.get('development_areas'):
                    print("\n【改善が望ましい領域】")
                    for area in assessment['development_areas']:
                        print(f"  • {area}")

                if assessment.get('recommendations'):
                    print("\n【推奨事項】")
                    for rec in assessment['recommendations']:
                        print(f"  • {rec}")

                print("\n" + "=" * 70)
                print("テスト完了です。ご協力ありがとうございました。")
                print("=" * 70 + "\n")

        except Exception as e:
            logger.error(f"Final assessment failed: {str(e)}")
            print(f"最終評価生成中にエラーが発生しました: {str(e)}")

    async def _collect_basic_knowledge_answers(self) -> Dict[str, str]:
        """Collect basic knowledge test answers."""
        print("【PM基礎知識テスト】(10問)\n")
        answers = {}

        questions = [
            ("BK-001", "プロジェクトの特性として正しいのは？", ["A) 継続的で反復的な業務活動", "B) 一時的な努力で独特な成果物を生み出す", "C) 日常的な運営活動", "D) 経営層による意思決定"]),
            ("BK-002", "ステークホルダー活動で重要でないのは？", ["A) ニーズ理解", "B) 期待値管理", "C) 関心度・影響度分析", "D) 反対意見の排除"]),
            ("BK-003", "スコープクリープの主な原因は？", ["A) スコープ定義と変更管理の欠如", "B) スキル不足", "C) 正確なスケジュール", "D) 効果的なコミュニケーション"]),
            ("BK-004", "リスク対応で確率を低減させるのは？", ["A) 受容", "B) 軽減", "C) 回避", "D) エスカレーション"]),
            ("BK-005", "コミュニケーション計画で定義しない項目は？", ["A) 対象者", "B) 内容・粒度", "C) 配信方法・頻度", "D) 給与水準"]),
            ("BK-006", "品質確保の活動順序として正しいのは？", ["A) 検証→統合→テスト", "B) 計画→設計→テスト→検証", "C) テスト→検証→統合", "D) 統合→検証→テスト"]),
            ("BK-007", "重要パスの特性として正しいのは？", ["A) 最短完了パス", "B) 最もリソース使用", "C) スラック無く遅延で全体遅延", "D) 最もコスト高"]),
            ("BK-008", "CPI=0.9の意味は？", ["A) コスト10%削減", "B) コスト10%超過", "C) スケジュール10%遅延", "D) 品質10%低下"]),
            ("BK-009", "変更管理プロセスの目的は？", ["A) 全変更受け入れ", "B) 全変更拒否", "C) 影響評価で判断", "D) PM一人で判定"]),
            ("BK-010", "終結段階で重要でない活動は？", ["A) 成果物引き渡し", "B) 契約終了", "C) メンバー再配置", "D) 過去比較分析"]),
        ]

        for qid, question, options in questions:
            print(f"{qid}: {question}")
            for i, opt in enumerate(options, 1):
                print(f"  {opt}")
            while True:
                answer = input("回答（A/B/C/D）: ").upper().strip()
                if answer in ["A", "B", "C", "D"]:
                    answers[qid] = answer
                    break
                print("A, B, C, D のいずれかで回答してください。")
            print()

        return answers

    async def _collect_office_migration_mc_answers(self) -> Dict[str, str]:
        """Collect office migration MC answers."""
        print("\n【オフィス移転テスト - 選択式】(5問)\n")
        answers = {}

        questions = [
            ("OM-MC-001", "計画段階で最初に確認すべきことは？", ["A) 家賃", "B) 立地条件", "C) スペース利用と将来ニーズ", "D) 移転業者選定"]),
            ("OM-MC-002", "異なるフロア配置への不安への対応は？", ["A) 強制受け入れ", "B) 説明なしに実施", "C) 意見交換会開催", "D) メール通知"]),
            ("OM-MC-003", "移転中のシステム障害対応として最適なのは？", ["A) IT部門のみ対応", "B) 全部門と調整", "C) 報告後回し", "D) 非公開対応"]),
            ("OM-MC-004", "当日の什器不足時の不適切な対応は？", ["A) 納入業者に交渉", "B) 優先度決定", "C) 強く叱責", "D) 配置図修正"]),
            ("OM-MC-005", "移転後の「慣れない」声への適切な対応は？", ["A) 聞き流す", "B) 関係者と相談", "C) 根拠なく安心させる", "D) 対応終了"]),
        ]

        for qid, question, options in questions:
            print(f"{qid}: {question}")
            for i, opt in enumerate(options, 1):
                print(f"  {opt}")
            while True:
                answer = input("回答（A/B/C/D）: ").upper().strip()
                if answer in ["A", "B", "C", "D"]:
                    answers[qid] = answer
                    break
                print("A, B, C, D のいずれかで回答してください。")
            print()

        return answers

    async def _collect_office_migration_essay_answers(self) -> Dict[str, str]:
        """Collect office migration essay answers."""
        print("\n【オフィス移転テスト - 記述式】(3問)\n")
        answers = {}

        questions = [
            ("OM-ES-001", "営業部と企画部のフロア距離短縮で想定されるリスク、対応策、コミュニケーション方法を述べなさい（200-300字）。"),
            ("OM-ES-002", "移転3日前に電気系統欠陥が発見された場合、どう対応するか、判断プロセス・選択肢・推奨案を述べなさい（200-300字）。"),
            ("OM-ES-003", "部員の不安を解消し、部門間協力を深めるための施策を述べなさい（200-300字）。"),
        ]

        for qid, question in questions:
            print(f"{qid}: {question}\n")
            answer = input("回答を入力してください（終了時はEnter2回）:\n").strip()
            answers[qid] = answer
            print()

        return answers

    async def _collect_mindset_answers(self) -> Dict[str, str]:
        """Collect mindset scenario answers."""
        print("\n【マインドセット検証】(6シナリオ)\n")
        answers = {}

        scenarios = [
            ("MS-S01", "予算30%削減要請への対応", ["A) 即座に削減受け入れ", "B) 削減拒否", "C) 削減下での複数案作成", "D) 品質低下提案"]),
            ("MS-S02", "チーム内意見対立への対応", ["A) 技術優先指示", "B) 営業優先指示", "C) 両者に詳しく話を聴く", "D) あいまいな指示"]),
            ("MS-S03", "新入メンバーの不安への対応", ["A) 自分で学習", "B) 既存メンバーに任せる", "C) マンツーマンで支援", "D) 進捗一時停止"]),
            ("MS-S04", "複数部門相反要望への対応", ["A) PM一人で決定", "B) 関係者と合意で決定", "C) 全て実装約束", "D) 最大公約数に絞る"]),
            ("MS-S05", "フロア移転反発への対応", ["A) 強制受け入れ", "B) 除外配置", "C) 個別対話と段階的進行", "D) 経営層に任せる"]),
            ("MS-S06", "新規領域プロジェクトでの連携", ["A) 一人で決定", "B) アドバイザー断る", "C) チーム全体の力を活かす", "D) 延期提案"]),
        ]

        for sid, scenario, options in scenarios:
            print(f"{sid}: {scenario}")
            for opt in options:
                print(f"  {opt}")
            while True:
                answer = input("回答（A/B/C/D）: ").upper().strip()
                if answer in ["A", "B", "C", "D"]:
                    answers[sid] = answer
                    break
                print("A, B, C, D のいずれかで回答してください。")
            print()

        return answers

    async def _collect_interview_responses(self) -> Dict[str, str]:
        """Collect interview responses."""
        responses = {}

        interview_questions = [
            ("1", "過去にプロジェクトを進める中で、長期的な視点から判断を変えた経験はありますか？その時どのような点を重視しましたか？"),
            ("2", "困難な状況で、自分の責任として問題を解決した経験を教えてください。その時の考え方や行動を詳しく説明してください。"),
            ("3", "チームメンバーが不安や悩みを抱えていた時、あなたはどのように対応しましたか？相手の気持ちにどう向き合いましたか？"),
            ("4", "相手の意見と異なる場合、相手の意見をどのように理解しようとしましたか？具体的な例を挙げて説明してください。"),
        ]

        for qnum, question in interview_questions:
            print(f"【質問 {qnum}】")
            print(question)
            response = input("\nご回答をお願いします:\n").strip()
            responses[qnum] = response
            print()

        return responses


async def main():
    """Main entry point."""
    cli = PMDiagnosticCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
