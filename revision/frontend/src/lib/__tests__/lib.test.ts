import type { Root } from 'hast'
import { describe, expect, it } from 'vitest'
import { formatInterval } from '../format'
import { normalizeMath } from '../markdown'
import { CLOZE_END, CLOZE_START, rehypeCloze } from '../rehypeCloze'
import { emptySpec, specFromSearch, specToSearch } from '../session'
import { choiceOrder } from '../shuffle'
import { previewText } from '../text'

describe('normalizeMath', () => {
  it('turns one-line $$…$$ into a display block', () => {
    expect(normalizeMath('leads to $$x = 1$$ end')).toBe('leads to \n\n$$\nx = 1\n$$\n\n end')
  })
  it('keeps existing blocks valid and escaped dollars untouched', () => {
    const out = normalizeMath('$$\na\n$$')
    expect(out).toContain('$$\na\n$$')
    expect(normalizeMath('costs \\$$5')).toBe('costs \\$$5')
  })
  it('uses displaystyle for inline fractions only', () => {
    expect(normalizeMath('a $\\frac{1}{2}$ b')).toBe('a $\\displaystyle \\frac{1}{2}$ b')
    expect(normalizeMath('a $x^2$ b')).toBe('a $x^2$ b')
    expect(normalizeMath('$\\displaystyle \\frac{1}{2}$')).toBe('$\\displaystyle \\frac{1}{2}$')
  })
  it('does not treat display blocks as inline math', () => {
    expect(normalizeMath('$$\\frac{a}{b}$$')).toBe('\n\n$$\n\\frac{a}{b}\n$$\n\n')
  })
  it('works right after a cloze marker', () => {
    expect(normalizeMath(`${CLOZE_START}$\\sqrt{\\frac{a}{b}}$${CLOZE_END}`)).toBe(
      `${CLOZE_START}$\\displaystyle \\sqrt{\\frac{a}{b}}$${CLOZE_END}`,
    )
  })
})

describe('rehypeCloze', () => {
  const run = (tree: Root) => {
    rehypeCloze()(tree)
    return tree
  }
  it('wraps the marked span, across element siblings, in <mark>', () => {
    const tree: Root = {
      type: 'root',
      children: [
        {
          type: 'element',
          tagName: 'p',
          properties: {},
          children: [
            { type: 'text', value: `bound ${CLOZE_START}` },
            { type: 'element', tagName: 'span', properties: { className: ['katex'] }, children: [] },
            { type: 'text', value: `${CLOZE_END} end` },
          ],
        },
      ],
    }
    const p = run(tree).children[0] as any
    expect(p.children.map((c: any) => c.tagName ?? c.value)).toEqual(['bound ', 'mark', ' end'])
    expect(p.children[1].children[0].tagName).toBe('span')
  })
  it('handles a marker pair inside one text node and drops unmatched markers', () => {
    const tree: Root = { type: 'root', children: [{ type: 'text', value: `a ${CLOZE_START}[…]${CLOZE_END} b ${CLOZE_END}` }] }
    const out = run(tree).children as any[]
    expect(out.map((c) => c.tagName ?? c.value)).toEqual(['a ', 'mark', ' b '])
    expect(out[1].children[0].value).toBe('[…]')
  })
})

describe('choiceOrder', () => {
  it('is a stable permutation for a seed', () => {
    const a = choiceOrder(5, true, 'seed')
    expect([...a].sort()).toEqual([0, 1, 2, 3, 4])
    expect(choiceOrder(5, true, 'seed')).toEqual(a)
  })
  it('keeps the order when shuffle is off', () => {
    expect(choiceOrder(4, false, 'x')).toEqual([0, 1, 2, 3])
  })
})

describe('study spec <-> URL', () => {
  it('round-trips', () => {
    const spec = { ...emptySpec('drill'), weeks: [3, 4], lectures: ['04a'], themes: ['ridge'], core: true, limit: 15 }
    expect(specFromSearch(new URLSearchParams(specToSearch(spec)))).toEqual(spec)
  })
  it('defaults unknown modes to study', () => {
    expect(specFromSearch(new URLSearchParams('mode=nope')).mode).toBe('study')
  })
})

describe('formatInterval / previewText', () => {
  it('formats intervals compactly', () => {
    expect(formatInterval(30)).toBe('<1m')
    expect(formatInterval(600)).toBe('10m')
    expect(formatInterval(3 * 3600)).toBe('3h')
    expect(formatInterval(8 * 86400)).toBe('8d')
    expect(formatInterval(90 * 86400)).toBe('3mo')
    expect(formatInterval(800 * 86400)).toBe('2.2y')
  })
  it('strips markup and shows cloze answers', () => {
    expect(previewText('*(Ridge)* cost {{c1::$O(N)$::rate}} of **it**')).toBe('(Ridge) cost O(N) of it')
  })
})
