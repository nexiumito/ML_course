/** "10m", "3h", "4d", "2.5mo", "1.2y" — compact interval label for grade buttons. */
export function formatInterval(seconds: number): string {
  const m = seconds / 60
  if (m < 1) return '<1m'
  if (m < 60) return `${Math.round(m)}m`
  const h = m / 60
  if (h < 24) return `${Math.round(h)}h`
  const d = h / 24
  if (d < 30) return `${Math.round(d)}d`
  const mo = d / 30.44
  if (mo < 12) return `${mo < 10 ? mo.toFixed(1).replace(/\.0$/, '') : Math.round(mo)}mo`
  const y = d / 365.25
  return `${y.toFixed(1).replace(/\.0$/, '')}y`
}

export function formatDuration(ms: number): string {
  const s = Math.round(ms / 1000)
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ${String(s % 60).padStart(2, '0')}s`
  return `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, '0')}m`
}

export function pct(x: number | null | undefined, digits = 0): string {
  return x === null || x === undefined ? '—' : `${(x * 100).toFixed(digits)}%`
}

/** Relative due date: "now", "in 3 min", "in 2 d", "3 d ago". */
export function relativeTime(iso: string | null, now: Date = new Date()): string {
  if (!iso) return '—'
  const diff = (new Date(iso).getTime() - now.getTime()) / 1000
  const abs = Math.abs(diff)
  if (abs < 45) return 'now'
  const label = formatInterval(abs)
  return diff > 0 ? `in ${label}` : `${label} ago`
}

export function shortDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
