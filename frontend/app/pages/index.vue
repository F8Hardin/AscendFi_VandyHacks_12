<template>
  <div class="landing">
    <!-- Hero — split layout inspired by clear fintech marketing (e.g. Rocket-style clarity + imagery) -->
    <section class="landing__hero" aria-labelledby="landing-hero-heading">
      <div class="landing__hero-glow" aria-hidden="true" />
      <div class="landing__hero-inner">
        <div class="landing__hero-grid">
          <div class="landing__hero-copy">
            <p class="landing__eyebrow">
              <span class="landing__dot" aria-hidden="true" />
              AI Financial · VandyHacks 12 · Real-time guidance
            </p>

            <h1 id="landing-hero-heading" class="landing__headline">
              <span class="landing__headline-pre">The right plan unlocks</span>
              <span class="landing__headline-emphasis" aria-live="polite">
                <span class="landing__headline-word">lower stress.</span>
                <span class="landing__headline-word">faster payoff.</span>
                <span class="landing__headline-word">real savings.</span>
              </span>
            </h1>

            <p class="landing__lede">
              <strong class="landing__brand-inline">AI Financial</strong> (AscendFi) helps you see risk early, optimize debt,
              understand spending, and build a paycheck plan—so you can move toward stability with confidence.
            </p>

            <div class="landing__hero-cta">
              <NuxtLink
                :to="{ path: '/login', query: { redirect: '/dashboard' } }"
                class="landing__cta landing__cta--primary landing__cta--large"
              >
                See your financial picture
              </NuxtLink>
              <NuxtLink
                :to="{ path: '/login', query: { redirect: '/chat' } }"
                class="landing__cta landing__cta--secondary landing__cta--large"
              >
                Talk to an AI advisor
              </NuxtLink>
            </div>

            <p class="landing__hero-pill-label">Start here</p>
            <div class="landing__hero-pills" role="navigation" aria-label="Quick start options">
              <NuxtLink :to="{ path: '/login', query: { redirect: '/dashboard' } }" class="landing__pill">
                Recovery dashboard
              </NuxtLink>
              <NuxtLink :to="{ path: '/login', query: { redirect: '/chat' } }" class="landing__pill">
                AI chat
              </NuxtLink>
              <NuxtLink to="/product" class="landing__pill">How it works</NuxtLink>
              <NuxtLink to="/resources" class="landing__pill">API &amp; docs</NuxtLink>
            </div>

            <ul class="landing__hero-metrics" aria-label="Product highlights">
              <li><strong>Live</strong> risk &amp; debt signals</li>
              <li><strong>Streaming</strong> AI guidance</li>
              <li><strong>Demo</strong> or your own data</li>
            </ul>
          </div>

          <div class="landing__hero-media">
            <figure
              class="landing__hero-figure"
              @mouseenter="pauseHeroCarousel"
              @mouseleave="resumeHeroCarousel"
              @focusin="pauseHeroCarousel"
              @focusout="resumeHeroCarousel"
            >
              <div class="landing__hero-slides-viewport" aria-roledescription="carousel" aria-label="Financial life imagery">
                <div
                  class="landing__hero-slides-track"
                  :class="{ 'landing__hero-slides-track--no-motion': carouselReducedMotion }"
                  :style="{
                    width: `${heroSlides.length * 100}%`,
                    transform: `translateX(-${(activeHeroSlide * 100) / heroSlides.length}%)`,
                  }"
                >
                  <div
                    v-for="(slide, i) in heroSlides"
                    :key="slide.id"
                    class="landing__hero-slide-pane"
                    :style="{ flex: `0 0 ${100 / heroSlides.length}%` }"
                  >
                    <img
                      class="landing__hero-img"
                      :src="unsplashUrl(slide.photoId, 1600)"
                      :srcset="`${unsplashUrl(slide.photoId, 800)} 800w, ${unsplashUrl(slide.photoId, 1200)} 1200w, ${unsplashUrl(slide.photoId, 1600)} 1600w`"
                      sizes="(max-width: 1024px) 100vw, 46vw"
                      width="1600"
                      height="1067"
                      :alt="slide.alt"
                      :loading="i === 0 ? 'eager' : 'lazy'"
                      :fetchpriority="i === 0 ? 'high' : undefined"
                      decoding="async"
                    />
                  </div>
                </div>

                <div class="landing__hero-dots" role="tablist" aria-label="Choose hero photo">
                  <button
                    v-for="(slide, i) in heroSlides"
                    :key="`dot-${slide.id}`"
                    type="button"
                    role="tab"
                    class="landing__hero-dot"
                    :class="{ 'landing__hero-dot--active': i === activeHeroSlide }"
                    :aria-selected="i === activeHeroSlide"
                    :aria-label="`Show image ${i + 1}: ${slide.shortLabel}`"
                    @click="goToHeroSlide(i)"
                  />
                </div>
              </div>
            </figure>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick action strip (secondary CTAs) -->
    <section class="landing__quick-strip" aria-label="Popular next steps">
      <div class="landing__quick-strip-inner">
        <NuxtLink :to="{ path: '/login', query: { redirect: '/dashboard' } }" class="landing__quick-item">
          <span class="landing__quick-kicker">Step 1</span>
          <span class="landing__quick-title">Open your dashboard</span>
          <span class="landing__quick-desc">KPIs, gauges, and charts with demo data.</span>
        </NuxtLink>
        <NuxtLink :to="{ path: '/login', query: { redirect: '/chat' } }" class="landing__quick-item">
          <span class="landing__quick-kicker">Step 2</span>
          <span class="landing__quick-title">Ask the AI advisor</span>
          <span class="landing__quick-desc">Streaming answers tuned to your situation.</span>
        </NuxtLink>
        <NuxtLink to="/product" class="landing__quick-item">
          <span class="landing__quick-kicker">Learn</span>
          <span class="landing__quick-title">Explore the product</span>
          <span class="landing__quick-desc">Five capabilities for financial recovery.</span>
        </NuxtLink>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="landing__section">
      <div class="landing__section-inner">
        <h2 class="landing__section-title">Four engines, one ascent</h2>
        <p class="landing__section-sub">
          Everything in the product maps to how you actually recover—not generic tips.
        </p>
        <div class="landing__grid">
          <article class="landing__card">
            <div class="landing__card-icon" style="--icon-bg: var(--color-danger-dim); --icon-fg: var(--color-danger)">◎</div>
            <h3 class="landing__card-title">Predictive risk</h3>
            <p class="landing__card-body">
              Surface missing-payment risk, overdraft probability, and credit-shift signals before they hit your account.
            </p>
          </article>
          <article class="landing__card">
            <div class="landing__card-icon" style="--icon-bg: var(--color-primary-glow); --icon-fg: var(--color-primary)">◇</div>
            <h3 class="landing__card-title">Debt optimization</h3>
            <p class="landing__card-body">
              Compare avalanche, snowball, and hybrid strategies with a month-by-month payoff plan and interest saved.
            </p>
          </article>
          <article class="landing__card">
            <div class="landing__card-icon" style="--icon-bg: var(--color-info-dim); --icon-fg: var(--color-info)">◎</div>
            <h3 class="landing__card-title">Behavioral spending</h3>
            <p class="landing__card-body">
              Spot category patterns, anomalies, and life-event-driven spending so advice matches your reality.
            </p>
          </article>
          <article class="landing__card">
            <div class="landing__card-icon" style="--icon-bg: var(--color-warning-dim); --icon-fg: var(--color-warning)">▣</div>
            <h3 class="landing__card-title">Autonomous finance</h3>
            <p class="landing__card-body">
              Get a recommended paycheck split, emergency-fund targets, and investment suggestions tuned to your state.
            </p>
          </article>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how" class="landing__section landing__section--alt">
      <div class="landing__section-inner">
        <h2 class="landing__section-title">How it works</h2>
        <p class="landing__section-sub">From raw context to a plan you can act on today.</p>
        <ol class="landing__steps">
          <li class="landing__step">
            <span class="landing__step-num">1</span>
            <div>
              <h3 class="landing__step-title">Connect context</h3>
              <p class="landing__step-body">
                Start with demo data or your own profile—debts, income, balances, and spending shape every model call.
              </p>
            </div>
          </li>
          <li class="landing__step">
            <span class="landing__step-num">2</span>
            <div>
              <h3 class="landing__step-title">Run the engines</h3>
              <p class="landing__step-body">
                FastAPI routes power risk, debt, spending, and autonomous planning behind one agent interface.
              </p>
            </div>
          </li>
          <li class="landing__step">
            <span class="landing__step-num">3</span>
            <div>
              <h3 class="landing__step-title">Act with AI</h3>
              <p class="landing__step-body">
                Use the dashboard for signals and charts, then go deeper in streaming chat with your financial context.
              </p>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <!-- CTA -->
    <section class="landing__cta-band">
      <div class="landing__cta-inner">
        <h2 class="landing__cta-title">Ready to see your recovery path?</h2>
        <p class="landing__cta-sub">Open the dashboard with demo data or jump straight into the advisor.</p>
        <div class="landing__hero-cta landing__hero-cta--center">
          <NuxtLink
            :to="{ path: '/login', query: { redirect: '/dashboard' } }"
            class="landing__cta landing__cta--primary"
          >
            Get started
          </NuxtLink>
          <NuxtLink
            :to="{ path: '/login', query: { redirect: '/chat' } }"
            class="landing__cta landing__cta--secondary"
          >
            Start chatting
          </NuxtLink>
          <NuxtLink to="/resources" class="landing__cta landing__cta--ghost">Developer resources</NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'marketing',
})

