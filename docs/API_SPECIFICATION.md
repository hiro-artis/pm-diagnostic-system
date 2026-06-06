# PM協会テスト診断システム - API仕様書

**バージョン：** 1.0  
**作成日：** 2026年6月6日  
**ステータス：** 本運用対応

---

## 1. 概要

PM診断システムの REST API 仕様書です。クライアント（CLI、Web UI、外部システム）とバックエンドエージェント間の通信インターフェースを定義します。

### 1.1 ベース URL

```
http://localhost:8000/api/v1
```

### 1.2 認証

現在：なし（開発環境）  
本運用：APIキー認証（ヘッダ: `X-API-Key`）

### 1.3 データ形式

- **リクエスト：** JSON
- **レスポンス：** JSON
- **文字コード：** UTF-8

---

## 2. セッション管理 API

### 2.1 セッション開始

```
POST /sessions/start
```

**説明：** 新規テストセッションを開始します。

**リクエスト：**

```json
{
  "user_id": "string",
  "user_name": "string",
  "email": "string",
  "test_config": {
    "language": "ja",
    "timeout_minutes": 90
  }
}
```

**レスポンス（成功）：** `201 Created`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user001",
  "status": "started",
  "current_phase": "primary",
  "created_at": "2026-06-06T10:00:00Z",
  "time_limit_seconds": 5400,
  "message": "テストセッションを開始しました。"
}
```

**エラーレスポンス：** `400 Bad Request`

```json
{
  "error": "user_id is required",
  "error_code": "INVALID_INPUT"
}
```

---

### 2.2 セッション状態取得

```
GET /sessions/{session_id}
```

**説明：** 現在のセッション状態を取得します。

**レスポンス：** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user001",
  "status": "in_progress",
  "current_phase": "primary",
  "current_test": "mindset",
  "current_question_index": 3,
  "elapsed_time_seconds": 1800,
  "time_limit_seconds": 5400,
  "progress_percent": 50
}
```

---

### 2.3 セッション再開

```
POST /sessions/{session_id}/resume
```

**説明：** 中断されたセッションを再開します。

**リクエスト：**

```json
{
  "user_id": "user001"
}
```

**レスポンス：** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "message": "セッションを再開しました。"
}
```

---

## 3. テスト API

### 3.1 テスト開始（1次テスト）

```
POST /tests/primary/start
```

**説明：** 1次テストを開始します（Basic Knowledge → Office Migration → Mindset）

**リクエスト：**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**レスポンス：** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "next_test": "basic_knowledge",
  "message": "1次テストを開始します。"
}
```

---

### 3.2 問題取得

```
GET /tests/questions/{question_id}
```

**説明：** 特定の問題情報を取得します。

**レスポンス：** `200 OK`

```json
{
  "question_id": "BK-001",
  "section": "basic_knowledge",
  "question_text": "プロジェクト管理の定義として、最も適切なものはどれか？",
  "question_type": "multiple_choice",
  "options": {
    "A": "計画に従って業務を遂行すること",
    "B": "明確に定義された目標を達成するために、資源を計画的に配分・管理し、時間内に成果物を完成させること",
    "C": "チームメンバーを管理して作業を進めること",
    "D": "顧客の要望をすべて聞き入れること"
  }
}
```

---

### 3.3 回答送信

```
POST /tests/answers
```

**説明：** テスト回答を送信・保存します。

**リクエスト：**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_id": "BK-001",
  "answer": "B",
  "time_spent_seconds": 45
}
```

**レスポンス：** `200 OK`

```json
{
  "question_id": "BK-001",
  "status": "saved",
  "message": "回答を保存しました。",
  "next_question_id": "BK-002"
}
```

---

### 3.4 テスト結果（1次テスト）

```
GET /tests/primary/results/{session_id}
```

**説明：** 1次テストの結果を取得します。

**レスポンス：** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "primary_completed": true,
  "scores": {
    "basic_knowledge": {
      "score": 85,
      "passed": true,
      "correct_answers": 8,
      "total_questions": 10
    },
    "office_migration": {
      "score": 72,
      "passed": true,
      "mc_score": 80,
      "essay_score": 65
    },
    "mindset": {
      "total_score": 68,
      "passed": true,
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
  "proceed_to_secondary": true,
  "message": "1次テストが完了しました。2次テストの対象となります。"
}
```

---

## 4. 2次テスト（面接） API

### 4.1 2次テスト開始

```
POST /tests/secondary/start
```

**説明：** 2次テスト（マインドセット面接）を開始します。

