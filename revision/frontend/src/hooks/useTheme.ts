import { useEffect } from 'react'
import type { Settings } from '../api/types'

const KEY = 'cs433-ui'

/** Last-known UI prefs, so the page does not flash the wrong theme before /api/meta answers. */
export function cachedUi(): Pick<Settings, 'theme' | 'font_size'> {
  try {
    const raw = localStorage.getItem(KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    /* storage unavailable */
  }
  return { theme: 'system', font_size: 'md' }
}

export function applyUi(ui: Pick<Settings, 'theme' | 'font_size'>) {
  const dark =
    ui.theme === 'dark' || (ui.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', dark)
  document.documentElement.dataset.font = ui.font_size
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#020617' : '#f8fafc')
  try {
    localStorage.setItem(KEY, JSON.stringify(ui))
  } catch {
    /* storage unavailable */
  }
}

export function useTheme(ui: Pick<Settings, 'theme' | 'font_size'>) {
  useEffect(() => {
    applyUi(ui)
    if (ui.theme !== 'system') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const onChange = () => applyUi(ui)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [ui.theme, ui.font_size]) // eslint-disable-line react-hooks/exhaustive-deps
}
