import { useEffect, useState } from 'react'
import type { Settings as S } from '../api/types'
import { useApp } from '../AppContext'
import { PageTitle } from '../components/Layout'
import { Panel, SectionTitle, Segmented, Spinner, Toggle } from '../components/ui'

export default function Settings() {
  const { settings, saveSettings, toast } = useApp()
  const [retention, setRetention] = useState<number | null>(null)
  useEffect(() => setRetention(settings?.desired_retention ?? null), [settings?.desired_retention])
  if (!settings || retention === null) return <Spinner />

  const save = (patch: Partial<S>) => saveSettings(patch).then(() => toast('Saved', 'success')).catch(() => {})

  return (
    <div className="space-y-5">
      <PageTitle>Settings</PageTitle>

      <Panel>
        <SectionTitle>Scheduling (FSRS)</SectionTitle>
        <div className="space-y-5">
          <div>
            <label htmlFor="retention" className="flex items-baseline justify-between font-medium">
              Desired retention <span className="tabular-nums">{Math.round(retention * 100)}%</span>
            </label>
            <input
              id="retention"
              type="range"
              min={0.8}
              max={0.97}
              step={0.01}
              value={retention}
              onChange={(e) => setRetention(Number(e.target.value))}
              onPointerUp={() => save({ desired_retention: retention })}
              onKeyUp={() => save({ desired_retention: retention })}
              className="mt-2 w-full accent-indigo-600"
            />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Probability of recalling a card when it comes back. Higher = more reviews. 90% is the usual sweet spot.
            </p>
          </div>
          <NumberField label="New items per day" value={settings.new_per_day} min={0} max={500} onSave={(v) => save({ new_per_day: v })} />
          <NumberField
            label="Maximum reviews per day"
            hint="Soft cap: a “Review anyway” button lets you go past it."
            value={settings.max_reviews_per_day}
            min={1}
            max={5000}
            onSave={(v) => save({ max_reviews_per_day: v })}
          />
          <NumberField
            label="Interleave: 1 new item every N reviews"
            value={settings.interleave_ratio}
            min={1}
            max={20}
            onSave={(v) => save({ interleave_ratio: v })}
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="font-medium">New cards order</span>
            <Segmented
              ariaLabel="New cards order"
              value={settings.new_order}
              onChange={(v) => save({ new_order: v })}
              options={[
                { value: 'course', label: 'Course order' },
                { value: 'random', label: 'Random' },
              ]}
            />
          </div>
          <NumberField label="Weak points session size" value={settings.weak_points_n} min={1} max={500} onSave={(v) => save({ weak_points_n: v })} />
          <NumberField label="Default drill size" value={settings.drill_n} min={1} max={500} onSave={(v) => save({ drill_n: v })} />
        </div>
      </Panel>

      <Panel>
        <SectionTitle>Display</SectionTitle>
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="font-medium">Theme</span>
            <Segmented
              ariaLabel="Theme"
              value={settings.theme}
              onChange={(v) => save({ theme: v })}
              options={[
                { value: 'system', label: 'System' },
                { value: 'light', label: 'Light' },
                { value: 'dark', label: 'Dark' },
              ]}
            />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="font-medium">Text size</span>
            <Segmented
              ariaLabel="Text size"
              value={settings.font_size}
              onChange={(v) => save({ font_size: v })}
              options={[
                { value: 'sm', label: 'S' },
                { value: 'md', label: 'M' },
                { value: 'lg', label: 'L' },
                { value: 'xl', label: 'XL' },
              ]}
            />
          </div>
          <Toggle
            checked={settings.swipe}
            onChange={(v) => save({ swipe: v })}
            label="Swipe gestures"
            hint="On a revealed Q→A or cloze card: swipe left = Again, right = Good."
          />
        </div>
      </Panel>

      <Panel>
        <SectionTitle>Data</SectionTitle>
        <p className="mb-3 text-sm text-slate-500 dark:text-slate-400">
          Full JSON dump of your progress (items, review log, reports, settings). Server backups run with{' '}
          <code>uv run revision backup</code>.
        </p>
        <a
          href="/api/export"
          download={`cs433-review-export-${new Date().toISOString().slice(0, 10)}.json`}
          className="inline-flex min-h-11 items-center rounded-xl bg-white px-4 font-medium ring-1 ring-slate-200 hover:bg-slate-50 dark:bg-slate-900 dark:ring-slate-700"
        >
          ⬇ Export JSON
        </a>
      </Panel>
    </div>
  )
}

function NumberField({
  label,
  hint,
  value,
  min,
  max,
  onSave,
}: {
  label: string
  hint?: string
  value: number
  min: number
  max: number
  onSave: (v: number) => void
}) {
  const [v, setV] = useState(String(value))
  useEffect(() => setV(String(value)), [value])
  const commit = () => {
    const n = Math.round(Number(v))
    if (!Number.isFinite(n) || n < min || n > max) {
      setV(String(value))
      return
    }
    if (n !== value) onSave(n)
  }
  const id = label.replace(/\W+/g, '-').toLowerCase()
  return (
    <div className="flex items-center justify-between gap-4">
      <label htmlFor={id}>
        <span className="block font-medium">{label}</span>
        {hint && <span className="block text-sm text-slate-500 dark:text-slate-400">{hint}</span>}
      </label>
      <input
        id={id}
        type="number"
        inputMode="numeric"
        min={min}
        max={max}
        value={v}
        onChange={(e) => setV(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => e.key === 'Enter' && (e.target as HTMLInputElement).blur()}
        className="h-11 w-24 shrink-0 rounded-xl border border-slate-200 bg-white px-3 text-right text-base tabular-nums dark:border-slate-700 dark:bg-slate-950"
      />
    </div>
  )
}
