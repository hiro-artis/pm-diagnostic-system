# PM協会テスト診断 エージェント仕様書

## 概要
各エージェントの詳細な実装仕様。インターフェース、入出力、処理ロジック、エラーハンドリングを定義。

---

## 1. テスト進行エージェント (Main Orchestrator Agent)

### 識別子
`agent_test_orchestrator`

### 責務
- テスト進行全体の統制
- 各テストエージェントの起動・終了
- テスト結果の集約
- 次フェーズの判定

### 入力スキーマ

```json
{
  "action": "start_primary_test" | "check_primary_results" | "start_secondary_test" | "finalize",
  "userId": "string",
  "sessionId": "uuid",
  "testConfig": {
    "retakeAllowed": boolean,
    "secondaryTestThreshold": 60,
    "primaryTestTimeout": 3600
  }
}
```

### 出力スキーマ

```json
{
  "status": "in_progress" | "primary_complete" | "secondary_complete" | "finalized",
  "nextAction": "run_basic_knowledge_test" | "run_office_migration_test" | "run_mindset_test" | "run_secondary_interview" | "generate_final_report",
  "results": {
    "primaryTest": { /* 1次テスト結果 */ },
    "secondaryTest": { /* 2次テスト結果（実施時のみ） */ }
  },
  "qualifiesForSecondary": boolean,
  "sessionEndTime": "ISO8601"
}
```

### 処理フロー

```
[START]
  ↓
[1次テスト開始判定]
  ├→ 新規セッション：基礎知識テスト開始
  └→ 再受検：前回結果確認
  ↓
[3つのテスト順序実行]
  1. 基礎知識テスト（100点）
  2. オフィス移転テスト（100点）
  3. マインドセット（90点）
  ↓
[合格判定]
  ├→ 全セクション合格 → 2次テスト進出
  ├→ 1つ以上不合格 → 再検査対象（1週間後に再受検可能）
  └→ マインドセット60点未満 → 2次テスト不可
  ↓
[2次テスト実施（条件合致時）]
  1. マインドセット検証エージェント起動
  2. 面接実施
  3. 詳細採点
  ↓
[最終レポート生成]
  ├→ スコア集計
  ├→ 評価判定
  ├→ フィードバック生成
  └→ ユーザーへ通知
  ↓
[END]
```

### エラーハンドリング

| エラー | 対応 |
|-------|------|
| セッションタイムアウト | 進捗状況保存 → ユーザーに通知 → 再開可能にする |
| エージェント起動失敗 | ログ記録 → 管理者通知 → ユーザーに再試行指示 |
| テスト結果の矛盾 | 詳細採点エージェント起動 → 再評価 |
| ネットワーク遮断 | 接続復帰時に対話再開 |

---

## 2. 基礎知識テスト実行エージェント

### 識別子
`agent_basic_knowledge_test`

### 責務
- PMの基礎知識10問を順序呈示
- 選択式回答の受け取り
- 正誤判定
- スコア計算（正答数 × 10点）

### 入力スキーマ

```json
{
  "sessionId": "uuid",
  "userId": "string",
  "questionSetVersion": "1.0"
}
```

### 出力スキーマ

```json
{
  "testId": "BK_<timestamp>",
  "score": 0-100,
  "totalQuestions": 10,
  "correctAnswers": 0-10,
  "questions": [
    {
      "questionId": "BK-001",
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "userAnswer": "string",
      "correctAnswer": "string",
      "isCorrect": boolean,
      "explanation": "string"
    }
  ],
  "passed": boolean,  // score >= 70
  "timeSpent": "seconds",
  "startTime": "ISO8601",
  "endTime": "ISO8601"
}
```

### 質問配信ロジック

```
1. 質問セットからランダムに10問選択（シャッフル）
2. 各問題で：
   - 質問テキストを表示
   - 4択オプション（A,B,C,D）を表示
   - ユーザー回答を取得
   - 正誤と解説を記録
3. 最後に全体スコアを表示
```

### 時間管理
- 推奨時間：15分
- タイムアウト：30分（警告は20分時点）

### エラーハンドリング

