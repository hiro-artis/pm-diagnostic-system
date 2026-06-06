"""Test question data and definitions."""

from src.models.schemas import (
    BasicKnowledgeQuestion,
    OfficeMigrationMCQuestion,
    OfficeMigrationEssayQuestion,
    MindsetScenario,
    Mindset,
)


# ============================================================================
# Basic Knowledge Test Questions (10 questions)
# ============================================================================

BASIC_KNOWLEDGE_QUESTIONS = [
    BasicKnowledgeQuestion(
        question_id="BK-001",
        question="以下の中で、プロジェクトの特性として正しいものはどれか？",
        options=[
            "A) 継続的で反復的な業務活動",
            "B) 一時的な努力で独特な成果物を生み出す活動",
            "C) 組織の日常的な運営活動",
            "D) 経営層による意思決定プロセス",
        ],
        correct_answer="B",
        explanation="プロジェクトは期限を持ち、ユニークな成果物を作成する一時的な事業である（PMBOK定義）",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-002",
        question="プロジェクト成功のために重要でないステークホルダー活動は？",
        options=[
            "A) ステークホルダーのニーズ理解",
            "B) 期待値管理",
            "C) ステークホルダーの関心度・影響度分析",
            "D) 反対意見のステークホルダーの排除",
        ],
        correct_answer="D",
        explanation="反対意見でも、ステークホルダーを巻き込み理解を得ることがPMの重要なスキル",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-003",
        question="スコープクリープが起こる主な原因は？",
        options=[
            "A) 厳密なスコープ定義と変更管理の欠如",
            "B) チームメンバーが十分なスキルを持たない",
            "C) 正確なスケジュール計画",
            "D) 効果的なコミュニケーション",
        ],
        correct_answer="A",
        explanation="要件変更を許可制なしに受け入れるとスコープクリープが発生",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-004",
        question="リスク対応戦略の中で、リスク発生確率を低減させる戦略は？",
        options=[
            "A) 受容（Accept）",
            "B) 軽減（Mitigate）",
            "C) 回避（Avoid）",
            "D) エスカレーション（Escalate）",
        ],
        correct_answer="B",
        explanation="軽減は確率または影響を減らす対応。回避は活動そのものを避ける。",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-005",
        question="以下の中でコミュニケーション計画で定義する項目ではないのはどれ？",
        options=[
            "A) コミュニケーション対象者",
            "B) 情報の内容・粒度",
            "C) 配信方法・頻度",
            "D) 配信者の給与水準",
        ],
        correct_answer="D",
        explanation="給与は人事・経理の管轄。PMコミュニケーション計画には含まない",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-006",
        question="プロジェクト品質を確保するための活動順序として正しいのは？",
        options=[
            "A) 検証 → 統合 → テスト",
            "B) 計画 → 設計 → テスト → 検証",
            "C) テスト → 検証 → 統合",
            "D) 統合 → 検証 → テスト",
        ],
        correct_answer="B",
        explanation="計画段階で品質基準を決定し、各フェーズで組み込む必要がある",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-007",
        question="重要パスの特性として正しいのはどれ？",
        options=[
            "A) 最短で完了できるパス",
            "B) 最も多くのリソースを使うパス",
            "C) スラックがなく、遅延するとプロジェクト全体が遅延するパス",
            "D) 最もコストが高いパス",
        ],
        correct_answer="C",
        explanation="重要パスは遅延の余地がないため、重点的に監視する必要がある",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-008",
        question="コスト超過指数（Cost Performance Index：CPI）が0.9の場合、その意味は？",
        options=[
            "A) コストが10%削減されている",
            "B) コストが10%超過している",
            "C) スケジュールが10%遅延している",
            "D) 品質が10%低下している",
        ],
        correct_answer="B",
        explanation="CPI = EV/AC。0.9は実際の支出に対して実績値が90%＝超過",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-009",
        question="変更管理プロセスの目的として最適なものはどれ？",
        options=[
            "A) すべての変更要望を受け入れる",
            "B) 変更を可能な限り拒否する",
            "C) 変更の影響を評価し、承認・拒否を判断する",
            "D) PМが一人で変更判断を行う",
        ],
        correct_answer="C",
        explanation="変更管理委員会（CCB）で適切に評価・判断することが重要",
    ),
    BasicKnowledgeQuestion(
        question_id="BK-010",
        question="プロジェクト終結段階で重要でない活動は？",
        options=[
            "A) 成果物の引き渡し",
            "B) 契約の正式終了",
            "C) プロジェクトメンバーの再配置計画",
            "D) 過去プロジェクトの実績と比較分析",
        ],
        correct_answer="D",
        explanation="過去比較は有用だが、終結段階の必須活動ではない",
    ),
]


