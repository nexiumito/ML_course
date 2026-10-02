import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../api/client'
import type { DrillCounts, ItemView, QueueResponse, ReviewResult, SessionSummary, StudyCounts } from '../api/types'
import { useApp } from '../AppContext'
import { CardHeader, CardImages, ChoiceList, Explanation, TrapNote } from '../components/CardParts'
import { Markdown } from '../components/Markdown'
import { formatAnswer } from '../lib/text'
import { ReportDialog } from '../components/ReportDialog'
import { ShortcutHelp } from '../components/ShortcutHelp'
import { SourceViewer } from '../components/SourceViewer'
import { Button, ErrorBox, Kbd, Segmented, Spinner } from '../components/ui'
import { useKeys } from '../hooks/useKeys'
import { formatDuration, formatInterval, pct } from '../lib/format'
import { reviewKeyAction } from '../lib/keys'
import { describeSpec, newSessionId, specFromSearch, specToParams } from '../lib/session'
import { choiceOrder } from '../lib/shuffle'

type Phase =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'question'; item: ItemView }
  | { kind: 'revealed'; item: ItemView }
  | { kind: 'graded'; item: ItemView; result: ReviewResult; answer: boolean | number[] }
  | { kind: 'waiting'; until: string }
  | { kind: 'limit' }
  | { kind: 'done' }

type Sheet = 'source' | 'report' | 'help' | null

const GRADES = [
  { r: 1, label: 'Again', cls: 'bg-red-600 hover:bg-red-500 text-white' },
  { r: 2, label: 'Hard', cls: 'bg-amber-500 hover:bg-amber-400 text-white' },
  { r: 3, label: 'Good', cls: 'bg-emerald-600 hover:bg-emerald-500 text-white' },
  { r: 4, label: 'Easy', cls: 'bg-sky-600 hover:bg-sky-500 text-white' },
] as const

const isAuto = (item: ItemView) => item.type === 'tf' || item.type === 'mcq'

