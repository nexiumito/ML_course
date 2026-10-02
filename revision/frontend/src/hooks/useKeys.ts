import { useEffect, useLayoutEffect, useRef } from 'react'

/** Global keydown handler, ignored while typing in a field or when a modifier is held. */
export function useKeys(handler: (e: KeyboardEvent) => void, enabled = true) {
  const ref = useRef(handler)
  useLayoutEffect(() => {
    ref.current = handler
  })
  useEffect(() => {
    if (!enabled) return
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return
      const t = e.target as HTMLElement | null
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return
      ref.current(e)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [enabled])
}
