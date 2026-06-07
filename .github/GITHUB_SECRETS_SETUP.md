# 📋 GitHub シークレット設定 詳細ガイド

**目的**: GitHub Actions 自動デプロイメント用のシークレットを設定する  
**所要時間**: 10-15分  
**難易度**: 初級

---

## 🎯 設定が必要なシークレット

### 【必須】GCP 関連 (3個)

```
1. GCP_PROJECT_ID
   - Google Cloud プロジェクトの ID
   - 形式: pm-diagnostic-123456

2. GCP_SA_KEY
   - GCP サービスアカウント JSON キー
   - Base64 エンコード形式

3. GCP_REGION
   - デプロイリージョン
   - 固定値: asia-northeast1
```

### 【必須】Vercel 関連 (3個)

```
4. VERCEL_TOKEN
   - Vercel API トークン
   - 形式: 英数字混在の長い文字列

5. VERCEL_ORG_ID
   - Vercel 組織 ID
   - 形式: 英数字

6. VERCEL_PROJECT_ID
   - Vercel プロジェクト ID
   - 形式: 英数字
```

### 【オプション】Slack 通知

```
7. SLACK_WEBHOOK_URL
   - Slack Incoming Webhook URL
   - 形式: https://hooks.slack.com/services/...
   
   ※ 通知が不要な場合はスキップ可能
```

---

## 📝 ステップバイステップ設定手順

### ステップ 1️⃣: GitHub リポジトリを開く

```
1. https://github.com/{owner}/{repo} を開く
   例: https://github.com/hiro-artis/pm-diagnostic-system

2. "Settings" タブをクリック
   右上の歯車アイコン
```

### ステップ 2️⃣: Secrets and variables セクションへ移動

```
1. Settings ページで左側メニューを下にスクロール
2. "Secrets and variables" をクリック
3. "Actions" をクリック
```

### ステップ 3️⃣: GCP_PROJECT_ID を設定

```
1. "New repository secret" ボタンをクリック

2. 以下を入力:
   Name: GCP_PROJECT_ID
   Secret: [GCP プロジェクト ID を入力]
   
   例: pm-diagnostic-123456

3. "Add secret" をクリック
```

### ステップ 4️⃣: GCP_SA_KEY を設定

```
【事前準備】GCP サービスアカウント キーを取得

1. https://console.cloud.google.com を開く
2. プロジェクト選択
3. "IAM and Admin" → "Service Accounts"
4. "pm-diagnostic-api" サービスアカウント選択
5. "Keys" タブ → "Add Key" → "Create new key"
6. "JSON" を選択
7. JSON キーファイルをダウンロード

【Base64 エンコード】ターミナルで実行

1. ダウンロードしたファイルをホームディレクトリに配置
2. ターミナルを開く
3. 以下を実行:
   cat ~/[ファイル名].json | base64
4. 出力された長い文字列をコピー

【GitHub に登録】

1. GitHub の "New repository secret" をクリック
2. 以下を入力:
   Name: GCP_SA_KEY
   Secret: [Base64 エンコードされた JSON]
3. "Add secret" をクリック
```

### ステップ 5️⃣: VERCEL_TOKEN を設定

```
【事前準備】Vercel API トークンを取得

1. https://vercel.com/account/tokens を開く
2. "Create" ボタンをクリック
3. Token name: "GitHub Actions" を入力
4. Expiration: "No expiration" を選択（推奨）
5. "Create token" をクリック
6. トークン文字列をコピー（表示されるのは1回限り）

【GitHub に登録】

1. GitHub の "New repository secret" をクリック
2. 以下を入力:
   Name: VERCEL_TOKEN
   Secret: [Vercel API トークン]
3. "Add secret" をクリック
```

### ステップ 6️⃣: VERCEL_ORG_ID を設定

```
【事前準備】Vercel 組織 ID を確認

1. https://vercel.com/account/overview を開く
2. "Team / Org ID" を探す
3. ID をコピー
   形式: xxxxxxxxxxxxxxxx (16文字以上)

【GitHub に登録】

1. GitHub の "New repository secret" をクリック
2. 以下を入力:
   Name: VERCEL_ORG_ID
   Secret: [Vercel 組織 ID]
3. "Add secret" をクリック
```

### ステップ 7️⃣: VERCEL_PROJECT_ID を設定

```
【事前準備】Vercel プロジェクト ID を確認

1. https://vercel.com/dashboard を開く
2. "pm-diagnostic-frontend" プロジェクト選択
3. "Settings" → "General"
4. "Project ID" をコピー
   形式: xxxxxxxxxxxxxxxxxxxxxxxx (24文字)

【GitHub に登録】

1. GitHub の "New repository secret" をクリック
2. 以下を入力:
   Name: VERCEL_PROJECT_ID
   Secret: [Vercel プロジェクト ID]
3. "Add secret" をクリック
```

### ステップ 8️⃣: SLACK_WEBHOOK_URL を設定（オプション）