export default function Review() {
  const [search] = useSearchParams()
  const navigate = useNavigate()
  const { settings, toast } = useApp()
  const spec = useMemo(() => specFromSearch(search), [search])
  const sessionId = useMemo(() => newSessionId(), [search]) // eslint-disable-line react-hooks/exhaustive-deps

  const [phase, setPhase] = useState<Phase>({ kind: 'loading' })
  const [counts, setCounts] = useState<QueueResponse['counts'] | null>(null)
  const [limitReached, setLimitReached] = useState(false)
  const [selected, setSelected] = useState<number[]>([])
  const [guessed, setGuessed] = useState(false)
  const [tooEasy, setTooEasy] = useState(false)
  const [busy, setBusy] = useState(false)
  const [sheet, setSheet] = useState<Sheet>(null)
  const [reviewedCount, setReviewedCount] = useState(0)
  const [ignoreLimits, setIgnoreLimits] = useState(false)
  const shownAt = useRef(Date.now())
  const lastItem = useRef<string | undefined>(undefined)
  const durationOfGraded = useRef(0)

  const showItem = useCallback((item: ItemView) => {
    setSelected([])
    setGuessed(false)
    setTooEasy(false)
    shownAt.current = Date.now()
    setPhase({ kind: 'question', item })
    window.scrollTo({ top: 0 })
  }, [])

  const loadNext = useCallback(
    async (opts: { learnAhead?: boolean; ignoreLimits?: boolean } = {}) => {
      try {
        const q = await api.queue({
          ...specToParams(spec),
          session_id: sessionId,
          exclude: lastItem.current,
          learn_ahead: opts.learnAhead || undefined,
          ignore_limits: (opts.ignoreLimits ?? ignoreLimits) || undefined,
        })
        setCounts(q.counts)
        setLimitReached(q.limit_reached)
        if (q.item) showItem(q.item)
        else if (q.waiting_until) setPhase({ kind: 'waiting', until: q.waiting_until })
        else if (q.limit_reached) setPhase({ kind: 'limit' })
        else setPhase({ kind: 'done' })
      } catch (e) {
        setPhase({ kind: 'error', message: (e as Error).message })
      }
    },
    [spec, sessionId, ignoreLimits, showItem],
  )

  useEffect(() => {
    lastItem.current = undefined
    setReviewedCount(0)
    setPhase({ kind: 'loading' })
    loadNext()
  }, [spec, sessionId]) // eslint-disable-line react-hooks/exhaustive-deps

  // waiting for a learning card: poll again when it becomes due
  useEffect(() => {
    if (phase.kind !== 'waiting') return
    const ms = Math.max(1000, new Date(phase.until).getTime() - Date.now() + 500)
    const t = setTimeout(() => loadNext(), Math.min(ms, 2 ** 31 - 1))
    return () => clearTimeout(t)
  }, [phase, loadNext])

  const elapsed = () => Date.now() - shownAt.current

  const gradeSelf = async (rating: number) => {
    if (phase.kind !== 'revealed' || busy) return
    setBusy(true)
    try {
      await api.review({ item_id: phase.item.item_id, mode: spec.mode, session_id: sessionId, rating, duration_ms: elapsed() })
      lastItem.current = phase.item.item_id
      setReviewedCount((n) => n + 1)
      await loadNext()
    } catch (e) {
      toast((e as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  const submitAuto = async (answer: boolean | number[]) => {
    if (phase.kind !== 'question' || busy) return
    setBusy(true)
    durationOfGraded.current = elapsed()
    try {
      const result = await api.review({
        item_id: phase.item.item_id,
        mode: spec.mode,
        session_id: sessionId,
        answer,
        guessed,
        too_easy: tooEasy,
        duration_ms: durationOfGraded.current,
      })
      lastItem.current = phase.item.item_id
      setReviewedCount((n) => n + 1)
      setPhase({ kind: 'graded', item: phase.item, result, answer })
    } catch (e) {
      toast((e as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  /** After a correct auto-graded answer: change Good ↔ Hard (guessed) ↔ Easy (too easy) by undo + re-review. */
  const regrade = async (target: 'hard' | 'good' | 'easy') => {
    if (phase.kind !== 'graded' || !phase.result.correct || busy) return
    const current = phase.result.rating === 2 ? 'hard' : phase.result.rating === 4 ? 'easy' : 'good'
    if (current === target) return
    setBusy(true)
    try {
      await api.undo(sessionId)
      const result = await api.review({
        item_id: phase.item.item_id,
        mode: spec.mode,
        session_id: sessionId,
        answer: phase.answer,
        guessed: target === 'hard',
        too_easy: target === 'easy',
        duration_ms: durationOfGraded.current,
      })
      setGuessed(target === 'hard')
      setTooEasy(target === 'easy')
      setPhase({ ...phase, result })
    } catch (e) {
      toast((e as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  const undo = async () => {
    if (busy) return
    setBusy(true)
    try {
      const u = await api.undo(sessionId)
      const item = await api.item(u.item_id)
      setReviewedCount((n) => Math.max(0, n - 1))
      lastItem.current = undefined
      showItem(item)
      toast('Last review undone')
    } catch (e) {
      toast(e instanceof ApiError && e.status === 404 ? 'Nothing to undo in this session' : (e as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  const reveal = () => phase.kind === 'question' && !isAuto(phase.item) && setPhase({ kind: 'revealed', item: phase.item })
  const end = () => setPhase({ kind: 'done' })
  const cont = () => {
    setPhase({ kind: 'loading' })
    loadNext()
  }

  const item = 'item' in phase ? phase.item : null
  const order = useMemo(
    () => (item?.choices ? choiceOrder(item.choices.length, item.shuffle, item.item_id + sessionId) : []),
    [item, sessionId],
  )

  const toggleChoice = (orig: number) => {
    if (!item) return
    setSelected((sel) => (item.multi ? (sel.includes(orig) ? sel.filter((x) => x !== orig) : [...sel, orig]) : [orig]))
  }

  useKeys((e) => {
    const action = reviewKeyAction(e.key, {
      phase: phase.kind,
      cardType: item?.type,
      nChoices: order.length,
      hasSelection: selected.length > 0,
      rating: phase.kind === 'graded' ? phase.result.rating : undefined,
      correct: phase.kind === 'graded' ? phase.result.correct : undefined,
    })
    if (!action) return
    if (e.key === ' ' || e.key === 'Enter') e.preventDefault()
    switch (action.type) {
      case 'help':
        return setSheet('help')
      case 'end':
        return phase.kind === 'done' ? navigate('/') : end()
      case 'undo':
        return undo()
      case 'source':
        return setSheet('source')
      case 'report':
        return setSheet('report')
      case 'reveal':
        return reveal()
      case 'grade':
        return gradeSelf(action.rating)
      case 'toggleGuessed':
        return setGuessed((g) => !g)
      case 'toggleTooEasy':
        return setTooEasy((t) => !t)
      case 'answerTf':
        return submitAuto(action.value)
      case 'selectChoice':
        return toggleChoice(order[action.position])
      case 'check':
        return submitAuto(selected)
      case 'continue':
        return cont()
      case 'regrade':
        return regrade(action.target)
      case 'learnAhead':
        return loadNext({ learnAhead: true })
    }
  }, sheet === null && !busy)

  // swipe on a revealed self-graded card: left = Again, right = Good (opt-in setting)
  const touch = useRef<{ x: number; y: number } | null>(null)
  const swipeOn = settings?.swipe && phase.kind === 'revealed'
  const onTouchStart = (e: React.TouchEvent) => {
    if (swipeOn) touch.current = { x: e.touches[0].clientX, y: e.touches[0].clientY }
  }
  const onTouchEnd = (e: React.TouchEvent) => {
    const t0 = touch.current
    touch.current = null
    if (!swipeOn || !t0) return
    const dx = e.changedTouches[0].clientX - t0.x
    const dy = e.changedTouches[0].clientY - t0.y
    if (Math.abs(dx) > 90 && Math.abs(dx) > 2 * Math.abs(dy)) gradeSelf(dx < 0 ? 1 : 3)
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <ReviewHeader
        title={describeSpec(spec)}
        counts={counts}
        item={item}
        reviewed={reviewedCount}
        onEnd={phase.kind === 'done' ? () => navigate('/') : end}
        onUndo={undo}
        onHelp={() => setSheet('help')}
        onSource={() => setSheet('source')}
        onReport={() => setSheet('report')}
      />

      <main className="px-safe mx-auto w-full max-w-3xl flex-1 pt-4 pb-56">
        {phase.kind === 'loading' && <Spinner />}
        {phase.kind === 'error' && <ErrorBox message={phase.message} onRetry={cont} />}
        {phase.kind === 'waiting' && (
          <WaitingCard until={phase.until} onContinue={() => loadNext({ learnAhead: true })} onEnd={end} />
        )}
        {phase.kind === 'limit' && (
          <CenterCard title="Daily review limit reached">
            <p className="text-slate-600 dark:text-slate-300">
              You reached today's review cap ({settings?.max_reviews_per_day}). More reviews are due.
            </p>
            <div className="mt-5 flex flex-wrap justify-center gap-2">
              <Button
                variant="primary"
                onClick={() => {
                  setIgnoreLimits(true)
                  loadNext({ ignoreLimits: true })
                }}
              >
                Review anyway
              </Button>
              <Button onClick={end}>End session</Button>
            </div>
          </CenterCard>
        )}
        {phase.kind === 'done' && <Summary sessionId={sessionId} limitReached={limitReached} onMore={cont} />}

        {item && (
          <article
            onTouchStart={onTouchStart}
            onTouchEnd={onTouchEnd}
            onClick={(e) => {
              if (phase.kind === 'question' && !isAuto(item) && !(e.target as HTMLElement).closest('button,a')) reveal()
            }}
            className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-7 dark:bg-slate-900 dark:ring-slate-800"
          >
            <CardHeader view={item} />
            <div className="mt-4 text-[1.05rem]">
              <Markdown>{item.type === 'cloze' && phase.kind === 'revealed' ? item.back ?? item.front : item.front}</Markdown>
            </div>
            <CardImages images={item.images} />

            {item.type === 'mcq' && item.choices && (
              <ChoiceList
                choices={item.choices}
                order={order}
                selected={phase.kind === 'graded' && Array.isArray(phase.answer) ? phase.answer : selected}
                onToggle={phase.kind === 'question' ? toggleChoice : undefined}
                correct={phase.kind === 'graded' ? (phase.result.correct_answer as number[]) : undefined}
                multi={item.multi}
              />
            )}

            {phase.kind === 'revealed' && item.type === 'basic' && (
              <div className="mt-5 border-t-2 border-dashed border-slate-200 pt-5 dark:border-slate-700">
                <Markdown className="text-[1.05rem]">{item.back ?? ''}</Markdown>
              </div>
            )}
            {phase.kind === 'revealed' && (
              <>
                <TrapNote trap={item.trap} />
                <Explanation text={item.explanation} />
              </>
            )}
            {phase.kind === 'graded' && <GradedBlock item={item} result={phase.result} answer={phase.answer} />}
            {phase.kind === 'question' && !isAuto(item) && (
              <p className="mt-6 text-center text-sm text-slate-400 sm:hidden">Tap the card to reveal</p>
            )}
          </article>
        )}
      </main>

      {item && (
        <footer className="pb-safe fixed inset-x-0 bottom-0 z-20 border-t border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
          <div className="px-safe mx-auto max-w-3xl pt-3">
            {phase.kind === 'question' && !isAuto(item) && (
              <Button variant="primary" className="h-14 w-full text-lg" onClick={reveal}>
                Show answer <Kbd>Space</Kbd>
              </Button>
            )}
            {phase.kind === 'revealed' && (
              <div className="grid grid-cols-4 gap-2">
                {GRADES.map((g) => (
                  <button
                    key={g.r}
                    type="button"
                    disabled={busy}
                    onClick={() => gradeSelf(g.r)}
                    className={`flex h-16 flex-col items-center justify-center rounded-xl font-semibold transition-colors disabled:opacity-60 ${g.cls}`}
                  >
                    <span>{g.label}</span>
                    <span className="text-xs font-normal opacity-90">
                      {formatInterval(item.previews[String(g.r) as '1']) } <Kbd>{g.r}</Kbd>
                    </span>
                  </button>
                ))}
              </div>
            )}
            {phase.kind === 'question' && isAuto(item) && (
              <div className="space-y-2.5">
                <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
                  <FlagToggle on={guessed} onClick={() => setGuessed((g) => !g)} label="I guessed" k="G" />
                  {item.type === 'tf' && (
                    <FlagToggle on={tooEasy} onClick={() => setTooEasy((t) => !t)} label="Too easy" k="E" />
                  )}
                </div>
                {item.type === 'tf' ? (
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="secondary" className="h-14 text-lg" disabled={busy} onClick={() => submitAuto(true)}>
                      True <Kbd>T</Kbd>
                    </Button>
                    <Button variant="secondary" className="h-14 text-lg" disabled={busy} onClick={() => submitAuto(false)}>
                      False <Kbd>F</Kbd>
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    className="h-14 w-full text-lg"
                    disabled={!selected.length || busy}
                    onClick={() => submitAuto(selected)}
                  >
                    Check <Kbd>Enter</Kbd>
                  </Button>
                )}
              </div>
            )}
            {phase.kind === 'graded' && (
              <div className="space-y-2.5">
                {phase.result.correct && (
                  <div className="flex justify-center">
                    <Segmented
                      ariaLabel="Adjust rating"
                      value={phase.result.rating === 2 ? 'hard' : phase.result.rating === 4 ? 'easy' : 'good'}
                      onChange={(v) => regrade(v)}
                      options={[
                        { value: 'hard', label: 'Guessed' },
                        { value: 'good', label: 'Good' },
                        { value: 'easy', label: 'Too easy' },
                      ]}
                    />
                  </div>
                )}
                <Button variant="primary" className="h-14 w-full text-lg" disabled={busy} onClick={cont}>
                  Continue <Kbd>Enter</Kbd>
                </Button>
              </div>
            )}
          </div>
        </footer>
      )}

      {item && (
        <>
          <SourceViewer sources={item.sources} open={sheet === 'source'} onClose={() => setSheet(null)} />
          <ReportDialog
            open={sheet === 'report'}
            onClose={() => setSheet(null)}
            cardId={item.card_id}
            itemId={item.item_id}
          />
        </>
      )}
      <ShortcutHelp open={sheet === 'help'} onClose={() => setSheet(null)} />
    </div>
  )
}

function FlagToggle({ on, onClick, label, k }: { on: boolean; onClick: () => void; label: string; k: string }) {
  return (
    <button
      type="button"
      aria-pressed={on}
      onClick={onClick}
      className={`min-h-9 rounded-full px-3 font-medium ${
        on ? 'bg-amber-500 text-white' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
      }`}
    >
      {on ? '✓ ' : ''}
      {label} <Kbd>{k}</Kbd>
    </button>
  )
}

function GradedBlock({ item, result, answer }: { item: ItemView; result: ReviewResult; answer: boolean | number[] }) {
  return (
    <div className="mt-5">
      <div
        role="status"
        className={`rounded-xl px-4 py-3 ${
          result.correct
            ? 'bg-emerald-50 text-emerald-900 dark:bg-emerald-500/15 dark:text-emerald-200'
            : 'bg-red-50 text-red-900 dark:bg-red-500/15 dark:text-red-200'
        }`}
      >
        <div className="flex items-center gap-2 font-semibold">
          <span className="text-xl" aria-hidden="true">
            {result.correct ? '✓' : '✗'}
          </span>
          {result.correct ? 'Correct' : 'Incorrect'}
          {item.type === 'tf' && (
            <span className="font-normal">
              {result.correct
                ? ` — ${formatAnswer(answer, null)}`
                : ` — the answer is ${formatAnswer(result.correct_answer, null)}`}
            </span>
          )}
        </div>
        <div className="mt-0.5 text-sm opacity-80">Next review in {formatInterval(result.interval_seconds)}</div>
      </div>
      {item.origin === 'exam_style' && (
        <p className="mt-2 text-sm text-violet-700 dark:text-violet-300">
          Unofficial question written for revision — not from a past exam.
        </p>
      )}
      <TrapNote trap={result.trap} />
      <Explanation text={result.explanation} />
    </div>
  )
}

function ReviewHeader({
  title,
  counts,
  item,
  reviewed,
  onEnd,
  onUndo,
  onHelp,
  onSource,
  onReport,
}: {
  title: string
  counts: QueueResponse['counts'] | null
  item: ItemView | null
  reviewed: number
  onEnd: () => void
  onUndo: () => void
  onHelp: () => void
  onSource: () => void
  onReport: () => void
}) {
  const iconBtn =
    'inline-flex h-11 min-w-11 items-center justify-center gap-1 rounded-xl px-2 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-40 dark:text-slate-300 dark:hover:bg-slate-800'
  return (
    <header className="pt-safe sticky top-0 z-20 border-b border-slate-200 bg-slate-50/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
      <div className="px-safe mx-auto flex max-w-3xl items-center gap-1 py-1.5">
        <button type="button" className={iconBtn} onClick={onEnd} aria-label="End session" title="End session (Esc)">
          ✕
        </button>
        <div className="min-w-0 flex-1 px-1">
          <div className="truncate text-sm font-semibold">{title}</div>
          <Counts counts={counts} reviewed={reviewed} />
        </div>
        <button type="button" className={iconBtn} onClick={onSource} disabled={!item} title="Source (S)">
          <span aria-hidden="true">📄</span>
          <span className="hidden sm:inline">Source</span>
        </button>
        <button type="button" className={iconBtn} onClick={onReport} disabled={!item} title="Flag this card (R)">
          <span aria-hidden="true">⚑</span>
          <span className="hidden sm:inline">Flag</span>
        </button>
        <button type="button" className={iconBtn} onClick={onUndo} disabled={reviewed === 0} title="Undo (U)">
          <span aria-hidden="true">↶</span>
          <span className="hidden sm:inline">Undo</span>
        </button>
        <button type="button" className={`${iconBtn} hidden sm:inline-flex`} onClick={onHelp} title="Shortcuts (?)">
          ?
        </button>
      </div>
    </header>
  )
}

function Counts({ counts, reviewed }: { counts: QueueResponse['counts'] | null; reviewed: number }) {
  if (!counts) return <div className="h-5" />
  if ('remaining' in counts) {
    const c = counts as DrillCounts
    return (
      <div className="text-xs text-slate-500 tabular-nums dark:text-slate-400" title={`${reviewed} reviews this session`}>
        {c.done}/{c.total} done
      </div>
    )
  }
  const c = counts as StudyCounts
  return (
    <div className="flex gap-3 text-xs font-semibold tabular-nums">
      <span className="text-sky-600 dark:text-sky-400" title="New">
        {c.new} new
      </span>
      <span className="text-orange-600 dark:text-orange-400" title="Learning">
        {c.learning} learning
      </span>
      <span className="text-emerald-600 dark:text-emerald-400" title="Due reviews">
        {c.review} due
      </span>
    </div>
  )
}

function CenterCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mx-auto mt-10 max-w-md rounded-3xl bg-white p-6 text-center shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:ring-slate-800">
      <h2 className="mb-2 text-xl font-semibold">{title}</h2>
      {children}
    </div>
  )
}

function WaitingCard({ until, onContinue, onEnd }: { until: string; onContinue: () => void; onEnd: () => void }) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [])
  const s = Math.max(0, Math.round((new Date(until).getTime() - now) / 1000))
  return (
    <CenterCard title="Nothing else right now">
      <p className="text-slate-600 dark:text-slate-300">
        A learning card comes back in{' '}
        <span className="font-semibold tabular-nums">
          {Math.floor(s / 60)}:{String(s % 60).padStart(2, '0')}
        </span>
        .
      </p>
      <div className="mt-5 flex flex-wrap justify-center gap-2">
        <Button variant="primary" onClick={onContinue}>
          Show it now <Kbd>Enter</Kbd>
        </Button>
        <Button onClick={onEnd}>End session</Button>
      </div>
    </CenterCard>
  )
}

function Summary({ sessionId, limitReached, onMore }: { sessionId: string; limitReached: boolean; onMore: () => void }) {
  const [s, setS] = useState<SessionSummary | null>(null)
  const [err, setErr] = useState<string | null>(null)
  useEffect(() => {
    api.summary(sessionId).then(setS).catch((e: Error) => setErr(e.message))
  }, [sessionId])
  if (err) return <ErrorBox message={err} />
  if (!s) return <Spinner />
  return (
    <CenterCard title={s.reviews ? 'Session complete' : 'All caught up'}>
      {s.reviews === 0 ? (
        <p className="text-slate-600 dark:text-slate-300">
          {limitReached ? 'Daily limits reached.' : 'Nothing is due for this selection. Come back later!'}
        </p>
      ) : (
        <>
          <dl className="mt-3 grid grid-cols-3 gap-3 text-center">
            <Stat label="reviews" value={String(s.reviews)} />
            <Stat label="time" value={formatDuration(s.duration_ms)} />
            <Stat
              label="auto-graded"
              value={s.auto_graded ? pct(s.auto_correct / s.auto_graded) : '—'}
              hint={s.auto_graded ? `${s.auto_correct}/${s.auto_graded}` : undefined}
            />
          </dl>
          <div className="mt-4 flex justify-center gap-3 text-sm tabular-nums">
            {GRADES.map((g) => (
              <span key={g.r} className="text-slate-600 dark:text-slate-300">
                {g.label} <b>{s.ratings[String(g.r) as '1']}</b>
              </span>
            ))}
          </div>
          {s.again_items.length > 0 && (
            <div className="mt-5 text-left">
              <h3 className="mb-1 text-sm font-semibold">To come back to</h3>
              <ul className="space-y-1 text-sm">
                {[...new Set(s.again_items.map((i) => i.split('::')[0]))].map((id) => (
                  <li key={id}>
                    <Link className="text-indigo-600 hover:underline dark:text-indigo-400" to={`/browse/${id}`}>
                      {id}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <Link to="/" className="inline-flex min-h-11 items-center rounded-xl bg-indigo-600 px-4 font-medium text-white">
          Home
        </Link>
        <Button onClick={onMore}>Check again</Button>
      </div>
    </CenterCard>
  )
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-3 dark:bg-slate-800/60">
      <dd className="text-xl font-semibold tabular-nums">{value}</dd>
      <dt className="text-xs text-slate-500 dark:text-slate-400">
        {label}
        {hint ? ` · ${hint}` : ''}
      </dt>
    </div>
  )
}
