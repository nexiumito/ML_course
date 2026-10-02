import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useApp } from '../AppContext'
import { PageTitle } from '../components/Layout'
import { Button, ErrorBox, Panel, Segmented, Spinner, Tag } from '../components/ui'
import { useAsync } from '../hooks/useAsync'
import { shortDate } from '../lib/format'

export default function Reports() {
  const { toast } = useApp()
  const [status, setStatus] = useState<'open' | 'resolved'>('open')
  const { data, error, reload } = useAsync(() => api.reports(status), [status])

  const resolve = async (id: number) => {
    const note = window.prompt('Resolution note (what was fixed)?')
    if (note === null) return
    try {
      await api.resolveReport(id, note)
      toast('Report resolved', 'success')
      reload()
    } catch (e) {
      toast((e as Error).message, 'error')
    }
  }

  return (
    <div>
      <PageTitle
        right={
          <Segmented
            ariaLabel="Report status"
            value={status}
            onChange={setStatus}
            options={[
              { value: 'open', label: 'Open' },
              { value: 'resolved', label: 'Resolved' },
            ]}
          />
        }
      >
        Reports
      </PageTitle>
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
        Cards flagged with ⚑ during review. Claude processes open reports at the start of each content session
        (<code>uv run revision reports list</code>).
      </p>
      {error && <ErrorBox message={error} onRetry={reload} />}
      {!data && !error && <Spinner />}
      {data && (
        <ul className="space-y-2">
          {data.reports.map((r) => (
            <li key={r.id}>
              <Panel className="p-3.5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold">#{r.id}</span>
                  <Tag>{r.reason}</Tag>
                  <Link to={`/browse/${r.card_id}`} className="font-mono text-xs text-indigo-600 hover:underline dark:text-indigo-400">
                    {r.item_id ?? r.card_id}
                  </Link>
                  <span className="ml-auto text-xs text-slate-500">{shortDate(r.created_utc)}</span>
                </div>
                {r.comment && <p className="mt-2 text-sm whitespace-pre-wrap">{r.comment}</p>}
                {r.status === 'resolved' ? (
                  <p className="mt-2 text-sm text-emerald-700 dark:text-emerald-400">
                    ✓ {shortDate(r.resolved_utc)} — {r.resolution_note || 'resolved'}
                  </p>
                ) : (
                  <div className="mt-2">
                    <Button variant="ghost" onClick={() => resolve(r.id)}>
                      Mark resolved
                    </Button>
                  </div>
                )}
              </Panel>
            </li>
          ))}
          {!data.reports.length && (
            <Panel>
              <p className="text-slate-500">{status === 'open' ? 'No open reports. 🎉' : 'No resolved reports yet.'}</p>
            </Panel>
          )}
        </ul>
      )}
    </div>
  )
}
