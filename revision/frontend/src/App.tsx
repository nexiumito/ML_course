import { useEffect, useState } from 'react'
import { Markdown } from './components/Markdown'

type Health = { status: string; cards: number; items: number }

// Placeholder shell (M0). The real pages (Home, Review, Browse, Stats, Reports, Settings) come in M3.
export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setHealth)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-semibold">CS-433 Review</h1>
      <p className="mt-2 text-sm text-slate-500">
        {health
          ? `Backend OK — ${health.cards} cards, ${health.items} review items`
          : error
            ? `Backend unreachable (${error})`
            : 'Connecting…'}
      </p>
      <div className="mt-6 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <Markdown>
          {'KaTeX check: $L_\\mathcal{D}(f) = \\mathbb{E}_{(x,y)\\sim\\mathcal{D}}[\\ell(y, f(x))]$\n\n$$\\sqrt{\\frac{(b-a)^2 \\ln(2/\\delta)}{2|S_\\text{test}|}}$$'}
        </Markdown>
      </div>
    </main>
  )
}
