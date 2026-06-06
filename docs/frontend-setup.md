# Vercel フロントエンドセットアップガイド

## 概要

PM協会テスト診断システムの WebUI を Next.js + React で実装します。

**構成**：
- 言語：TypeScript
- UIフレームワーク：React + Next.js 14
- スタイリング：Tailwind CSS
- ホスティング：Vercel（無料）
- API通信：Cloud Run バックエンド

---

## セットアップ手順

### 1. プロジェクト初期化

```bash
# プロジェクトディレクトリ作成
mkdir pm-diagnostic-frontend
cd pm-diagnostic-frontend

# Next.js プロジェクト初期化
npx create-next-app@latest . \
  --typescript \
  --tailwind \
  --eslint \
  --app

# または Git から
git clone https://github.com/your-org/pm-diagnostic-frontend
cd pm-diagnostic-frontend
npm install
```

### 2. 環境変数設定

`.env.local` ファイル作成：

```env
NEXT_PUBLIC_API_BASE_URL=https://pm-diagnostic-backend-xxx.run.app
NEXT_PUBLIC_APP_NAME=PM協会テスト診断システム
```

### 3. API クライアント実装

`lib/api-client.ts`：

```typescript
export const apiClient = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,

  async startSession(userId: string, userName?: string) {
    const response = await fetch(`${this.baseURL}/api/sessions/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, user_name: userName }),
    });
    return response.json();
  },

  async submitPrimaryTest(sessionId: string, answers: any) {
    const response = await fetch(`${this.baseURL}/api/tests/primary/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, ...answers }),
    });
    return response.json();
  },

  async submitSecondaryTest(sessionId: string, responses: any) {
    const response = await fetch(`${this.baseURL}/api/tests/secondary/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, interview_responses: responses }),
    });
    return response.json();
  },

  async generateFinalAssessment(sessionId: string, primaryScores: any, secondaryScores?: any) {
    const response = await fetch(`${this.baseURL}/api/assessment/final`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, primary_scores: primaryScores, secondary_scores: secondaryScores }),
    });
    return response.json();
  },
};
```

### 4. ページ構成

推奨ページ構成：

```
app/
├── page.tsx                    # ホーム・スタート画面
├── test/
│   ├── primary/
│   │   ├── basic-knowledge/    # 1次テスト - 基礎知識
│   │   ├── office-migration/   # 1次テスト - オフィス移転
│   │   └── mindset/            # 1次テスト - マインドセット
│   ├── secondary/              # 2次テスト - 面接
│   └── results/                # 結果表示
├── api/                        # API ルート（オプション）
└── layout.tsx                  # 共通レイアウト
```

### 5. 主要コンポーネント

#### TestFlow コンポーネント（進捗管理）

```typescript
'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function TestFlow() {
  const [sessionId, setSessionId] = useState<string>('');
  const [currentStep, setCurrentStep] = useState<'start' | 'primary' | 'secondary' | 'results'>('start');
  const [results, setResults] = useState(null);

  const handleStartTest = async (userId: string) => {
    const session = await apiClient.startSession(userId);
    setSessionId(session.session_id);
    setCurrentStep('primary');
  };

  const handlePrimaryTestSubmit = async (answers: any) => {
    const result = await apiClient.submitPrimaryTest(sessionId, answers);
    
    if (result.qualifies_for_secondary) {
      setCurrentStep('secondary');
    } else {
      setResults(result);
      setCurrentStep('results');
    }
  };

  const handleSecondaryTestSubmit = async (responses: any) => {
    const result = await apiClient.submitSecondaryTest(sessionId, responses);
    setResults(result);
    setCurrentStep('results');
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      {currentStep === 'start' && (
        <StartScreen onStart={handleStartTest} />
      )}
      {currentStep === 'primary' && (
        <PrimaryTestScreen onSubmit={handlePrimaryTestSubmit} />
      )}
      {currentStep === 'secondary' && (
        <SecondaryTestScreen onSubmit={handleSecondaryTestSubmit} />
      )}
      {currentStep === 'results' && (
        <ResultsScreen data={results} />
      )}
    </div>
  );
}
```

#### 結果表示コンポーネント

```typescript
export function ResultsScreen({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      <div className="bg-blue-50 p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">最終評価</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-600">評価等級</p>
            <p className="text-3xl font-bold">{data.grade_level}</p>
          </div>
          <div>
            <p className="text-gray-600">総合スコア</p>
            <p className="text-3xl font-bold">{data.total_score}/100</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-bold">サマリー</h3>
        <p className="text-gray-700">{data.summary}</p>
      </div>

      {data.strengths && (
        <div className="space-y-2">
          <h3 className="text-lg font-bold text-green-700">強み</h3>
          <ul className="list-disc pl-6 space-y-1">
            {data.strengths.map((s: string) => (
              <li key={s} className="text-gray-700">{s}</li>
            ))}
          </ul>
        </div>
      )}

      {data.development_areas && (
        <div className="space-y-2">
          <h3 className="text-lg font-bold text-orange-700">改善が望ましい領域</h3>
          <ul className="list-disc pl-6 space-y-1">
            {data.development_areas.map((a: string) => (
              <li key={a} className="text-gray-700">{a}</li>
            ))}
          </ul>
        </div>
      )}

      {data.recommendations && (
        <div className="space-y-2">
          <h3 className="text-lg font-bold text-blue-700">推奨事項</h3>
          <ul className="list-disc pl-6 space-y-1">
            {data.recommendations.map((r: string) => (
              <li key={r} className="text-gray-700">{r}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={() => window.location.href = '/'}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
      >
        ホームに戻る
      </button>
    </div>
  );
}
```

### 6. モバイル対応

Tailwind CSS のレスポンシブ機能を使用：

```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* レスポンシブレイアウト */}
</div>
```

### 7. デプロイ手順

#### GitHub リポジトリ作成

```bash
git init
git add .
git commit -m "Initial commit: PM diagnostic frontend"
git branch -M main
git remote add origin https://github.com/your-org/pm-diagnostic-frontend
git push -u origin main
```

#### Vercel へのデプロイ

**方法 1: Web UI（推奨）**

1. https://vercel.com にアクセス
2. 「New Project」をクリック
3. GitHub リポジトリを選択
4. 環境変数設定：
   - `NEXT_PUBLIC_API_BASE_URL`: Cloud Run URL
5. 「Deploy」をクリック

**方法 2: CLI**

```bash
npm install -g vercel
vercel --prod
```

---

## 各テスト画面の実装例

### 基礎知識テスト

```typescript
export function BasicKnowledgeTest({ onSubmit }: { onSubmit: (answers: any) => void }) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const questions = [
    { id: 'BK-001', text: 'プロジェクトの特性として正しいのは？', options: ['A) 継続的で反復的な業務活動', 'B) 一時的な努力で独特な成果物を生み出す', 'C) 日常的な運営活動', 'D) 経営層による意思決定'] },
    // ... 他の問題
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">PM基礎知識テスト（10問）</h2>
      
      {questions.map((q) => (
        <div key={q.id} className="border rounded-lg p-4">
          <p className="font-semibold mb-3">{q.id}: {q.text}</p>
          <div className="space-y-2">
            {q.options.map((opt, idx) => (
              <label key={idx} className="flex items-center space-x-2">
                <input
                  type="radio"
                  name={q.id}
                  value={String.fromCharCode(65 + idx)}
                  onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                  className="w-4 h-4"
                />
                <span>{opt}</span>
              </label>
            ))}
          </div>
        </div>
      ))}

      <button
        onClick={() => onSubmit({ basic_knowledge: answers })}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
      >
        次へ
      </button>
    </div>
  );
}
```

---

## トラブルシューティング

### CORS エラー

Cloud Run 側の `api.py` で確認：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "https://pm-diagnostic.vercel.app")],
    ...
)
```

### API 接続エラー

```bash
# 環境変数確認
echo $NEXT_PUBLIC_API_BASE_URL

# Vercel ビルドログ確認
vercel logs
```

---

## 参考資料

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Deployment Guide](https://vercel.com/docs/concepts/deployments/overview)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript React Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

---

**最終更新**：2026年6月6日
