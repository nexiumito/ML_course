import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

const backend = 'http://127.0.0.1:8433'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'CS-433 Review',
        short_name: 'CS-433',
        description: 'Spaced-repetition revision for EPFL CS-433 Machine Learning',
        theme_color: '#1e3a8a',
        background_color: '#0b1020',
        display: 'standalone',
        start_url: '/',
        icons: [{ src: 'favicon.svg', sizes: 'any', type: 'image/svg+xml' }],
      },
      workbox: {
        // App shell only: the API, PDFs and page renders are network-only.
        navigateFallbackDenylist: [/^\/api\//, /^\/files\//, /^\/content-img\//],
        runtimeCaching: [],
      },
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': backend,
      '/files': backend,
      '/content-img': backend,
    },
  },
})
