'use client'

export const dynamic = 'force-dynamic'

import { useState, Suspense } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react'
import { useTestContext } from '@/contexts/TestContext'

const BASIC_KNOWLEDGE_QUESTIONS = [
  {
    id: 'BK-001',
    question: 'プロジェクトの定義として正しいものはどれか？',
    options: [
      { value: 'A', label: '継続的で反復的な業務活動' },
      { value: 'B', label: '一時的な努力で独特な成果物を生み出す活動' },
      { value: 'C', label: '組織の日常的な運営活動' },
      { value: 'D', label: '経営層による意思決定プロセス' },
    ],
  },
  {
    id: 'BK-002',
    question: 'プロジェクト成功のために重要なステークホルダー活動として誤りがあるものはどれか？',
    options: [
      { value: 'A', label: 'ステークホルダーのニーズ理解' },
      { value: 'B', label: '期待値管理' },
      { value: 'C', label: 'ステークホルダーの関心度・影響度分析' },
      { value: 'D', label: '反対意見のステークホルダーの排除' },
    ],
  },
  {
    id: 'BK-003',
    question: 'スコープクリープが起こる主な原因は？',
    options: [
      { value: 'A', label: '厳密なスコープ定義と変更管理の欠如' },
      { value: 'B', label: 'チームメンバーが十分なスキルを持たない' },
      { value: 'C', label: '正確なスケジュール計画' },
      { value: 'D', label: '効果的なコミュニケーション' },
    ],
  },
  {
    id: 'BK-004',
    question: 'リスク対応戦略の中で、リスク発生確率を低減させる戦略は？',
    options: [
      { value: 'A', label: '受容（Accept）' },
      { value: 'B', label: '軽減（Mitigate）' },
      { value: 'C', label: '回避（Avoid）' },
      { value: 'D', label: 'エスカレーション（Escalate）' },
    ],
  },
  {
    id: 'BK-005',
    question: 'コミュニケーション計画で定義する項目ではないのはどれ？',
    options: [
      { value: 'A', label: 'コミュニケーション対象者' },
      { value: 'B', label: '情報の内容・粒度' },
      { value: 'C', label: '配信方法・頻度' },
      { value: 'D', label: '配信者の給与水準' },
    ],
  },
  {
    id: 'BK-006',
    question: 'プロジェクト品質を確保するための活動順序として正しいのは？',
    options: [
      { value: 'A', label: '検証 → 統合 → テスト' },
      { value: 'B', label: '計画 → 設計 → テスト → 検証' },
      { value: 'C', label: 'テスト → 検証 → 統合' },
      { value: 'D', label: '統合 → 検証 → テスト' },
    ],
  },
  {
    id: 'BK-007',
    question: '重要パスの特性として正しいのはどれ？',
    options: [
      { value: 'A', label: '最短で完了できるパス' },
      { value: 'B', label: '最も多くのリソースを使うパス' },
      { value: 'C', label: 'スラックがなく、遅延するとプロジェクト全体が遅延するパス' },
      { value: 'D', label: '最もコストが高いパス' },
    ],
  },
  {
    id: 'BK-008',
    question: 'コスト超過指数（CPI）が0.9の場合、その意味は？',
    options: [
      { value: 'A', label: 'コストが10%削減されている' },
      { value: 'B', label: 'コストが10%超過している' },
      { value: 'C', label: 'スケジュールが10%遅延している' },
      { value: 'D', label: '品質が10%低下している' },
    ],
  },
  {
    id: 'BK-009',
    question: 'プロジェクトマネージャーのステークホルダーマネジメントにおいて最も重要な活動は？',
    options: [
      { value: 'A', label: '定期的なステータスレポート提出' },
      { value: 'B', label: 'ステークホルダーの期待値設定と管理' },
      { value: 'C', label: 'プロジェクト予算管理' },
      { value: 'D', label: 'チームメンバーの給与管理' },
    ],
  },
  {
    id: 'BK-010',
    question: 'インテグレーション・マネジメント（統合管理）が重要な理由は？',
    options: [
      { value: 'A', label: '各知識エリア間の相互作用を調整するため' },
      { value: 'B', label: 'プロジェクト経費を削減するため' },
      { value: 'C', label: 'スケジュール遅延を防ぐため' },
      { value: 'D', label: 'チームサイズを最小化するため' },
    ],
  },
]

function BasicKnowledgeContent() {
  const router = useRouter()
  const { sessionId, userId, answers: contextAnswers, updateAnswers } = useTestContext()

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [error, setError] = useState('')

  if (!sessionId || !userId) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">セッション情報が見つかりません</p>
      </div>
    )
  }

  const currentQuestion = BASIC_KNOWLEDGE_QUESTIONS[currentQuestionIndex]
  const isAnswered = contextAnswers.basicKnowledge[currentQuestion.id] !== undefined
  const isLastQuestion = currentQuestionIndex === BASIC_KNOWLEDGE_QUESTIONS.length - 1
  const answeredCount = Object.keys(contextAnswers.basicKnowledge).length

  const handleAnswer = (value: string) => {
    updateAnswers('basicKnowledge', currentQuestion.id, value)
    setError('')
  }

  const handleNext = () => {
    if (!isAnswered) {
      setError('回答を選択してください')
      return
    }
    if (isLastQuestion) {
      router.push(`/test/primary/office-migration?sessionId=${sessionId}&userId=${userId}`)
    } else {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setError('')
    }
  }

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
      setError('')
    }
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white z-10 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              PM基礎知識テスト
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              プロジェクト管理の基礎知識について問います
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">
              {currentQuestionIndex + 1}/{BASIC_KNOWLEDGE_QUESTIONS.length}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              回答済み: {answeredCount}問
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${((currentQuestionIndex + 1) / BASIC_KNOWLEDGE_QUESTIONS.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
        {/* Question Text */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Q{currentQuestionIndex + 1}: {currentQuestion.question}
          </h3>

          {/* Options */}
          <div className="space-y-3">
            {currentQuestion.options.map((option) => (
              <label
                key={option.value}
                className="block cursor-pointer"
              >
                <div
                  className={`flex items-center p-4 rounded-lg border-2 transition-all ${
                    contextAnswers.basicKnowledge[currentQuestion.id] === option.value
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestion.id}`}
                    value={option.value}
                    checked={contextAnswers.basicKnowledge[currentQuestion.id] === option.value}
                    onChange={() => handleAnswer(option.value)}
                    className="w-5 h-5 text-blue-600 cursor-pointer"
                  />
                  <span className="ml-3 font-semibold text-gray-900">
                    {option.value}
                  </span>
                  <span className="ml-2 text-gray-700">
                    {option.label}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handlePrevious}
          disabled={currentQuestionIndex === 0}
          className={`flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            currentQuestionIndex === 0
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
              : 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
        >
          <ArrowLeft className="w-5 h-5" />
          前の問題
        </button>

        <button
          onClick={handleNext}
          className={`flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            isAnswered
              ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isLastQuestion ? '次へ（オフィス移転テスト）' : '次の問題'}
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>

      {/* Footer Info */}
      <div className="text-xs text-gray-500 text-center">
        回答を選択して「次へ」をクリックしてください。
        前の問題に戻ることも可能です。
      </div>
    </div>
  )
}

export default function BasicKnowledgePage() {
  return (
    <Suspense fallback={<div className="text-center py-12">読み込み中...</div>}>
      <BasicKnowledgeContent />
    </Suspense>
  )
}
