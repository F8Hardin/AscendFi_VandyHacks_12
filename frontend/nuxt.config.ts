export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss', '@nuxtjs/supabase'],
  supabase: {
    redirectOptions: {
      login: '/login',
      callback: '/confirm',
      exclude: ['/login'],
    },
  },
  components: [{ path: '~/components', pathPrefix: false }],
  css: ['~/assets/css/tokens.css'],
  build: {
    transpile: ['chart.js', 'vue-chartjs'],
  },
  vite: {
    optimizeDeps: {
      include: ['chart.js'],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api',
      agentBase: 'http://localhost:3001',
      useDummyData: 'true',
    },
  },
})
