/**
 * Layout check of rendered cards (Sheet page, `?check=1`): finds what would be unreadable on a phone.
 * Each card root must carry `data-card-id`.
 */
export function layoutIssues(root: ParentNode): string[] {
  const out: string[] = []
  for (const card of root.querySelectorAll<HTMLElement>('[data-card-id]')) {
    const id = card.dataset.cardId
    const R = card.getBoundingClientRect()
    for (const k of card.querySelectorAll<HTMLElement>('.katex')) {
      const disp = k.closest('.katex-display')
      if (disp) {
        if (disp.classList.contains('katex-overflow')) out.push(`${id}: display formula still too wide (scrolls)`)
        continue
      }
      if (k.closest('button span.overflow-x-auto')) continue // choices scroll inside their own box
      for (const b of k.querySelectorAll('.base')) {
        const r = b.getBoundingClientRect()
        if (r.right > R.right + 1) {
          out.push(`${id}: inline formula chunk overflows by ${Math.round(r.right - R.right)}px (use $$…$$ or split it)`)
          break
        }
      }
    }
    for (const sp of card.querySelectorAll<HTMLElement>('button span.overflow-x-auto'))
      if (sp.scrollWidth > sp.clientWidth + 1) out.push(`${id}: a choice scrolls horizontally`)
    for (const img of card.querySelectorAll<HTMLImageElement>('img'))
      if (!img.complete || img.naturalWidth === 0) out.push(`${id}: image not loaded (${img.alt.slice(0, 30)})`)
    if (card.querySelector('.katex-error')) out.push(`${id}: KaTeX error`)
  }
  return [...new Set(out)]
}
