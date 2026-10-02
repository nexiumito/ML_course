import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { useApp } from '../AppContext'
import { CardHeader, CardImages, ChoiceList, Explanation, TrapNote } from '../components/CardParts'
import { Markdown } from '../components/Markdown'
import { formatAnswer } from '../lib/text'
import { ReportDialog } from '../components/ReportDialog'
import { SourceViewer } from '../components/SourceViewer'
import { Button, ErrorBox, Panel, SectionTitle, Spinner } from '../components/ui'
import { useAsync } from '../hooks/useAsync'
import { pct, relativeTime, shortDate } from '../lib/format'

const RATING = ['', 'Again', 'Hard', 'Good', 'Easy']

export default function CardPage() {
  const { id = '' } = useParams()
  const { toast } = useApp()
  const { data, error, reload } = useAsync(() => api.card(id), [id])
  const [sources, setSources] = useState(false)
  const [report, setReport] = useState<string | null>(null)

  if (error) return <ErrorBox message={error} onRetry={reload} />
  if (!data) return <Spinner />
  const c = data.card

  const suspend = async (itemId: string, on: boolean) => {
    try {
      await api.suspend(itemId, on)
      toast(on ? 'Suspended' : 'Unsuspended')
      reload()
    } catch (e) {
      toast((e as Error).message, 'error')
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <Link to="/browse" className="text-sm text-indigo-600 hover:underline dark:text-indigo-400">
          ← Browse
        </Link>
        <div className="flex gap-2">
          <Button onClick={() => setSources(true)}>📄 Source</Button>
          <Button onClick={() => setReport(data.items[0]?.view.item_id ?? null)}>⚑ Flag</Button>
        </div>
      </div>

      {data.items.map(({ view, state, history }) => (
        <Panel key={view.item_id} className="p-5">
          <CardHeader view={view} />
          {view.cloze_index !== null && (
            <p className="mt-2 text-xs font-semibold text-slate-500">Cloze c{view.cloze_index}</p>
          )}
          <div className="mt-3">
            <Markdown>{c.type === 'cloze' ? (view.back ?? '') : view.front}</Markdown>
          </div>
          <CardImages images={view.images} />
          {c.type === 'basic' && (
            <div className="mt-4 border-t-2 border-dashed border-slate-200 pt-4 dark:border-slate-700">
              <Markdown>{c.back ?? ''}</Markdown>
            </div>
          )}
          {c.type === 'mcq' && c.choices && (
            <ChoiceList
              choices={c.choices}
              order={c.choices.map((_, i) => i)}
              selected={(c.answer as number[]) ?? []}
              correct={c.answer as number[]}
              multi={c.multi}
            />
          )}
          {c.type === 'tf' && (
            <p className="mt-4 font-semibold">
              Answer: <span className="text-emerald-700 dark:text-emerald-400">{formatAnswer(c.answer, null)}</span>
            </p>
          )}
          <TrapNote trap={c.trap} />
          <Explanation text={c.explanation} />

          <div className="mt-5 grid grid-cols-2 gap-x-4 gap-y-1 border-t border-slate-100 pt-4 text-sm sm:grid-cols-4 dark:border-slate-800">
            <Field label="State" value={state.suspended ? `${state.state} (suspended)` : state.state} />
            <Field label="Due" value={state.state === 'new' ? '—' : relativeTime(state.due_utc)} />
            <Field label="Retrievability" value={pct(state.retrievability)} />
            <Field label="Stability" value={state.stability ? `${state.stability.toFixed(1)} d` : '—'} />
            <Field label="Difficulty" value={state.difficulty ? state.difficulty.toFixed(1) : '—'} />
            <Field label="Reviews" value={String(state.reps)} />
            <Field label="Lapses" value={String(state.lapses)} />
            <Field label="Last review" value={shortDate(state.last_review_utc)} />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button onClick={() => suspend(view.item_id, !state.suspended)}>
              {state.suspended ? 'Unsuspend' : 'Suspend'}
            </Button>
            {data.items.length > 1 && <Button onClick={() => setReport(view.item_id)}>⚑ Flag this cloze</Button>}
          </div>
          {history.length > 0 && (
            <details className="mt-3 text-sm">
              <summary className="cursor-pointer text-slate-500">History ({history.length})</summary>
              <ul className="mt-2 space-y-1 tabular-nums">
                {history.map((h) => (
                  <li key={h.id} className="text-slate-600 dark:text-slate-300">
                    {shortDate(h.reviewed_utc)} · {RATING[h.rating]}
                    {h.auto_graded ? ` · ${h.correct ? '✓' : '✗'}${h.guessed ? ' (guessed)' : ''}` : ''} · {h.mode}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </Panel>
      ))}

      <Panel>
        <SectionTitle>Card</SectionTitle>
        <dl className="grid grid-cols-1 gap-1 text-sm sm:grid-cols-2">
          <Field label="Id" value={c.id} mono />
          <Field label="File" value={`${data.file} #${data.position}`} mono />
          <Field label="Added" value={c.added} />
          <Field label="Active" value={data.active ? 'yes' : 'no (a lecture is inactive)'} />
        </dl>
        <ul className="mt-3 space-y-1 text-sm">
          {c.sources.map((s, i) => (
            <li key={i}>
              {s.pdf ? (
                <a className="text-indigo-600 hover:underline dark:text-indigo-400" href={s.file_url} target="_blank" rel="noreferrer">
                  {s.label}
                </a>
              ) : (
                s.label
              )}{' '}
              <span className="text-slate-400">{s.pdf ?? s.path}</span>
            </li>
          ))}
        </ul>
      </Panel>

      <SourceViewer sources={c.sources} open={sources} onClose={() => setSources(false)} />
      <ReportDialog open={report !== null} onClose={() => setReport(null)} cardId={c.id} itemId={report} />
    </div>
  )
}

function Field({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className={`truncate ${mono ? 'font-mono text-xs' : 'tabular-nums'}`}>{value}</dd>
    </div>
  )
}
