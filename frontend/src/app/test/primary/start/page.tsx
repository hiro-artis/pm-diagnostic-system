'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowRight, CheckCircle } from 'lucide-react'

function StartContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('sessionId')
  const userId = searchParams.get('userId')
  const [confirmed, setConfirmed] = useState(false)

  if (!sessionId || !userId) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">セッション情報が見つかりません</p>
      </div>
    )
  }

  const handleProceed = () => {
    if (confirmed) {
      router.push(
        `/test/primary/basic-knowledge?sessionId=${sessionId}&userId=${userId}`
      )
    }
  }

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold text-gray-900">
          1次テストについて
        </h2>
        <p className="text-gray-600">
          テスト開始前に、以下の内容をご確認ください
        </p>
      </div>

      {/* Test Structure */}
      <div className="bg-white rounded-lg shadow p-8 space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            1次テストの構成
          </h3>
          <div className="space-y-4">
            <div className="flex gap-4 pb-4 border-b border-gray-200">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-100">
                  <span className="text-blue-600 font-semibold">1</span>
                </div>
              </div>
              <div>
                <p className="font-semibold text-gray-900">PM基礎知識テスト</p>
                <p className="text-sm text-gray-600 mt-1">
                  プロジェクト管理の基礎知識 10 問 / 選択式
                </p>
                <p className="text-xs text-gray-500 mt-1">所要時間：10〜15 分</p>
              </div>
            </div>

            <div className="flex gap-4 pb-4 border-b border-gray-200">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-green-100">
                  <span className="text-green-600 font-semibold">2</span>
                </div>
              </div>
              <div>
                <p className="font-semibold text-gray-900">オフィス移転実務テスト</p>
                <p className="text-sm text-gray-600 mt-1">
                  選択式 5 問 + 記述式 3 問 / 実践的シナリオ
                </p>
                <p className="text-xs text-gray-500 mt-1">所要時間：25〜35 分</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-purple-100">
                  <span className="text-purple-600 font-semibold">3</span>
                </div>
              </div>
              <div>
                <p className="font-semibold text-gray-900">マインドセット検証</p>
                <p className="text-sm text-gray-600 mt-1">
                  6 つのシナリオ型問題 / PM最重要スキル
                </p>
                <p className="text-xs text-gray-500 mt-1">所要時間：15〜25 分</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Important Notes */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-4">
          テスト実施時のご注意
        </h3>
        <ul className="space-y-3 text-sm text-gray-700">
          <li className="flex gap-3">
            <span className="text-yellow-600 font-bold">•</span>
            <span>テスト開始後の中断・一時停止はできません</span>
          </li>
          <li className="flex gap-3">
            <span className="text-yellow-600 font-bold">•</span>
            <span>合計 60 分程度の時間を確保してからご開始ください</span>
          </li>
          <li className="flex gap-3">
            <span className="text-yellow-600 font-bold">•</span>
            <span>通信環境が安定している場所でご実施ください</span>
          </li>
          <li className="flex gap-3">
            <span className="text-yellow-600 font-bold">•</span>
            <span>正答・不正答を競うテストではなく、マインドセットを評価します</span>
          </li>
          <li className="flex gap-3">
            <span className="text-yellow-600 font-bold">•</span>
            <span>あなたの率直な考えと判断をお答えください</span>
          </li>
        </ul>
      </div>

      {/* Confirmation Checkbox */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 mt-0.5"
          />
          <span className="text-gray-700">
            上記の内容を確認しました。
            <br />
            テストを開始します。
          </span>
        </label>
      </div>

      {/* Action Button */}
      <div className="flex gap-3">
        <button
          onClick={() => router.back()}
          className="flex-1 py-3 rounded-lg font-semibold border-2 border-gray-300 text-gray-700 hover:bg-gray-50"
        >
          戻る
        </button>
        <button
          onClick={handleProceed}
          disabled={!confirmed}
          className={`flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            confirmed
              ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {confirmed && <CheckCircle className="w-5 h-5" />}
          テストを開始
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}

export default function StartPage() {
  return (
    <Suspense fallback={<div>読み込み中...</div>}>
      <StartContent />
    </Suspense>
  )
}
