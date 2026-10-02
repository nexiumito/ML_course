import type { Mode } from '../api/types'

export function newSessionId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID()
  return `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

/** What a review session is asked to do. Serialized in the /review URL so sessions are linkable. */
export interface StudySpec {
  mode: Mode
  weeks: number[]
  lectures: string[]
  themes: string[]
  origins: string[]
  types: string[]
  core: boolean
  includeNotDue: boolean
  limit?: number
}

export const emptySpec = (mode: Mode = 'study'): StudySpec => ({
  mode,
  weeks: [],
  lectures: [],
  themes: [],
  origins: [],
  types: [],
  core: false,
  includeNotDue: false,
})

const list = (v: string | null) => (v ? v.split(',').filter(Boolean) : [])

export function specFromSearch(sp: URLSearchParams): StudySpec {
  const mode = (sp.get('mode') as Mode) || 'study'
  const limit = sp.get('limit')
  return {
    mode: ['study', 'exam', 'weak', 'drill'].includes(mode) ? mode : 'study',
    weeks: list(sp.get('weeks')).map(Number).filter((n) => Number.isFinite(n)),
    lectures: list(sp.get('lectures')),
    themes: list(sp.get('themes')),
    origins: list(sp.get('origins')),
    types: list(sp.get('types')),
    core: sp.get('core') === 'true',
    includeNotDue: sp.get('include_not_due') === 'true',
    limit: limit ? Number(limit) : undefined,
  }
}

/** Query params shared by the /review URL and GET /api/queue. */
export function specToParams(s: StudySpec): Record<string, string | number | boolean | undefined> {
  return {
    mode: s.mode,
    weeks: s.weeks.join(',') || undefined,
    lectures: s.lectures.join(',') || undefined,
    themes: s.themes.join(',') || undefined,
    origins: s.origins.join(',') || undefined,
    types: s.types.join(',') || undefined,
    core: s.core || undefined,
    include_not_due: s.includeNotDue || undefined,
    limit: s.limit,
  }
}

export function specToSearch(s: StudySpec): string {
  const u = new URLSearchParams()
  for (const [k, v] of Object.entries(specToParams(s))) if (v !== undefined) u.set(k, String(v))
  return u.toString()
}

export function describeSpec(s: StudySpec): string {
  const base =
    s.mode === 'exam'
      ? s.includeNotDue
        ? 'Exam drill (all unlocked)'
        : 'Exam mode'
      : s.mode === 'weak'
        ? 'Weak points'
        : s.mode === 'drill'
          ? `Custom drill${s.limit ? ` · ${s.limit}` : ''}`
          : 'Study'
  const parts: string[] = []
  if (s.weeks.length) parts.push(`week ${s.weeks.join(', ')}`)
  if (s.lectures.length) parts.push(s.lectures.join(', '))
  if (s.themes.length) parts.push(s.themes.join(', '))
  if (s.origins.length) parts.push(s.origins.map(originShort).join(', '))
  if (s.types.length) parts.push(s.types.join(', '))
  if (s.core) parts.push('essentials')
  return parts.length ? `${base} — ${parts.join(' · ')}` : base
}

export function originShort(o: string): string {
  return o === 'exam_official' ? 'official exam' : o === 'exam_style' ? 'unofficial exam-style' : 'concept'
}
