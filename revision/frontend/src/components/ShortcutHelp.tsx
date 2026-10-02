import { Sheet } from './ui'

const ROWS: [string, string][] = [
  ['Space / Enter', 'Reveal · then Good · Continue'],
  ['1 2 3 4', 'Again · Hard · Good · Easy (self-graded)'],
  ['1–6 or A–F', 'Select a choice (multiple choice)'],
  ['Enter', 'Check answer / continue'],
  ['T / F  or  ← / →', 'Answer True / False'],
  ['G', 'Toggle "I guessed" (correct ⇒ Hard)'],
  ['E', 'Toggle "Too easy" (correct ⇒ Easy)'],
  ['U', 'Undo last review'],
  ['S', 'Show source (slide / exam page)'],
  ['R', 'Flag this card'],
  ['Esc', 'End session'],
  ['?', 'This help'],
]

export function ShortcutHelp({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Sheet open={open} onClose={onClose} title="Keyboard shortcuts">
      <table className="w-full text-sm">
        <tbody>
          {ROWS.map(([k, v]) => (
            <tr key={k} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
              <td className="py-2 pr-4 font-mono text-xs whitespace-nowrap text-slate-700 dark:text-slate-200">{k}</td>
              <td className="py-2 text-slate-600 dark:text-slate-300">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Sheet>
  )
}
