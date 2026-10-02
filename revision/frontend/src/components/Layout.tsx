import type { ReactNode } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useApp } from '../AppContext'

const LINKS = [
  { to: '/', label: 'Home', icon: '⌂' },
  { to: '/browse', label: 'Browse', icon: '☰' },
  { to: '/stats', label: 'Stats', icon: '▤' },
  { to: '/reports', label: 'Reports', icon: '⚑' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
]

export function Layout() {
  const { metaError, reloadMeta } = useApp()
  return (
    <div className="min-h-dvh">
      <header className="pt-safe sticky top-0 z-30 hidden border-b border-slate-200 bg-slate-50/90 backdrop-blur sm:block dark:border-slate-800 dark:bg-slate-950/90">
        <nav className="px-safe mx-auto flex max-w-5xl items-center gap-1 py-2">
          <span className="mr-4 font-semibold tracking-tight">
            CS-433 <span className="text-indigo-600 dark:text-indigo-400">Review</span>
          </span>
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive
                    ? 'bg-white text-slate-900 shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:text-white dark:ring-slate-700'
                    : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </header>
      {metaError && (
        <div className="bg-red-600 px-4 py-2 text-center text-sm text-white" role="alert">
          {metaError}{' '}
          <button type="button" className="underline" onClick={reloadMeta}>
            Retry
          </button>
        </div>
      )}
      <main className="pt-safe px-safe mx-auto max-w-5xl pt-4 pb-28 sm:pt-6 sm:pb-12">
        <Outlet />
      </main>
      <nav
        aria-label="Main"
        className="pb-safe fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 border-t border-slate-200 bg-white/95 backdrop-blur sm:hidden dark:border-slate-800 dark:bg-slate-950/95"
      >
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            className={({ isActive }) =>
              `flex min-h-14 flex-col items-center justify-center gap-0.5 text-[0.7rem] font-medium ${
                isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400'
              }`
            }
          >
            <span className="text-lg leading-none" aria-hidden="true">
              {l.icon}
            </span>
            {l.label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}

export function PageTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">
      <h1 className="text-2xl font-semibold tracking-tight">{children}</h1>
      {right}
    </div>
  )
}
