# PM協会テスト診断システム - 実装要件定義書

**作成日：** 2026年6月6日  
**ステータス：** 実装フェーズ準備  
**対象フェーズ：** Phase 1 ～ Phase 5

---

## 1. システム要件概要

### 1.1 目的
PM適性診断を自動化するAIエージェントシステムの実装により、PM候補者・既存PMの判定を迅速・公正に実施する。

### 1.2 スコープ
- **1次テスト** ：基礎知識（10問）+ オフィス移転（8問）+ マインドセット（6シナリオ）
- **2次テスト** ：マインドセット面接（開放型質問ベース）
- **最終評価** ：A/B/C/再検査の4段階判定
- **運用サポート** ：テスト結果管理・再受検・分析

### 1.3 ユーザー
- **受診者** ：PM候補者・既存PM（年間推定50-200名）
- **管理者** ：テスト実施・結果管理担当者

---

## 2. 機能要件 (Functional Requirements)

### 2.1 コア機能

#### FR-01: テスト進行管理
- **概要** ：全テストのライフサイクル管理・結果統合
- **詳細** ：
  - セッション初期化・再開機能
  - テスト順序制御（1次→2次）
  - 進捗保存・復旧
  - タイムアウト管理（1次＝90分、2次＝30分）
- **実装対象** ：Orchestrator エージェント

#### FR-02: 基礎知識テスト実行
- **概要** ：PM基礎知識を選択式で評価（4択×10問）
- **詳細** ：
  - 問題セットのランダム配信
  - 自動採点（正答判定）
  - スコア計算（0-100点）
  - 合格判定（70%以上）
- **実装対象** ：BasicKnowledgeTest エージェント

#### FR-03: オフィス移転テスト実行
- **概要** ：実務経験を選択式（5問）+ 記述式（3問）で評価
- **詳細** ：
  - 選択式問題の配信・採点
  - 記述式問題の配信・テキスト回収
  - 記述式採点エージェント呼び出し
  - 統合スコア計算（0-100点）
  - 合格判定（65点以上）
- **実装対象** ：OfficeMigrationTest エージェント + ComprehensiveScorer

#### FR-04: マインドセットテスト実行 ⭐重要
- **概要** ：6つのマインドセットをシナリオ型選択式で評価（6シナリオ）
- **詳細** ：
  - シナリオ提示・選択肢配信
  - 各選択肢に対する6つのマインドセット別スコア評価
  - マインドセット個別スコア計算（各0-100点）
  - 総合スコア計算（0-100点）
  - 2次進出判定（60点以上）
- **マインドセット種別** ：
  1. 未来志向 (Future Focused)
  2. 自責 (Self Responsibility)
  3. 優しさ (Kindness)
  4. 聴く力 (Listening Skill)
  5. 置いてきぼりにしない (Inclusivity)
  6. 一人で進まない (Collaboration)
- **実装対象** ：MindsetTest エージェント

#### FR-05: マインドセット面接実行
- **概要** ：2次テストで1次結果を深掘り（開放型質問ベース）
- **詳細** ：
  - 1次結果分析→弱点マインドセット抽出
  - 質問動的生成（開放型・深掘り・検証型）
  - テキスト回答取得・分析
  - マインドセット別スコア再評価
  - 一貫性チェック（1次との乖離検出）
  - 信頼度スコア計算
- **実施条件** ：1次テスト マインドセット60点以上
- **実装対象** ：MindsetInterview エージェント

#### FR-06: 詳細採点・最終評価
- **概要** ：1次＋2次結果を統合し、最終評価を判定
- **詳細** ：
  - 3つのセクション別スコア確定
  - 6つのマインドセット個別スコア確定
  - 総合スコア計算
  - 最終評価判定（A/B/C/再検査）
  - フィードバック・推奨事項生成
- **判定ロジック** ：
  - **A判定** ：全セクション合格 + マインドセット80点以上
  - **B判定** ：全セクション合格 + マインドセット60-79点
  - **C判定** ：いずれかのセクション不合格
  - **再検査** ：1次で複数セクション不合格 / 1次2次で大きな乖離
- **実装対象** ：ComprehensiveScorer エージェント

