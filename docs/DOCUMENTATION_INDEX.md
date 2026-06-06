# PM協会テスト診断システム - ドキュメント索引

**最終更新：** 2026年6月6日  
**ドキュメント総数：** 10個

---

## 📚 ドキュメント体系（読むべき順序）

### 🎯 プロジェクト理解（最初に読む）

#### 1. **IMPLEMENTATION_SUMMARY.md** （本ドキュメント関連）
- **目的：** プロジェクト全体像の把握
- **対象者：** 全関係者
- **内容：** 実装完了状況、コンポーネント構成、テスト結果、本運用チェックリスト
- **読了時間：** 15-20分
- **次ステップ：** 詳細な部分に応じて、以下のドキュメントを参照

#### 2. **CLAUDE.md**（リポジトリルート）
- **目的：** 実装計画・フェーズ定義
- **対象者：** プロジェクトマネージャ、リード開発者
- **内容：** 実装方針、5フェーズの詳細、技術選定、リスク管理
- **読了時間：** 20-30分

---

### 🏗️ 設計・要件（アーキテクチャ理解）

#### 3. **REQUIREMENTS.md**
- **目的：** 機能・非機能要件の詳細定義
- **対象者：** 要件定義者、開発リード、QA
- **内容：**
  - 機能要件（FR-01～FR-08）
  - 非機能要件（パフォーマンス、セキュリティ）
  - 技術要件（スタック、DB スキーマ）
  - 採点ロジック詳細
  - Phase 別実装内容
- **読了時間：** 30-40分
- **用途：** 実装時の仕様確認、テスト設計時の基準

#### 4. **agent-map.md**
- **目的：** システムアーキテクチャ・エージェント構成
- **対象者：** アーキテクト、開発者
- **内容：**
  - システム全体フロー図
  - 6つのエージェント詳細設計
  - データ構造・スキーマ
  - 実装フェーズ概要
  - マインドセット採点ルール
- **読了時間：** 20-30分
- **用途：** エージェント実装時の参照、システム設計の確認

#### 5. **agent-specifications.md**
- **目的：** 各エージェントの詳細仕様
- **対象者：** 開発者（エージェント実装者）
- **内容：**
  - 各エージェントの入出力
  - 処理ロジック詳細
  - 采点基準と計算方式
  - テスト用サンプルデータ
- **読了時間：** 30-40分
- **用途：** エージェント実装・テスト時の参照

---

### ❓ テスト・問題設計

#### 6. **test-questions.md**
- **目的：** 全テスト問題セット（35問）
- **対象者：** テスト設計者、出題者、教科書作成者
- **内容：**
  - **1次テスト問題**
    - 基礎知識テスト（10問）
    - オフィス移転テスト（5問 + 3問）
    - マインドセット（6シナリオ）
  - 各問題の詳細説明
  - 採点基準
  - 評価パターン
- **読了時間：** 40-60分
- **用途：** テスト出題、採点基準確認

---

### 🔌 API・インターフェース

#### 7. **API_SPECIFICATION.md**
- **目的：** REST API 完全仕様書
- **対象者：** API利用者、フロントエンド開発者、外部統合担当者
- **内容：**
  - セッション管理 API
  - テスト実施 API
  - 面接 API
  - 最終評価 API
  - 管理 API
  - エラーハンドリング
  - 実装例（curl）
- **読了時間：** 20-30分
- **用途：** クライアント実装、API 連携

---

### 📋 運用・保守

#### 8. **OPERATION_MANUAL.md**
- **目的：** システム運用手順・トラブル対応
- **対象者：** システム管理者、運用担当者
- **内容：**
  - 環境セットアップ手順
  - システム起動方法（CLI / Web API）
  - テスト実施手順
  - テスト問題管理
  - データ管理・バックアップ
  - トラブルシューティング
  - パフォーマンスチューニング
  - 定期メンテナンス
- **読了時間：** 30-40分
- **用途：** 日常運用、問題解決

---

### 📊 プロジェクト進捗報告（参考）

#### 9. **PROJECT_COMPLETE.md**
- **目的：** プロジェクト完了報告書
- **対象者：** ステークホルダー、経営層
- **内容：**
  - 実装統計（コード行数、コンポーネント数）
  - テスト成功率（48/48 = 100%）
  - システムアーキテクチャ図
  - 診断フロー
  - 実装コンポーネント一覧
  - 実装品質指標
- **読了時間：** 15-20分

#### 10. **PROJECT_STATUS.md**
- **目的：** プロジェクト進捗報告（各フェーズごと）
- **対象者：** プロジェクトマネージャ、利害関係者
- **内容：**
  - フェーズ別完成度
  - 実装済みコンポーネント
  - コード量統計
  - テストカバレッジ
- **読了時間：** 10-15分

---

## 📖 用途別ドキュメント参照ガイド

### システム開発者向け

**初回セットアップ時：**
1. IMPLEMENTATION_SUMMARY.md（全体像）
2. REQUIREMENTS.md（要件確認）
3. agent-map.md（アーキテクチャ）
4. agent-specifications.md（詳細仕様）

**実装時：**
- agent-specifications.md（エージェント実装）
- test-questions.md（テスト問題確認）

**テスト時：**
- test-questions.md（テストケース）
- agent-specifications.md（期待値確認）

### API 利用者・フロントエンド開発者向け

