'use client'

import { useState, Suspense, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { CheckCircle, AlertCircle, Home, RotateCcw } from 'lucide-react'
import { useTestContext } from '@/contexts/TestContext'

interface ResultData {
  primary_score: number
  pass: boolean
  details: {
    basic_knowledge: { score: number; pass: boolean }
    office_migration: { score: number; pass: boolean }
    mindset: { score: number; pass: boolean }
  }
  message: string
  next_steps: string
}

function ResultsContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { sessionId, userId, clearSession } = useTestContext()

  const [result, setResult] = useState<ResultData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const primaryScore = searchParams.get('primaryScore')

  useEffect(() => {
    if (primaryScore) {
      try {
        const parsed = JSON.parse(primaryScore)
        setResult(parsed)
      } catch {
        setResult({
          primary_score: 0,
          pass: false,
          details: {
            basic_knowledge: { score: 0, pass: false },
            office_migration: { score: 0, pass: false },
            mindset: { score: 0, pass: false },
          },
          message: 'テスト結果の取得に失敗しました',
          next_steps: 'もう一度お試しください',
        })
      }
      setLoading(false)
    } else {
      setError('テスト結果が見つかりません')
      setLoading(false)
    }
  }, [primaryScore])

  const handleHome = () => {
    clearSession()
    router.push('/')
  }

  const handleRetry = () => {
    clearSession()
    router.push('/')
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto"></div>
        <p className="text-gray-600 mt-4">結果を表示中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
        <p className="text-red-600 text-lg font-semibold">{error}</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">テスト結果を読み込めません</p>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex justify-center mb-4">
          {result.pass ? (
            <CheckCircle className="w-16 h-16 text-green-600" />
          ) : (
            <AlertCircle className="w-16 h-16 text-orange-600" />
          )}
        </div>
        <h2 className="text-3xl font-bold text-gray-900">
          {result.pass ? '合格です！' : 'ご受検ありがとうございました'}
        </h2>
        <p className="text-lg text-gray-600">{result.message}</p>
      </div>

      {/* Score Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
        <div className="text-center">
          <div className="text-5xl font-bold text-blue-600 mb-2">
            {result.primary_score}
          </div>
          <p className="text-gray-600">総合スコア / 290点</p>
        </div>

        {/* Section Scores */}
        <div className="border-t border-gray-200 pt-6 space-y-4">
          <h3 className="font-semibold text-gray-900 mb-4">セクション別結果</h3>

          {/* Basic Knowledge */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-gray-900">PM基礎知識</span>
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-blue-600">
                  {result.details.basic_knowledge.score}
                </span>
                <span className="text-sm text-gray-600">/ 100点</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  result.details.basic_knowledge.pass ? 'bg-green-600' : 'bg-red-600'
                }`}
                style={{
                  width: `${(result.details.basic_knowledge.score / 100) * 100}%`,
                }}
              />
            </div>
            <div className="text-sm text-gray-600">
              {result.details.basic_knowledge.pass ? (
                <span className="text-green-600 font-semibold">✓ 合格（70点以上）</span>
              ) : (
                <span className="text-red-600 font-semibold">✗ 不合格（70点未満）</span>
              )}
            </div>
          </div>

          {/* Office Migration */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-gray-900">オフィス移転実務</span>
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-green-600">
                  {result.details.office_migration.score}
                </span>
                <span className="text-sm text-gray-600">/ 100点</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  result.details.office_migration.pass ? 'bg-green-600' : 'bg-red-600'
                }`}
                style={{
                  width: `${(result.details.office_migration.score / 100) * 100}%`,
                }}
              />
            </div>
            <div className="text-sm text-gray-600">
              {result.details.office_migration.pass ? (
                <span className="text-green-600 font-semibold">✓ 合格（65点以上）</span>
              ) : (
                <span className="text-red-600 font-semibold">✗ 不合格（65点未満）</span>
              )}
            </div>
          </div>

          {/* Mindset */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-gray-900">マインドセット</span>
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-purple-600">
                  {result.details.mindset.score}
                </span>
                <span className="text-sm text-gray-600">/ 90点</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  result.details.mindset.pass ? 'bg-green-600' : 'bg-red-600'
                }`}
                style={{
                  width: `${(result.details.mindset.score / 90) * 100}%`,
                }}
              />
            </div>
            <div className="text-sm text-gray-600">
              {result.details.mindset.pass ? (
                <span className="text-green-600 font-semibold">✓ 合格（60点以上）</span>
              ) : (
                <span className="text-red-600 font-semibold">✗ 不合格（60点未満）</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div
        className={`rounded-lg border-l-4 p-6 ${
          result.pass
            ? 'bg-green-50 border-green-500'
            : 'bg-orange-50 border-orange-500'
        }`}
      >
        <h3 className="font-semibold text-gray-900 mb-2">次のステップ</h3>
        <p className="text-gray-700">{result.next_steps}</p>
      </div>

      {/* Info */}
      {result.pass && (
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <p className="text-sm text-gray-700">
            <strong>お疲れ様でした！</strong>
            <br />
            1次テスト合格者の皆様は、2次テスト（マインドセット面接）にお進みいただきます。
            詳細はメール及び当社ウェブサイトでご案内いたします。
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleHome}
          className="flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50"
        >
          <Home className="w-5 h-5" />
          ホームに戻る
        </button>

        {!result.pass && (
          <button
            onClick={handleRetry}
            className="flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all bg-blue-600 text-white hover:bg-blue-700"
          >
            <RotateCcw className="w-5 h-5" />
            再受検する
          </button>
        )}
      </div>

      {/* Footer */}
      <div className="text-xs text-gray-500 text-center space-y-2">
        <p>セッションID: {sessionId}</p>
        <p>ユーザーID: {userId}</p>
      </div>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="text-center py-12">読み込み中...</div>}>
      <ResultsContent />
    </Suspense>
  )
}
