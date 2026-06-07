'use client'

export const dynamic = 'force-dynamic'

import { useState, Suspense } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useTestContext } from '@/contexts/TestContext'

const MINDSET_SCENARIOS = [
  {
    id: 'MS-S01',
    title: '予算削減要請への対応',
    scenario: 'プロジェクトが中盤に差し掛かったとき、突然経営層から「経営環境の変化により、プロジェクト予算を30%削減してほしい」と言われました。\n\n現状：\n• 計画通り進捗している\n• 当初のスコープ・品質基準は内部で周知済み\n• チームメンバーの士気は良好\n• 削減されるなら、何らかのスコープ削減は必須',
    options: [
      {
        value: 'A',
        label: '経営層の決定に従い、即座に予算削減を受け入れスコープを縮小する',
      },
      {
        value: 'B',
        label: '「計画通り進捗しているので予算削減は難しい」と経営層に報告し、削減を拒否する',
      },
      {
        value: 'C',
        label: '予算削減が必要な背景・期待を経営層から聴取した上で、削減下での実現可能なスコープ案・品質維持案を複数作成し提示する',
      },
      {
        value: 'D',
        label: '予算削減には応じず、代わりに品質を下げることを提案する',
      },
    ],
  },
  {
    id: 'MS-S02',
    title: 'チーム内の意見対立への対応',
    scenario: '技術チームと営業チームの意見が対立しています。\n\n技術チーム：「新機能を実装するには最低4週間必要。品質を落とすべきではない」\n営業チーム：「顧客は2週間での納期を期待している。実装を急ぐべき」\n\nチーム双方ともあなたのサポートを待っています。経営層の判断も示されていません。',
    options: [
      {
        value: 'A',
        label: '技術チームの意見が正しいと判断し、営業チームに納期変更を受け入れるよう指示する',
      },
      {
        value: 'B',
        label: '営業チームの期待に応えるべく、技術チームに2週間での納期を指示する',
      },
      {
        value: 'C',
        label: 'まず両チームに個別に詳しく話を聴き、各視点での課題・制約を理解した上で、技術と営業が一堂に会して解決案を協議する場を設定する',
      },
      {
        value: 'D',
        label: '「こういうことがあるプロジェクトだから、双方で妥協してほしい」と曖昧に伝える',
      },
    ],
  },
  {
    id: 'MS-S03',
    title: '新入メンバーの不安への対応',
    scenario: 'プロジェクト開始から3ヶ月経った時点で、新しいメンバーがプロジェクトに参加しました。\n\n1週間後、メンバーから「プロジェクトの背景や進捗が十分理解できていない」「既存メンバーとのコミュニケーションがしづらい」との相談がありました。\n\n既存メンバーは忙しく、新入メンバーへの対応に時間を割く余裕がありません。',
    options: [
      {
        value: 'A',
        label: '「プロジェクトは忙しいから、自分で学習するしかない」と伝え、個人の努力に任せる',
      },
      {
        value: 'B',
        label: '既存メンバーに「新入メンバーの対応をお願いします」と指示し、対応を任せる',
      },
      {
        value: 'C',
        label: '自分の時間を使ってでも新入メンバーとマンツーマンでプロジェクト背景を説明し、既存メンバーとの交流機会を意図的に作り、段階的にプロジェクトへの帰属意識を高めるよう支援する',
      },
      {
        value: 'D',
        label: '新入メンバーのためにプロジェクトの進捗を一時停止し、説明会を開催する',
      },
    ],
  },
  {
    id: 'MS-S04',
    title: '複数部門の相反する要望への対応',
    scenario: 'システム導入プロジェクトで、複数部門から相反する要望が出ています。\n\n営業部：「営業ツール機能を重視したい。納期は3ヶ月」\n企画部：「企画プロセスの見える化を重視したい。納期は柔軟」\nIT部門：「システム安定性が最優先。追加機能は限定したい」\n\n各部門の責任者は、それぞれの部門の利益を重視しており、譲歩する気配がありません。',
    options: [
      {
        value: 'A',
        label: 'PMの判断で最も重要度の高い部門の要望を採用し、他は後回しにする',
      },
      {
        value: 'B',
        label: '各部門から詳しく話を聴き、それぞれの要望の背景・優先順位を理解した上で、経営層・各部門責任者の合意の下で、優先機能・納期・品質を決定する',
      },
      {
        value: 'C',
        label: '「全て実装できるように頑張ります」と約束してから、後で実装不可を伝える',
      },
      {
        value: 'D',
        label: '各部門の言い分を聴いた後、最大公約数的な要望だけに絞り、各部門に納得してもらう',
      },
    ],
  },
  {
    id: 'MS-S05',
    title: 'フロア移転時の意見対立への対応',
    scenario: 'オフィス移転計画で、一部のメンバー（主に長期勤続者）から「現在のフロア配置を変えたくない」「新しい部門との協力は難しい」という強い反発が出ています。\n\n一方、経営層は「部門間連携を強化するために、移転を機にフロア配置を変えるべき」と決定しています。\n\n反発しているメンバーの意見を黙殺して移転を進めると、彼らのモチベーション低下や離職の可能性があります。',
    options: [
      {
        value: 'A',
        label: '経営層の決定に従い、反発しているメンバーには「会社の決定ですから」と伝える',
      },
      {
        value: 'B',
        label: '反発しているメンバーを新しいフロア配置から除外し、別のエリアに残す',
      },
      {
        value: 'C',
        label: '反発しているメンバーと個別に、移転理由・期待・懸念について何度も対話し、新しい配置に向けた段階的な準備・フォローアップを計画する。同時に、経営層にも「メンバーの懸念・段階的進行」を報告し、全体での着地点を整える',
      },
      {
        value: 'D',
        label: '反発しているメンバーの懸念を経営層に報告し、経営層に判断・説得を任せる',
      },
    ],
  },
  {
    id: 'MS-S06',
    title: '新規領域プロジェクトでの連携',
    scenario: 'あなたは新規事業プロジェクトのPMに抜擢されました。自分の経験がない領域です。\n\nチーム構成：\n• 自分（PM）：営業経験10年、管理経験3年\n• 技術リーダー：その道の専門家だが、プロジェクト管理経験は少ない\n• ビジネス分析者：初心者で、自分の判断に自信がない\n• 外部アドバイザー：専門知識は豊富だが、費用が高い\n\nプロジェクト開始1ヶ月で、当初の計画では成功する見込みが低いことが判明しました。',
    options: [
      {
        value: 'A',
        label: '自分のPM経験を活かして、一人で計画を修正し実行する',
      },
      {
        value: 'B',
        label: '費用を理由に外部アドバイザーを断り、メンバーだけで対応する',
      },
      {
        value: 'C',
        label: '技術リーダー・ビジネス分析者・外部アドバイザー（必要に応じて）を交えた検討会を開催し、各自の知見を引き出しながら、新しい計画案を共同で作成する。責任はPMが負いながらも、チーム全体の力を活かす',
      },
      {
        value: 'D',
        label: '「新規領域なので成功保証はできない」と経営層に報告し、プロジェクトの延期を提案する',
      },
    ],
  },
]

