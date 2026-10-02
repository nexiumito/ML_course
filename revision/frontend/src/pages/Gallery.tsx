import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { CardDetail } from '../api/types'
import { useApp } from '../AppContext'
import { CardHeader, CardImages, ChoiceList, Explanation, TrapNote } from '../components/CardParts'
import { PageTitle } from '../components/Layout'
import { Markdown } from '../components/Markdown'
import { Chip, ErrorBox, Panel, Spinner } from '../components/ui'
import { layoutIssues } from '../lib/layoutCheck'
import { formatAnswer } from '../lib/text'

/** All cards of one lecture with their answers, on one page: a revision sheet (and the visual check of new cards). */
export default function Gallery() {
  const { meta } = useApp()
  const [sp, setSp] = useSearchParams()
  const lecture = sp.get('lecture') ?? meta?.lectures.find((l) => l.active)?.id ?? ''
  const [cards, setCards] = useState<CardDetail[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const check = sp.get('check') === '1'
  const [issues, setIssues] = useState<string[] | null>(null)
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!check || !cards) return
    setIssues(null)
    let cancelled = false
    // wait for fonts, images and the display-math fitting pass before measuring
    Promise.all([document.fonts.ready, new Promise((r) => setTimeout(r, 600))]).then(() => {
      if (!cancelled && listRef.current) setIssues(layoutIssues(listRef.current))
    })
    return () => {
      cancelled = true
    }
  }, [check, cards])

  useEffect(() => {
    if (!lecture) return
    setCards(null)
    api
      .cards({ lectures: lecture })
      .then((list) => Promise.all(list.cards.map((c) => api.card(c.id))))
      .then(setCards)
      .catch((e: Error) => setError(e.message))
  }, [lecture])

  return (
    <div>
      <PageTitle right={cards && <span className="text-sm text-slate-500">{cards.length} cards</span>}>Sheet</PageTitle>
      <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
        {meta?.lectures.map((l) => (
          <Chip
            key={l.id}
            active={lecture === l.id}
            onClick={() => setSp(check ? { lecture: l.id, check: '1' } : { lecture: l.id })}
            title={l.title}
          >
            {l.id}
          </Chip>
        ))}
      </div>
      {check && (
        <Panel className="mb-4 p-3 text-sm">
          {issues === null ? (
            'Layout check running…'
          ) : issues.length === 0 ? (
            <span className="text-emerald-700 dark:text-emerald-400">✓ Layout check: no issue at this width</span>
          ) : (
            <>
              <p className="font-semibold text-red-700 dark:text-red-400">⚠ Layout check: {issues.length} issue(s)</p>
              <ul className="mt-1 list-disc pl-5" data-testid="layout-issues">
                {issues.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </>
          )}
        </Panel>
      )}
      {error && <ErrorBox message={error} />}
      {!cards && !error && <Spinner />}
      <div className="space-y-3" ref={listRef}>
        {cards?.map((d) => (
          <CardSheet key={d.card.id} d={d} />
        ))}
      </div>
    </div>
  )
}

function CardSheet({ d }: { d: CardDetail }) {
  const c = d.card
  const first = d.items[0]?.view
  if (!first) return null
  return (
    <Panel className="p-4">
      <div data-card-id={c.id}>
        <CardHeader view={first} />
        {c.type === 'cloze' ? (
          d.items.map((it) => (
            <div key={it.view.item_id} className="mt-3">
              {d.items.length > 1 && <p className="text-xs font-semibold text-slate-500">c{it.view.cloze_index}</p>}
              <Markdown>{it.view.back ?? ''}</Markdown>
            </div>
          ))
        ) : (
          <div className="mt-3">
            <Markdown>{c.front}</Markdown>
          </div>
        )}
        <CardImages images={first.images} />
        {c.type === 'basic' && (
          <div className="mt-3 border-t-2 border-dashed border-slate-200 pt-3 dark:border-slate-700">
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
          <p className="mt-3 font-semibold">
            Answer: <span className="text-emerald-700 dark:text-emerald-400">{formatAnswer(c.answer, null)}</span>
          </p>
        )}
        <TrapNote trap={c.trap} />
        <Explanation text={c.explanation} />
        <p className="mt-3 text-xs text-slate-400">
          <Link to={`/browse/${c.id}`} className="font-mono hover:underline">
            {c.id}
          </Link>{' '}
          · {c.sources.map((s) => s.label).join(' · ')}
        </p>
      </div>
    </Panel>
  )
}