**リクエスト：**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**レスポンス：** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "phase": "secondary",
  "message": "2次テスト（マインドセット面接）を開始します。",
  "expected_duration_minutes": 20
}
```

---

### 4.2 面接質問取得

```
GET /tests/secondary/questions
```

**説明：** 面接の質問を取得します（動的に生成される）

**レスポンス：** `200 OK`

```json
{
  "questions": [
    {
      "question_number": 1,
      "question_text": "1次テストで「優しさ」のスコアが低かった傾向です。チームメンバーが仕事と個人的な悩みで悩んでいる場合、どのような対応をしますか？",
      "question_type": "open",
      "evaluated_mindsets": ["kindness", "listening_skill"]
    },
    {
      "question_number": 2,
      "question_text": "その対応を選んだ理由は何ですか？",
      "question_type": "deep_dive"
    }
  ]
}
```

---

### 4.3 面接回答送信

```
POST /tests/secondary/answers
```

**説明：** 面接の回答を送信します。

**リクエスト：**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_number": 1,
  "response_text": "まず、そのメンバーの話を丁寧に聞いて、背景にある課題を理解することが大切だと考えます。仕事と個人的な悩みが絡み合っている場合、双方の視点から一緒に整理することが重要です。...",
  "time_spent_seconds": 180
}
```

**レスポンス：** `200 OK`

```json
{
  "question_number": 1,
  "status": "saved",
  "message": "回答を保存しました。"
}
```

---

## 5. 最終評価 API

### 5.1 最終評価取得

```
GET /assessments/final/{session_id}
```

**説明：** 最終評価レポートを取得します。

**レスポンス：** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user001",
  "test_date": "2026-06-06T10:00:00Z",
  "scores": {
    "basic_knowledge": 85,
    "office_migration": 72,
    "mindset": 68,
    "interview": 70,
    "total": 73.5
  },
  "mindset_breakdown": {
    "future_focused": 72,
    "self_responsibility": 68,
    "kindness": 70,
    "listening_skill": 69,
    "inclusivity": 67,
    "collaboration": 65
  },
  "grade": "B",
  "summary": "優れたPM人材として、基本的な知識とスキルを備えています。マインドセットについても良好で、チームをまとめるリーダーシップが期待できます。",
  "strengths": [
    "PM基礎知識の理解が深い",
    "実務経験が豊富",
    "聴く力が優れている"
  ],
  "development_areas": [
    "一人で進まない姿勢をさらに強化する",
    "置いてきぼりにしない心遣いを継続的に意識する"
  ],
  "recommendations": [
    "複数部門の協力が必要なプロジェクトでの経験を積む",
    "チームビルディングに関する研修に参加する"
  ]
}
```

---

## 6. 管理 API

### 6.1 結果検索

```
GET /admin/results
```

**パラメータ：**

```
?user_id=user001
?date_from=2026-06-01
?date_to=2026-06-30
?grade=A,B,C
```

**レスポンス：** `200 OK`

```json
{
  "results": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user001",
      "user_name": "山田太郎",
      "test_date": "2026-06-06T10:00:00Z",
      "total_score": 73.5,
      "grade": "B",
      "status": "completed"
    }
  ],
  "total_count": 1
}
```

---

### 6.2 結果エクスポート

```
POST /admin/export
```

**リクエスト：**

```json
{
  "format": "csv",
  "date_from": "2026-06-01",
  "date_to": "2026-06-30"
}
```

**レスポンス：** `200 OK`  
ファイルダウンロード（CSV）

---

## 7. エラーハンドリング

### 7.1 標準エラーレスポンス

```json
{
  "error": "string",
  "error_code": "string",
  "details": "optional string"
}
```

### 7.2 エラーコード一覧

| エラーコード | HTTP Status | 説明 |
|-------------|-------------|------|
| INVALID_INPUT | 400 | 入力値が不正 |
| SESSION_NOT_FOUND | 404 | セッションが見つからない |
| SESSION_EXPIRED | 410 | セッションが期限切れ |
| UNAUTHORIZED | 401 | 認証失敗 |
| INTERNAL_ERROR | 500 | サーバーエラー |
| TIMEOUT | 504 | タイムアウト |

---

## 8. レート制限

- **制限：** 100 requests / 1 minute
- **ヘッダ：**
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

---

## 9. 実装例（curl）

### セッション開始

```bash
curl -X POST http://localhost:8000/api/v1/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user001",
    "user_name": "山田太郎",
    "email": "yamada@example.com"
  }'
```

### 回答送信

```bash
curl -X POST http://localhost:8000/api/v1/tests/answers \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "question_id": "BK-001",
    "answer": "B",
    "time_spent_seconds": 45
  }'
```

---

**最終更新：** 2026年6月6日  
**次版予定：** 2次テスト詳細化（2026年7月）
