# PM協会テスト診断システム - デプロイメントガイド

## 本運用環境構成

```
┌─────────────────────────────────┐
│   Vercel Frontend               │
│   (Next.js + React)             │
│   pm-diagnostic.vercel.app      │
└──────────────┬──────────────────┘
               │ HTTPS API calls
┌──────────────▼──────────────────┐
│   Google Cloud Run              │
│   (FastAPI + Python)            │
│   pm-diagnostic-backend.run.app │
└──────────────┬──────────────────┘
               │ Cloud SQL Proxy
┌──────────────▼──────────────────┐
│   Cloud SQL PostgreSQL          │
│   (db-f1-micro / shared)        │
└─────────────────────────────────┘
```

---

## ステップ1：Google Cloud Project セットアップ

### 前提条件

- Google Cloud アカウント（無料枠対象）
- `gcloud` CLI インストール
- 管理者: Hiro さん

### 初期セットアップ

```bash
# プロジェクド作成（既存プロジェクトがあれば使用）
gcloud projects create pm-diagnostic-system \
  --name="PM協会テスト診断システム"

# プロジェクド設定
PROJECT_ID=pm-diagnostic-system
gcloud config set project $PROJECT_ID

# 課金有効化（Cloud Run/Cloud SQL用）
gcloud billing projects link $PROJECT_ID \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### 必要なAPI有効化

```bash
# Cloud Run API
gcloud services enable run.googleapis.com

# Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com

# Cloud Build API（自動デプロイ用）
gcloud services enable cloudbuild.googleapis.com

# Container Registry
gcloud services enable containerregistry.googleapis.com
```

---

## ステップ2：Cloud SQL データベース準備

### PostgreSQL インスタンス作成

```bash
gcloud sql instances create pm-diagnostic-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast1 \
  --backup-start-time=03:00 \
  --enable-bin-log
```

**料金目安**：月約 ¥650（db-f1-micro）

### データベース・ユーザー作成

```bash
# データベース作成
gcloud sql databases create pm_diagnostic \
  --instance=pm-diagnostic-db

# パスワード生成（安全なパスワードを設定）
DB_PASSWORD=$(openssl rand -base64 32)
echo "DB_PASSWORD=$DB_PASSWORD" > /tmp/db_password.txt

# ユーザー作成
gcloud sql users create pm_user \
  --instance=pm-diagnostic-db \
  --password=$DB_PASSWORD
```

### 接続テスト

```bash
# Cloud SQL Proxy を使用（ローカルから接続テスト）
cloud-sql-proxy pm-diagnostic-system:asia-northeast1:pm-diagnostic-db &
psql -h localhost -U pm_user -d pm_diagnostic
```

---

## ステップ3：Cloud Run デプロイ

### 認証設定

```bash
# Docker に Google Cloud 認証を追加
gcloud auth configure-docker
```

### イメージビルド・プッシュ

```bash
# イメージビルド
docker build -t pm-diagnostic-backend:latest .

# タグ付け（Google Container Registry）
docker tag pm-diagnostic-backend:latest \
  gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest

# プッシュ
docker push gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest
```

### Cloud Run デプロイ

```bash
gcloud run deploy pm-diagnostic-backend \
  --image gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest \
  --platform managed \
  --region asia-northeast1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
  --set-env-vars "FRONTEND_URL=https://pm-diagnostic.vercel.app" \
  --no-allow-unauthenticated
```

### 環境変数設定

```bash
gcloud run services update pm-diagnostic-backend \
  --region asia-northeast1 \
  --update-env-vars ANTHROPIC_API_KEY=your_key_here
```

### デプロイ確認

```bash
# サービス URL 取得
gcloud run services describe pm-diagnostic-backend \
  --region asia-northeast1 \
  --format='value(status.url)'

# ヘルスチェック
curl https://pm-diagnostic-backend-xxx.run.app/health
```

---

## ステップ4：Vercel フロントエンド デプロイ

### リポジトリ準備

```bash
# Vercel 用フロントエンド実装
mkdir frontend
cd frontend
npx create-next-app@latest . --typescript --tailwind

# または git clone してきた場合
git clone https://github.com/your-org/pm-diagnostic-frontend
cd pm-diagnostic-frontend
```

### 環境変数設定

`.env.local` をプロジェクト直下に作成：

```env
NEXT_PUBLIC_API_BASE_URL=https://pm-diagnostic-backend-xxx.run.app
NEXT_PUBLIC_API_KEY=your_optional_api_key
```

### Vercel へのデプロイ

**方法 1: Git 連携（推奨）**

```bash
# GitHub リポジトリプッシュ
git push origin main

# Vercel.com にアクセス
# 1. import プロジェクト
# 2. GitHub リポジトリ選択
# 3. 環境変数設定
# 4. デプロイ
```

**方法 2: CLI デプロイ**

```bash
npm install -g vercel
vercel --prod
```

---

## ステップ5：継続的デプロイ

### Cloud Run 自動デプロイ（GitHub 連携）

```bash
# Cloud Build トリガー作成（GitHub と連携）
gcloud builds connect github \
  --repository-name pm-diagnostic-backend \
  --repository-owner your-github-org \
  --region asia-northeast1