```
【事前準備】Slack Webhook を作成（スキップ可能）

1. https://api.slack.com/apps を開く
2. "Create New App" → "From scratch"
3. App Name: "PM Diagnostic Deploy" を入力
4. Workspace を選択
5. "Create App" をクリック
6. 左側メニュー → "Incoming Webhooks"
7. "Activate Incoming Webhooks" を ON
8. "Add New Webhook to Workspace" をクリック
9. チャネルを選択（#notifications など）
10. "Allow" をクリック
11. Webhook URL をコピー

【GitHub に登録】

1. GitHub の "New repository secret" をクリック
2. 以下を入力:
   Name: SLACK_WEBHOOK_URL
   Secret: [Slack Webhook URL]
3. "Add secret" をクリック

※ 通知不要な場合は、このステップをスキップしても問題ありません
```

---

## ✅ 設定完了確認

### GitHub で確認

```
1. GitHub Settings → Secrets and variables → Actions
2. 以下のシークレットが表示されていることを確認:
   ✅ GCP_PROJECT_ID
   ✅ GCP_SA_KEY
   ✅ VERCEL_TOKEN
   ✅ VERCEL_ORG_ID
   ✅ VERCEL_PROJECT_ID
   ✅ SLACK_WEBHOOK_URL（設定した場合）
```

### デプロイメント テスト

```
1. ローカルで小さな変更を作成
   例: README.md に 1行追加

2. Git コミット・プッシュ
   git add .
   git commit -m "test: trigger deployment"
   git push origin main

3. GitHub Actions で実行確認
   https://github.com/{owner}/{repo}/actions

4. 実行ログで以下を確認:
   ✅ "Deploy to GCP and Vercel" ワークフロー実行中
   ✅ Backend デプロイ進行中
   ✅ Frontend デプロイ進行中
   ✅ テスト実行中
   ✅ Slack 通知送信
```

---

## 🔧 トラブルシューティング

### エラー: "secrets.GCP_PROJECT_ID is not set"

```
❌ 問題: GCP_PROJECT_ID シークレットが設定されていない
✅ 解決策:
   1. GitHub Settings を確認
   2. GCP_PROJECT_ID が登録されているか確認
   3. 名前が正確に一致しているか確認（大文字・小文字）
   4. 再度登録
```

### エラー: "Invalid GCP_SA_KEY format"

```
❌ 問題: GCP_SA_KEY が Base64 エンコードされていない
✅ 解決策:
   1. GCP JSON キーファイルを取得
   2. ターミナルで: cat key.json | base64
   3. 出力文字列全体をコピー
   4. GitHub で更新
```

### エラー: "Vercel deployment failed"

```
❌ 問題: VERCEL_TOKEN または VERCEL_ORG_ID が無効
✅ 解決策:
   1. Vercel で新しい API トークンを生成
   2. GitHub シークレット更新
   3. 再度デプロイメント実行
```

### Slack 通知が来ない（設定した場合）

```
❌ 問題: SLACK_WEBHOOK_URL が無効
✅ 解決策:
   1. Slack Webhook URL が正確か確認
   2. Slack ワークスペースで Webhook が有効か確認
   3. チャネルに Bot がアクセス可能か確認
   4. GitHub で URL を更新
```

---

## 📊 設定完了チェックリスト

```
【必須】
□ GCP_PROJECT_ID: 設定完了
□ GCP_SA_KEY: Base64 エンコード・設定完了
□ VERCEL_TOKEN: 設定完了
□ VERCEL_ORG_ID: 設定完了
□ VERCEL_PROJECT_ID: 設定完了

【オプション】
□ SLACK_WEBHOOK_URL: 設定完了（または スキップ）

【動作確認】
□ デプロイメント テスト実行
□ GitHub Actions ログで成功確認
□ 本番環境で更新されたバージョン確認

総合: 🟢 設定完了！
```

---

## 🎯 次のステップ

```
1️⃣ 全シークレット設定完了
   ↓
2️⃣ テスト デプロイメント実行
   git push origin main
   ↓
3️⃣ 自動デプロイメント 確認
   GitHub Actions で成功確認
   ↓
4️⃣ 本運用開始
   自動デプロイメント ワークフロー 有効化
   継続的デリバリー（CD） スタート
```

---

## 💡 ベストプラクティス

### シークレット管理

```
✅ シークレット値は絶対に共有しない
✅ 定期的にトークンをローテーション（3ヶ月ごと）
✅ 不要になったシークレットは削除
✅ Git にコミットしない
```

### セキュリティ

```
✅ GitHub 2FA（2要素認証）を有効化
✅ GCP サービスアカウントに最小権限を付与
✅ Vercel API トークンに有効期限を設定
✅ Slack Webhook URL を定期的に更新
```

---

**GitHub シークレット設定ガイド 完成！** 🎉

このガイドに従って設定すれば、自動デプロイメント ワークフローが完全に動作します。