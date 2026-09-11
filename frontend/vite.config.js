import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    // Mismo-origen también en dev (ADR-012, Luis): reenvía /api y /auth al
    // API local, para que api.js pueda usar rutas relativas sin CORS, igual
    // que en producción vía proxy_pass de nginx. No definas
    // VITE_API_BASE_URL en un .env local -- si pones una URL absoluta te
    // saltas este proxy y vuelves a necesitar CORS.
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/auth': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