function unsplashUrl(photoId: string, w: number) {
  return `https://images.unsplash.com/${photoId}?auto=format&fit=crop&w=${w}&q=${w >= 1600 ? 85 : 80}`
}

/** Unsplash — free photos; see https://unsplash.com/license */
const heroSlides = [
  {
    id: 'h1',
    photoId: 'photo-1600585154340-be6161a56a0c',
    shortLabel: 'Modern home',
    alt: 'Modern home at dusk—stability and long-term financial planning.',
  },
  {
    id: 'h2',
    photoId: 'photo-1600596542815-ffad4c1539a9',
    shortLabel: 'Bright living space',
    alt: 'Sunlit living room—comfort and clarity at home.',
  },
  {
    id: 'h3',
    photoId: 'photo-1554224155-6726b3ff858f',
    shortLabel: 'Planning at a desk',
    alt: 'Hands reviewing finances on a laptop—planning and decisions.',
  },
  {
    id: 'h4',
    photoId: 'photo-1560518883-ce09059eeffa',
    shortLabel: 'Keys to a new chapter',
    alt: 'House keys on a table—new home and financial milestones.',
  },
] as const

const activeHeroSlide = ref(0)
const carouselPaused = ref(false)
const carouselReducedMotion = ref(false)

let heroCarouselTimer: ReturnType<typeof setInterval> | null = null