#### FR-07: セッション・結果管理
- **概要** ：テスト実施中のセッション管理・結果永続化
- **詳細** ：
  - セッション開始・中断・再開
  - テスト進捗の保存
  - 全テスト結果の保存・検索
  - 複数受診者の管理
- **実装対象** ：SessionManager + ResultStore

#### FR-08: 管理画面機能
- **概要** ：管理者向けテスト実施・結果閲覧機能
- **詳細** ：
  - テスト実施者管理（リスト表示）
  - 結果検索・フィルタ
  - 採点再計算（必要時）
  - エクスポート（CSV/JSON）
- **実装対象** ：UI/Web フレームワーク（FastAPI + 簡易フロントエンド）

---

### 2.2 機能詳細度

| 機能ID | 機能名 | 優先度 | 実装難度 | 推定工数 | Phase |
|--------|--------|--------|---------|---------|-------|
| FR-01 | テスト進行管理 | 最高 | 中 | 40h | 1 |
| FR-02 | 基礎知識テスト | 高 | 低 | 20h | 2 |
| FR-03 | オフィス移転テスト | 高 | 中 | 30h | 2 |
| FR-04 | マインドセットテスト | **最高** | 高 | 50h | 3 |
| FR-05 | マインドセット面接 | 中 | 高 | 40h | 4 |
| FR-06 | 詳細採点・評価 | 高 | 中 | 30h | 4-5 |
| FR-07 | セッション・結果管理 | 高 | 中 | 35h | 1-2 |
| FR-08 | 管理画面 | 中 | 中 | 25h | 5 |

---

## 3. 非機能要件 (Non-Functional Requirements)

### 3.1 パフォーマンス

| 項目 | 要件 | 備考 |
|------|------|------|
| API応答時間 | < 2秒（通常）, < 5秒（採点） | ユーザー体験 |
| 1次テスト所要時間 | 90分以内 | 集中力維持 |
| 2次テスト所要時間 | 30分以内 | 負担軽減 |
| 同時実施上限 | 10セッション | スケーラビリティ |

### 3.2 信頼性・精度

| 項目 | 要件 | 実現方法 |
|------|------|----------|
| 採点ばらつき | ±5点以内（マインドセット） | 評価パターン定義 + 複数回評価 |
| 記述式採点精度 | 85%以上の一貫性 | ルーブリック定義 + AI採点検証 |
| 一貫性チェック | 1次/2次乖離<10点 | 面接での検証質問 |
| システム可用性 | 99%以上 | 冗長化・エラーハンドリング |

### 3.3 セキュリティ

| 項目 | 要件 |
|------|------|
| 認証 | 管理者認証（簡易版：パスワード/APIキー） |
| データ暗号化 | 保存時・転送時ともTLS/AES-256 |
| アクセス制御 | 受診者は自分の結果のみ閲覧可 |
| 監査ログ | すべてのテスト実施・結果変更を記録 |
| GDPR対応 | ユーザーデータ削除機能 |

### 3.4 スケーラビリティ

| 項目 | 要件 |
|------|------|
| ユーザー数 | 初期50名/年 → 将来200名/年 |
| テスト実施数 | 1日最大5セッション（推定） |
| データ保持期間 | 3年 |
| ストレージ | 1受診者あたり 500KB 想定 |

---

## 4. 技術要件 (Technical Requirements)

### 4.1 スタック

#### バックエンド
```
言語：Python 3.9+
フレームワーク：FastAPI
LLM：Claude API (Anthropic SDK)
DB：SQLite (開発) / PostgreSQL (本運用)
スキーマ：Pydantic v2
非同期：asyncio + aiohttp
```

#### フロントエンド（簡易版）
```
フレームワーク：Streamlit or Flask + Jinja2
CSS：Bootstrap or Tailwind
JavaScript：最小限（フォーム検証のみ）
```

#### テスト・CI/CD
```
ユニットテスト：pytest
統合テスト：pytest-asyncio
カバレッジ：>80%
CI/CD：GitHub Actions (検討)
```

### 4.2 外部API・サービス

| サービス | 用途 | 使用量目安 |
|---------|------|----------|
| Claude API | エージェント LLM処理 | ~1,000呼び出し/月 |
| Gmail API | 結果メール送付（将来） | 100通/月 |

### 4.3 データベーススキーマ主要テーブル

