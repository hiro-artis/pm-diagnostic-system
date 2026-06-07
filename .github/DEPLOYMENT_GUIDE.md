# 🚀 自動デプロイメント セットアップガイド

**対象**: GitHub Actions を使用した GCP Cloud Run + Vercel 自動デプロイメント

---

## 📋 必要な準備

### 1️⃣ GitHub リポジトリ シークレットの設定

GitHub リポジトリの `Settings > Secrets and variables > Actions` で以下のシークレットを追加してください：

#### GCP 関連

```
GCP_PROJECT_ID
  説明: Google Cloud プロジェクト ID
  例: pm-diagnostic-123456

GCP_SA_KEY
  説明: GCP サービスアカウント JSON キー（Base64 エンコード）
  取得方法:
    1. GCP Console → サービスアカウント
    2. pm-diagnostic-api サービスアカウント選択
    3. キータブ → JSON キーをダウンロード
    4. cat key.json | base64 でエンコード
    5. GitHub シークレットに登録
```

#### Vercel 関連

```
VERCEL_TOKEN
  説明: Vercel API トークン
  取得方法:
    1. https://vercel.com/account/tokens
    2. "Create" で新しいトークン生成
    3. GitHub シークレットに登録

VERCEL_ORG_ID
  説明: Vercel 組織 ID
  取得方法:
    1. https://vercel.com/account/overview
    2. Team / Org ID の値

VERCEL_PROJECT_ID
  説明: Vercel プロジェクト ID
  取得方法:
    1. Vercel ダッシュボード → プロジェクト選択
    2. Settings → Project ID コピー
```

#### Slack 通知 関連

```
SLACK_WEBHOOK_URL
  説明: Slack Incoming Webhook URL
  取得方法:
    1. https://api.slack.com/apps
    2. アプリ作成 または 既存アプリ選択
    3. Incoming Webhooks 有効化
    4. Add New Webhook to Workspace
    5. URL をコピー

  （オプション: 通知が不要な場合はスキップ可）
```

---

## 🔄 デプロイメント フロー

### トリガー

```
イベント: main ブランチへの push
条件: GitHub Actions が有効な状態

デプロイメント開始:
  1. Backend (GCP Cloud Run) デプロイ
  2. Frontend (Vercel) デプロイ
  ※ 並行実行（同時）
```

### デプロイメント ステップ

#### Backend (Cloud Run)

```
1️⃣ Docker イメージのビルド
   - Dockerfile を使用
   - gcr.io/{PROJECT_ID}/pm-diagnostic-api:latest にタグ付け

2️⃣ Google Container Registry (GCR) へプッシュ
   - GCP 認証済み状態で実行
   - :latest と :{COMMIT_SHA} タグでプッシュ

3️⃣ Cloud Run へのデプロイ
   - イメージ: gcr.io/{PROJECT_ID}/pm-diagnostic-api:{COMMIT_SHA}
   - リージョン: asia-northeast1
   - メモリ: 512Mi
   - CPU: 1 コア
   - タイムアウト: 300秒

4️⃣ デプロイ URL ログ出力
   - 成功したデプロイメント URL を表示
```

#### Frontend (Vercel)

```
1️⃣ Vercel CLI インストール
   - npm install -g vercel

2️⃣ Vercel へデプロイ
   - --prod フラグで本番環境デプロイ
   - 環境変数: NEXT_PUBLIC_API_BASE_URL を設定

3️⃣ デプロイ URL 取得
   - https://pm-diagnostic.vercel.app
```

### テストと通知

```
1️⃣ 統合テスト実行
   - Health check テスト
   - API エンドポイント テスト

2️⃣ Slack 通知送信
   - 成功時: 緑色メッセージ + デプロイ URL
   - 失敗時: 赤色メッセージ + エラーリンク
```

---

## 📊 デプロイメント状態確認

### リアルタイム監視

GitHub リポジトリの `Actions` タブで実行状況を確認：

```
Running: デプロイ実行中
Completed: デプロイ完了
Failed: デプロイ失敗
```

### ログの確認

```
1. GitHub Actions タブを開く
2. 最新の "Deploy to GCP and Vercel" ワークフロー選択
3. ジョブ名をクリック
4. ログを確認
```

### デプロイ後の確認

```
✅ Backend API
   curl https://pm-diagnostic-api.run.app/health

✅ Frontend
   https://pm-diagnostic.vercel.app にアクセス
```

---

## 🔧 トラブルシューティング

### GCP デプロイが失敗する場合

```
❌ 原因: GCP_SA_KEY が無効
✅ 対策:
  1. GCP Console で サービスアカウントキーを再生成
  2. Base64 エンコード
  3. GitHub シークレットを更新

❌ 原因: Cloud Run クォータ超過
✅ 対策:
  1. GCP Console → Cloud Run
  2. 既存サービスの不要な公開リビジョンを削除
  3. 再度デプロイ
```

### Vercel デプロイが失敗する場合

```
❌ 原因: VERCEL_TOKEN が無効
✅ 対策:
  1. Vercel で トークンを再生成
  2. GitHub シークレットを更新

❌ 原因: Next.js ビルドエラー
✅ 対策:
  1. ローカルで npm run build を実行
  2. エラーを修正
  3. push で再デプロイ
```

### Slack 通知が来ない場合

```
❌ 原因: SLACK_WEBHOOK_URL が設定されていない
✅ 対策:
  1. Slack Incoming Webhook を作成
  2. GitHub シークレットに登録

❌ 原因: Webhook URL が無効
✅ 対策:
  1. https://api.slack.com で確認
  2. URL を再生成
  3. GitHub シークレットを更新
```

---

## 📈 パフォーマンス目標

```
デプロイ時間: 10-15分
  - Backend ビルド: 5分
  - GCR プッシュ: 2分
  - Cloud Run デプロイ: 3分
  - Frontend デプロイ: 5分

可用性: 99.9% 以上
  - Cloud Run: SLA 99.95%
  - Vercel: SLA 99.99%
```

---

## 🎯 次のステップ

```
1️⃣ GitHub シークレット設定
   └─ すべてのシークレットを登録

2️⃣ 初回デプロイ
   └─ main ブランチに小さな変更を push
   └─ Actions で実行状況を確認

3️⃣ 本番運用
   └─ 日々のコミットで自動デプロイ
   └─ Slack 通知で監視
```

---

**自動デプロイメント セットアップ完了！** 🎉