const HERO_CAROUSEL_MS = 5200

function goToHeroSlide(i: number) {
  activeHeroSlide.value = ((i % heroSlides.length) + heroSlides.length) % heroSlides.length
}

function startHeroCarouselTimer() {
  stopHeroCarouselTimer()
  if (carouselReducedMotion.value) return
  heroCarouselTimer = setInterval(() => {
    if (!carouselPaused.value) {
      goToHeroSlide(activeHeroSlide.value + 1)
    }
  }, HERO_CAROUSEL_MS)
}

function stopHeroCarouselTimer() {
  if (heroCarouselTimer) {
    clearInterval(heroCarouselTimer)
    heroCarouselTimer = null
  }
}

function pauseHeroCarousel() {
  carouselPaused.value = true
}

function resumeHeroCarousel() {
  carouselPaused.value = false
}

onMounted(() => {
  if (import.meta.client) {
    carouselReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    startHeroCarouselTimer()
  }
})

onUnmounted(() => {
  stopHeroCarouselTimer()
})

const heroImagePreload = unsplashUrl(heroSlides[0]!.photoId, 1600)

useHead({
  title: 'AI Financial — AI financial recovery',
  meta: [
    {
      name: 'description',
      content:
        'Predict risk, optimize debt, understand spending behavior, and build autonomous finance plans with AscendFi.',
    },
  ],
  link: [{ rel: 'preload', as: 'image', href: heroImagePreload }],
})
</script>

<style scoped>
.landing {
  --landing-max: 1120px;
}

.landing__hero {
  position: relative;
  padding: clamp(2.5rem, 6vw, 4rem) 1.5rem clamp(3rem, 7vw, 5rem);
  overflow: hidden;
}

.landing__hero-glow {
  position: absolute;
  inset: -35% -15% auto -15%;
  height: min(75vh, 560px);
  background:
    radial-gradient(ellipse 50% 45% at 18% 20%, color-mix(in srgb, var(--color-primary) 10%, transparent), transparent 65%),
    radial-gradient(ellipse 45% 40% at 85% 10%, rgba(37, 99, 235, 0.06), transparent 60%),
    radial-gradient(ellipse 40% 35% at 50% 0%, rgba(255, 255, 255, 0.9), transparent 55%);
  pointer-events: none;
}

