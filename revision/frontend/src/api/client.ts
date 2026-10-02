import type {
  CardDetail,
  CardSummary,
  ExamStats,
  ItemView,
  Mastery,
  Meta,
  Overview,
  QueueResponse,
  Report,
  Retention,
  ReviewResult,
  SessionSummary,
  Settings,
  WeakItem,
} from './types'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, {
      ...init,
      headers: init?.body ? { 'Content-Type': 'application/json', ...init.headers } : init?.headers,
    })
  } catch {
    throw new ApiError(0, 'Server unreachable — are you online / on the tailnet?')
  }
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try {
      const body = await res.json()
      msg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail ?? body)
    } catch {
      /* not JSON */
    }
    throw new ApiError(res.status, msg)
  }
  return res.json() as Promise<T>
}

const post = <T>(path: string, body: unknown = {}) => request<T>(path, { method: 'POST', body: JSON.stringify(body) })

export function qs(params: Record<string, string | number | boolean | null | undefined>): string {
  const u = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '' || v === false) continue
    u.set(k, String(v))
  }
  const s = u.toString()
  return s ? `?${s}` : ''
}

export const api = {
  meta: () => request<Meta>('/api/meta'),
  queue: (params: Record<string, string | number | boolean | undefined>) =>
    request<QueueResponse>(`/api/queue${qs(params)}`),
  item: (itemId: string) => request<ItemView>(`/api/items/${encodeURIComponent(itemId)}`),
  review: (body: {
    item_id: string
    mode: string
    session_id: string
    rating?: number
    answer?: boolean | number[]
    guessed?: boolean
    too_easy?: boolean
    duration_ms?: number
  }) => post<ReviewResult>('/api/review', body),
  undo: (session_id?: string) => post<{ item_id: string; undone_log_id: number }>('/api/undo', { session_id }),
  summary: (sessionId: string) => request<SessionSummary>(`/api/session/${encodeURIComponent(sessionId)}/summary`),
  cards: (params: Record<string, string | boolean | undefined>) =>
    request<{ cards: CardSummary[]; total: number }>(`/api/cards${qs(params)}`),
  card: (id: string) => request<CardDetail>(`/api/cards/${encodeURIComponent(id)}`),
  suspend: (itemId: string, on: boolean) =>
    post<{ item_id: string; suspended: boolean }>(
      `/api/items/${encodeURIComponent(itemId)}/${on ? 'suspend' : 'unsuspend'}`,
    ),
  report: (body: { card_id: string; item_id?: string | null; reason: string; comment: string }) =>
    post<{ id: number }>('/api/reports', body),
  reports: (status?: 'open' | 'resolved') => request<{ reports: Report[] }>(`/api/reports${qs({ status })}`),
  resolveReport: (id: number, note: string) => post<Report>(`/api/reports/${id}/resolve`, { note }),
  overview: () => request<Overview>('/api/stats/overview'),
  calendar: (days = 182) =>
    request<{ days: { day: string; reviews: number }[]; retention: Retention }>(`/api/stats/calendar?days=${days}`),
  forecast: (days = 30) => request<{ days: { day: string; due: number }[] }>(`/api/stats/forecast?days=${days}`),
  byLecture: () => request<{ lectures: Mastery[] }>('/api/stats/by-lecture'),
  byTheme: () => request<{ themes: Mastery[] }>('/api/stats/by-theme'),
  examStats: () => request<ExamStats>('/api/stats/exam'),
  weakest: (n = 20) => request<{ items: WeakItem[] }>(`/api/stats/weakest?n=${n}`),
  settings: () => request<Settings>('/api/settings'),
  saveSettings: (patch: Partial<Settings>) =>
    request<Settings>('/api/settings', { method: 'PUT', body: JSON.stringify(patch) }),
}
