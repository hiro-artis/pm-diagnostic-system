# PM協会テスト診断システム - フロントエンド

## 概要

Next.js + React + Tailwind CSS で実装された PM 診断システムの Web フロントエンド。
Vercel で無料ホストされます。

## セットアップ

### 前提条件

- Node.js 18.0 以上
- npm または yarn

### インストール

```bash
# 依存パッケージをインストール
npm install

# または
yarn install
```

### 環境変数設定

`.env.local` ファイルをプロジェクトルートに作成：

```env
NEXT_PUBLIC_API_BASE_URL=https://pm-diagnostic-backend-xxx.run.app
```

**注意**：`NEXT_PUBLIC_` プレフィックスが付いている変数はクライアント側で公開されます。
API キーなどの秘密情報はここに含めないでください。

## ローカル開発

```bash
# 開発サーバー起動（http://localhost:3000）
npm run dev

# または
yarn dev
```

ブラウザで `http://localhost:3000` にアクセスしてください。

## ビルド

```bash
# 本番ビルド
npm run build

# 本番サーバー起動
npm run start
```

## デプロイ

### Vercel へのデプロイ

#### 方法 1: Web UI（推奨）

1. [Vercel](https://vercel.com) にアクセス
2. GitHub アカウントで ログイン
3. 「New Project」をクリック
4. このリポジトリを選択
5. 環境変数を設定：
   - `NEXT_PUBLIC_API_BASE_URL`: Cloud Run バックエンド URL
6. 「Deploy」をクリック

#### 方法 2: CLI

```bash
npm install -g vercel
vercel --prod \
  --env NEXT_PUBLIC_API_BASE_URL=https://pm-diagnostic-backend-xxx.run.app
```

## ページ構成

### 実装済み

- `/` - ホーム・スタート画面
- `/test/primary/start` - 1次テスト開始確認

### 実装予定

- `/test/primary/basic-knowledge` - PM 基礎知識テスト
- `/test/primary/office-migration` - オフィス移転テスト
- `/test/primary/mindset` - マインドセット検証
- `/test/secondary` - 2次テスト（面接）
- `/test/results` - 結果表示
- `/api/health` - ヘルスチェック（Backend）

## API 連携

### API クライアント（`src/lib/api-client.ts`）

```typescript
// セッション開始
const session = await apiClient.startSession('user@example.com')

// 1次テスト提出
const result = await apiClient.submitPrimaryTest(
  sessionId,
  basicKnowledge,
  officeMigrationMc,
  officeMigrationEssay,
  mindset
)

// 2次テスト提出
const secondaryResult = await apiClient.submitSecondaryTest(
  sessionId,
  interviewResponses
)

// 最終評価
const assessment = await apiClient.generateFinalAssessment(
  sessionId,
  primaryScores,
  secondaryScores
)
```

## トラブルシューティング

### CORS エラー

**エラー**: `Access to XMLHttpRequest has been blocked by CORS policy`

**原因**: Backend の CORS 設定が Frontend URL を許可していない

**対策**:
```python
# src/api.py で確認
allow_origins=[
    "http://localhost:3000",
    "https://your-vercel-app.vercel.app"
]
```

### API 接続エラー

**エラー**: `Failed to connect to API`

**対策**:
```bash
# 環境変数確認
echo $NEXT_PUBLIC_API_BASE_URL

# 開発環境の場合、ローカル Backend に接続
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

### ビルドエラー

```bash
# キャッシュをクリアして再ビルド
rm -rf .next node_modules
npm install
npm run build
```

## 開発ガイドライン

### コンポーネント構成

```
src/
├── app/
│   ├── globals.css
│   ├── layout.tsx          # Root Layout
│   ├── page.tsx            # ホーム画面
│   └── test/
│       ├── primary/
│       │   ├── start/
│       │   ├── basic-knowledge/
│       │   ├── office-migration/
│       │   └── mindset/
│       └── secondary/
├── components/
│   ├── TestForm.tsx
│   ├── ProgressBar.tsx
│   └── ResultDisplay.tsx
└── lib/
    └── api-client.ts
```

### スタイリング

Tailwind CSS を使用しています。

```tsx
<div className="max-w-2xl mx-auto px-4 py-8">
  <h1 className="text-2xl font-bold text-gray-900">タイトル</h1>
</div>
```

### API 呼び出し

```tsx
'use client'

import { apiClient } from '@/lib/api-client'

export default function MyComponent() {
  const handleSubmit = async () => {
    try {
      const result = await apiClient.submitPrimaryTest(...)
      // 処理
    } catch (error) {
      console.error(error)
    }
  }
}
```

## 参考資料

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Deployment](https://vercel.com/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript React](https://react-typescript-cheatsheet.netlify.app/)

## ライセンス

PM Association. All rights reserved.

## サポート

問題が発生した場合は、以下をご確認ください：

1. `NEXT_PUBLIC_API_BASE_URL` が正しく設定されているか
2. Backend が起動しているか（`/health` で確認）
3. ブラウザのコンソール（F12）でエラーメッセージを確認

---

**最終更新**: 2026年6月6日