#### users テーブル
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  role ENUM ('candidate', 'admin'),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

#### test_sessions テーブル
```sql
CREATE TABLE test_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  status ENUM ('started', 'paused', 'completed'),
  current_phase ENUM ('primary', 'secondary'),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  metadata JSON
);
```

#### test_results テーブル
```sql
CREATE TABLE test_results (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES test_sessions(id),
  section VARCHAR(50),  -- 'basic_knowledge', 'office_migration', 'mindset'
  raw_score DECIMAL,
  final_score DECIMAL,
  details JSON,
  created_at TIMESTAMP
);
```

#### mindset_scores テーブル
```sql
CREATE TABLE mindset_scores (
  id UUID PRIMARY KEY,
  session_id UUID,
  mindset_name VARCHAR(50),  -- 'future_focused', 'self_responsibility', ...
  score DECIMAL,
  confidence DECIMAL,
  test_phase ENUM ('primary', 'secondary')
);
```

#### final_assessment テーブル
```sql
CREATE TABLE final_assessment (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES test_sessions(id),
  total_score DECIMAL,
  grade ENUM ('A', 'B', 'C', 'needs_retest'),
  summary TEXT,
  recommendations JSON,
  created_at TIMESTAMP
);
```

---

## 5. 実装フェーズ詳細

### Phase 1: コア基盤構築（1-2週間）

**目標** ：エージェント実行環境の構築・セッション管理の完成

**成果物** ：
- [ ] `src/agents/base_agent.py` ─ 基底エージェントクラス
- [ ] `src/models/schemas.py` ─ Pydantic スキーマ定義
- [ ] `src/agents/orchestrator.py` ─ テスト進行エージェント
- [ ] `src/storage/session_manager.py` ─ セッション管理
- [ ] `src/storage/result_store.py` ─ 結果永続化
- [ ] `.env.example` ─ 環境設定テンプレート
- [ ] `requirements.txt` ─ 依存ライブラリ

**テスト基準** ：
- Orchestrator エージェントが1次テスト開始指示を出力可能
- セッション情報が保存・復旧可能
- エージェント間のメッセージ送受信が機能

---

### Phase 2: 基礎テスト実装（1-2週間）

**目標** ：基礎知識テスト・オフィス移転テストの完成

**成果物** ：
- [ ] `src/agents/basic_knowledge_test.py` ─ 基礎知識テスト
- [ ] `src/agents/office_migration_test.py` ─ オフィス移転テスト
- [ ] `src/agents/comprehensive_scorer.py` ─ 記述式採点エージェント
- [ ] `src/utils/scoring_logic.py` ─ スコア計算ロジック
- [ ] `tests/test_basic_knowledge.py` ─ ユニットテスト
- [ ] `tests/test_office_migration.py` ─ ユニットテスト
- [ ] `tests/test_orchestrator.py` ─ 統合テスト

**テスト基準** ：
- 基礎知識テスト完走 → 正確な採点
- オフィス移転テスト完走 → 選択式＆記述式が機能
- 記述式採点の精度が ±5点以内

---

### Phase 3: マインドセット実装（2-3週間）⭐重要

**目標** ：マインドセット検証の完成（システムの心臓部）

**成果物** ：
- [ ] `src/agents/mindset_test.py` ─ マインドセットテスト
- [ ] `src/utils/mindset_scoring.py` ─ マインドセット採点ロジック詳細化
- [ ] `tests/test_mindset.py` ─ 複数パターンテスト
- [ ] `docs/mindset_evaluation_patterns.md` ─ 評価パターン定義書

**テスト基準** ：
- 6つのマインドセット個別スコアが適切に計算される
- マインドセット総合スコアが納得性高く算出される
- 信頼度スコアが適切に評価される

**重要ポイント** ：
- 各シナリオの選択肢別にマインドセット評価パターンをハード定義
- Claude APIに「評価パターン」を明示指示
- 複数回の評価で平均化してばらつきを最小化

---

### Phase 4: 2次テスト・最終評価実装（2-3週間）

**目標** ：面接形式テスト＆統合評価完成

**成果物** ：
- [ ] `src/agents/mindset_interview.py` ─ マインドセット面接
- [ ] `tests/test_mindset_interview.py` ─ ユニットテスト
- [ ] `tests/integration/test_full_flow.py` ─ E2Eテスト
- [ ] `src/agents/final_evaluator.py` ─ 最終評価エージェント

