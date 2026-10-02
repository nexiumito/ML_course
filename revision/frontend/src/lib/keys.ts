import type { CardType } from '../api/types'

/** What a key press means on the Review screen (pure, so it can be unit-tested). */
export type KeyAction =
  | { type: 'help' }
  | { type: 'end' }
  | { type: 'undo' }
  | { type: 'source' }
  | { type: 'report' }
  | { type: 'reveal' }
  | { type: 'grade'; rating: 1 | 2 | 3 | 4 }
  | { type: 'toggleGuessed' }
  | { type: 'toggleTooEasy' }
  | { type: 'answerTf'; value: boolean }
  | { type: 'selectChoice'; position: number }
  | { type: 'check' }
  | { type: 'continue' }
  | { type: 'regrade'; target: 'hard' | 'good' | 'easy' }
  | { type: 'learnAhead' }

export interface KeyContext {
  phase: 'loading' | 'error' | 'question' | 'revealed' | 'graded' | 'waiting' | 'limit' | 'done'
  cardType?: CardType
  nChoices?: number
  hasSelection?: boolean
  /** rating of the graded auto-graded review (2 = guessed, 3 = good, 4 = too easy) */
  rating?: number
  correct?: boolean | null
}

const is = (k: string, ...keys: string[]) => keys.includes(k) || keys.includes(k.toLowerCase())

export function reviewKeyAction(key: string, c: KeyContext): KeyAction | null {
  const hasItem = c.phase === 'question' || c.phase === 'revealed' || c.phase === 'graded'
  if (key === '?') return { type: 'help' }
  if (key === 'Escape') return { type: 'end' }
  if (is(key, 'u')) return { type: 'undo' }
  if (hasItem && is(key, 's')) return { type: 'source' }
  if (hasItem && is(key, 'r')) return { type: 'report' }

  const auto = c.cardType === 'tf' || c.cardType === 'mcq'
  switch (c.phase) {
    case 'question':
      if (!auto) return key === ' ' || key === 'Enter' ? { type: 'reveal' } : null
      if (is(key, 'g')) return { type: 'toggleGuessed' }
      if (c.cardType === 'tf') {
        if (is(key, 't') || key === 'ArrowLeft') return { type: 'answerTf', value: true }
        if (is(key, 'f') || key === 'ArrowRight') return { type: 'answerTf', value: false }
        if (is(key, 'e')) return { type: 'toggleTooEasy' }
        return null
      }
      {
        // mcq: 1–6 or A–F pick the choice at that display position (E/F are choices here, not shortcuts)
        const pos = /^[1-6]$/.test(key) ? Number(key) - 1 : /^[a-f]$/i.test(key) ? key.toLowerCase().charCodeAt(0) - 97 : -1
        if (pos >= 0 && pos < (c.nChoices ?? 0)) return { type: 'selectChoice', position: pos }
        if (key === 'Enter' && c.hasSelection) return { type: 'check' }
        return null
      }
    case 'revealed':
      if (/^[1-4]$/.test(key)) return { type: 'grade', rating: Number(key) as 1 | 2 | 3 | 4 }
      if (key === ' ' || key === 'Enter') return { type: 'grade', rating: 3 }
      return null
    case 'graded':
      if (key === ' ' || key === 'Enter') return { type: 'continue' }
      if (c.correct && is(key, 'g')) return { type: 'regrade', target: c.rating === 2 ? 'good' : 'hard' }
      if (c.correct && is(key, 'e')) return { type: 'regrade', target: c.rating === 4 ? 'good' : 'easy' }
      return null
    case 'waiting':
      return key === 'Enter' ? { type: 'learnAhead' } : null
    default:
      return null
  }
}
