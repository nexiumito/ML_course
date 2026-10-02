import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { CardSummary } from '../api/types'
import { useApp } from '../AppContext'
import { PageTitle } from '../components/Layout'
import { Chip, ErrorBox, OriginBadge, Panel, Spinner, Tag } from '../components/ui'
import { useAsync } from '../hooks/useAsync'
import { previewText } from '../lib/text'

const STATE_STYLE: Record<string, string> = {
  new: 'bg-sky-500',
  learning: 'bg-orange-500',
  relearning: 'bg-orange-500',
  review: 'bg-emerald-500',
}

export default function Browse() {
  const { meta } = useApp()
  const [sp, setSp] = useSearchParams()
  const [q, setQ] = useState(sp.get('q') ?? '')
  const lecture = sp.get('lecture') ?? ''
  const origin = sp.get('origin') ?? ''
  const type = sp.get('type') ?? ''

  useEffect(() => {
    const t = setTimeout(() => {
      const next = new URLSearchParams(sp)
      if (q) next.set('q', q)
      else next.delete('q')
      if (next.toString() !== sp.toString()) setSp(next, { replace: true })
    }, 250)
    return () => clearTimeout(t)
  }, [q]) // eslint-disable-line react-hooks/exhaustive-deps

  const query = sp.get('q') ?? ''
  const { data, error, loading, reload } = useAsync(
    () => api.cards({ q: query || undefined, lectures: lecture || undefined, origins: origin || undefined, types: type || undefined }),
    [query, lecture, origin, type],
  )

  const setParam = (k: string, v: string) => {
    const next = new URLSearchParams(sp)
    if (next.get(k) === v || !v) next.delete(k)
    else next.set(k, v)
    setSp(next, { replace: true })
  }

  return (
    <div>
      <PageTitle right={data && <span className="text-sm text-slate-500">{data.total} cards</span>}>Browse</PageTitle>
      <input
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search fronts, answers, explanations, ids…"
        aria-label="Search cards"
        className="mb-3 h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-base dark:border-slate-700 dark:bg-slate-900"
      />
      <div className="mb-2 flex gap-2 overflow-x-auto pb-1">
        {meta?.lectures.map((l) => (
          <Chip key={l.id} active={lecture === l.id} onClick={() => setParam('lecture', l.id)} title={l.title}>
            {l.id}
          </Chip>
        ))}
      </div>
      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            ['origin', 'concept', 'Concept'],
            ['origin', 'exam_official', 'Official exam'],
            ['origin', 'exam_style', 'Unofficial'],
            ['type', 'basic', 'Q→A'],
            ['type', 'cloze', 'Cloze'],
            ['type', 'tf', 'T/F'],
            ['type', 'mcq', 'MCQ'],
          ] as const
        ).map(([k, v, l]) => (
          <Chip key={v} active={(k === 'origin' ? origin : type) === v} onClick={() => setParam(k, v)}>
            {l}
          </Chip>
        ))}
      </div>
      {error && <ErrorBox message={error} onRetry={reload} />}
      {loading && !data && <Spinner />}
      {data && (
        <ul className={`space-y-2 ${loading ? 'opacity-60' : ''}`}>
          {data.cards.map((c) => (
            <CardRow key={c.id} c={c} />
          ))}
          {!data.cards.length && (
            <Panel>
              <p className="text-slate-500">No card matches.</p>
            </Panel>
          )}
        </ul>
      )}
    </div>
  )
}

function CardRow({ c }: { c: CardSummary }) {
  return (
    <li>
      <Link
        to={`/browse/${c.id}`}
        className={`block rounded-2xl bg-white p-3.5 shadow-sm ring-1 ring-slate-200 hover:ring-indigo-400 dark:bg-slate-900 dark:ring-slate-800 ${
          c.active ? '' : 'opacity-60'
        }`}
      >
        <div className="mb-1.5 flex flex-wrap items-center gap-1.5">
          <OriginBadge origin={c.origin} examLabel={c.exam_label} />
          <Tag>{c.lecture}</Tag>
          <Tag>{c.type}</Tag>
          {!c.active && <Tag>inactive</Tag>}
          <span className="ml-auto flex items-center gap-1" aria-label="Item states">
            {c.items.map((i) => (
              <span
                key={i.item_id}
                title={`${i.item_id}: ${i.suspended ? 'suspended' : i.state}`}
                className={`h-2.5 w-2.5 rounded-full ${i.suspended ? 'bg-slate-300 dark:bg-slate-600' : STATE_STYLE[i.state]}`}
              />
            ))}
          </span>
        </div>
        <p className="text-[0.95rem] text-slate-700 dark:text-slate-200">{previewText(c.front)}</p>
        <p className="mt-1 font-mono text-xs text-slate-400">{c.id}</p>
      </Link>
    </li>
  )
}
