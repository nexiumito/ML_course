import type { Answer } from '../api/types'

/** Plain-text preview: drop markdown/LaTeX noise, show the cloze answers. */
export function previewText(md: string, max = 180): string {
  const t = md
    .replace(/\{\{c\d+::([\s\S]*?)(::[\s\S]*?)?\}\}/g, '$1')
    .replace(/\$\$?([^$]*)\$\$?/g, '$1')
    .replace(/\\(text|mathcal|mathbb|operatorname)\{([^}]*)\}/g, '$2')
    .replace(/[*_`#>]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  return t.length > max ? `${t.slice(0, max - 1)}…` : t
}

export function formatAnswer(answer: Answer | null | undefined, choices: string[] | null): string {
  if (answer === null || answer === undefined) return '—'
  if (typeof answer === 'boolean') return answer ? 'True' : 'False'
  return answer.map((i) => choices?.[i] ?? String(i)).join(' · ')
}
