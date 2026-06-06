# 🚀 デプロイメント クイックスタート

## 5分で読む実行計画

このドキュメントは、デプロイメントを **今すぐ開始したい方** 向けです。

---

## 📋 準備チェック

デプロイ前に以下を確認してください：

- [ ] Google Cloud アカウント作成済み
- [ ] 課金情報設定済み
- [ ] `gcloud` CLI インストール済み（`gcloud --version`）
- [ ] GitHub アカウント作成済み
- [ ] Vercel アカウント作成済み

**上記がない場合：**
1. [Google Cloud](https://cloud.google.com) → 無料アカウント作成
2. [GitHub](https://github.com) → アカウント作成
3. [Vercel](https://vercel.com) → GitHub で サインアップ

---

## 🎯 実行計画（全体：3-4時間）

### **フェーズ 0：初期化（30分）**

```bash
# 1. Google Cloud 初期化
gcloud init
gcloud auth login

# プロジェクト作成
PROJECT_ID="pm-diagnostic-system"
gcloud projects create $PROJECT_ID --name="PM協会テスト診断"
gcloud config set project $PROJECT_ID

# 2. GitHub にコミット
cd /Users/h.tsuchiyama/PM協会テスト診断/PM協会テスト診断
git remote add origin https://github.com/your-org/pm-diagnostic-backend
git push -u origin main
```

---

### **フェーズ 1：Google Cloud セットアップ（30分）**

```bash
# 1. 課金を有効化（Web UI）
# → Google Cloud Console で課金情報を入力

# 2. 必要な API を有効化
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 3. Docker 認証設定
gcloud auth configure-docker
```

**確認コマンド**：
```bash
gcloud services list --enabled | grep -E "run|sql|build|container"
```

---

### **フェーズ 2：Cloud SQL 構築（20分）**

```bash
# 1. PostgreSQL インスタンス作成（10-15分待機）
gcloud sql instances create pm-diagnostic-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast1 \
  --backup-start-time=03:00 \
  --quiet

# 2. データベース・ユーザー作成
gcloud sql databases create pm_diagnostic \
  --instance=pm-diagnostic-db \
  --quiet

# 安全なパスワード生成
DB_PASSWORD=$(openssl rand -base64 32)
echo "DB_PASSWORD=$DB_PASSWORD" > ~/.pm_db_password

gcloud sql users create pm_user \
  --instance=pm-diagnostic-db \
  --password=$DB_PASSWORD \
  --quiet

echo "✅ Cloud SQL インスタンス作成完了"
```

**確認コマンド**：
```bash
gcloud sql instances describe pm-diagnostic-db --format="value(state)"
```

---

### **フェーズ 3：Cloud Run デプロイ（40分）**

```bash
# 1. イメージビルド＆プッシュ
cd /Users/h.tsuchiyama/PM協会テスト診断/PM協会テスト診断

docker build -t pm-diagnostic-backend:latest .
docker tag pm-diagnostic-backend:latest \
  gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest
docker push gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest

# 2. Cloud Run デプロイ
ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f2)

gcloud run deploy pm-diagnostic-backend \
  --image gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest \
  --platform managed \
  --region asia-northeast1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
  --set-env-vars "ENVIRONMENT=production" \
  --no-allow-unauthenticated

# 3. サービス URL 取得
BACKEND_URL=$(gcloud run services describe pm-diagnostic-backend \
  --region asia-northeast1 \
  --format='value(status.url)')

echo "✅ Cloud Run デプロイ完了"
echo "Backend URL: $BACKEND_URL"

# 4. ヘルスチェック
curl $BACKEND_URL/health
```

**期待出力**：
```json
{"status": "ok", "service": "PM診断システム API", "version": "1.0.0"}
```

---

### **フェーズ 4：Vercel フロントエンド（30分）**

**方法 A：Web UI（推奨・簡単）**

1. [Vercel.com](https://vercel.com) を開く
2. 「New Project」をクリック
3. GitHub リポジトリ選択：`pm-diagnostic-frontend`
4. 環境変数設定：
   - `NEXT_PUBLIC_API_BASE_URL`: 上記で取得した `$BACKEND_URL`
5. 「Deploy」クリック（3-5分待機）
6. 自動生成 URL で確認

**方法 B：CLI**

```bash
# Frontend ディレクトリに移動
cd frontend

# 環境変数設定
echo "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL" > .env.local

# Vercel デプロイ
npm install -g vercel
vercel --prod
```

**確認**：
```bash
# デプロイ完了後、URL にアクセス
# → ホーム画面が表示されることを確認
```

---

### **フェーズ 5：本番テスト（1時間）**

#### ステップ 1：エンドツーエンドテスト

```bash
# 1. Vercel URL にアクセス
# 例：https://pm-diagnostic-xxxxx.vercel.app

# 2. 以下をテスト
- ユーザーID 入力 → セッション開始
- 1次テスト フロー完走（基礎知識 → オフィス移転 → マインドセット）
- 結果表示確認
```

#### ステップ 2：ログ確認

```bash
# Cloud Run ログ確認
gcloud run logs read pm-diagnostic-backend \
  --region asia-northeast1 \
  --limit 50

# エラーが無いか確認
# → API 応答時間が 1-2秒以内であることを確認
```

#### ステップ 3：バックアップテスト

```bash
# Cloud SQL バックアップ確認
gcloud sql backups list --instance=pm-diagnostic-db

# バックアップが自動実行中であることを確認
```

---

## 🎉 完成時のチェックリスト

デプロイ完了時に以下を確認：

```
✅ Cloud Run サービス起動
  - URL: https://pm-diagnostic-backend-xxx.run.app/health

✅ Vercel フロントエンド起動
  - URL: https://pm-diagnostic-xxxxx.vercel.app
  - ホーム画面表示確認

✅ API 連携動作確認
  - セッション開始 → 正常に進行
  - 1次テスト フロー完走
  - エラーログなし

✅ インフラストラクチャ
  - Cloud SQL: PostgreSQL 15
  - Cloud Run: 512Mi メモリ、1 CPU
  - ストレージ: Cloud Storage 設定済み

✅ 監視・ログ
  - Cloud Logging: エラー検出設定
  - バックアップ: 毎日自動実行

✅ ドキュメント整備
  - DEPLOYMENT.md: 参照可能
  - frontend/README.md: セットアップ手順完備
```

---

## 📊 本番費用

```
Cloud Run:   ¥0/月（無料枠内）
Cloud SQL:   ¥650/月（db-f1-micro）
Vercel:      ¥0/月（無料プラン）
─────────────────────
合計:       ¥650/月
```

---

## 🔧 トラブルシューティング

### Cloud Run デプロイエラー

**エラー**：`Error: build step "docker push" failed`

**対策**：
```bash
# Docker イメージ再ビルド
docker build --no-cache -t pm-diagnostic-backend:latest .
docker tag pm-diagnostic-backend:latest \
  gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest
docker push gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest
```

### API 接続エラー

**エラー**：`NEXT_PUBLIC_API_BASE_URL not found`

**対策**：
```bash
# Vercel の環境変数を確認
vercel env ls

# 再設定
vercel env add NEXT_PUBLIC_API_BASE_URL
# → Cloud Run URL を入力
```

### Cloud SQL 接続失敗

**エラー**：`Connection timeout`

**対策**：
```bash
# Cloud SQL インスタンス状態確認
gcloud sql instances describe pm-diagnostic-db

# 再起動（必要な場合）
gcloud sql instances restart pm-diagnostic-db
```

---

## 📞 次のステップ

デプロイ完了後：

1. **運用マニュアル確認**
   - `DEPLOYMENT.md` → 詳細設定
   - 月次メンテナンスタスク確認

2. **フロントエンド追加実装**
   - 他のテストページ実装（基礎知識、オフィス移転など）
   - 結果表示画面実装
   - エラーハンドリング強化

3. **本番運用開始**
   - ユーザー ID リスト準備
   - テストデータ運用開始
   - ログ監視開始

---

## 🆘 サポート

問題が発生した場合：

1. **ログ確認**：`gcloud run logs read ...`
2. **API ヘルスチェック**：`curl $BACKEND_URL/health`
3. **詳細ドキュメント**：`DEPLOYMENT.md` 参照
4. **トラブルシューティング**：`docs/deployment-guide.md` 参照

---

**推定実行時間**: 3-4 時間  
**必要なコマンド数**: 20-30 個  
**難易度**: ⭐⭐（初心者向け）  

**今すぐ開始できます！** 🚀