function MindsetContent() {
  const router = useRouter()
  const { sessionId, userId, answers: contextAnswers, updateAnswers } = useTestContext()

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!sessionId || !userId) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">セッション情報が見つかりません</p>
      </div>
    )
  }

  const currentScenario = MINDSET_SCENARIOS[currentQuestionIndex]
  const isAnswered = contextAnswers.mindset[currentScenario.id] !== undefined
  const isLastQuestion = currentQuestionIndex === MINDSET_SCENARIOS.length - 1
  const answeredCount = Object.keys(contextAnswers.mindset).length

  const handleAnswer = (value: string) => {
    updateAnswers('mindset', currentScenario.id, value)
    setError('')
  }

  const handleNext = async () => {
    if (!isAnswered) {
      setError('回答を選択してください')
      return
    }

    if (isLastQuestion) {
      setIsSubmitting(true)
      try {
        const result = await apiClient.submitPrimaryTest(
          sessionId,
          contextAnswers.basicKnowledge,
          contextAnswers.officeMigrationMc,
          contextAnswers.officeMigrationEssay,
          contextAnswers.mindset
        )

        router.push(
          `/test/results?sessionId=${sessionId}&userId=${userId}&primaryScore=${result.primary_score}`
        )
      } catch (err) {
        setError('テストの送信に失敗しました。もう一度お試しください。')
        console.error(err)
      } finally {
        setIsSubmitting(false)
      }
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
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white z-10 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              マインドセット検証
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              PM として最も重要なマインドセットを評価します
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-purple-600">
              {currentQuestionIndex + 1}/{MINDSET_SCENARIOS.length}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              回答済み: {answeredCount}シナリオ
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${((currentQuestionIndex + 1) / MINDSET_SCENARIOS.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Scenario Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
        {/* Scenario Title */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            シナリオ{currentQuestionIndex + 1}: {currentScenario.title}
          </h3>
        </div>

        {/* Scenario Description */}
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {currentScenario.scenario}
          </p>
        </div>

        {/* Question */}
        <div className="border-t border-gray-200 pt-6">
          <p className="font-semibold text-gray-900 mb-4">あなたならどうしますか？</p>

          {/* Options */}
          <div className="space-y-3">
            {currentScenario.options.map((option) => (
              <label
                key={option.value}
                className="block cursor-pointer"
              >
                <div
                  className={`flex items-start p-4 rounded-lg border-2 transition-all ${
                    contextAnswers.mindset[currentScenario.id] === option.value
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name={`scenario-${currentScenario.id}`}
                    value={option.value}
                    checked={contextAnswers.mindset[currentScenario.id] === option.value}
                    onChange={() => handleAnswer(option.value)}
                    className="w-5 h-5 text-purple-600 cursor-pointer mt-0.5 flex-shrink-0"
                  />
                  <div className="ml-3 flex-1">
                    <span className="font-semibold text-gray-900">
                      {option.value}
                    </span>
                    <p className="text-gray-700 mt-1 text-sm">
                      {option.label}
                    </p>
                  </div>
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
          前のシナリオ
        </button>

        <button
          onClick={handleNext}
          disabled={!isAnswered || isSubmitting}
          className={`flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            isAnswered && !isSubmitting
              ? 'bg-purple-600 text-white hover:bg-purple-700 active:scale-95'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              送信中...
            </>
          ) : (
            <>
              {isLastQuestion ? '1次テストを送信' : '次のシナリオ'}
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>

      {/* Footer Info */}
      <div className="text-xs text-gray-500 text-center">
        シナリオをよく読んで、あなたの判断に最も近い選択肢を選んでください。
      </div>
    </div>
  )
}

export default function MindsetPage() {
  return (
    <Suspense fallback={<div className="text-center py-12">読み込み中...</div>}>
      <MindsetContent />
    </Suspense>
  )
}
