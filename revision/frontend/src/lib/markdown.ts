/**
 * Pre-processing of card markdown before remark-math:
 * 1. remark-math treats `$$…$$` written on one line (or inside a paragraph) as *inline* math, which renders
 *    in cramped text style. Turn every `$$…$$` into a proper display block (`$$` on their own lines).
 * 2. Inline fractions (`$…\frac…$`) are rendered in text style by default, which squeezes numerator and
 *    denominator into the line height. Prefix such inline formulas with `\displaystyle` so they keep full size.
 */
export function normalizeMath(src: string): string {
  const blocks = src.replace(
    /(^|[^\\])\$\$([\s\S]+?)\$\$/g,
    (_m, pre: string, body: string) => `${pre}\n\n$$\n${body.trim()}\n$$\n\n`,
  )
  return blocks.replace(/(^|[^\\$])\$(?!\$)((?:\\\$|[^$])+?)\$(?!\$)/g, (m, pre: string, body: string) =>
    /\\(frac|sqrt\{\\frac)/.test(body) && !/\\displaystyle/.test(body) ? `${pre}$\\displaystyle ${body}$` : m,
  )
}
