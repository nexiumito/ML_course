import { useCallback, useEffect, useRef, useState } from 'react'

/** Load data on mount / when deps change; `reload()` refetches. Ignores responses of stale calls. */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const callId = useRef(0)

  const run = useCallback(() => {
    const id = ++callId.current
    setLoading(true)
    fn()
      .then((d) => {
        if (id === callId.current) {
          setData(d)
          setError(null)
        }
      })
      .catch((e: Error) => id === callId.current && setError(e.message))
      .finally(() => id === callId.current && setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    run()
  }, [run])

  return { data, error, loading, reload: run, setData }
}
