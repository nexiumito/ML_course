import { useState, type ReactNode } from 'react'

/* Charts follow the dataviz method: one sequential blue ramp, thin marks (≤ 24px, 4px rounded data-end,
   square at the baseline, 2px gaps), hover + focus tooltips, a data table for every chart, text in ink. */

function Tooltip({ children }: { children: ReactNode }) {
  return (
    <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs whitespace-nowrap text-white shadow-lg dark:bg-slate-100 dark:text-slate-900">
      {children}
    </div>
  )
}

export function DataTable({ head, rows }: { head: string[]; rows: (string | number)[][] }) {
  return (
    <details className="mt-2 text-sm">
      <summary className="cursor-pointer text-slate-500 select-none dark:text-slate-400">Data table</summary>
      <div className="mt-2 max-h-64 overflow-auto">
        <table className="w-full text-left tabular-nums">
          <thead>
            <tr className="text-slate-500 dark:text-slate-400">
              {head.map((h) => (
                <th key={h} className="py-1 pr-4 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
                {r.map((c, j) => (
                  <td key={j} className="py-1 pr-4">
                    {c}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}

function niceMax(v: number): number {
  if (v <= 5) return 5
  const p = 10 ** Math.floor(Math.log10(v))
  for (const m of [1, 2, 2.5, 5, 10]) if (m * p >= v) return m * p
  return 10 * p
}

/** Single-series column chart (e.g. reviews per day, due forecast). */
export function ColumnChart({
  data,
  unit,
  height = 140,
  xLabels,
}: {
  data: { key: string; label: string; value: number }[]
  unit: string
  height?: number
  xLabels?: number[] // indices that get an axis label
}) {
  const [hover, setHover] = useState<number | null>(null)
  const max = niceMax(Math.max(0, ...data.map((d) => d.value)))
  const labelIdx = new Set(xLabels ?? [0, Math.floor((data.length - 1) / 2), data.length - 1])
  return (
    <div>
      <div className="flex gap-2">
        <div className="flex flex-col justify-between text-right text-[0.7rem] text-slate-500 tabular-nums dark:text-slate-400" style={{ height }}>
          <span>{max}</span>
          <span>{Number.isInteger(max / 2) ? max / 2 : ''}</span>
          <span>0</span>
        </div>
        <div className="relative min-w-0 flex-1">
          <div className="absolute inset-x-0 top-0 border-t border-[var(--viz-grid)]" />
          <div className="absolute inset-x-0 top-1/2 border-t border-[var(--viz-grid)]" />
          <div
            className="relative flex items-end border-b border-[var(--viz-grid)]"
            style={{ height, gap: data.length > 60 ? 1 : 2 }}
            onPointerLeave={() => setHover(null)}
          >
            {data.map((d, i) => (
              <div
                key={d.key}
                tabIndex={0}
                role="img"
                aria-label={`${d.label}: ${d.value} ${unit}`}
                onPointerEnter={() => setHover(i)}
                onFocus={() => setHover(i)}
                onBlur={() => setHover(null)}
                className="relative flex h-full min-w-0 flex-1 items-end justify-center outline-none"
              >
                <div
                  className="w-full rounded-t-[4px] transition-opacity"
                  style={{
                    maxWidth: 24,
                    height: d.value ? `${Math.max(2, (d.value / max) * 100)}%` : 0,
                    background: 'var(--viz-strong)',
                    opacity: hover === null || hover === i ? 1 : 0.55,
                  }}
                />
                {hover === i && (
                  <Tooltip>
                    <b>
                      {d.value} {unit}
                    </b>{' '}
                    · {d.label}
                  </Tooltip>
                )}
              </div>
            ))}
          </div>
          <div className="relative mt-1 h-4 text-[0.7rem] text-slate-500 dark:text-slate-400">
            {data.map((d, i) =>
              labelIdx.has(i) ? (
                <span
                  key={d.key}
                  className="absolute -translate-x-1/2 whitespace-nowrap"
                  style={{ left: `${((i + 0.5) / data.length) * 100}%` }}
                >
                  {d.label}
                </span>
              ) : null,
            )}
          </div>
        </div>
      </div>
      <DataTable head={['Day', unit]} rows={data.filter((d) => d.value).map((d) => [d.label, d.value])} />
    </div>
  )
}

/** GitHub-style calendar heatmap: columns = weeks (Mon→Sun), 6-step sequential ramp. */
export function CalendarHeatmap({ days }: { days: { day: string; reviews: number }[] }) {
  const [hover, setHover] = useState<string | null>(null)
  if (!days.length) return null
  const max = Math.max(1, ...days.map((d) => d.reviews))
  const level = (n: number) => (n === 0 ? 0 : Math.min(5, 1 + Math.floor((n / max) * 4.999)))
  const first = new Date(days[0].day + 'T12:00:00')
  const pad = (first.getDay() + 6) % 7 // Monday = 0
  const cells: ({ day: string; reviews: number } | null)[] = [...Array(pad).fill(null), ...days]
  const weeks: (typeof cells)[] = []
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7))
  return (
    <div>
      <div className="overflow-x-auto pb-1">
        <div className="flex w-max gap-[3px]" onPointerLeave={() => setHover(null)}>
          {weeks.map((w, wi) => (
            <div key={wi} className="flex flex-col gap-[3px]">
              {Array.from({ length: 7 }, (_, di) => {
                const c = w[di]
                if (!c) return <div key={di} className="h-3.5 w-3.5" />
                return (
                  <div
                    key={di}
                    tabIndex={0}
                    role="img"
                    aria-label={`${c.day}: ${c.reviews} reviews`}
                    onPointerEnter={() => setHover(c.day)}
                    onFocus={() => setHover(c.day)}
                    onBlur={() => setHover(null)}
                    className="relative h-3.5 w-3.5 rounded-[3px] outline-offset-1"
                    style={{ background: `var(--viz-heat-${level(c.reviews)})` }}
                  >
                    {hover === c.day && (
                      <Tooltip>
                        <b>{c.reviews} reviews</b> · {c.day}
                      </Tooltip>
                    )}
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
      <div className="mt-2 flex items-center gap-1 text-[0.7rem] text-slate-500 dark:text-slate-400">
        less
        {[0, 1, 2, 3, 4, 5].map((l) => (
          <span key={l} className="h-3 w-3 rounded-[3px]" style={{ background: `var(--viz-heat-${l})` }} />
        ))}
        more
      </div>
    </div>
  )
}

/** Part-to-whole progress: mature | seen (not mature) | unseen track. Legend rendered by the caller once. */
export function ProgressStack({ total, seen, mature, label }: { total: number; seen: number; mature: number; label: string }) {
  const [hover, setHover] = useState(false)
  const pm = total ? (mature / total) * 100 : 0
  const ps = total ? ((seen - mature) / total) * 100 : 0
  return (
    <div
      className="relative"
      tabIndex={0}
      role="img"
      aria-label={`${label}: ${seen} of ${total} seen, ${mature} mature`}
      onPointerEnter={() => setHover(true)}
      onPointerLeave={() => setHover(false)}
      onFocus={() => setHover(true)}
      onBlur={() => setHover(false)}
    >
      <div className="flex h-3 w-full overflow-hidden rounded-[4px]" style={{ background: 'var(--viz-track)' }}>
        {pm > 0 && <div style={{ width: `${pm}%`, background: 'var(--viz-strong)' }} />}
        {ps > 0 && (
          <div
            style={{
              width: `${ps}%`,
              background: 'var(--viz-soft)',
              borderLeft: pm > 0 ? '2px solid var(--viz-surface)' : undefined,
            }}
          />
        )}
      </div>
      {hover && (
        <Tooltip>
          <b>
            {seen}/{total}
          </b>{' '}
          seen · <b>{mature}</b> mature
        </Tooltip>
      )}
    </div>
  )
}

export function ProgressLegend() {
  return (
    <div className="flex flex-wrap gap-3 text-xs text-slate-500 dark:text-slate-400">
      <span className="inline-flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--viz-strong)' }} /> mature (interval ≥ 21 d)
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--viz-soft)' }} /> seen
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--viz-track)' }} /> not seen yet
      </span>
    </div>
  )
}

/** Horizontal meter for a ratio in [0, 1] (retrievability, accuracy); value printed beside, in ink. */
export function Meter({ value, label }: { value: number | null; label: string }) {
  return (
    <div className="flex items-center gap-2" role="img" aria-label={`${label}: ${value === null ? 'no data' : Math.round(value * 100) + '%'}`}>
      <div className="h-2.5 flex-1 overflow-hidden rounded-[4px]" style={{ background: 'var(--viz-track)' }}>
        {value !== null && (
          <div className="h-full rounded-r-[4px]" style={{ width: `${value * 100}%`, background: 'var(--viz-strong)' }} />
        )}
      </div>
      <span className="w-11 text-right text-sm tabular-nums">{value === null ? '—' : `${Math.round(value * 100)}%`}</span>
    </div>
  )
}
