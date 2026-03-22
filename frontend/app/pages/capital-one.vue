<template>
  <div class="co1">
    <div v-if="pending" class="co1__state">Loading…</div>
    <div v-else-if="error" class="co1__state co1__state--err">
      Something went wrong.
      <button type="button" class="co1__retry" @click="refresh()">Try again</button>
    </div>

    <template v-else-if="payload">
      <!-- Hero -->
      <header class="co1__hero">
        <div class="co1__hero-media">
          <img
            class="co1__hero-img"
            :src="payload.hero.image"
            :alt="payload.hero.imageAlt"
            width="1600"
            height="900"
            loading="eager"
            decoding="async"
            referrerpolicy="no-referrer"
            @error="onCoImgError"
          />
          <div class="co1__hero-shade" aria-hidden="true" />
        </div>
        <div class="co1__hero-copy">
          <p class="co1__eyebrow">Educational overview · Not sponsored</p>
          <h1 class="co1__title">{{ payload.hero.title }}</h1>
          <p class="co1__subtitle">{{ payload.hero.subtitle }}</p>
        </div>
      </header>

      <div class="co1__notice" role="status">
        <span class="co1__notice-icon" aria-hidden="true">!</span>
        <p class="co1__notice-text">{{ payload.disclaimer }}</p>
      </div>

      <!-- Tools -->
      <section class="co1__block" aria-labelledby="co1-tools">
        <div class="co1__block-head">
          <h2 id="co1-tools" class="co1__h2">Apps &amp; tools</h2>
          <p class="co1__lede">Free add-ons many customers use next to their card or bank account.</p>
        </div>
        <div class="co1__tools">
          <a
            v-for="e in payload.ecosystem"
            :key="e.id"
            :href="e.url"
            target="_blank"
            rel="noopener noreferrer"
            class="co1__tool"
          >
            <div class="co1__tool-img-wrap">
              <img
                class="co1__tool-img"
                :src="e.image"
                :alt="e.imageAlt"
                width="800"
                height="520"
                loading="lazy"
                decoding="async"
                referrerpolicy="no-referrer"
                @error="onCoImgError"
              />
            </div>
            <div class="co1__tool-body">
              <h3 class="co1__tool-title">{{ e.title }}</h3>
              <p class="co1__tool-desc">{{ e.description }}</p>
              <span class="co1__tool-cta">Open on Capital One →</span>
            </div>
          </a>
        </div>
      </section>

      <!-- Categories -->
      <section v-for="cat in payload.categories" :key="cat.id" class="co1__block co1__cat">
        <div class="co1__cat-banner">
          <img
            class="co1__cat-banner-img"
            :src="cat.image"
            :alt="cat.imageAlt"
            width="1200"
            height="480"
            loading="lazy"
            decoding="async"
            referrerpolicy="no-referrer"
            @error="onCoImgError"
          />
          <div class="co1__cat-banner-cap">
            <h2 class="co1__cat-title">{{ cat.title }}</h2>
            <a :href="cat.hubUrl" target="_blank" rel="noopener noreferrer" class="co1__cat-hub">See all on capitalone.com →</a>
          </div>
        </div>
        <p class="co1__cat-blurb">{{ cat.blurb }}</p>
        <div class="co1__cards">
          <article v-for="o in cat.offers" :key="o.id" class="co1__card">
            <div class="co1__card-img-wrap">
              <img
                class="co1__card-img"
                :src="o.image"
                :alt="o.imageAlt"
                width="720"
                height="400"
                loading="lazy"
                decoding="async"
                referrerpolicy="no-referrer"
                @error="onCoImgError"
              />
            </div>
            <div class="co1__card-body">
              <h3 class="co1__card-name">{{ o.name }}</h3>
              <p class="co1__card-pitch">{{ o.pitch }}</p>
              <ul class="co1__card-list">
                <li v-for="(h, i) in o.highlights" :key="i">{{ h }}</li>
              </ul>
              <a :href="o.url" target="_blank" rel="noopener noreferrer" class="co1__card-btn">Details &amp; apply</a>
            </div>
          </article>
        </div>
      </section>

      <section class="co1__foot">
        <h2 class="co1__h2 co1__h2--sm">Use this with AscendFi</h2>
        <p class="co1__foot-p">
          Check <NuxtLink to="/dashboard/debt">Debt &amp; predictions</NuxtLink> before taking on a new payment. Ask the
          <NuxtLink to="/chat">AI Advisor</NuxtLink> how a new account fits your next few months.
        </p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  ssr: false,
})