# cloudbuild.yaml 作成（プロジェクトルート）
cat > cloudbuild.yaml << 'EOF'
steps:
  # Test
  - name: 'python:3.11'
    entrypoint: pip
    args: ['install', '-r', 'requirements.txt']
  
  - name: 'python:3.11'
    entrypoint: pytest
    args: ['tests/']
  
  # Build
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t',
      'gcr.io/$PROJECT_ID/pm-diagnostic-backend:$COMMIT_SHA',
      '-t',
      'gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest',
      '.'
    ]
  
  # Push
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/pm-diagnostic-backend:$COMMIT_SHA']
  
  # Deploy
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - run
      - --filename=k8s/
      - --image=gcr.io/$PROJECT_ID/pm-diagnostic-backend:$COMMIT_SHA
      - --location=asia-northeast1
      - --cluster=pm-diagnostic

images:
  - 'gcr.io/$PROJECT_ID/pm-diagnostic-backend:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest'
EOF
```

### Vercel 自動デプロイ

GitHub 連携設定で自動デプロイが有効化されます。

---

## ステップ6：監視・ロギング

### Cloud Run ログ確認

```bash
gcloud run logs read pm-diagnostic-backend \
  --region asia-northeast1 \
  --limit 50 \
  --follow
```

### Cloud Logging ダッシュボード

Google Cloud Console:
- Cloud Run → pm-diagnostic-backend → ログ
- エラー検出 → アラート設定

### アラート設定（推奨）

```bash
# エラーレート > 1% でアラート
gcloud monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="PM Diagnostic - High Error Rate" \
  --condition-display-name="Error rate > 1%" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s
```

---

## ステップ7：本番チェックリスト

### デプロイ前

- [ ] テスト全て合格確認（`pytest tests/`）
- [ ] 環境変数設定確認（ANTHROPIC_API_KEY等）
- [ ] Dockerfile ヘルスチェック動作確認
- [ ] 無料枠内であること確認

### デプロイ後

- [ ] ヘルスチェック `/health` 疎通確認
- [ ] 1次テスト フローテスト（Vercel UI から）
- [ ] マインドセット採点正確性確認
- [ ] Cloud SQL バックアップ有効確認
- [ ] ログ記録正常確認

### 運用

- [ ] 月1回：ログ確認・エラー確認
- [ ] 月1回：バックアップテスト（Cloud SQL）
- [ ] 3ヶ月1回：セキュリティアップデート確認

---

## トラブルシューティング

### Cloud Run がデプロイ失敗

```bash
# ビルドログ確認
gcloud builds log <BUILD_ID> --stream

# よくある原因
# 1. Python 依存パッケージ不足 → requirements.txt 確認
# 2. ポート指定が 8080 でない → Dockerfile 確認
# 3. メモリ不足 → 512Mi -> 1Gi に増やす
```

### Cloud SQL 接続エラー

```bash
# Cloud SQL Proxy 起動（ローカル開発）
cloud-sql-proxy pm-diagnostic-system:asia-northeast1:pm-diagnostic-db

# Cloud Run 側で Cloud SQL Proxy 接続確認
gcloud run services update pm-diagnostic-backend \
  --update-env-vars CLOUDSQL_INSTANCE=pm-diagnostic-system:asia-northeast1:pm-diagnostic-db
```

### Vercel API 接続エラー

```bash
# Vercel ビルドログ確認
vercel logs

# CORS エラーの場合
# 1. Vercel フロントエンド URL 確認
# 2. Cloud Run CORS 設定確認
```

---

## 無料枠の活用

| サービス | 無料枠 | 推定使用量 | 費用 |
|---------|--------|-----------|------|
| Cloud Run | 180,000 vCPU秒/月 | 月5名 * 10分 = ~50 | ¥0 |
| Cloud SQL (db-f1-micro) | 30日×24時間 | 月間連続稼働 | ¥650 |
| Cloud Storage | 5GB | ログ・バックアップ | ¥0 |
| Vercel | 無制限 | WebUI ホスト | ¥0 |
| **合計** | - | - | **¥650/月** |

**注**：db-f1-micro は無料枠の対象外です。最小料金が ¥650/月 です。

---

## 今後の拡張（必要に応じて）

1. **カスタムドメイン**
   - Cloud Run: `pm-diagnostic-api.pm-kyokai.jp`
   - Vercel: `pm-diagnostic.pm-kyokai.jp`

2. **SSL 証明書自動更新**
   - Cloud Run: 自動管理
   - Vercel: 自動管理

3. **CDN キャッシング**
   - Cloudflare 統合（無料枠あり）

4. **監視ダッシュボード**
   - Google Data Studio
   - Grafana

---

## 参考資料

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vercel Deployment Documentation](https://vercel.com/docs)
- [Cloud SQL PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Cloud Build CI/CD](https://cloud.google.com/build/docs)

---

**最終更新**：2026年6月6日
**メンテナンス責任者**：Hiro
