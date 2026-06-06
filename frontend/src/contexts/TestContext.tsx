'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface TestAnswers {
  basicKnowledge: Record<string, string>
  officeMigrationMc: Record<string, string>
  officeMigrationEssay: Record<string, string>
  mindset: Record<string, string>
}

interface TestContextType {
  sessionId: string | null
  userId: string | null
  answers: TestAnswers
  updateAnswers: (section: keyof TestAnswers, questionId: string, value: string) => void
  clearSession: () => void
}

const TestContext = createContext<TestContextType | undefined>(undefined)

const STORAGE_KEY = 'pm_test_session'

export function TestProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [userId, setUserId] = useState<string | null>(null)
  const [answers, setAnswers] = useState<TestAnswers>({
    basicKnowledge: {},
    officeMigrationMc: {},
    officeMigrationEssay: {},
    mindset: {},
  })
  const [isLoaded, setIsLoaded] = useState(false)

  // Load from sessionStorage on mount
  useEffect(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const data = JSON.parse(stored)
        setSessionId(data.sessionId)
        setUserId(data.userId)
        setAnswers(data.answers)
      } catch (error) {
        console.error('Failed to load session from storage:', error)
      }
    }
    setIsLoaded(true)
  }, [])

  // Save to sessionStorage whenever answers change
  useEffect(() => {
    if (isLoaded && sessionId && userId) {
      const data = {
        sessionId,
        userId,
        answers,
        timestamp: new Date().toISOString(),
      }
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    }
  }, [answers, isLoaded, sessionId, userId])

  const updateAnswers = (section: keyof TestAnswers, questionId: string, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [questionId]: value,
      },
    }))
  }

  const clearSession = () => {
    setSessionId(null)
    setUserId(null)
    setAnswers({
      basicKnowledge: {},
      officeMigrationMc: {},
      officeMigrationEssay: {},
      mindset: {},
    })
    sessionStorage.removeItem(STORAGE_KEY)
  }

  // Initialize session from URL params (first page load)
  useEffect(() => {
    if (isLoaded && !sessionId) {
      const params = new URLSearchParams(window.location.search)
      const paramSessionId = params.get('sessionId')
      const paramUserId = params.get('userId')

      if (paramSessionId && paramUserId) {
        setSessionId(paramSessionId)
        setUserId(paramUserId)
      }
    }
  }, [isLoaded, sessionId])

  if (!isLoaded) {
    return <>{children}</> // Return children while loading
  }

  return (
    <TestContext.Provider value={{ sessionId, userId, answers, updateAnswers, clearSession }}>
      {children}
    </TestContext.Provider>
  )
}

export function useTestContext() {
  const context = useContext(TestContext)
  if (context === undefined) {
    throw new Error('useTestContext must be used within TestProvider')
  }
  return context
}