type Offer = {
  id: string
  name: string
  pitch: string
  highlights: string[]
  url: string
  image: string
  imageAlt: string
}

type Category = {
  id: string
  title: string
  blurb: string
  hubUrl: string
  image: string
  imageAlt: string
  offers: Offer[]
}

type Payload = {
  disclaimer: string
  hero: { image: string; imageAlt: string; title: string; subtitle: string }
  ecosystem: {
    id: string
    title: string
    description: string
    url: string
    image: string
    imageAlt: string
  }[]
  categories: Category[]
}

const { data, pending, error, refresh } = await useFetch<Payload>('/api/capital-one-offers', {
  key: 'capital-one-offers',
})

const payload = computed(() => data.value ?? null)

const CO_IMG_FALLBACK = '/images/co-fallback.svg'

function onCoImgError(e: Event) {
  const el = e.target as HTMLImageElement | null
  if (!el || el.dataset.coFallback === '1') return
  el.dataset.coFallback = '1'
  el.src = CO_IMG_FALLBACK
}

useHead({
  title: 'Capital One — AI Financial',
  meta: [{ name: 'description', content: 'Illustrated overview of Capital One cards, banking, and auto—with links to official offers.' }],
})
</script>

<style scoped>
.co1 {
  max-width: 56rem;
  margin: 0 auto;
  padding-bottom: 2rem;
}

.co1__state {
  padding: 1.25rem;
  border-radius: 0.75rem;
  background: var(--color-surface-raised);
  color: var(--color-text-muted);
  font-size: 0.9rem;
}
.co1__state--err {
  border: 1px solid color-mix(in srgb, #dc2626 35%, var(--color-border));
}
.co1__retry {
  margin-left: 0.5rem;
  padding: 0.35rem 0.75rem;
  border-radius: 0.45rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-weight: 600;
  cursor: pointer;
}

/* Hero */
.co1__hero {
  position: relative;
  border-radius: 1.125rem;
  overflow: hidden;
  margin-bottom: 1.25rem;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.12);
}
.co1__hero-media {
  position: relative;
  aspect-ratio: 16 / 9;
  min-height: 220px;
  background: #0f172a;
}
@media (max-width: 640px) {
  .co1__hero-media {
    aspect-ratio: 4 / 3;
    min-height: 200px;
  }
}
.co1__hero-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  display: block;
}
.co1__hero-shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, rgba(15, 23, 42, 0.88) 0%, rgba(15, 23, 42, 0.45) 55%, transparent 100%);
}
.co1__hero-copy {
  position: absolute;
  left: 0;
  bottom: 0;
  right: 0;
  padding: 1.35rem 1.5rem 1.5rem;
  max-width: 26rem;
}
.co1__eyebrow {
  margin: 0 0 0.4rem;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.72);
}
.co1__title {
  margin: 0;
  font-size: clamp(1.75rem, 4vw, 2.35rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #fff;
  line-height: 1.1;
}
.co1__subtitle {
  margin: 0.5rem 0 0;
  font-size: 0.95rem;
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.88);
}

