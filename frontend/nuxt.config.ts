export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  devServer: { host: '127.0.0.1' },
  modules: ['@nuxtjs/tailwindcss'],
  components: [{ path: '~/components', pathPrefix: false }],
  css: ['~/assets/css/tokens.css', '~/assets/css/dashboard-pages.css'],
  /** Dashboard uses vue-chartjs — keep these routes client-only to avoid SSR crashes. */
  routeRules: {
    '/dashboard': { ssr: false },
    '/dashboard/**': { ssr: false },
    '/invest': { ssr: false },
    // Proxy Node backend through Nuxt so cookies are same-origin (avoids SameSite cross-site rejection)
    '/node/**': { proxy: 'http://127.0.0.1:3001/**' },
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
    /**
     * Python FastAPI agent URL (server-side only — never exposed to browser).
     * Override with NUXT_PYTHON_AGENT_URL env var.
     * The Python FastAPI server is started via: cd Hackathon && uvicorn app.main:app --port 8000
     */
    pythonAgentUrl: 'http://127.0.0.1:8000',
    public: {
      /** Python FastAPI base (also used by Node backend proxy). Override with NUXT_PUBLIC_API_BASE */
      apiBase: 'http://127.0.0.1:8000/api',
      /** Node session + chat proxy (backend). Override with NUXT_PUBLIC_AGENT_BASE */
      agentBase: '/node',
      /**
       * Set to 'false' to use AI-powered data from the Python agent.
       * Set to 'true' to always show static demo data (no backend needed).
       * Override with NUXT_PUBLIC_USE_DUMMY_DATA env var.
       */
      useDummyData: 'false',
      /** Site key for Turnstile widget (public). Use Cloudflare test keys locally if needed. */
      turnstileSiteKey: '',
    },
  },
})
