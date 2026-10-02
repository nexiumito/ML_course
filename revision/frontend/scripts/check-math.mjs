// Render every shown text field of every card through the app's markdown pipeline with KaTeX in strict mode.
// Input: JSON lines {id, field, text} on stdin (produced by `uv run revision content dump-texts`). Exit 1 on any error.
import rehypeKatex from 'rehype-katex'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import { unified } from 'unified'
import { VFile } from 'vfile'
import { normalizeMath } from '../src/lib/markdown.ts'

const input = await new Promise((resolve) => {
  let data = ''
  process.stdin.on('data', (c) => (data += c))
  process.stdin.on('end', () => resolve(data))
})
let errors = 0
let n = 0
for (const line of input.split('\n')) {
  if (!line.trim()) continue
  const { id, field, text } = JSON.parse(line)
  n++
  const warnings = []
  const proc = unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkMath)
    .use(remarkRehype)
    .use(rehypeKatex, { throwOnError: true, strict: (code, msg) => (warnings.push(`${code}: ${msg}`), 'ignore') })
  // rehype-katex reports render failures as vfile messages (it falls back to an error span instead of throwing)
  const file = new VFile(normalizeMath(text))
  try {
    proc.runSync(proc.parse(file), file)
  } catch (e) {
    file.message(String(e.message))
  }
  for (const m of file.messages) {
    errors++
    const cause = m.cause && m.cause.message ? ` — ${m.cause.message.split('\n')[0]}` : ''
    console.log(`ERROR ${id} [${field}]: ${m.reason}${cause}`)
  }
  for (const w of warnings) console.log(`warn  ${id} [${field}]: ${w}`)
}
console.log(`${n} texts checked, ${errors} KaTeX error(s)`)
process.exit(errors ? 1 : 0)