.landing__hero-inner {
  position: relative;
  max-width: var(--landing-max);
  margin: 0 auto;
}

.landing__hero-grid {
  display: grid;
  gap: clamp(2rem, 5vw, 3.5rem);
  align-items: center;
}

@media (min-width: 1024px) {
  .landing__hero-grid {
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    gap: 3rem 2.5rem;
  }
}

.landing__hero-copy {
  animation: rise 0.75s ease-out both;
}

.landing__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 1.1rem;
}

.landing__dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}

.landing__headline {
  margin: 0 0 1.25rem;
  font-size: clamp(2rem, 4.2vw, 3.15rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.08;
  color: var(--color-text);
  max-width: 20ch;
}

.landing__headline-pre {
  display: block;
  font-weight: 600;
  color: var(--color-text);
}

.landing__headline-emphasis {
  display: block;
  margin-top: 0.2em;
  position: relative;
  min-height: 1.2em;
  color: var(--color-primary);
  font-weight: 800;
}

.landing__headline-word {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  opacity: 0;
  transform: translateY(10px);
}

.landing__headline-word:nth-child(1) {
  animation: heroWord1 9s ease-in-out infinite;
}

.landing__headline-word:nth-child(2) {
  animation: heroWord2 9s ease-in-out infinite;
}

.landing__headline-word:nth-child(3) {
  animation: heroWord3 9s ease-in-out infinite;
}

@keyframes heroWord1 {
  0%,
  3% {
    opacity: 0;
    transform: translateY(10px);
  }
  6%,
  28% {
    opacity: 1;
    transform: translateY(0);
  }
  31%,
  100% {
    opacity: 0;
    transform: translateY(-8px);
  }
}

@keyframes heroWord2 {
  0%,
  30% {
    opacity: 0;
    transform: translateY(10px);
  }
  33%,
  61% {
    opacity: 1;
    transform: translateY(0);
  }
  64%,
  100% {
    opacity: 0;
    transform: translateY(-8px);
  }
}

@keyframes heroWord3 {
  0%,
  63% {
    opacity: 0;
    transform: translateY(10px);
  }
  66%,
  93% {
    opacity: 1;
    transform: translateY(0);
  }
  96%,
  100% {
    opacity: 0;
    transform: translateY(-8px);
  }
}

.landing__lede {
  font-size: clamp(1rem, 1.5vw, 1.125rem);
  line-height: 1.65;
  color: var(--color-text-muted);
  max-width: 36rem;
  margin-bottom: 1.75rem;
}

.landing__brand-inline {
  color: var(--color-text);
  font-weight: 600;
}

.landing__hero-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.landing__hero-cta--center {
  justify-content: center;
}

.landing__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.35rem;
  border-radius: 0.625rem;
  font-size: 0.9375rem;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.18s ease, filter 0.18s ease, background 0.18s ease, border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.landing__cta--large {
  padding: 0.85rem 1.5rem;
  font-size: 1rem;
  border-radius: 0.75rem;
}

.landing__cta:hover {
  transform: translateY(-2px);
}

.landing__cta--primary {
  background: var(--color-primary);
  color: var(--color-on-primary);
  box-shadow: 0 2px 8px color-mix(in srgb, var(--color-primary) 35%, transparent);
}

.landing__cta--primary:hover {
  filter: brightness(1.05);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--color-primary) 28%, transparent);
}

.landing__cta--secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border-strong);
  box-shadow: var(--shadow-card);
}

.landing__cta--secondary:hover {
  background: var(--color-surface-raised);
  border-color: var(--color-text-faint);
}

.landing__cta--ghost {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid transparent;
  font-weight: 600;
}

.landing__cta--ghost:hover {
  background: var(--color-primary-glow);
}

.landing__hero-pill-label {
  margin: 0 0 0.5rem;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}

.landing__hero-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.75rem;
}