**テスト基準** ：
- 面接が完走し、1次との一貫性が検証される
- 最終評価（A/B/C/再検査）が適切に判定される
- フィードバック・推奨事項が生成される

---

### Phase 5: UI実装・統合・本運用準備（2-3週間）

**目標** ：システム全体の動作確認・UI完成・本運用準備

**成果物** ：
- [ ] `src/main.py` ─ エントリーポイント
- [ ] `src/api/routes.py` ─ API エンドポイント
- [ ] `frontend/` ─ 簡易 Web UI（Streamlit or Flask）
- [ ] `tests/integration/` ─ 統合テスト群
- [ ] `docs/OPERATION_MANUAL.md` ─ 運用マニュアル
- [ ] `docs/API_SPEC.md` ─ API 仕様書
- [ ] ベータテスト結果報告書

**テスト基準** ：
- システム全体がE2Eで動作
- ベータテスター（5-10名）から「採点が適切」との評価を得る
- パフォーマンス・セキュリティ基準を満たす

---

## 6. 採点・評価ロジック詳細

### 6.1 基礎知識テスト採点

```python
BasicKnowledge_Score = (正答数 / 出題数) × 100

合格判定：
  - 70点以上 → 合格
  - 70点未満 → 不合格
```

### 6.2 オフィス移転テスト採点

```python
OffceMigration_MCScore = (正答数 / 5) × 100  # 選択式

OffceMigration_EssayScore = Claude APIによる記述式採点
  - 各問あたり0-5点 → 平均 × 20 = 0-100点

OffceMigration_FinalScore = (MC_Score × 0.5) + (Essay_Score × 0.5)

合格判定：
  - 65点以上 → 合格
  - 65点未満 → 不合格
```

### 6.3 マインドセット採点 ⭐重要

```python
# 各シナリオの選択肢ごとに、6つのマインドセット別スコアを定義
MINDSET_PATTERNS = {
  "scenario_id": {
    "option_A": {
      "future_focused": 3,
      "self_responsibility": 2,
      "kindness": 1,
      "listening_skill": 2,
      "inclusivity": 3,
      "collaboration": 2,
      "confidence": 0.85
    },
    "option_B": {
      "future_focused": 5,
      "self_responsibility": 4,
      "kindness": 5,
      "listening_skill": 4,
      "inclusivity": 5,
      "collaboration": 5,
      "confidence": 0.95
    },
    ...
  }
}

# マインドセット別スコア計算
Mindset_Score = avg(各シナリオの当該マインドセットスコア) × 20
  → 0-100点の範囲

# 総合スコア
Mindset_TotalScore = avg(6つのマインドセット別スコア)

合格判定：
  - 1次テストで60点以上 → 2次テスト進出
  - 1次テストで60点未満 → 不合格
```

### 6.4 マインドセット面接採点

```python
# 2次テストでの各質問に対する回答を分析
Interview_Scores = Claude APIによる回答分析
  - 各マインドセット別スコア再評価
  - 一貫性スコア（1次との乖離）

# 統合スコア（1次+2次）
Final_Mindset_Score = (Primary_Score × 0.6) + (Secondary_Score × 0.4)
  - 1次を重視しつつ、2次で補正

# 一貫性チェック
Consistency_Check：乖離 > 15点の場合、フラグ
  - 乖離が大きい場合 → 再検査推奨
```

### 6.5 最終評価判定

```python
# 3つのセクション別スコア確定
Section_Scores = {
  "basic_knowledge": BasicKnowledge_Score,
  "office_migration": OffceMigration_FinalScore,
  "mindset": Final_Mindset_Score
}

# 合格判定（各セクションで合格必須）
All_Passed = all(score >= threshold for score in Section_Scores.values())

# 総合スコア
Total_Score = (Basic_Knowledge × 0.2) + (OffceMigration × 0.2) + (Mindset × 0.6)

# 最終評価判定
if All_Passed and Mindset >= 80:
  Grade = 'A'  # 理想的PM人材
elif All_Passed and Mindset >= 60:
  Grade = 'B'  # 良好なPM人材
elif any(score < threshold):
  Grade = 'C'  # 不合格
elif Consistency_Check > 15:
  Grade = 'needs_retest'  # 再検査推奨
```

