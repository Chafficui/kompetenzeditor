export default defineNuxtConfig({
  compatibilityDate: '2025-05-13',
  devtools: { enabled: true },
  modules: ['@pinia/nuxt'],
  css: [
    '@mdi/font/css/materialdesignicons.css',
    '~/assets/css/main.css',
    '~/assets/css/editor.css',
  ],
  build: { transpile: ['vuetify'] },
  routeRules: { '/**': { ssr: false } },
  vite: {
    optimizeDeps: {
      include: ['dexie'],
    },
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          rewrite: (path: string) => path.replace(/^\/api/, ''),
        },
      },
    },
  },
})
