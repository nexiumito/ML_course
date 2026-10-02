import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useApp } from '../AppContext'
import { Button, Sheet } from './ui'

const LABELS: Record<string, string> = {
  wrong: 'Wrong',
  unclear: 'Unclear',
  typo: 'Typo',
  'too-long': 'Too long',
  duplicate: 'Duplicate',
  'bad-source': 'Bad source',
  other: 'Other',
}

export function ReportDialog({
  open,
  onClose,
  cardId,
  itemId,
}: {
  open: boolean
  onClose: () => void
  cardId: string
  itemId?: string | null
}) {
  const { meta, toast } = useApp()
  const [reason, setReason] = useState('wrong')
  const [comment, setComment] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    if (open) {
      setReason('wrong')
      setComment('')
    }
  }, [open])

  const submit = async () => {
    setBusy(true)
    try {
      await api.report({ card_id: cardId, item_id: itemId, reason, comment })
      toast('Report saved — it will be processed in the next content session', 'success')
      onClose()
    } catch (e) {
      toast((e as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Sheet open={open} onClose={onClose} title="⚑ Flag this card">
      <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">
        <code className="text-xs">{cardId}</code>
      </p>
      <div className="mb-4 flex flex-wrap gap-2" role="radiogroup" aria-label="Reason">
        {(meta?.report_reasons ?? Object.keys(LABELS)).map((r) => (
          <button
            key={r}
            type="button"
            role="radio"
            aria-checked={reason === r}
            onClick={() => setReason(r)}
            className={`min-h-10 rounded-full px-3.5 text-sm font-medium ${
              reason === r ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-800'
            }`}
          >
            {LABELS[r] ?? r}
          </button>
        ))}
      </div>
      <label className="mb-1 block text-sm font-medium" htmlFor="report-comment">
        What is wrong? (optional)
      </label>
      <textarea
        id="report-comment"
        rows={4}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
        }}
        className="w-full rounded-xl border border-slate-200 bg-white p-3 text-base dark:border-slate-700 dark:bg-slate-950"
        placeholder="e.g. the slide says 1/N, not 1/(2N)"
      />
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={submit} disabled={busy}>
          Send report
        </Button>
      </div>
    </Sheet>
  )
}