| エラー | 対応 |
|-------|------|
| 回答タイムアウト | 20分時点で警告 → 30分でテスト終了 → 暫定スコア表示 |
| ネットワーク遮断 | 最後の回答地点から再開 |
| 不正な回答入力 | 再入力要求 |

---

## 3. オフィス移転テスト実行エージェント

### 識別子
`agent_office_migration_test`

### 責務
- 選択式5問の実施（各5点）
- 記述式3問の実施（各25点）
- 記述式回答の採点エージェントへの送信

### 入力スキーマ

```json
{
  "sessionId": "uuid",
  "userId": "string",
  "questionSetVersion": "1.0"
}
```

### 出力スキーマ

```json
{
  "testId": "OM_<timestamp>",
  "mcScore": 0-25,           // 選択式：各5点×5問
  "essayScore": 0-75,        // 記述式：各25点×3問
  "totalScore": 0-100,       // 合計
  "questions": [
    {
      "questionId": "OM-MC-001",
      "type": "multiple_choice",
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "userAnswer": "string",
      "correctAnswer": "string",
      "score": 0-5
    },
    {
      "questionId": "OM-ES-001",
      "type": "essay",
      "question": "string",
      "userAnswer": "string",
      "wordCount": number,
      "score": 0-25,
      "scoringRationale": "string",
      "feedbackPoints": ["string"]
    }
  ],
  "passed": boolean,         // totalScore >= 65
  "timeSpent": "seconds",
  "startTime": "ISO8601",
  "endTime": "ISO8601"
}
```

### テスト進行フロー

#### フェーズ1：選択式（5問・合計25分推奨）
```
1. 各問題を順序呈示
2. ユーザー回答取得
3. 正誤判定と解説提示
4. スコア計算
```

#### フェーズ2：記述式（3問・合計60分推奨）
```
1. 各問題の背景・設問を詳しく説明
2. ユーザーの記述回答を取得
3. 記述内容の質チェック（文字数カウント等）
4. 採点エージェントへ送信
5. 採点結果を受け取り表示
```

### 記述式採点ロジック

記述式採点エージェント (`agent_essay_scorer`) へ以下を送信：

```json
{
  "questionId": "OM-ES-001",
  "questionText": "string",
  "userAnswer": "string",
  "evaluationCriteria": {
    "dimension1": {"name": "リスク認識の適切性", "maxScore": 5},
    "dimension2": {"name": "対応策の実現性", "maxScore": 10},
    "dimension3": {"name": "コミュニケーション戦略", "maxScore": 10}
  }
}
```

### エラーハンドリング

| エラー | 対応 |
|-------|------|
| 記述が短すぎる（100字未満） | 警告 → 追記を促す |
| 記述が長すぎる（400字超） | 警告 → 重要部分を確認 |
| タイムアウト | 現在までの回答で採点 → 暫定結果表示 |
| 採点エージェント遮断 | 管理者に通知 → 後日採点スケジュール |

---

## 4. マインドセットテスト実行エージェント

### 識別子
`agent_mindset_test`

### 責務
- 6つのシナリオ（各15点）を順序呈示
- マインドセット観点での採点
- 6つのマインドセット別スコア算出

### 入力スキーマ

```json
{
  "sessionId": "uuid",
  "userId": "string",
  "questionSetVersion": "1.0"
}
```

### 出力スキーマ

```json
{
  "testId": "MS_<timestamp>",
  "totalScore": 0-100,  // 概算スコア（AI回答分析による）
  "mindsetScores": {
    "futureFocused": 0-100,           // 未来志向
    "selfResponsibility": 0-100,      // 自責
    "kindness": 0-100,                // 優しさ
    "listeningSkill": 0-100,          // 聴く力
    "inclusivity": 0-100,             // 置いてきぼりにしない
    "collaboration": 0-100            // 一人で進まない
  },
  "scenarios": [
    {
      "scenarioId": "MS-S01",
      "scenario": "string",
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "userAnswer": "string",
      "correctAnswer": "string",
      "score": 0-15,
      "scoringRationale": "string",
      "evaluatedMindsets": {
        "futureFocused": 5,
        "selfResponsibility": 5
      }
    }
  ],
  "passed": boolean,  // totalScore >= 60
  "passedSecondaryTest": boolean,  // 2次テスト進出判定
  "timeSpent": "seconds",
  "startTime": "ISO8601",
  "endTime": "ISO8601"
}
```