# ============================================================================
# Office Migration Test - Multiple Choice Questions (5 questions)
# ============================================================================

OFFICE_MIGRATION_MC_QUESTIONS = [
    OfficeMigrationMCQuestion(
        question_id="OM-MC-001",
        question="オフィス移転の計画段階で最初に確認すべきことは？",
        options=[
            "A) 現在のオフィスの家賃",
            "B) 移転先の立地条件",
            "C) 現在のスペース利用状況と将来のニーズ確認",
            "D) 移転業者の選定",
        ],
        correct_answer="C",
        score_per_question=5,
    ),
    OfficeMigrationMCQuestion(
        question_id="OM-MC-002",
        question="異なるフロアに配置される部門の不安に対して、最初に取るべき行動は？",
        options=[
            "A) 経営判断として異動受け入れを強制する",
            "B) 理由を説明せず既成事実を作る",
            "C) 関係者との意見交換会を開催し、懸念事項を聴取する",
            "D) メール一通で通知を済ませる",
        ],
        correct_answer="C",
        score_per_question=5,
    ),
    OfficeMigrationMCQuestion(
        question_id="OM-MC-003",
        question="移転中に大型システムの障害が発生した場合の対応として最適なのは？",
        options=[
            "A) IT部門だけで対応を進める",
            "B) 全部門と調整し、影響範囲を最小化する対応計画を立てる",
            "C) 経営層への報告を後回しにする",
            "D) 障害を公開せず対応を進める",
        ],
        correct_answer="B",
        score_per_question=5,
    ),
    OfficeMigrationMCQuestion(
        question_id="OM-MC-004",
        question="移転当日、想定外の什器（机・椅子）が手元にない場合の対応として不適切なのは？",
        options=[
            "A) 納入業者に確認し納期短縮を交渉する",
            "B) 部門長と優先度を決め一部は代替品で対応する",
            "C) 業者を強く叱責して当日の納入を無理に進める",
            "D) 配置図を修正し一時的な運用方法を決定する",
        ],
        correct_answer="C",
        score_per_question=5,
    ),
    OfficeMigrationMCQuestion(
        question_id="OM-MC-005",
        question="移転後2週間で「新しいフロア配置に慣れない」との声が上がった場合、適切な対応は？",
        options=[
            "A) 部門の文句として聞き流す",
            "B) フロア配置の工夫や追加サポートについて関係者と相談する",
            "C) 「すぐに慣れるはず」と根拠なく安心させる",
            "D) 移転完了として対応を終わらせる",
        ],
        correct_answer="B",
        score_per_question=5,
    ),
]


# ============================================================================
# Office Migration Test - Essay Questions (3 questions)
# ============================================================================

OFFICE_MIGRATION_ESSAY_QUESTIONS = [
    OfficeMigrationEssayQuestion(
        question_id="OM-ES-001",
        question="""あなたは大規模オフィス移転プロジェクトのPMとなりました。
現在のオフィスでは営業部と企画部が異なるフロアにあり、日常的に連携が必要ですが、
行き来に15分かかっています。新しいオフィスではこの距離を短縮する計画です。

ただし以下の制約があります：
- 営業部は新規顧客対応で現オフィスの引越し作業に参加できない
- 企画部は企画立案の繁忙期で移転後すぐに稼働が必要
- 新オフィスの什器納期は、営業部完全移転の5日後

この状況で想定されるリスク、それに対する対応策、
および関係者とのコミュニケーション方法を具体的に述べなさい。""",
        word_count_min=200,
        word_count_max=300,
        evaluation_criteria={
            "リスク認識": {"max_score": 5, "description": "複数のリスク認識"},
            "対応策の実現性": {"max_score": 10, "description": "スコープ・品質・人員配置の工夫"},
            "コミュニケーション": {"max_score": 10, "description": "ニーズ対応と期待値設定"},
        },
    ),
    OfficeMigrationEssayQuestion(
        question_id="OM-ES-002",
        question="""移転予定日の3日前、新オフィスの電気系統に欠陥が見つかりました。
完全な改修には5日必要です。

関係者の状況：
- 経営層：予定通り移転したい（既に顧客・取引先に新住所を通知）
- 営業部：顧客対応の都合で予定日の移転が必須
- IT部門：不完全な状態での稼働は避けたい
- 建設・不動産会社：追加費用・スケジュール変更で抵抗

この状況をどのように収拾させるか、あなたの判断プロセス・検討すべき選択肢・推奨案を述べなさい。""",
        word_count_min=200,
        word_count_max=300,
        evaluation_criteria={
            "自責の姿勢": {"max_score": 5, "description": "主体的取り組み"},
            "マルチステークホルダー対応": {"max_score": 10, "description": "複数立場の理解"},
            "意思決定の透明性": {"max_score": 10, "description": "判断基準の明示"},
        },
    ),
    OfficeMigrationEssayQuestion(
        question_id="OM-ES-003",
        question="""新しいオフィスへの移転を機に、異なる部門のメンバーが近い場所に配置されることになります。
一部のメンバー（主に長期勤続者）からは「新しい部門との距離が近すぎて不安」
「プライバシーが守られるか心配」という声が上がっています。

この状況で、メンバーの不安を解消し、新しい配置を機に部門間の協力関係を深めていくための施策を
具体的に述べなさい。""",
        word_count_min=200,
        word_count_max=300,
        evaluation_criteria={
            "相手への優しさ": {"max_score": 5, "description": "不安への配慮"},
            "聴く力": {"max_score": 10, "description": "メンバーの声を引き出す"},
            "前向きな施策": {"max_score": 10, "description": "実行可能な施策"},
        },
    ),
]


