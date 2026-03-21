export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  css: ['~/assets/css/tokens.css'],
  build: {
    transpile: ['chart.js'],
  },
  vite: {
    optimizeDeps: {
      include: ['chart.js', 'chart.js/auto'],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api',
      useDummyData: 'true',
    },
  },
})
