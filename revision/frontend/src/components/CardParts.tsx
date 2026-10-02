import { useState } from 'react'
import type { ItemView } from '../api/types'
import { Markdown } from './Markdown'
import { OriginBadge, Sheet, Tag } from './ui'

export function CardHeader({ view }: { view: ItemView }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <OriginBadge origin={view.origin} examLabel={view.exam_label} />
      <Tag>
        {view.lecture} · {view.lecture_title}
      </Tag>
      {view.themes.map((t) => (
        <Tag key={t.id}>{t.label}</Tag>
      ))}
      {view.priority === 'core' && (
        <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400" title="Exam-essential">
          ● core
        </span>
      )}
      {view.is_new && <span className="text-xs font-semibold text-sky-600 dark:text-sky-400">new</span>}
    </div>
  )
}

export function CardImages({ images }: { images: ItemView['images'] }) {
  const [zoomed, setZoomed] = useState<string | null>(null)
  if (!images.length) return null
  return (
    <div className="mt-4 space-y-3">
      {images.map((im) => (
        <button key={im.url} type="button" className="block w-full" onClick={() => setZoomed(im.url)}>
          <img src={im.url} alt={im.alt} className="mx-auto max-h-80 max-w-full rounded-lg bg-white" />
        </button>
      ))}
      <Sheet open={zoomed !== null} onClose={() => setZoomed(null)} title="Figure" wide>
        {zoomed && <img src={zoomed} alt="" className="mx-auto max-w-none bg-white" style={{ width: '100%' }} />}
      </Sheet>
    </div>
  )
}

export function TrapNote({ trap }: { trap: string | null }) {
  if (!trap) return null
  return (
    <div className="mt-4 flex gap-2 rounded-xl bg-amber-50 p-3 text-[0.95rem] text-amber-950 ring-1 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-100 dark:ring-amber-500/30">
      <span aria-hidden="true">⚠︎</span>
      <div className="min-w-0 flex-1">
        <span className="sr-only">Classic trap: </span>
        <Markdown>{trap}</Markdown>
      </div>
    </div>
  )
}

export function Explanation({ text }: { text: string | null }) {
  if (!text) return null
  return (
    <div className="mt-4 border-t border-slate-100 pt-4 text-slate-700 dark:border-slate-800 dark:text-slate-300">
      <Markdown>{text}</Markdown>
    </div>
  )
}

type ChoiceState = 'idle' | 'selected' | 'correct' | 'wrong-picked' | 'missed' | 'neutral'

const choiceStyles: Record<ChoiceState, string> = {
  idle: 'ring-slate-200 bg-white hover:bg-slate-50 dark:bg-slate-900 dark:ring-slate-700 dark:hover:bg-slate-800',
  selected: 'ring-2 ring-indigo-500 bg-indigo-50 dark:bg-indigo-500/15',
  correct: 'ring-2 ring-emerald-500 bg-emerald-50 dark:bg-emerald-500/15',
  'wrong-picked': 'ring-2 ring-red-500 bg-red-50 dark:bg-red-500/15',
  missed: 'ring-2 ring-emerald-400 bg-white dark:bg-slate-900',
  neutral: 'ring-slate-200 bg-white opacity-70 dark:bg-slate-900 dark:ring-slate-700',
}

const LETTERS = 'ABCDEF'

/** MCQ choices in display `order` (original indices). After grading, shows ✓ / ✗ with text, never color alone. */
export function ChoiceList({
  choices,
  order,
  selected,
  onToggle,
  correct,
  multi,
}: {
  choices: string[]
  order: number[]
  selected: number[]
  onToggle?: (originalIndex: number) => void
  correct?: number[] | null
  multi: boolean
}) {
  const graded = correct !== undefined && correct !== null
  return (
    <div className="mt-4 space-y-2.5" role={multi ? 'group' : 'radiogroup'}>
      {multi && !graded && <p className="text-sm text-slate-500 dark:text-slate-400">Select all that apply.</p>}
      {order.map((orig, pos) => {
        const isSel = selected.includes(orig)
        const isCorrect = graded && correct!.includes(orig)
        const state: ChoiceState = !graded
          ? isSel
            ? 'selected'
            : 'idle'
          : isCorrect
            ? isSel
              ? 'correct'
              : 'missed'
            : isSel
              ? 'wrong-picked'
              : 'neutral'
        const mark = graded ? (isCorrect ? (isSel ? '✓' : '✓ correct') : isSel ? '✗' : '') : ''
        return (
          <button
            key={orig}
            type="button"
            role={multi ? 'checkbox' : 'radio'}
            aria-checked={isSel}
            disabled={graded || !onToggle}
            onClick={() => onToggle?.(orig)}
            className={`flex w-full items-start gap-3 rounded-xl px-3.5 py-3 text-left ring-1 transition-colors ${choiceStyles[state]}`}
          >
            <span
              className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center text-sm font-semibold ${
                multi ? 'rounded-md' : 'rounded-full'
              } ${isSel ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'}`}
            >
              {LETTERS[pos]}
            </span>
            <span className="min-w-0 flex-1">
              <Markdown>{choices[orig]}</Markdown>
            </span>
            {mark && (
              <span
                className={`shrink-0 text-sm font-semibold ${isCorrect ? 'text-emerald-700 dark:text-emerald-400' : 'text-red-700 dark:text-red-400'}`}
              >
                {mark}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
