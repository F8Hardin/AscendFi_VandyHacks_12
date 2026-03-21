export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  css: ['~/assets/css/tokens.css'],
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api',
      useDummyData: 'true', // overridden by NUXT_PUBLIC_USE_DUMMY_DATA env var
    },
  },
})
