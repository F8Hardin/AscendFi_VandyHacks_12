export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  css: ['~/assets/css/tokens.css'],
  build: {
    transpile: ['chart.js', 'vue-chartjs'],
  },
  vite: {
    // Avoid "null is not an object (reading 'currentRenderingInstance.ce')" during SSR
    // when multiple Vue copies get bundled (vue-chartjs, @nuxtjs/tailwindcss, etc.).
    resolve: {
      dedupe: ['vue', 'vue-router'],
    },
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
