'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Clock, AlertCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

export default function HomePage() {
  const router = useRouter()
  const [userId, setUserId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleStartTest = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!userId.trim()) {
      setError('ユーザーIDを入力してください')
      return
    }

    setLoading(true)
    setError('')

    try {
      const session = await apiClient.startSession(userId.trim())
      if (session.session_id) {
        router.push(`/test/primary/start?sessionId=${session.session_id}&userId=${userId}`)
      } else {
        setError('セッション作成に失敗しました')
      }
    } catch (err) {
      setError('エラーが発生しました。通信を確認してください。')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h2 className="text-4xl font-bold text-gray-900">
          PM 適性診断へようこそ
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          このテストでは、PM としての基礎知識、実務対応力、そして最も重要なマインドセットを多面的に診断します。
        </p>
      </div>

      {/* Test Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center mb-3">
            <div className="text-2xl font-bold text-blue-600">1</div>
            <h3 className="ml-3 font-semibold text-gray-900">1次テスト</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-2">
            <li>• PM 基礎知識（10問）</li>
            <li>• オフィス移転実務（8問）</li>
            <li>• マインドセット（6シナリオ）</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center mb-3">
            <div className="text-2xl font-bold text-green-600">2</div>
            <h3 className="ml-3 font-semibold text-gray-900">2次テスト</h3>
          </div>
          <p className="text-sm text-gray-600 mb-3">
            1次テスト合格者対象
          </p>
          <ul className="text-sm text-gray-600 space-y-2">
            <li>• マインドセット面接</li>
            <li>• 開放型質問</li>
            <li>• 詳細な検証</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center mb-3">
            <div className="text-2xl font-bold text-purple-600">3</div>
            <h3 className="ml-3 font-semibold text-gray-900">最終評価</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-2">
            <li>• A / B / C 等級判定</li>
            <li>• 強み・改善点分析</li>
            <li>• 推奨事項提示</li>
          </ul>
        </div>
      </div>

      {/* Test Details */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <div className="flex gap-4">
          <Clock className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">所要時間</h3>
            <p className="text-gray-700">
              約 60〜90 分です。集中できる環境での実施をお勧めします。
            </p>
          </div>
        </div>
      </div>

      {/* Start Form */}
      <form onSubmit={handleStartTest} className="bg-white rounded-lg shadow-lg p-8 space-y-6">
        <div>
          <label htmlFor="userId" className="block text-sm font-semibold text-gray-900 mb-2">
            ユーザーID（メールアドレス推奨）
          </label>
          <input
            id="userId"
            type="email"
            placeholder="example@company.com"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">
            結果照会時に使用します。メールアドレスまたは社員番号をご入力ください。
          </p>
        </div>

        {error && (
          <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            loading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
          }`}
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              準備中...
            </>
          ) : (
            <>
              テストを開始する
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>

        <p className="text-xs text-gray-500 text-center">
          このテストはご自身の率直な回答をお願いします。
          <br />
          マークシート形式と記述式、自由記述形式が混在しています。
        </p>
      </form>

      {/* Notes */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">注意事項</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• テスト開始後、中断することはできません。時間に余裕を持ってご実施ください。</li>
          <li>• 正答・不正答ではなく、PM としてのマインドセットを重視しています。</li>
          <li>• 外部資料の参照や他者への相談は避けてください。</li>
          <li>• 通信が遮断された場合は、サポートまでお問い合わせください。</li>
        </ul>
      </div>
    </div>
  )
}
