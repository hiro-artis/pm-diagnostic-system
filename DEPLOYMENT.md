# デプロイメント実行計画

## 📋 概要

**構成**：Cloud Run + Vercel（最小運用構成）  
**予算**：月額 ¥650（Cloud SQL db-f1-micro）  
**運用者**：Hiro（管理者）  
**期限**：制限なし

---

## 🚀 実行フェーズ

### **フェーズ 0：前準備**（所要時間：1-2時間）

#### タスク 0-1：Google Cloud アカウント準備
- [ ] Google Cloud アカウント作成または既存アカウント確認
- [ ] 課金情報設定
- [ ] `gcloud` CLI インストール（`gcloud init`）
- [ ] 参考：[Google Cloud セットアップ](https://cloud.google.com/docs/setup)

**確認コマンド**：
```bash
gcloud auth list
gcloud config list
```

#### タスク 0-2：GitHub リポジトリ準備
- [ ] GitHub リポジトリ作成（`pm-diagnostic-backend`）
- [ ] 以下をプッシュ：
  - `src/` （バックエンド実装）
  - `Dockerfile`
  - `requirements.txt`
  - `.gcloudignore`
  - `.env.example`

#### タスク 0-3：ローカル動作確認
- [ ] `pip install -r requirements.txt`
- [ ] `pytest tests/` が全て合格
- [ ] `python src/api.py` でサーバー起動確認（`http://localhost:8000/health`）
- [ ] `docker build -t pm-diagnostic .` でDockerビルド成功確認

---

### **フェーズ 1：Google Cloud セットアップ**（所要時間：30分）

#### タスク 1-1：プロジェクト・API 有効化

```bash
# プロジェクト作成
PROJECT_ID=pm-diagnostic-system
gcloud projects create $PROJECT_ID --name="PM協会テスト診断"
gcloud config set project $PROJECT_ID

# 課金有効化（クレジットカード必須）
# → Google Cloud Console で手動実施

# API 有効化
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

- [ ] プロジェクト作成
- [ ] 課金有効化
- [ ] API 4つ有効化確認

#### タスク 1-2：Docker 認証設定

```bash
gcloud auth configure-docker
```

- [ ] 認証設定完了

---

### **フェーズ 2：Cloud SQL セットアップ**（所要時間：20分）

#### タスク 2-1：PostgreSQL インスタンス作成

```bash
gcloud sql instances create pm-diagnostic-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast1 \
  --backup-start-time=03:00
```

- [ ] インスタンス作成完了（10-15分待機）

#### タスク 2-2：データベース・ユーザー作成

```bash
# データベース作成
gcloud sql databases create pm_diagnostic \
  --instance=pm-diagnostic-db

# パスワード生成
DB_PASSWORD=$(openssl rand -base64 32)
echo "DB_PASSWORD=$DB_PASSWORD" > ~/.pm_diagnostic_db_password

# ユーザー作成
gcloud sql users create pm_user \
  --instance=pm-diagnostic-db \
  --password=$DB_PASSWORD
```

- [ ] `pm_diagnostic` データベース作成
- [ ] `pm_user` ユーザー作成
- [ ] パスワード安全に保管（`~/.pm_diagnostic_db_password`）

#### タスク 2-3：接続確認（オプション）

```bash
# Cloud SQL Proxy インストール
curl https://dl.google.com/cloudsql/cloud_sql_proxy.mac.x64 \
  -o cloud_sql_proxy
chmod +x cloud_sql_proxy

# テスト接続
./cloud_sql_proxy -instances=$PROJECT_ID:asia-northeast1:pm-diagnostic-db=tcp:5432 &
psql -h localhost -U pm_user -d pm_diagnostic
```

- [ ] 接続確認完了

---

### **フェーズ 3：Cloud Run デプロイ**（所要時間：40分）

#### タスク 3-1：イメージビルド・プッシュ

```bash
# リポジトリ clone
git clone https://github.com/your-org/pm-diagnostic-backend
cd pm-diagnostic-backend

# イメージビルド
docker build -t pm-diagnostic-backend:latest .

# タグ付け
docker tag pm-diagnostic-backend:latest \
  gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest

# プッシュ
docker push gcr.io/$PROJECT_ID/pm-diagnostic-backend:latest
```

- [ ] Docker イメージビルド成功
- [ ] Google Container Registry にプッシュ完了

#### タスク 3-2：Cloud Run デプロイ

```bash
# 環境変数用意（.env から取得）
ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f2)

