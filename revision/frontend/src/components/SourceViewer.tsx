import { useEffect, useState } from 'react'
import type { Source } from '../api/types'
import { Button, Sheet } from './ui'

const ZOOMS = [100, 150, 200, 300]

function pageUrl(pdf: string, page: number) {
  return `/api/source/page?pdf=${encodeURIComponent(pdf)}&page=${page}&scale=2`
}

/** Rendered PDF page of a card source (works on iOS, where Safari ignores #page=N). */
export function SourceViewer({ sources, open, onClose }: { sources: Source[]; open: boolean; onClose: () => void }) {
  const [idx, setIdx] = useState(0)
  const [page, setPage] = useState<number | null>(null)
  const [zoom, setZoom] = useState(100)
  const [loaded, setLoaded] = useState(false)
  const src = sources[idx]

  useEffect(() => {
    if (open) {
      setIdx(0)
      setZoom(100)
    }
  }, [open])
  useEffect(() => {
    setPage(src?.page ?? null)
  }, [src])
  useEffect(() => setLoaded(false), [src, page])

  useEffect(() => {
    if (!open || !src?.pdf) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') setPage((p) => (p && p > 1 ? p - 1 : p))
      if (e.key === 'ArrowRight') setPage((p) => (p && (!src.page_count || p < src.page_count) ? p + 1 : p))
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, src])

  if (!src) return null
  const max = src.page_count ?? undefined

  return (
    <Sheet open={open} onClose={onClose} title={src.label} wide>
      {sources.length > 1 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {sources.map((s, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setIdx(i)}
              className={`min-h-9 rounded-full px-3 text-sm font-medium ${
                i === idx ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-800'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      )}
      {src.pdf && page ? (
        <>
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-1">
              <Button variant="ghost" aria-label="Previous page" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                ‹
              </Button>
              <span className="min-w-24 text-center text-sm tabular-nums text-slate-600 dark:text-slate-300">
                page {page}
                {max ? ` / ${max}` : ''}
                {page !== src.page && (
                  <button type="button" className="ml-1 text-indigo-600 underline" onClick={() => setPage(src.page)}>
                    back
                  </button>
                )}
              </span>
              <Button
                variant="ghost"
                aria-label="Next page"
                disabled={max !== undefined && page >= max}
                onClick={() => setPage(page + 1)}
              >
                ›
              </Button>
            </div>
            <div className="flex items-center gap-1">
              {ZOOMS.map((z) => (
                <button
                  key={z}
                  type="button"
                  onClick={() => setZoom(z)}
                  className={`min-h-9 rounded-lg px-2 text-sm tabular-nums ${
                    zoom === z ? 'bg-slate-200 font-semibold dark:bg-slate-700' : 'text-slate-500'
                  }`}
                >
                  {z}%
                </button>
              ))}
              <a
                className="ml-1 inline-flex min-h-9 items-center rounded-lg px-2 text-sm text-indigo-600 hover:underline dark:text-indigo-400"
                href={`/files/${src.pdf}#page=${page}`}
                target="_blank"
                rel="noreferrer"
              >
                Full PDF ↗
              </a>
            </div>
          </div>
          <div className="relative overflow-auto rounded-xl bg-slate-100 dark:bg-slate-950" style={{ maxHeight: '72dvh' }}>
            {!loaded && <div className="absolute inset-0 animate-pulse bg-slate-200/60 dark:bg-slate-800/60" />}
            <img
              key={`${src.pdf}-${page}`}
              src={pageUrl(src.pdf, page)}
              alt={`${src.label} — page ${page}`}
              onLoad={() => setLoaded(true)}
              style={{ width: `${zoom}%`, maxWidth: 'none' }}
              className="block select-none"
              draggable={false}
            />
          </div>
        </>
      ) : (
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Repository document: <code>{src.path}</code>
        </p>
      )}
    </Sheet>
  )
}
