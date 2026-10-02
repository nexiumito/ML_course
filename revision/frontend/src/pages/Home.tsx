import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Mastery } from '../api/types'
import { useApp } from '../AppContext'
import { ProgressLegend, ProgressStack } from '../components/charts'
import { PageTitle } from '../components/Layout'
import { Button, Chip, ErrorBox, Panel, SectionTitle, Spinner, Toggle } from '../components/ui'
import { useAsync } from '../hooks/useAsync'
import { emptySpec, specToSearch, type StudySpec } from '../lib/session'

export default function Home() {
  const { meta, settings } = useApp()
  const navigate = useNavigate()
  const ov = useAsync(() => api.overview(), [])
  const lec = useAsync(() => api.byLecture(), [])
  const [spec, setSpec] = useState<StudySpec>(emptySpec())
  const [drillN, setDrillN] = useState<number | null>(null)

  const go = (s: StudySpec) => navigate(`/review?${specToSearch(s)}`)
  const toggle = <K extends 'weeks' | 'lectures' | 'themes' | 'origins' | 'types'>(key: K, v: StudySpec[K][number]) =>
    setSpec((s) => {
      const arr = s[key] as (typeof v)[]
      return { ...s, [key]: arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v] }
    })

  const activeLectures = meta?.lectures.filter((l) => l.active) ?? []
  const weekRows = useMemo(() => groupByWeek(lec.data?.lectures ?? []), [lec.data])
  const filtered =
    spec.weeks.length + spec.lectures.length + spec.themes.length + spec.origins.length + spec.types.length > 0 ||
    spec.core

  if (ov.error) return <ErrorBox message={ov.error} onRetry={ov.reload} />
  const o = ov.data
  const due = o?.due
  const total = due ? due.new + due.learning + due.review : 0

  return (
    <div className="space-y-5">
      <PageTitle
        right={
          o?.days_to_exam != null ? (
            <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-900 dark:bg-amber-500/20 dark:text-amber-200">
              Exam in {o.days_to_exam} d
            </span>
          ) : undefined
        }
      >
        <span className="sm:hidden">CS-433 Review</span>
        <span className="hidden sm:inline">Today</span>
      </PageTitle>

      <Panel className="p-5 sm:p-6">
        {!o ? (
          <Spinner />
        ) : (
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">Due now</p>
              <p className="text-5xl font-semibold tracking-tight">{total}</p>
              <div className="mt-2 flex gap-4 text-sm font-semibold">
                <span className="text-sky-600 dark:text-sky-400">{due!.new} new</span>
                <span className="text-orange-600 dark:text-orange-400">{due!.learning} learning</span>
                <span className="text-emerald-600 dark:text-emerald-400">{due!.review} review</span>
              </div>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                Today: {o.today.reviews} reviews · {o.today.minutes} min · streak {o.streak} d
                {o.today.auto_graded > 0 && ` · exam questions ${o.today.auto_correct}/${o.today.auto_graded}`}
              </p>
            </div>
            <Button variant="primary" className="h-14 px-8 text-lg sm:min-w-56" onClick={() => go(emptySpec())}>
              {total ? 'Study now' : 'All caught up ✓'}
            </Button>
          </div>
        )}
      </Panel>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <QuickTile
          title="Exam mode"
          text="Due T/F & MCQ (official + unofficial)"
          onClick={() => go(emptySpec('exam'))}
        />
        <QuickTile
          title="Exam drill"
          text="All unlocked exam questions, random"
          onClick={() => go({ ...emptySpec('exam'), includeNotDue: true })}
        />
        <QuickTile
          title="Weak points"
          text={`Top ${settings?.weak_points_n ?? 30} weakest items`}
          onClick={() => go(emptySpec('weak'))}
        />
        <QuickTile title="Essentials only" text="Due core cards" onClick={() => go({ ...emptySpec(), core: true })} />
      </div>

      <Panel>
        <SectionTitle
          right={
            filtered ? (
              <button type="button" className="text-sm text-indigo-600 dark:text-indigo-400" onClick={() => setSpec(emptySpec())}>
                Clear
              </button>
            ) : undefined
          }
        >
          Custom selection
        </SectionTitle>
        {!meta ? (
          <Spinner />
        ) : (
          <div className="space-y-4">
            <FilterRow label="Weeks">
              {meta.weeks.map((w) => (
                <Chip key={w} active={spec.weeks.includes(w)} onClick={() => toggle('weeks', w)}>
                  Week {w}
                </Chip>
              ))}
            </FilterRow>
            <FilterRow label="Lectures">
              {activeLectures.map((l) => (
                <Chip key={l.id} active={spec.lectures.includes(l.id)} onClick={() => toggle('lectures', l.id)} title={l.title}>
                  {l.id} <span className="hidden opacity-75 sm:inline">· {l.title}</span>
                </Chip>
              ))}
            </FilterRow>
            <FilterRow label="Themes">
              {meta.themes.map((t) => (
                <Chip key={t.id} active={spec.themes.includes(t.id)} onClick={() => toggle('themes', t.id)}>
                  {t.label}
                </Chip>
              ))}
            </FilterRow>
            <FilterRow label="Origin">
              {(
                [
                  ['concept', 'Concept'],
                  ['exam_official', 'Official exam'],
                  ['exam_style', 'Unofficial exam-style'],
                ] as const
              ).map(([v, l]) => (
                <Chip key={v} active={spec.origins.includes(v)} onClick={() => toggle('origins', v)}>
                  {l}
                </Chip>
              ))}
            </FilterRow>
            <FilterRow label="Type">
              {(
                [
                  ['basic', 'Q → A'],
                  ['cloze', 'Cloze'],
                  ['tf', 'True/False'],
                  ['mcq', 'Multiple choice'],
                ] as const
              ).map(([v, l]) => (
                <Chip key={v} active={spec.types.includes(v)} onClick={() => toggle('types', v)}>
                  {l}
                </Chip>
              ))}
            </FilterRow>
            <Toggle
              checked={spec.core}
              onChange={(core) => setSpec((s) => ({ ...s, core }))}
              label="Essentials only"
              hint="Only cards marked core (exam-essential)"
            />
            <div className="flex flex-wrap items-center gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
              <Button variant="primary" onClick={() => go({ ...spec, mode: 'study' })}>
                Study due cards
              </Button>
              <Button onClick={() => go({ ...spec, mode: 'exam', includeNotDue: true })}>Drill exam questions</Button>
              <span className="inline-flex items-center gap-2">
                <Button onClick={() => go({ ...spec, mode: 'drill', limit: drillN ?? settings?.drill_n ?? 20 })}>
                  Drill random
                </Button>
                <label className="sr-only" htmlFor="drill-n">
                  Number of cards
                </label>
                <input
                  id="drill-n"
                  type="number"
                  min={1}
                  max={500}
                  value={drillN ?? settings?.drill_n ?? 20}
                  onChange={(e) => setDrillN(Math.max(1, Math.min(500, Number(e.target.value) || 1)))}
                  className="h-11 w-20 rounded-xl border border-slate-200 bg-white px-3 text-base tabular-nums dark:border-slate-700 dark:bg-slate-950"
                />
                <span className="text-sm text-slate-500">cards, ignoring due dates</span>
              </span>
            </div>
          </div>
        )}
      </Panel>

      <Panel>
        <SectionTitle right={<ProgressLegend />}>Progress by week</SectionTitle>
        {lec.error ? (
          <ErrorBox message={lec.error} onRetry={lec.reload} />
        ) : !lec.data ? (
          <Spinner />
        ) : (
          <div className="space-y-4">
            {weekRows.map((w) => (
              <div key={w.week}>
                <div className="mb-1.5 flex items-baseline justify-between text-sm">
                  <button
                    type="button"
                    className="font-medium hover:underline"
                    onClick={() => go({ ...emptySpec(), weeks: [w.week] })}
                  >
                    Week {w.week}
                    <span className="ml-2 font-normal text-slate-500 dark:text-slate-400">{w.lectures.join(', ')}</span>
                  </button>
                  <span className="text-slate-500 tabular-nums dark:text-slate-400">
                    {w.seen}/{w.items}
                  </span>
                </div>
                <ProgressStack total={w.items} seen={w.seen} mature={w.mature} label={`Week ${w.week}`} />
              </div>
            ))}
            {!weekRows.length && <p className="text-sm text-slate-500">No cards yet.</p>}
          </div>
        )}
        <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
          <Link to="/stats" className="text-indigo-600 hover:underline dark:text-indigo-400">
            More statistics →
          </Link>
        </p>
      </Panel>
    </div>
  )
}

function groupByWeek(rows: Mastery[]) {
  const map = new Map<number, { week: number; items: number; seen: number; mature: number; lectures: string[] }>()
  for (const r of rows) {
    if (!r.items || r.week === undefined) continue
    const w = map.get(r.week) ?? { week: r.week, items: 0, seen: 0, mature: 0, lectures: [] }
    w.items += r.items
    w.seen += r.seen
    w.mature += r.mature
    w.lectures.push(r.key)
    map.set(r.week, w)
  }
  return [...map.values()].sort((a, b) => a.week - b.week)
}

function QuickTile({ title, text, onClick }: { title: string; text: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex flex-col items-start justify-start rounded-2xl bg-white p-4 text-left shadow-sm ring-1 ring-slate-200 transition hover:ring-indigo-400 active:scale-[0.99] dark:bg-slate-900 dark:ring-slate-800 dark:hover:ring-indigo-500"
    >
      <span className="block font-semibold">{title}</span>
      <span className="mt-1 block text-sm text-slate-500 dark:text-slate-400">{text}</span>
    </button>
  )
}

function FilterRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1.5 text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">{label}</div>
      <div className="flex flex-wrap gap-2">{children}</div>
    </div>
  )
}