### マインドセット別採点ロジック

各シナリオで選択肢を評価。ポイント配分例（MS-S01）：

```
[ユーザーが選択肢Cを選んだ場合]
  ↓
  ✓ 未来志向：経営課題の背景理解 → 5点
  ✓ 自責：複数案の自分での提案 → 5点
  → 合計：15点
  
[ユーザーが選択肢Aを選んだ場合]
  ↓
  ✗ 自責が不足（指示への盲従）
  ✗ 未来志向が不足（スコープ検討がない）
  → 合計：3点
```

### マインドセット統合スコア計算

```
totalScore = (Σ各シナリオスコア) / 6 × (100/15)

例：
  MS-S01: 15点
  MS-S02: 15点
  MS-S03: 12点
  MS-S04: 15点
  MS-S05: 10点
  MS-S06: 8点
  合計：75点 → 総合スコア = 83点
```

### エラーハンドリング

| エラー | 対応 |
|-------|------|
| AIの採点にばらつき | 詳細採点エージェント起動で再採点 |
| シナリオ理解不足 | シナリオ詳細説明の提供 → 回答修正可能 |

---

## 5. マインドセット検証エージェント（面接）

### 識別子
`agent_mindset_interview`

### 責務
- 1次テスト結果に基づいた深掘り面接
- 6つのマインドセットの実践的検証
- 開放型・深掘り型・検証型質問の実施
- 回答分析と仮スコア算出

### 入力スキーマ

```json
{
  "sessionId": "uuid",
  "userId": "string",
  "primaryTestResults": {
    "mindsetScores": { /* 1次テストのマインドセット別スコア */ }
  },
  "focusAreas": ["futureFocused", "collaboration"],  // 弱点マインドセット
  "interviewDepth": "standard" | "detailed"
}
```

### 出力スキーマ

```json
{
  "interviewId": "INT_<timestamp>",
  "duration": "seconds",
  "questionsAsked": number,
  "responses": [
    {
      "questionNumber": 1,
      "questionText": "string",
      "responseText": "string",
      "evaluatedMindsets": {
        "futureFocused": 4,
        "collaboration": 3
      },
      "consistencyWithPrimary": "consistent" | "improved" | "declined" | "unclear",
      "notes": "string"
    }
  ],
  "mindsetVerification": {
    "futureFocused": {
      "primaryScore": 75,
      "interviewScore": 78,
      "consistencyRating": "consistent",
      "evidence": ["string"]
    }
  },
  "overallAssessment": {
    "totalScore": 0-100,
    "gradeLevel": "A" | "B" | "C" | "再検査",
    "recommendation": "string",
    "key_strengths": ["string"],
    "development_areas": ["string"]
  }
}
```

### 面接質問テンプレート

#### フェーズ1：導入（5分）
- ラポール構築
- 1次テスト結果の簡要説明
- 面接の目的説明

#### フェーズ2：開放型質問（15分）
```
例（マインドセット：未来志向）
「あなたが過去に取り組んだプロジェクトで、
 長期的な視点から判断を変えた経験を教えてください」
```

#### フェーズ3：深掘り質問（15分）
```
例（マインドセット：聴く力）
「その判断のとき、相手の声をどの程度聴けていたと思いますか？
 もし今やり直すとしたら、何が違いますか？」
```

#### フェーズ4：検証型質問（10分）
```
例（マインドセット：置いてきぼりにしない）
「1次テストのシナリオ5では、あなたはCを選びました。
 実際のプロジェクトではこのような対応ができていますか？」
```

#### フェーズ5：クロージング（5分）
- 最終確認質問
- ご質問への対応
- 次ステップ説明

### 回答分析ロジック

```
1. 回答内容の解析
   - 使用語彙から価値観抽出
   - 具体性レベル評価
   - 矛盾点検出

2. マインドセット別スコアリング
   - 各回答から6つのマインドセットへのマッピング
   - スコア（1-5）で採点

3. 1次テストとの比較
   - 一貫性評価
   - スコア変動の理由分析

4. 最終判定
   - 6つのマインドセットの重み付き総合スコア
   - 等級判定
```

