import { describe, expect, it } from 'vitest'
import { reviewKeyAction as k } from '../keys'

describe('reviewKeyAction', () => {
  it('global shortcuts', () => {
    expect(k('?', { phase: 'done' })).toEqual({ type: 'help' })
    expect(k('Escape', { phase: 'question', cardType: 'basic' })).toEqual({ type: 'end' })
    expect(k('U', { phase: 'loading' })).toEqual({ type: 'undo' })
    expect(k('s', { phase: 'question', cardType: 'basic' })).toEqual({ type: 'source' })
    expect(k('s', { phase: 'done' })).toBeNull() // no card on screen
    expect(k('r', { phase: 'graded', cardType: 'tf' })).toEqual({ type: 'report' })
  })

  it('self-graded: space reveals, then 1–4 / space grade', () => {
    expect(k(' ', { phase: 'question', cardType: 'cloze' })).toEqual({ type: 'reveal' })
    expect(k('3', { phase: 'question', cardType: 'cloze' })).toBeNull() // no grading before reveal
    expect(k('1', { phase: 'revealed', cardType: 'cloze' })).toEqual({ type: 'grade', rating: 1 })
    expect(k('Enter', { phase: 'revealed', cardType: 'basic' })).toEqual({ type: 'grade', rating: 3 })
    expect(k('5', { phase: 'revealed', cardType: 'basic' })).toBeNull()
  })

  it('true/false', () => {
    expect(k('t', { phase: 'question', cardType: 'tf' })).toEqual({ type: 'answerTf', value: true })
    expect(k('ArrowRight', { phase: 'question', cardType: 'tf' })).toEqual({ type: 'answerTf', value: false })
    expect(k('g', { phase: 'question', cardType: 'tf' })).toEqual({ type: 'toggleGuessed' })
    expect(k('e', { phase: 'question', cardType: 'tf' })).toEqual({ type: 'toggleTooEasy' })
  })

  it('multiple choice: digits and letters select, E/F are choices, Enter checks only with a selection', () => {
    const q = { phase: 'question' as const, cardType: 'mcq' as const, nChoices: 6 }
    expect(k('2', q)).toEqual({ type: 'selectChoice', position: 1 })
    expect(k('E', q)).toEqual({ type: 'selectChoice', position: 4 })
    expect(k('f', q)).toEqual({ type: 'selectChoice', position: 5 })
    expect(k('5', { ...q, nChoices: 4 })).toBeNull()
    expect(k('9', { ...q, nChoices: 9 })).toEqual({ type: 'selectChoice', position: 8 })
    expect(k('Enter', q)).toBeNull()
    expect(k('Enter', { ...q, hasSelection: true })).toEqual({ type: 'check' })
  })

  it('after grading: continue, and adjust the rating only when correct', () => {
    const g = { phase: 'graded' as const, cardType: 'mcq' as const, correct: true, rating: 3 }
    expect(k('Enter', g)).toEqual({ type: 'continue' })
    expect(k('g', g)).toEqual({ type: 'regrade', target: 'hard' })
    expect(k('g', { ...g, rating: 2 })).toEqual({ type: 'regrade', target: 'good' })
    expect(k('e', g)).toEqual({ type: 'regrade', target: 'easy' })
    expect(k('e', { ...g, correct: false })).toBeNull()
  })

  it('waiting: Enter shows the learning card now', () => {
    expect(k('Enter', { phase: 'waiting' })).toEqual({ type: 'learnAhead' })
  })
})