# ============================================================================
# Mindset Test Scenarios (6 scenarios)
# ============================================================================

MINDSET_SCENARIOS = [
    MindsetScenario(
        scenario_id="MS-S01",
        scenario="プロジェクトが中盤に差し掛かったとき、突然経営層から「経営環境の変化により、プロジェクト予算を30%削減してほしい」と言われました。",
        question="この状況で想定されるリスク、それに対する対応策、および関係者とのコミュニケーション方法を具体的に述べなさい。あなたならどうしますか？",
        options=[
            "A) 経営層の決定に従い、即座に予算削減を受け入れスコープを縮小する",
            "B) 「計画通り進捗しているので予算削減は難しい」と経営層に報告し、削減を拒否する",
            "C) 予算削減が必要な背景・期待を経営層から聴取した上で、削減下での実現可能なスコープ案・品質維持案を複数作成し提示する",
            "D) 予算削減には応じず、代わりに品質を下げることを提案する",
        ],
        correct_answer="C",
        score_per_question=15,
        evaluated_mindsets=[Mindset.FUTURE_FOCUSED, Mindset.SELF_RESPONSIBILITY],
    ),
    MindsetScenario(
        scenario_id="MS-S02",
        scenario="技術チームと営業チームの意見が対立しています。技術チーム：「新機能を実装するには最低4週間必要。品質を落とすべきではない」営業チーム：「顧客は2週間での納期を期待している。実装を急ぐべき」",
        question="チーム双方ともあなたのサポートを待っています。経営層の判断も示されていません。あなたならどうしますか？",
        options=[
            "A) 技術チームの意見が正しいと判断し、営業チームに納期変更を受け入れるよう指示する",
            "B) 営業チームの期待に応えるべく、技術チームに2週間での納期を指示する",
            "C) まず両チームに個別に詳しく話を聴き、各視点での課題・制約を理解した上で、技術と営業が一堂に会して解決案を協議する場を設定する",
            "D) 「こういうことがあるプロジェクトだから、双方で妥協してほしい」と曖昧に伝える",
        ],
        correct_answer="C",
        score_per_question=15,
        evaluated_mindsets=[Mindset.SELF_RESPONSIBILITY, Mindset.LISTENING_SKILL],
    ),
    MindsetScenario(
        scenario_id="MS-S03",
        scenario="プロジェクト開始から3ヶ月経った時点で、新しいメンバーがプロジェクトに参加しました。1週間後、メンバーから「プロジェクトの背景や進捗が十分理解できていない」「既存メンバーとのコミュニケーションがしづらい」との相談がありました。既存メンバーは忙しく、新入メンバーへの対応に時間を割く余裕がありません。",
        question="あなたならどうしますか？",
        options=[
            "A) 「プロジェクトは忙しいから、自分で学習するしかない」と伝え、個人の努力に任せる",
            "B) 既存メンバーに「新入メンバーの対応をお願いします」と指示し、対応を任せる",
            "C) 自分の時間を使ってでも新入メンバーとマンツーマンでプロジェクト背景を説明し、既存メンバーとの交流機会を意図的に作り、段階的にプロジェクトへの帰属意識を高めるよう支援する",
            "D) 新入メンバーのためにプロジェクトの進捗を一時停止し、説明会を開催する",
        ],
        correct_answer="C",
        score_per_question=15,
        evaluated_mindsets=[Mindset.KINDNESS, Mindset.INCLUSIVITY],
    ),
    MindsetScenario(
        scenario_id="MS-S04",
        scenario="システム導入プロジェクトで、複数部門から相反する要望が出ています。営業部：「営業ツール機能を重視したい。納期は3ヶ月」企画部：「企画プロセスの見える化を重視したい。納期は柔軟」IT部門：「システム安定性が最優先。追加機能は限定したい」各部門の責任者は、それぞれの部門の利益を重視しており、譲歩する気配がありません。",
        question="あなたならどうしますか？",
        options=[
            "A) PMの判断で最も重要度の高い部門の要望を採用し、他は後回しにする",
            "B) 各部門から詳しく話を聴き、それぞれの要望の背景・優先順位を理解した上で、経営層・各部門責任者の合意の下で、優先機能・納期・品質を決定する",
            "C) 「全て実装できるように頑張ります」と約束してから、後で実装不可を伝える",
            "D) 各部門の言い分を聴いた後、最大公約数的な要望だけに絞り、各部門に納得してもらう",
        ],
        correct_answer="B",
        score_per_question=15,
        evaluated_mindsets=[Mindset.LISTENING_SKILL, Mindset.COLLABORATION],
    ),
    MindsetScenario(
        scenario_id="MS-S05",
        scenario="オフィス移転計画で、一部のメンバー（主に長期勤続者）から「現在のフロア配置を変えたくない」「新しい部門との協力は難しい」という強い反発が出ています。一方、経営層は「部門間連携を強化するために、移転を機にフロア配置を変えるべき」と決定しています。反発しているメンバーの意見を黙殺して移転を進めると、彼らのモチベーション低下や離職の可能性があります。",
        question="あなたならどうしますか？",
        options=[
            "A) 経営層の決定に従い、反発しているメンバーには「会社の決定ですから」と伝える",
            "B) 反発しているメンバーを新しいフロア配置から除外し、別のエリアに残す",
            "C) 反発しているメンバーと個別に、移転理由・期待・懸念について何度も対話し、新しい配置に向けた段階的な準備・フォローアップを計画する。同時に、経営層にも「メンバーの懸念・段階的進行」を報告し、全体での着地点を整える",
            "D) 反発しているメンバーの懸念を経営層に報告し、経営層に判断・説得を任せる",
        ],
        correct_answer="C",
        score_per_question=15,
        evaluated_mindsets=[Mindset.INCLUSIVITY, Mindset.KINDNESS],
    ),
    MindsetScenario(
        scenario_id="MS-S06",
        scenario="あなたは新規事業プロジェクトのPMに抜擢されました。自分の経験がない領域です。チーム構成：自分（PM）：営業経験10年、管理経験3年／技術リーダー：その道の専門家だが、プロジェクト管理経験は少ない／ビジネス分析者：初心者で、自分の判断に自信がない／外部アドバイザー：専門知識は豊富だが、費用が高い。プロジェクト開始1ヶ月で、当初の計画では成功する見込みが低いことが判明しました。",
        question="あなたならどうしますか？",
        options=[
            "A) 自分のPM経験を活かして、一人で計画を修正し実行する",
            "B) 費用を理由に外部アドバイザーを断り、メンバーだけで対応する",
            "C) 技術リーダー・ビジネス分析者・外部アドバイザー（必要に応じて）を交えた検討会を開催し、各自の知見を引き出しながら、新しい計画案を共同で作成する。責任はPMが負いながらも、チーム全体の力を活かす",
            "D) 「新規領域なので成功保証はできない」と経営層に報告し、プロジェクトの延期を提案する",
        ],
        correct_answer="C",
        score_per_question=15,
        evaluated_mindsets=[Mindset.COLLABORATION, Mindset.FUTURE_FOCUSED],
    ),
]


def get_basic_knowledge_questions():
    """Get all basic knowledge questions."""
    return BASIC_KNOWLEDGE_QUESTIONS


def get_office_migration_mc_questions():
    """Get all office migration MC questions."""
    return OFFICE_MIGRATION_MC_QUESTIONS


def get_office_migration_essay_questions():
    """Get all office migration essay questions."""
    return OFFICE_MIGRATION_ESSAY_QUESTIONS


def get_mindset_scenarios():
    """Get all mindset scenarios."""
    return MINDSET_SCENARIOS
