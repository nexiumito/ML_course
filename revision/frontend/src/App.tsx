import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppProvider } from './AppContext'
import { Layout } from './components/Layout'
import { Spinner } from './components/ui'
import Home from './pages/Home'

// Review/Browse/Stats pull in KaTeX + markdown: load them on demand to keep the first paint small.
const Review = lazy(() => import('./pages/Review'))
const Browse = lazy(() => import('./pages/Browse'))
const CardPage = lazy(() => import('./pages/CardPage'))
const Stats = lazy(() => import('./pages/Stats'))
const Reports = lazy(() => import('./pages/Reports'))
const Settings = lazy(() => import('./pages/Settings'))
const Gallery = lazy(() => import('./pages/Gallery'))

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Suspense fallback={<Spinner />}>
          <Routes>
            <Route path="/review" element={<Review />} />
            <Route element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="browse" element={<Browse />} />
              <Route path="browse/:id" element={<CardPage />} />
              <Route path="sheet" element={<Gallery />} />
              <Route path="stats" element={<Stats />} />
              <Route path="reports" element={<Reports />} />
              <Route path="settings" element={<Settings />} />
              <Route
                path="*"
                element={<p className="py-10 text-center text-slate-500">Page not found.</p>}
              />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AppProvider>
  )
}
