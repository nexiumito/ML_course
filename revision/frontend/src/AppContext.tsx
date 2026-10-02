import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from './api/client'
import type { Meta, Settings } from './api/types'
import { cachedUi, useTheme } from './hooks/useTheme'

interface Toast {
  id: number
  text: string
  tone: 'info' | 'error' | 'success'
}

interface AppCtx {
  meta: Meta | null
  metaError: string | null
  reloadMeta: () => void
  settings: Settings | null
  saveSettings: (patch: Partial<Settings>) => Promise<void>
  toast: (text: string, tone?: Toast['tone']) => void
  lectureTitle: (id: string) => string
  themeLabel: (id: string) => string
}

const Ctx = createContext<AppCtx | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [metaError, setMetaError] = useState<string | null>(null)
  const [toasts, setToasts] = useState<Toast[]>([])

  const reloadMeta = useCallback(() => {
    api
      .meta()
      .then((m) => {
        setMeta(m)
        setMetaError(null)
      })
      .catch((e: Error) => setMetaError(e.message))
  }, [])
  useEffect(reloadMeta, [reloadMeta])

  const settings = meta?.settings ?? null
  useTheme(settings ?? cachedUi())

  const toast = useCallback((text: string, tone: Toast['tone'] = 'info') => {
    const id = Date.now() + Math.random()
    setToasts((t) => [...t, { id, text, tone }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3500)
  }, [])

  const saveSettings = useCallback(
    async (patch: Partial<Settings>) => {
      try {
        const s = await api.saveSettings(patch)
        setMeta((m) => (m ? { ...m, settings: s } : m))
      } catch (e) {
        toast((e as Error).message, 'error')
        throw e
      }
    },
    [toast],
  )

  const value = useMemo<AppCtx>(
    () => ({
      meta,
      metaError,
      reloadMeta,
      settings,
      saveSettings,
      toast,
      lectureTitle: (id) => meta?.lectures.find((l) => l.id === id)?.title ?? id,
      themeLabel: (id) => meta?.themes.find((t) => t.id === id)?.label ?? id,
    }),
    [meta, metaError, reloadMeta, settings, saveSettings, toast],
  )

  return (
    <Ctx.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 bottom-24 z-50 flex flex-col items-center gap-2 px-4 sm:bottom-6">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`pointer-events-auto max-w-md rounded-xl px-4 py-2.5 text-sm font-medium shadow-lg ${
              t.tone === 'error'
                ? 'bg-red-600 text-white'
                : t.tone === 'success'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900'
            }`}
          >
            {t.text}
          </div>
        ))}
      </div>
    </Ctx.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useApp(): AppCtx {
  const c = useContext(Ctx)
  if (!c) throw new Error('useApp outside AppProvider')
  return c
}
