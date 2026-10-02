import { memo, useLayoutEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import rehypeKatex from 'rehype-katex'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import { normalizeMath } from '../lib/markdown'
import { rehypeCloze } from '../lib/rehypeCloze'

const katexOptions = { throwOnError: false, strict: false, errorColor: '#dc2626' }

const DISPLAY_EM = 1.2 // matches `.md .katex-display > .katex` in index.css
const MIN_SCALE = 0.8 // below this the formula would get hard to read: wrap at relations, then scroll

/**
 * Display formulas wider than their box (phones): 1) shrink down to MIN_SCALE; 2) if still too wide, let
 * KaTeX's breakable chunks (split after =, ≤, ≥, +, …) wrap onto several lines; 3) if a single unbreakable
 * chunk is still too wide (e.g. a whole \left[…\right] group), scroll horizontally with a fade hint.
 */
function fitDisplayMath(root: HTMLElement) {
  root.querySelectorAll<HTMLElement>('.katex-display > .katex').forEach((el) => {
    const box = el.parentElement!
    el.style.fontSize = ''
    box.classList.remove('katex-wrap', 'katex-overflow')
    const avail = box.clientWidth
    const need = el.scrollWidth
    if (avail <= 0 || need <= avail) return
    el.style.fontSize = `${DISPLAY_EM * Math.max(MIN_SCALE, (avail - 2) / need)}em`
    if (box.scrollWidth > box.clientWidth + 1) box.classList.add('katex-wrap')
    if (box.scrollWidth > box.clientWidth + 1) box.classList.add('katex-overflow')
  })
}

export const Markdown = memo(function Markdown({ children, className = '' }: { children: string; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  useLayoutEffect(() => {
    const root = ref.current
    if (!root) return
    fitDisplayMath(root)
    const ro = new ResizeObserver(() => fitDisplayMath(root))
    ro.observe(root)
    // KaTeX fonts may finish loading after the first layout
    document.fonts?.ready.then(() => fitDisplayMath(root))
    return () => ro.disconnect()
  }, [children])

  return (
    <div ref={ref} className={`md ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[[rehypeKatex, katexOptions], rehypeCloze]}>
        {normalizeMath(children)}
      </ReactMarkdown>
    </div>
  )
})