# デプロイ
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
```

**注意**：デプロイに 2-3 分要します。

- [ ] Cloud Run デプロイ完了

#### タスク 3-3：デプロイ確認

```bash
# サービス URL 取得
BACKEND_URL=$(gcloud run services describe pm-diagnostic-backend \
  --region asia-northeast1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"

# ヘルスチェック
curl $BACKEND_URL/health
```

期待される出力：
```json
{"status": "ok", "service": "PM診断システム API", "version": "1.0.0"}
```

- [ ] ヘルスチェック成功

---

### **フェーズ 4：Vercel フロントエンド**（所要時間：30分）

#### タスク 4-1：フロントエンド実装

```bash
# フロントエンドリポジトリ作成
mkdir pm-diagnostic-frontend
cd pm-diagnostic-frontend

# Next.js 初期化
npx create-next-app@latest . \
  --typescript --tailwind --app

# 環境変数設定
echo "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL" > .env.local
```

- [ ] Next.js プロジェクト作成
- [ ] 環境変数設定（Cloud Run URL）

#### タスク 4-2：GitHub プッシュ

```bash
git init
git add .
git commit -m "Initial: PM diagnostic frontend"
git branch -M main
git remote add origin https://github.com/your-org/pm-diagnostic-frontend
git push -u origin main
```

- [ ] GitHub にプッシュ完了

#### タスク 4-3：Vercel デプロイ

**Web UI（推奨）**：
1. https://vercel.com にアクセス
2. GitHub アカウント連携
3. 「Import Project」→ GitHub リポジトリ選択
4. 環境変数設定：
   - `NEXT_PUBLIC_API_BASE_URL`: Cloud Run URL
5. 「Deploy」クリック

**CLI**：
```bash
npm install -g vercel
vercel --prod --env NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL
```

デプロイに 3-5 分要します。

- [ ] Vercel デプロイ完了
- [ ] 自動生成 URL で確認

---

### **フェーズ 5：本番テスト**（所要時間：30分）

#### タスク 5-1：エンドツーエンドテスト

1. **Vercel フロントエンド URL にアクセス**
2. **以下をテスト**：
   - ユーザー ID 入力 → セッション開始
   - 基礎知識テスト（10問）完了
   - オフィス移転テスト（5MC + 3記述式）完了
   - マインドセット（6シナリオ）完了
   - 1次テスト結果表示確認

- [ ] 1次テスト全フロー動作確認
- [ ] 結果表示確認

#### タスク 5-2：採点精度確認

```bash
# 複数回実施して採点にばらつきがないか確認
# （マインドセット採点が再現性を持つかチェック）
```

- [ ] 採点結果が期待値通りか確認
- [ ] エラーがないか確認

#### タスク 5-3：ログ・エラー確認

```bash
gcloud run logs read pm-diagnostic-backend \
  --region asia-northeast1 \
  --limit 50
```

- [ ] エラーログがないか確認
- [ ] API 応答時間が正常か確認（1-2秒以内）

---

### **フェーズ 6：運用準備**（所要時間：30分）

#### タスク 6-1：バックアップ設定

```bash
# Cloud SQL バックアップ自動有効化（デフォルト）
# 確認：
gcloud sql backups list --instance=pm-diagnostic-db

# リストアテスト（オプション）
# gcloud sql backups restore <BACKUP_ID> --backup-instance=pm-diagnostic-db
```

- [ ] バックアップ自動設定確認
- [ ] リストアテスト実施（推奨）

#### タスク 6-2：監視・ログ設定

```bash
# Cloud Logging ダッシュボード確認
# Cloud Console → Cloud Run → pm-diagnostic-backend → ログ
```

- [ ] ログダッシュボード確認
- [ ] エラー検出アラート設定（推奨）

#### タスク 6-3：ドキュメント整備

- [ ] デプロイメントガイド確認
- [ ] 運用マニュアル作成（Hiro 向け）
- [ ] エマージェンシー連絡先記録

#### タスク 6-4：カスタムドメイン（オプション）

```bash
# Cloud Run にカスタムドメイン追加
gcloud run domain-mappings create \
  --service=pm-diagnostic-backend \
  --domain=pm-diagnostic-api.example.com \
  --region=asia-northeast1
```

- [ ] カスタムドメイン設定（必要に応じて）

---

## ✅ 本番チェックリスト

デプロイ完了時点でのチェック：

### セキュリティ
- [ ] API Key（ANTHROPIC_API_KEY）が環境変数で保護
- [ ] Cloud Run サービスが非認証でアクセス不可（`--no-allow-unauthenticated`）
- [ ] PostgreSQL パスワードが安全に保管
- [ ] CORS 設定が Vercel URL のみ許可

### パフォーマンス
- [ ] API 応答時間 < 2秒（通常 1秒以内）
- [ ] 同時ユーザー 10名でも動作確認
- [ ] メモリ使用量 < 512Mi（Cloud Run 割り当て）

### 監視
- [ ] ログが正常に Cloud Logging に記録
- [ ] エラーがないか確認
- [ ] バックアップが毎日自動実行中

### ドキュメント
- [ ] デプロイメントガイド完成
- [ ] 運用マニュアル Hiro 向け完成
- [ ] トラブルシューティングガイド完成

---

## 📊 本番費用見積もり

| サービス | 使用量 | 月額 |
|---------|--------|------|
| Cloud Run | 月5名×10分 = 50vCPU秒 | ¥0（無料枠内） |
| Cloud SQL db-f1-micro | 連続稼働 | ¥650 |
| Cloud Storage | ログ・バックアップ | ¥0（< 5GB） |
| Vercel | フロントエンド | ¥0（無料プラン） |
| **合計** | - | **¥650/月** |

**注**：初月のみ、初期セットアップ時の API 呼び出しで若干追加費用の可能性。

---

## 🔄 デプロイ後の継続運用

### 日常運用
- **毎日**：ログをざっと確認（エラーないか）
- **毎週**：テスト実行（動作確認）
- **毎月**：バックアップ確認

### 定期メンテナンス
- **毎月 1日**：セキュリティアップデート確認
- **毎3ヶ月**：バックアップリストアテスト
- **毎年**：本格セキュリティ監査

### 緊急対応
- **API エラー**：`gcloud run logs read` でログ確認 → 修正 → 再デプロイ
- **DB 接続失敗**：Cloud SQL Proxy 再起動 → テスト
- **高レイテンシ**：メモリ増やす（512Mi → 1Gi）

---

## 📞 参考資料・サポート

- 📖 **デプロイメントガイド**：`docs/deployment-guide.md`
- 📖 **フロントエンドセットアップ**：`docs/frontend-setup.md`
- 🔗 **Google Cloud Docs**：https://cloud.google.com/docs
- 🔗 **Vercel Docs**：https://vercel.com/docs

---

**デプロイ実行者**：Hiro  
**作成日**：2026年6月6日  
**最終チェック日**：---（デプロイ後記入）