---

## 7. API仕様概要

### 7.1 主要エンドポイント

```
POST /api/v1/sessions/start
  → Session ID を返却

GET /api/v1/sessions/{session_id}
  → セッション情報・進捗を返却

POST /api/v1/tests/primary/start
  → 1次テスト開始

GET /api/v1/tests/questions/{question_id}
  → 問題情報を返却

POST /api/v1/tests/answer
  → 回答を送信・保存

GET /api/v1/results/{session_id}
  → テスト結果・評価を返却

POST /api/v1/admin/export
  → 結果をCSV/JSONでエクスポート
```

### 7.2 スキーマ例

```json
// GET /api/v1/sessions/{session_id}
{
  "session_id": "uuid",
  "user_id": "uuid",
  "status": "in_progress",
  "current_phase": "primary",
  "current_test": "mindset",
  "current_question": 3,
  "total_questions": 6,
  "elapsed_time_sec": 1200,
  "time_limit_sec": 5400
}

// GET /api/v1/results/{session_id}
{
  "session_id": "uuid",
  "scores": {
    "basic_knowledge": 85,
    "office_migration": 72,
    "mindset": {
      "total": 68,
      "breakdown": {
        "future_focused": 70,
        "self_responsibility": 65,
        "kindness": 72,
        "listening_skill": 68,
        "inclusivity": 66,
        "collaboration": 62
      }
    }
  },
  "final_grade": "B",
  "summary": "Good PM candidate",
  "recommendations": ["..."]
}
```

---

## 8. リスク・対策

### 8.1 技術的リスク

| リスク | 影響度 | 対策 |
|-------|--------|------|
| Claude API 呼び出し失敗 | 高 | リトライ機構（3回）+ タイムアウト（30秒） |
| 採点のばらつき | 高 | 評価パターン定義 + 複数回採点平均化 |
| テスト中断・復帰 | 中 | セッション永続化 + 再開機能 |
| スケーラビリティ | 中 | 非同期処理 + キャッシング + DB インデックス |

### 8.2 運用リスク

| リスク | 影響度 | 対策 |
|-------|--------|------|
| ベータテスター確保困難 | 中 | 早期に協力者との関係構築 |
| 採点基準への異議申し立て | 中 | 再受検機能 + 申し立てプロセス |
| ユーザーデータ漏洩 | 高 | データ暗号化 + アクセス制御 + 監査ログ |

---

## 9. 成功基準

| フェーズ | 成功基準 |
|---------|----------|
| Phase 1 | Orchestrator エージェントが1次テスト開始指示を出力可能 |
| Phase 2 | 基礎知識テスト完走し、正確な採点ができる |
| Phase 3 | マインドセット総合スコアが納得性高く算出される |
| Phase 4 | 面接が完走し、1次との一貫性が検証される |
| Phase 5 | ベータテスターから「採点が適切」との評価を得る |

---

## 10. スケジュール（目安）

| フェーズ | 期間 | 完了予定 | 成果物数 |
|---------|------|---------|---------|
| Phase 1 | 1-2週間 | 2026年6月 中旬 | 7 |
| Phase 2 | 1-2週間 | 2026年6月 下旬 | 8 |
| Phase 3 | 2-3週間 | 2026年7月 中旬 | 5 |
| Phase 4 | 2-3週間 | 2026年8月 初旬 | 4 |
| Phase 5 | 2-3週間 | 2026年8月 中旬 | 7 |
| ベータテスト | 1-2週間 | 2026年8月 下旬 | - |
| **本運用開始** | - | **2026年9月 初旬** | - |

---

## 11. 次のステップ

1. ✅ **エージェントマップ確認** → `docs/agent-map.md`
2. ✅ **要件定義書作成** → `docs/REQUIREMENTS.md` (本ドキュメント)
3. **Phase 1 実装開始** → `src/agents/base_agent.py` から着手
4. **テスト戦略詳細化** → テストフィクスチャ・テストケース定義
5. **UI/UXデザイン** → Figmaまたはスケッチで画面設計

---

**最終更新：** 2026年6月6日  
**次回レビュー：** Phase 1 完了時