.co1__notice {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  padding: 1rem 1.1rem;
  border-radius: 0.85rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  margin-bottom: 2rem;
  box-shadow: var(--shadow-card);
}
.co1__notice-icon {
  flex-shrink: 0;
  width: 1.65rem;
  height: 1.65rem;
  border-radius: 50%;
  background: color-mix(in srgb, #b91c1c 12%, var(--color-surface-raised));
  color: #b91c1c;
  font-weight: 900;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.co1__notice-text {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}

.co1__block {
  margin-bottom: 2.5rem;
}
.co1__block-head {
  margin-bottom: 1.1rem;
}
.co1__h2 {
  margin: 0 0 0.35rem;
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--color-text);
}
.co1__h2--sm {
  font-size: 1.05rem;
}
.co1__lede {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}

.co1__tools {
  display: grid;
  gap: 1rem;
}
@media (min-width: 720px) {
  .co1__tools {
    grid-template-columns: repeat(3, 1fr);
  }
}
.co1__tool {
  display: flex;
  flex-direction: column;
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  text-decoration: none;
  color: inherit;
  box-shadow: var(--shadow-card);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.co1__tool:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.1);
}
.co1__tool-img-wrap {
  aspect-ratio: 16 / 10;
  overflow: hidden;
  background: var(--color-surface-raised);
}
.co1__tool-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.co1__tool-body {
  padding: 1rem 1.05rem 1.1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.co1__tool-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 750;
  color: var(--color-text);
}
.co1__tool-desc {
  margin: 0.45rem 0 0;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--color-text-muted);
  flex: 1;
}
.co1__tool-cta {
  margin-top: 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: #b91c1c;
}

/* Category */
.co1__cat-banner {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  margin-bottom: 0.85rem;
  aspect-ratio: 21 / 8;
  min-height: 140px;
  max-height: 200px;
  background: #0f172a;
}
.co1__cat-banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.co1__cat-banner-cap {
  position: absolute;
  inset: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1rem 1.15rem;
  background: linear-gradient(0deg, rgba(15, 23, 42, 0.82) 0%, rgba(15, 23, 42, 0.2) 55%, transparent 100%);
}
.co1__cat-title {
  margin: 0;
  font-size: clamp(1.1rem, 2.5vw, 1.35rem);
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.02em;
}
.co1__cat-hub {
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  white-space: nowrap;
  padding: 0.35rem 0.65rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(6px);
}
.co1__cat-hub:hover {
  background: rgba(255, 255, 255, 0.28);
}
.co1__cat-blurb {
  margin: 0 0 1.15rem;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}

.co1__cards {
  display: grid;
  gap: 1rem;
}
@media (min-width: 640px) {
  .co1__cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 960px) {
  .co1__cards {
    grid-template-columns: repeat(3, 1fr);
  }
}
.co1__card {
  border-radius: 0.95rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-card);
}
.co1__card-img-wrap {
  aspect-ratio: 16 / 10;
  overflow: hidden;
  background: var(--color-surface-raised);
}
.co1__card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.co1__card-body {
  padding: 1rem 1.05rem 1.15rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.co1__card-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-text);
}
.co1__card-pitch {
  margin: 0.4rem 0 0.55rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
  flex: 1;
}
.co1__card-list {
  margin: 0 0 1rem;
  padding-left: 1.05rem;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}
.co1__card-list li + li {
  margin-top: 0.3rem;
}
.co1__card-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: auto;
  padding: 0.55rem 1rem;
  border-radius: 0.6rem;
  font-size: 0.8125rem;
  font-weight: 700;
  background: #b91c1c;
  color: #fff;
  text-decoration: none;
  transition: filter 0.15s ease;
}
.co1__card-btn:hover {
  filter: brightness(1.08);
}

.co1__foot {
  padding: 1.25rem 1.2rem;
  border-radius: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}
.co1__foot-p {
  margin: 0.4rem 0 0;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-muted);
}
.co1__foot :deep(a) {
  color: var(--color-primary-dim);
  font-weight: 650;
  text-decoration: none;
}
.co1__foot :deep(a:hover) {
  text-decoration: underline;
}
</style>