### エラーハンドリング

| エラー | 対応 |
|-------|------|
| 回答が簡潔すぎる | 「もう少し詳しく」と深掘り |
| 回答が1次テストと矛盾 | 「1次テストとの違いについて」と直接質問 |
| 面接中断 | 現在の回答で仮スコア算出 → 再開予定提示 |

---

## 6. 詳細採点エージェント

### 識別子
`agent_comprehensive_scorer`

### 責務
- 記述式問題の採点（オフィス移転テスト）
- マインドセット採点のばらつき補正
- 1次＋2次の統合採点
- 最終評価判定

### 入力スキーマ

```json
{
  "sessionId": "uuid",
  "targetType": "essay" | "mindset_variance" | "comprehensive_final",
  "payload": {
    // targetTypeに応じた詳細情報
  }
}
```

### 出力スキーマ

```json
{
  "scoringId": "SCORE_<timestamp>",
  "revisedScores": {
    "basicKnowledge": 0-100,
    "officeMigration": 0-100,
    "mindset": 0-100,
    "secondaryInterview": 0-100
  },
  "finalAssessment": {
    "totalScore": 0-100,
    "gradeLevel": "A" | "B" | "C" | "再検査",
    "summary": "string",
    "strengths": ["string"],
    "developmentAreas": ["string"],
    "recommendations": ["string"]
  },
  "scoringDetails": [
    {
      "questionId": "OM-ES-001",
      "originalScore": 20,
      "revisedScore": 22,
      "reason": "string",
      "scorerNotes": "string"
    }
  ]
}
```

### 採点基準（記述式例）

#### OM-ES-001: 移転前の課題発見と解決策

**評価ディメンション：**

| ディメンション | 配点 | 5点 | 3点 | 1点 |
|---|---|---|---|---|
| リスク認識 | 5点 | 複数の異なるリスクを特定 | 主なリスク1-2個を認識 | リスク認識が曖昧 |
| 対応策の実現性 | 10点 | スコープ・品質・人員配置の工夫がある | 1-2つの対応が示されている | 対応が抽象的・実現性不確実 |
| コミュニケーション | 10点 | 営業部・企画部の異なるニーズに対応した戦略 | コミュニケーション計画あるが片面的 | コミュニケーション未検討 |

**採点ロジック：**
```
1. 記述内容を各ディメンションに分類
2. 各ディメンション別にスコア判定
3. ディメンション合計が問題スコア
4. 複数の採点者による評価で平均化（クロスチェック）
```

---

## 7. エージェント間通信インターフェース

### メッセージ形式

```json
{
  "messageId": "uuid",
  "fromAgent": "agent_X",
  "toAgent": "agent_Y",
  "messageType": "execute" | "request_score" | "notify_result" | "error",
  "timestamp": "ISO8601",
  "payload": {},
  "priority": "high" | "normal" | "low"
}
```

### 主要な通信パターン

#### パターン1：オーケストレーター → テスト実行エージェント
```
messageType: "execute"
payload: {
  "testName": "basic_knowledge_test",
  "sessionId": "uuid",
  "userId": "string"
}
```

#### パターン2：テスト実行エージェント → 採点エージェント
```
messageType: "request_score"
payload: {
  "questionId": "OM-ES-001",
  "userAnswer": "string",
  "evaluationCriteria": {}
}
```

#### パターン3：採点エージェント → テスト実行エージェント
```
messageType: "notify_result"
payload: {
  "questionId": "OM-ES-001",
  "score": 22,
  "rationale": "string"
}
```

---

## 実装優先順位

### Phase 1: コア基盤
1. **テスト進行エージェント** ← 最優先
2. **基礎知識テスト実行エージェント** ← 最シンプルで優先度高
3. **エージェント通信インターフェース**

### Phase 2: 中核テスト
4. **オフィス移転テスト実行エージェント**
5. **記述式採点エージェント（簡易版）**

### Phase 3: マインドセット
6. **マインドセットテスト実行エージェント**
7. **詳細採点エージェント**

### Phase 4: 面接（2次テスト）
8. **マインドセット検証エージェント**

### Phase 5: 統合・検証
9. **統合テスト**
10. **UI/UX実装**