.landing__pill {
  display: inline-flex;
  align-items: center;
  padding: 0.45rem 0.9rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.landing__pill:hover {
  border-color: color-mix(in srgb, var(--color-primary) 35%, var(--color-border));
  background: var(--color-primary-glow);
  color: var(--color-primary-dim);
}

.landing__hero-media {
  animation: rise 0.85s ease-out 0.08s both;
}

@media (max-width: 1023px) {
  .landing__hero-media {
    order: -1;
  }
}

.landing__hero-figure {
  margin: 0;
  position: relative;
  border-radius: 1.25rem;
  box-shadow:
    var(--shadow-card-hover),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
  background: var(--color-surface-raised);
}

.landing__hero-slides-viewport {
  position: relative;
  overflow: hidden;
  border-radius: 1.25rem;
  aspect-ratio: 1600 / 1067;
}

.landing__hero-slides-track {
  display: flex;
  height: 100%;
  transition: transform 0.85s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

.landing__hero-slides-track--no-motion {
  transition: none;
}

.landing__hero-slide-pane {
  height: 100%;
  min-height: 0;
}

.landing__hero-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.landing__hero-dots {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0.65rem;
  display: flex;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.5rem;
  z-index: 2;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.35) 0%, transparent 100%);
  border-radius: 0 0 1.2rem 1.2rem;
}

.landing__hero-dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border: none;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.landing__hero-dot:hover {
  background: rgba(255, 255, 255, 0.85);
  transform: scale(1.15);
}

.landing__hero-dot--active {
  background: #fff;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 65%, transparent);
  transform: scale(1.2);
}

.landing__hero-dot:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.landing__hero-metrics {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 1.75rem;
  font-size: 0.8125rem;
  color: var(--color-text-faint);
}

.landing__hero-metrics strong {
  color: var(--color-text-muted);
  font-weight: 600;
}

/* Quick strip — secondary paths (Rocket-style “Buying | Refinancing | Rates”) */
.landing__quick-strip {
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  padding: 0;
}

.landing__quick-strip-inner {
  max-width: var(--landing-max);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .landing__quick-strip-inner {
    grid-template-columns: repeat(3, 1fr);
  }
}

.landing__quick-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1.35rem 1.5rem;
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.18s ease;
}

@media (min-width: 768px) {
  .landing__quick-item {
    border-bottom: none;
    border-right: 1px solid var(--color-border);
  }

  .landing__quick-item:last-child {
    border-right: none;
  }
}

.landing__quick-item:hover {
  background: var(--color-bg-subtle);
}

.landing__quick-kicker {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.landing__quick-title {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.landing__quick-desc {
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}

.landing__section {
  padding: 4rem 1.5rem;
}

.landing__section--alt {
  background: var(--color-bg-subtle);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.landing__section-inner {
  max-width: var(--landing-max);
  margin: 0 auto;
}

.landing__section-title {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.landing__section-sub {
  font-size: 1rem;
  color: var(--color-text-muted);
  max-width: 36rem;
  margin-bottom: 2.5rem;
  line-height: 1.55;
}

.landing__grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .landing__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.landing__card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.landing__section--alt .landing__card {
  background: var(--color-surface);
}

.landing__card:hover {
  border-color: color-mix(in srgb, var(--color-primary) 28%, var(--color-border));
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

.landing__card-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  background: var(--icon-bg);
  color: var(--icon-fg);
  margin-bottom: 1rem;
}

.landing__card-title {
  font-size: 1.0625rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.landing__card-body {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-text-muted);
}

.landing__steps {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 40rem;
}

.landing__step {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
}

.landing__step-num {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: var(--color-primary-glow);
  color: var(--color-primary);
  font-weight: 800;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.landing__step-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.landing__step-body {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-text-muted);
}

.landing__cta-band {
  padding: 4.5rem 1.5rem;
}

.landing__cta-inner {
  max-width: 36rem;
  margin: 0 auto;
  text-align: center;
}

.landing__cta-title {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.landing__cta-sub {
  font-size: 0.9375rem;
  color: var(--color-text-muted);
  margin-bottom: 1.75rem;
  line-height: 1.55;
}

@media (prefers-reduced-motion: reduce) {
  .landing__card:hover {
    transform: none;
  }

  .landing__headline-word {
    animation: none !important;
    position: static;
    opacity: 1;
    transform: none;
  }

  .landing__headline-word:nth-child(2),
  .landing__headline-word:nth-child(3) {
    display: none;
  }

  .landing__headline-emphasis {
    min-height: 0;
  }

  .landing__hero-slides-track {
    transition: none;
  }
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
