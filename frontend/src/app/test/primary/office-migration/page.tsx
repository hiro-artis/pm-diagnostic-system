'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react'
import { useTestContext } from '@/contexts/TestContext'

const OFFICE_MIGRATION_MC = [
  {
    id: 'OM-MC-001',
    question: 'オフィス移転の計画段階で最初に確認すべきことは？',
    options: [
      { value: 'A', label: '現在のオフィスの家賃' },
      { value: 'B', label: '移転先の立地条件' },
      { value: 'C', label: '現在のスペース利用状況と将来のニーズ確認' },
      { value: 'D', label: '移転業者の選定' },
    ],
  },
  {
    id: 'OM-MC-002',
    question: '異なるフロアに配置される部門の不安に対して、最初に取るべき行動は？',
    options: [
      { value: 'A', label: '経営判断として異動受け入れを強制する' },
      { value: 'B', label: '理由を説明せず既成事実を作る' },
      { value: 'C', label: '関係者との意見交換会を開催し、懸念事項を聴取する' },
      { value: 'D', label: 'メール一通で通知を済ませる' },
    ],
  },
  {
    id: 'OM-MC-003',
    question: '移転中に大型システムの障害が発生した場合の対応として最適なのは？',
    options: [
      { value: 'A', label: 'IT部門だけで対応を進める' },
      { value: 'B', label: '全部門と調整し、影響範囲を最小化する対応計画を立てる' },
      { value: 'C', label: '経営層への報告を後回しにする' },
      { value: 'D', label: '障害を公開せず対応を進める' },
    ],
  },
  {
    id: 'OM-MC-004',
    question: '移転当日、想定外の什器が手元にない場合の対応として不適切なのは？',
    options: [
      { value: 'A', label: '納入業者に確認し納期短縮を交渉する' },
      { value: 'B', label: '部門長と優先度を決め一部は代替品で対応する' },
      { value: 'C', label: '業者を強く叱責して当日の納入を無理に進める' },
      { value: 'D', label: '配置図を修正し一時的な運用方法を決定する' },
    ],
  },
  {
    id: 'OM-MC-005',
    question: '移転後2週間で「新しいフロア配置に慣れない」との声が上がった場合、適切な対応は？',
    options: [
      { value: 'A', label: '部門の文句として聞き流す' },
      { value: 'B', label: 'フロア配置の工夫や追加サポートについて関係者と相談する' },
      { value: 'C', label: '「すぐに慣れるはず」と根拠なく安心させる' },
      { value: 'D', label: '移転完了として対応を終わらせる' },
    ],
  },
]

const OFFICE_MIGRATION_ESSAYS = [
  {
    id: 'OM-ES-001',
    question: '移転前の課題発見と解決策',
    prompt: 'あなたは大規模オフィス移転プロジェクトのPMとなりました。現在のオフィスでは営業部と企画部が異なるフロアにあり、日常的に連携が必要ですが、行き来に15分かかっています。新しいオフィスではこの距離を短縮する計画です。\n\nただし以下の制約があります：\n- 営業部は新規顧客対応で現オフィスの引越し作業に参加できない\n- 企画部は企画立案の繁忙期で移転後すぐに稼働が必要\n- 新オフィスの什器納期は、営業部完全移転の5日後\n\nこの状況で想定されるリスク、それに対する対応策、および関係者とのコミュニケーション方法を具体的に述べなさい（200字以上300字以内）',
    minLength: 200,
    maxLength: 300,
  },
  {
    id: 'OM-ES-002',
    question: '予想外の状況への対応',
    prompt: '移転予定日の3日前、新オフィスの電気系統に欠陥が見つかりました。完全な改修には5日必要です。\n\n関係者の状況：\n- 経営層：予定通り移転したい（既に顧客・取引先に新住所を通知）\n- 営業部：顧客対応の都合で予定日の移転が必須\n- IT部門：不完全な状態での稼働は避けたい\n- 建設・不動産会社：追加費用・スケジュール変更で抵抗\n\nこの状況をどのように収拾させるか、あなたの判断プロセス・検討すべき選択肢・推奨案を述べなさい（200字以上300字以内）',
    minLength: 200,
    maxLength: 300,
  },
  {
    id: 'OM-ES-003',
    question: 'チームビルディングと信頼構築',
    prompt: '新しいオフィスへの移転を機に、異なる部門のメンバーが近い場所に配置されることになります。一部のメンバーからは「新しい部門との距離が近すぎて不安」「プライバシーが守られるか心配」という声が上がっています。\n\nこの状況で、メンバーの不安を解消し、新しい配置を機に部門間の協力関係を深めていくための施策を具体的に述べなさい（200字以上300字以内）',
    minLength: 200,
    maxLength: 300,
  },
]

