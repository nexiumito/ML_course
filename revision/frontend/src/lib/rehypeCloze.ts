import type { Element, ElementContent, Root, RootContent, Text } from 'hast'

/** Must match CLOZE_START / CLOZE_END in backend/revision/content.py. */
export const CLOZE_START = ''
export const CLOZE_END = ''

type Parent = Root | Element

function mark(children: ElementContent[]): Element {
  return { type: 'element', tagName: 'mark', properties: { className: ['cloze-mark'] }, children }
}

function text(value: string): Text {
  return { type: 'text', value }
}

/**
 * Rehype plugin: wrap everything between CLOZE_START and CLOZE_END (same parent, possibly spanning
 * KaTeX nodes) in <mark class="cloze-mark">. Unmatched markers are dropped.
 */
export function rehypeCloze() {
  return (tree: Root) => visit(tree)
}

function visit(node: Parent) {
  const out: (RootContent | ElementContent)[] = []
  let open: ElementContent[] | null = null
  const push = (n: ElementContent) => (open ? open.push(n) : out.push(n))

  for (const child of node.children) {
    if (child.type === 'text' && (child.value.includes(CLOZE_START) || child.value.includes(CLOZE_END))) {
      // split the text on the markers, opening/closing marks as we go
      const parts = child.value.split(/([])/)
      for (const part of parts) {
        if (part === CLOZE_START) {
          if (!open) open = []
        } else if (part === CLOZE_END) {
          if (open) {
            out.push(mark(open))
            open = null
          }
        } else if (part) {
          push(text(part))
        }
      }
      continue
    }
    if (child.type === 'element') visit(child)
    push(child as ElementContent)
  }
  if (open) out.push(...open) // unterminated: keep content, drop the marker
  node.children = out as typeof node.children
}
