export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  components: [{ path: '~/components', pathPrefix: false }],
  css: ['~/assets/css/tokens.css', '~/assets/css/dashboard-pages.css'],
  /** Dashboard uses vue-chartjs — keep these routes client-only to avoid SSR crashes. */
  routeRules: {
    '/dashboard': { ssr: false },
    '/dashboard/**': { ssr: false },
  },
  build: {
    transpile: ['chart.js', 'vue-chartjs'],
  },
  vite: {
    // Dedupe Vue so vue-chartjs never resolves a second runtime (breaks currentRenderingInstance).
    resolve: {
      dedupe: ['vue', 'vue-router', '@vue/runtime-core', '@vue/runtime-dom', '@vue/shared'],
    },
    // Do NOT put vue-chartjs/chart.js in ssr.noExternal — that bundles them into the server
    // build and can trigger "currentRenderingInstance.c(e)" during prerender/SSR.
    optimizeDeps: {
      include: ['vue', 'vue-chartjs', 'chart.js'],
    },
  },
  runtimeConfig: {
    /** Cloudflare Turnstile secret — server-only; see https://developers.cloudflare.com/turnstile/ */
    turnstileSecretKey: '',
    public: {
      /** FastAPI (backend_agent/api). Override with NUXT_PUBLIC_API_BASE */
      apiBase: 'http://localhost:8000/api',
      /** Node session + chat proxy (backend). Override with NUXT_PUBLIC_AGENT_BASE */
      agentBase: 'http://localhost:3120',
      useDummyData: 'true',
      /** Site key for Turnstile widget (public). Use Cloudflare test keys locally if needed. */
      turnstileSiteKey: '',
    },
  },
})
