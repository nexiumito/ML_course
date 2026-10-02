// Types mirroring the backend JSON (revision/backend/revision/api.py, reviews.py, stats.py).

export type CardType = 'basic' | 'cloze' | 'tf' | 'mcq'
export type Origin = 'concept' | 'exam_official' | 'exam_style'
export type Priority = 'core' | 'detail'
export type ItemState = 'new' | 'learning' | 'review' | 'relearning'
export type Mode = 'study' | 'exam' | 'weak' | 'drill'
export type Answer = boolean | number[]

export interface Source {
  kind: 'lecture' | 'exam' | 'lab' | 'doc'
  pdf: string | null
  page: number | null
  path: string | null
  label: string
  page_url?: string
  file_url?: string
  page_count?: number | null
}

export interface ItemView {
  item_id: string
  card_id: string
  cloze_index: number | null
  type: CardType
  origin: Origin
  exam_label: string | null
  lecture: string
  lecture_title: string
  week: number
  also_lectures: string[]
  themes: { id: string; label: string }[]
  priority: Priority
  front: string
  back: string | null
  choices: string[] | null
  multi: boolean
  shuffle: boolean
  explanation: string | null
  trap: string | null
  images: { url: string; alt: string }[]
  sources: Source[]
  state: ItemState
  is_new: boolean
  previews: Record<'1' | '2' | '3' | '4', number>
  hash: string
  answer?: Answer | null
}

export interface StudyCounts {
  new: number
  learning: number
  review: number
}
export interface DrillCounts {
  remaining: number
  done: number
  total: number
}

export interface QueueResponse {
  mode: Mode
  item: ItemView | null
  counts: StudyCounts | DrillCounts
  waiting_until: string | null
  limit_reached: boolean
  done: boolean
}

export interface ReviewResult {
  log_id: number
  item_id: string
  rating: 1 | 2 | 3 | 4
  auto_graded: boolean
  correct: boolean | null
  correct_answer: Answer | null
  state: ItemState
  due: string
  interval_seconds: number
  explanation: string | null
  trap: string | null
}

export interface SessionSummary {
  session_id: string
  reviews: number
  items: number
  new: number
  auto_graded: number
  auto_correct: number
  ratings: Record<'1' | '2' | '3' | '4', number>
  duration_ms: number
  again_items: string[]
}

export interface Lecture {
  id: string
  week: number
  title: string
  date: string | null
  pdf: string
  annotated_pdf: string | null
  sheet: string | null
  active: boolean
  counts: { cards?: number; items?: number; exam_official?: number; exam_style?: number }
}

export interface Settings {
  desired_retention: number
  new_per_day: number
  max_reviews_per_day: number
  new_order: 'course' | 'random'
  interleave_ratio: number
  learn_ahead_minutes: number
  weak_points_n: number
  drill_n: number
  theme: 'system' | 'light' | 'dark'
  font_size: 'sm' | 'md' | 'lg' | 'xl'
  swipe: boolean
}

export interface Meta {
  lectures: Lecture[]
  weeks: number[]
  themes: { id: string; label: string }[]
  exam_date: string | null
  timezone: string
  settings: Settings
  report_reasons: string[]
}

export interface Overview {
  cards: number
  items: number
  by_state: Record<ItemState, number>
  suspended: number
  due: StudyCounts
  today: { reviews: number; new: number; minutes: number; auto_graded: number; auto_correct: number }
  streak: number
  exam_date: string | null
  days_to_exam: number | null
}

export interface Mastery {
  key: string
  items: number
  seen: number
  mature: number
  mean_retrievability: number | null
  lapses: number
  title?: string
  week?: number
  label?: string
}

export interface RetentionBlock {
  n: number
  retention: number | null
}
export type Retention = Record<'7d' | '30d', Record<'all' | 'self' | 'auto', RetentionBlock>>

export interface ExamStats {
  by_year: { key: string; correct: number; n: number; accuracy: number }[]
  by_theme: { key: string; correct: number; n: number; accuracy: number }[]
  by_origin: { key: string; correct: number; n: number; accuracy: number }[]
}

export interface WeakItem {
  item_id: string
  card_id: string
  lecture: string
  score: number
  lapses: number
  retrievability: number | null
}

export interface CardSummary {
  id: string
  type: CardType
  origin: Origin
  lecture: string
  week: number
  themes: string[]
  priority: Priority
  front: string
  exam_label: string | null
  active: boolean
  file: string
  items: { item_id: string; state: ItemState; due_utc: string | null; suspended: boolean }[]
}

export interface ItemStateDetail {
  item_id: string
  card_id: string
  cloze_index: number | null
  state: ItemState
  due_utc: string | null
  stability: number | null
  difficulty: number | null
  reps: number
  lapses: number
  last_review_utc: string | null
  suspended: number
  introduced_utc: string | null
  retrievability: number | null
}

export interface HistoryEntry {
  id: number
  reviewed_utc: string
  rating: number
  auto_graded: number
  correct: number | null
  guessed: number
  duration_ms: number | null
  mode: string
}

export interface CardDetail {
  card: {
    id: string
    type: CardType
    origin: Origin
    lecture: string
    also_lectures: string[]
    themes: string[]
    priority: Priority
    front: string
    back: string | null
    choices: string[] | null
    answer: Answer | null
    multi: boolean
    explanation: string | null
    trap: string | null
    images: { src: string; alt: string }[]
    sources: Source[]
    added: string
  }
  file: string
  position: number
  hash: string
  active: boolean
  exam_label: string | null
  items: { view: ItemView; state: ItemStateDetail; history: HistoryEntry[] }[]
}

export interface Report {
  id: number
  card_id: string
  item_id: string | null
  reason: string
  comment: string
  created_utc: string
  status: 'open' | 'resolved'
  resolved_utc: string | null
  resolution_note: string | null
}