**初回セットアップ時：**
1. IMPLEMENTATION_SUMMARY.md（全体像）
2. API_SPECIFICATION.md（API 仕様）

**実装時：**
- API_SPECIFICATION.md（API 仕様・実装例）

**トラブル時：**
- API_SPECIFICATION.md（エラーコード）
- OPERATION_MANUAL.md（トラブルシューティング）

### システム管理者・運用担当者向け

**本運用開始前：**
1. OPERATION_MANUAL.md（セットアップ・運用手順）
2. REQUIREMENTS.md（非機能要件確認）

**日常運用時：**
- OPERATION_MANUAL.md（実施手順・トラブル対応）

**定期メンテナンス時：**
- OPERATION_MANUAL.md（定期メンテナンス項目）

### テスト設計者・出題者向け

**テスト問題設計時：**
1. test-questions.md（問題セット確認）
2. agent-specifications.md（採点基準確認）

**出題・採点時：**
- test-questions.md（全問題）
- agent-specifications.md（採点ルール）

### プロジェクトマネージャ・ステークホルダー向け

**プロジェクト開始時：**
1. CLAUDE.md（実装計画・フェーズ）
2. IMPLEMENTATION_SUMMARY.md（全体像）

**進捗確認時：**
- PROJECT_STATUS.md（フェーズ別進捗）
- PROJECT_COMPLETE.md（完了報告）

---

## 🔗 ドキュメント間の関連性

```
┌─────────────────────────────────────────────────────┐
│   IMPLEMENTATION_SUMMARY.md （全体のハブ）         │
│   ↓                                                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │  REQUIREMENTS.md │      │   agent-map.md   │   │
│  │  （要件定義）    │      │ （アーキテクチャ）│   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│           │                          │              │
│           ↓                          ↓              │
│  ┌──────────────────────────────────────────┐     │
│  │  agent-specifications.md                 │     │
│  │  （エージェント詳細仕様）                │     │
│  └──────────────────┬───────────────────────┘     │
│                     │                              │
│           ┌─────────┼─────────┐                   │
│           ↓         ↓         ↓                   │
│  ┌─────────────┐ ┌──────────────────┐ ┌──────┐  │
│  │test-        │ │OPERATION_MANUAL  │ │API_  │  │
│  │questions.md │ │（運用手順）      │ │SPEC  │  │
│  └─────────────┘ └──────────────────┘ └──────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘

参考情報：PROJECT_STATUS.md, PROJECT_COMPLETE.md
```

---

## 📝 ドキュメント更新ガイドライン

### 更新時期

| ドキュメント | 更新時期 | 担当者 |
|------------|---------|--------|
| REQUIREMENTS.md | フェーズ完了時 | PL・開発リード |
| agent-specifications.md | エージェント実装完了時 | 開発者 |
| test-questions.md | テスト問題変更時 | テスト設計者 |
| API_SPECIFICATION.md | API 仕様変更時 | API 開発者 |
| OPERATION_MANUAL.md | 運用手順変更時 | 運用管理者 |
| PROJECT_STATUS.md | フェーズ完了時 | PL |

### 更新手順

1. 該当ドキュメントを開く
2. 「最終更新日」を更新
3. 変更内容を記載
4. Git commit で履歴を残す
   ```bash
   git add docs/XXXXX.md
   git commit -m "Update XXXXX.md: [変更内容]"
   ```

---

## 🎓 学習パス（推奨読了順序）

### 初心者向け（20-30分）
1. IMPLEMENTATION_SUMMARY.md
2. agent-map.md

### 開発者向け（1-1.5時間）
1. IMPLEMENTATION_SUMMARY.md
2. REQUIREMENTS.md
3. agent-map.md
4. agent-specifications.md（関連部分）

### 運用者向け（1-2時間）
1. IMPLEMENTATION_SUMMARY.md
2. OPERATION_MANUAL.md
3. API_SPECIFICATION.md（参考）

### 総合的な理解（2-3時間）
1. CLAUDE.md
2. IMPLEMENTATION_SUMMARY.md
3. REQUIREMENTS.md
4. agent-map.md
5. agent-specifications.md
6. API_SPECIFICATION.md
7. OPERATION_MANUAL.md

---

## 🔍 キーワード検索ガイド

| キーワード | 参照ドキュメント |
|----------|-----------------|
| マインドセット採点 | agent-specifications.md, test-questions.md |
| API 仕様 | API_SPECIFICATION.md |
| エージェント実装 | agent-specifications.md |
| テスト問題 | test-questions.md |
| 運用手順 | OPERATION_MANUAL.md |
| エラー対応 | OPERATION_MANUAL.md, API_SPECIFICATION.md |
| セットアップ | OPERATION_MANUAL.md |
| 採点基準 | agent-specifications.md, test-questions.md |
| データモデル | agent-specifications.md, REQUIREMENTS.md |

---

## 📞 ドキュメント問い合わせ先

**質問や不明な点がある場合：**

1. まず、このドキュメント索引で関連ドキュメントを確認
2. 該当ドキュメントを読了
3. 解決しない場合は、以下に問い合わせ
   - **技術的質問：** support-dev@pm-association.jp
   - **運用質問：** support-ops@pm-association.jp
   - **その他：** support@pm-association.jp

---

**最終更新：** 2026年6月6日  
**作成者：** Claude Code (Anthropic)  
**バージョン：** 1.0