function OfficeMigrationContent() {
  const router = useRouter()
  const { sessionId, userId, answers: contextAnswers, updateAnswers } = useTestContext()

  const [section, setSection] = useState<'mc' | 'essay'>('mc')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [error, setError] = useState('')

  if (!sessionId || !userId) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">セッション情報が見つかりません</p>
      </div>
    )
  }

  const mcQuestion = OFFICE_MIGRATION_MC[currentQuestionIndex]
  const essayQuestion = OFFICE_MIGRATION_ESSAYS[currentQuestionIndex]
  const currentQuestion = section === 'mc' ? mcQuestion : essayQuestion

  const isMcAnswered = contextAnswers.officeMigrationMc[mcQuestion.id] !== undefined
  const isEssayAnswered =
    contextAnswers.officeMigrationEssay[essayQuestion.id] &&
    contextAnswers.officeMigrationEssay[essayQuestion.id].length >= essayQuestion.minLength
  const isCurrentAnswered = section === 'mc' ? isMcAnswered : isEssayAnswered

  const handleMcAnswer = (value: string) => {
    updateAnswers('officeMigrationMc', mcQuestion.id, value)
    setError('')
  }

  const handleEssayAnswer = (value: string) => {
    updateAnswers('officeMigrationEssay', essayQuestion.id, value)
    setError('')
  }

  const handleNext = () => {
    if (!isCurrentAnswered) {
      if (section === 'mc') {
        setError('回答を選択してください')
      } else {
        setError(`200字以上300字以内で答えてください（現在：${essayAnswers[essayQuestion.id]?.length || 0}字）`)
      }
      return
    }

    if (section === 'mc') {
      if (currentQuestionIndex < OFFICE_MIGRATION_MC.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1)
        setError('')
      } else {
        setSection('essay')
        setCurrentQuestionIndex(0)
        setError('')
      }
    } else {
      if (currentQuestionIndex < OFFICE_MIGRATION_ESSAYS.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1)
        setError('')
      } else {
        router.push(`/test/primary/mindset?sessionId=${sessionId}&userId=${userId}`)
      }
    }
  }

  const handlePrevious = () => {
    if (section === 'mc' && currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
      setError('')
    } else if (section === 'essay' && currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
      setError('')
    } else if (section === 'essay' && currentQuestionIndex === 0) {
      setSection('mc')
      setCurrentQuestionIndex(OFFICE_MIGRATION_MC.length - 1)
      setError('')
    }
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white z-10 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              オフィス移転実務テスト
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              実践的なシナリオに対する対応力を評価します
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600 mb-2">
              {section === 'mc' ? '選択式' : '記述式'}
              {section === 'mc'
                ? ` ${currentQuestionIndex + 1}/${OFFICE_MIGRATION_MC.length}`
                : ` ${currentQuestionIndex + 1}/${OFFICE_MIGRATION_ESSAYS.length}`
              }
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {section === 'mc' ? 'MC' : 'ES'}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${(
                (section === 'mc'
                  ? (currentQuestionIndex + 1) / OFFICE_MIGRATION_MC.length
                  : (OFFICE_MIGRATION_MC.length + currentQuestionIndex + 1) /
                    (OFFICE_MIGRATION_MC.length + OFFICE_MIGRATION_ESSAYS.length)) * 100
              )}%`,
            }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
        {/* Question Text */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {section === 'mc' ? `MC${currentQuestionIndex + 1}` : `ES${currentQuestionIndex + 1}`}: {currentQuestion.question}
          </h3>

          {section === 'mc' ? (
            // Multiple Choice
            <div className="space-y-3">
              {(mcQuestion.options || []).map((option: any) => (
                <label
                  key={option.value}
                  className="block cursor-pointer"
                >
                  <div
                    className={`flex items-center p-4 rounded-lg border-2 transition-all ${
                      mcAnswers[mcQuestion.id] === option.value
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${mcQuestion.id}`}
                      value={option.value}
                      checked={mcAnswers[mcQuestion.id] === option.value}
                      onChange={() => handleMcAnswer(option.value)}
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
          ) : (
            // Essay
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 whitespace-pre-wrap text-sm text-gray-700">
                {essayQuestion.prompt}
              </div>
              <div>
                <textarea
                  value={contextAnswers.officeMigrationEssay[essayQuestion.id] || ''}
                  onChange={(e) => handleEssayAnswer(e.target.value)}
                  placeholder="あなたの回答を記入してください..."
                  className="w-full h-64 px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-600 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                />
                <div className="mt-2 text-sm text-gray-600">
                  {contextAnswers.officeMigrationEssay[essayQuestion.id]?.length || 0}字 /
                  {essayQuestion.minLength}〜{essayQuestion.maxLength}字
                </div>
              </div>
            </div>
          )}
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
          disabled={section === 'mc' && currentQuestionIndex === 0}
          className={`flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            section === 'mc' && currentQuestionIndex === 0
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
              : 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
        >
          <ArrowLeft className="w-5 h-5" />
          前へ
        </button>

        <button
          onClick={handleNext}
          className={`flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            isCurrentAnswered
              ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {section === 'essay' && currentQuestionIndex === OFFICE_MIGRATION_ESSAYS.length - 1
            ? 'マインドセットテストへ'
            : '次へ'}
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}

export default function OfficeMigrationPage() {
  return (
    <Suspense fallback={<div className="text-center py-12">読み込み中...</div>}>
      <OfficeMigrationContent />
    </Suspense>
  )
}
