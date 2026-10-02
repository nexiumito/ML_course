import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Mastery } from '../api/types'
import { useApp } from '../AppContext'
import { CalendarHeatmap, ColumnChart, DataTable, Meter, ProgressLegend, ProgressStack } from '../components/charts'
import { PageTitle } from '../components/Layout'
import { ErrorBox, Panel, SectionTitle, Spinner } from '../components/ui'
import { useAsync } from '../hooks/useAsync'
import { pct } from '../lib/format'

const shortDay = (iso: string) =>
  new Date(iso + 'T12:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })

export default function Stats() {
  const { themeLabel } = useApp()
  const ov = useAsync(() => api.overview(), [])
  const cal = useAsync(() => api.calendar(182), [])
  const fc = useAsync(() => api.forecast(30), [])
  const lec = useAsync(() => api.byLecture(), [])
  const th = useAsync(() => api.byTheme(), [])
  const ex = useAsync(() => api.examStats(), [])
  const weak = useAsync(() => api.weakest(20), [])

  const err = ov.error || cal.error || fc.error || lec.error || th.error || ex.error || weak.error
  if (err) return <ErrorBox message={err} onRetry={() => [ov, cal, fc, lec, th, ex, weak].forEach((x) => x.reload())} />
  if (!ov.data || !cal.data || !fc.data || !lec.data || !th.data || !ex.data || !weak.data) return <Spinner />

  const o = ov.data
  const r30 = cal.data.retention['30d']
  const seen = o.items - o.by_state.new
  const last30 = cal.data.days.slice(-30)

  return (
    <div className="space-y-5">
      <PageTitle>Statistics</PageTitle>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Tile label="Reviews today" value={String(o.today.reviews)} sub={`${o.today.minutes} min`} />
        <Tile label="Streak" value={`${o.streak} d`} />
        <Tile label="True retention (30 d)" value={pct(r30.all.retention)} sub={`${r30.all.n} reviews`} />
        <Tile
          label={o.days_to_exam != null ? 'Days to exam' : 'Items seen'}
          value={o.days_to_exam != null ? String(o.days_to_exam) : `${seen}/${o.items}`}
          sub={o.days_to_exam != null ? `${seen}/${o.items} items seen` : undefined}
        />
      </div>

      <Panel>
        <SectionTitle>Reviews — last 30 days</SectionTitle>
        <ColumnChart data={last30.map((d) => ({ key: d.day, label: shortDay(d.day), value: d.reviews }))} unit="reviews" />
      </Panel>

      <Panel>
        <SectionTitle>Activity — last 6 months</SectionTitle>
        <CalendarHeatmap days={cal.data.days} />
      </Panel>

      <Panel>
        <SectionTitle>Due forecast — next 30 days</SectionTitle>
        <ColumnChart data={fc.data.days.map((d) => ({ key: d.day, label: shortDay(d.day), value: d.due }))} unit="due" />
      </Panel>

      <div className="grid gap-5 lg:grid-cols-2">
        <Panel>
          <SectionTitle>Items by state</SectionTitle>
          <dl className="grid grid-cols-3 gap-2 text-center">
            {(['new', 'learning', 'review', 'relearning'] as const).map((s) => (
              <div key={s} className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/60">
                <dd className="text-xl font-semibold">{o.by_state[s]}</dd>
                <dt className="text-xs text-slate-500 dark:text-slate-400">{s}</dt>
              </div>
            ))}
            <div className="rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/60">
              <dd className="text-xl font-semibold">{o.suspended}</dd>
              <dt className="text-xs text-slate-500 dark:text-slate-400">suspended</dt>
            </div>
          </dl>
        </Panel>
        <Panel>
          <SectionTitle>True retention</SectionTitle>
          <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
            Share of reviews of mature-track items answered without “Again”. Target ≈ desired retention.
          </p>
          <table className="w-full text-sm tabular-nums">
            <thead>
              <tr className="text-left text-slate-500 dark:text-slate-400">
                <th className="py-1 font-medium" />
                <th className="py-1 font-medium">All</th>
                <th className="py-1 font-medium">Self-graded</th>
                <th className="py-1 font-medium">Auto-graded</th>
              </tr>
            </thead>
            <tbody>
              {(['7d', '30d'] as const).map((w) => (
                <tr key={w} className="border-t border-slate-100 dark:border-slate-800">
                  <td className="py-1.5 font-medium">{w}</td>
                  {(['all', 'self', 'auto'] as const).map((k) => (
                    <td key={k} className="py-1.5">
                      {pct(cal.data!.retention[w][k].retention)}{' '}
                      <span className="text-xs text-slate-400">({cal.data!.retention[w][k].n})</span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </div>

      <Panel>
        <SectionTitle right={<ProgressLegend />}>Mastery by lecture</SectionTitle>
        <MasteryTable rows={lec.data.lectures.filter((l) => l.items > 0)} name={(m) => `${m.key} · ${m.title}`} />
      </Panel>

      <Panel>
        <SectionTitle right={<ProgressLegend />}>Mastery by theme</SectionTitle>
        <MasteryTable rows={th.data.themes.filter((t) => t.items > 0)} name={(m) => m.label ?? m.key} />
      </Panel>

      <Panel>
        <SectionTitle>Exam questions</SectionTitle>
        {ex.data.by_origin.length === 0 ? (
          <p className="text-sm text-slate-500">No exam question answered yet.</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-3">
            <AccuracyList
              title="By origin"
              rows={ex.data.by_origin.map((r) => ({ ...r, name: r.key === 'exam_official' ? 'Official' : 'Unofficial' }))}
            />
            <AccuracyList title="By exam year" rows={ex.data.by_year.map((r) => ({ ...r, name: r.key }))} />
            <AccuracyList title="By theme" rows={ex.data.by_theme.map((r) => ({ ...r, name: themeLabel(r.key) }))} />
          </div>
        )}
      </Panel>

      <Panel>
        <SectionTitle>Weakest items</SectionTitle>
        {weak.data.items.length === 0 ? (
          <p className="text-sm text-slate-500">Nothing reviewed yet.</p>
        ) : (
          <ol className="space-y-1.5 text-sm">
            {weak.data.items.map((w) => (
              <li key={w.item_id} className="flex items-center gap-3">
                <span className="w-12 text-right text-slate-400 tabular-nums">{w.score.toFixed(1)}</span>
                <Link className="min-w-0 truncate font-mono text-xs text-indigo-600 hover:underline dark:text-indigo-400" to={`/browse/${w.card_id}`}>
                  {w.item_id}
                </Link>
                <span className="ml-auto shrink-0 text-xs text-slate-500 tabular-nums">
                  {w.lapses} lapses · R {pct(w.retrievability)}
                </span>
              </li>
            ))}
          </ol>
        )}
      </Panel>
    </div>
  )
}

function Tile({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:ring-slate-800">
      <div className="text-sm text-slate-500 dark:text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      {sub && <div className="text-xs text-slate-500 dark:text-slate-400">{sub}</div>}
    </div>
  )
}

function MasteryTable({ rows, name }: { rows: Mastery[]; name: (m: Mastery) => string }) {
  return (
    <div>
      <div className="space-y-3">
        {rows.map((m) => (
          <div key={m.key} className="grid grid-cols-1 gap-1 sm:grid-cols-[minmax(0,14rem)_1fr_10rem] sm:items-center sm:gap-4">
            <div className="truncate text-sm font-medium" title={name(m)}>
              {name(m)}
            </div>
            <ProgressStack total={m.items} seen={m.seen} mature={m.mature} label={name(m)} />
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <span className="shrink-0">mean R</span>
              <div className="flex-1">
                <Meter value={m.mean_retrievability} label={`${name(m)} mean retrievability`} />
              </div>
            </div>
          </div>
        ))}
      </div>
      <DataTable
        head={['Group', 'Items', 'Seen', 'Mature', 'Mean R', 'Lapses']}
        rows={rows.map((m) => [name(m), m.items, m.seen, m.mature, pct(m.mean_retrievability), m.lapses])}
      />
    </div>
  )
}

function AccuracyList({ title, rows }: { title: string; rows: { name: string; correct: number; n: number; accuracy: number }[] }) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold">{title}</h3>
      <ul className="space-y-2">
        {rows.map((r) => (
          <li key={r.name}>
            <div className="flex justify-between text-sm">
              <span className="truncate">{r.name}</span>
              <span className="text-slate-500 tabular-nums">
                {r.correct}/{r.n}
              </span>
            </div>
            <Meter value={r.accuracy} label={`${r.name} accuracy`} />
          </li>
        ))}
      </ul>
    </div>
  )
}
