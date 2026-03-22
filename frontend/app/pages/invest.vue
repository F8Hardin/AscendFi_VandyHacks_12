<template>
  <div class="inv">

    <!-- ── Page Header ──────────────────────────────────────────────────── -->
    <header class="inv__header">
      <div>
        <p class="inv__eyebrow">Live Market Data · Yahoo Finance · Paper Trading</p>
        <h1 class="inv__title">Markets</h1>
      </div>
      <div class="inv__balance-chip">
        <span class="inv__balance-label">Checking</span>
        <span class="inv__balance-val">
          ${{ checkingBalance.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
        </span>
      </div>
    </header>

    <!-- ── Scrolling Ticker Strip ────────────────────────────────────────── -->
    <div class="inv__ticker-wrap">
      <div class="inv__ticker-track">
        <span
          v-for="sym in tickerSymbols"
          :key="sym"
          class="inv__tick"
          :class="{ 'inv__tick--clickable': true }"
          @click="selectSymbol(sym)"
        >
          <span class="inv__tick-sym">{{ sym }}</span>
          <span class="inv__tick-px">
            {{ fmt(quotes[sym]?.current_price) }}
          </span>
          <span
            v-if="quotes[sym]?.day_change_pct != null"
            class="inv__tick-ch"
            :class="quotes[sym].day_change_pct >= 0 ? 'green' : 'red'"
          >{{ quotes[sym].day_change_pct >= 0 ? '+' : '' }}{{ quotes[sym].day_change_pct.toFixed(2) }}%</span>
        </span>
      </div>
    </div>

    <div class="inv__warn">
      Paper trading only — prices from Yahoo Finance (up to 15 min delayed). Not investment advice.
    </div>

    <!-- ── Tabs ─────────────────────────────────────────────────────────── -->
    <div class="inv__tabs" role="tablist">
      <button role="tab" class="inv__tab" :class="{ 'inv__tab--active': activeTab === 'discover' }" @click="activeTab = 'discover'">
        Discover
      </button>
      <button role="tab" class="inv__tab" :class="{ 'inv__tab--active': activeTab === 'portfolio' }" @click="activeTab = 'portfolio'; fetchPortfolio()">
        My Portfolio{{ holdings.length ? ` (${holdings.length})` : '' }}
      </button>
    </div>

    <!-- ════════════════════════════════ DISCOVER ════════════════════════ -->
    <div v-if="activeTab === 'discover'" class="inv__discover">

      <!-- ── Search ─────────────────────────────────────────────────────── -->
      <div class="inv__search-wrap">
        <div class="inv__search-inner">
          <span class="inv__search-icon">⌕</span>
          <input
            v-model="searchQuery"
            class="inv__search"
            type="search"
            placeholder="Search stocks and ETFs — e.g. AAPL, Vanguard, Tesla"
            autocomplete="off"
            @input="onSearchInput"
            @keydown.escape="closeSearch"
            @keydown.enter="pickFirst"
            aria-label="Search stocks"
            aria-autocomplete="list"
            :aria-expanded="showSearchDropdown"
          />
          <span v-if="isSearching" class="inv__search-spinner">⟳</span>
        </div>

        <!-- Dropdown results -->
        <ul v-if="showSearchDropdown" class="inv__search-drop" role="listbox">
          <li
            v-for="r in searchResults"
            :key="r.symbol"
            class="inv__search-item"
            role="option"
            @mousedown.prevent="selectSymbol(r.symbol); closeSearch()"
          >
            <span class="inv__search-sym">{{ r.symbol }}</span>
            <span class="inv__search-name">{{ r.name }}</span>
            <span class="inv__search-badge">{{ r.type === 'ETF' ? 'ETF' : r.exchange }}</span>
          </li>
          <li v-if="!searchResults.length && !isSearching" class="inv__search-empty">
            No results for "{{ searchQuery }}"
          </li>
        </ul>
      </div>

      <!-- ── Main layout ────────────────────────────────────────────────── -->
      <div class="inv__layout">

        <!-- ── Watchlist sidebar ────────────────────────────────────────── -->
        <div class="inv__sidebar">
          <div class="inv__sidebar-head">Watchlist</div>

          <div v-if="isLoadingQuotes && !Object.keys(quotes).length" class="inv__skeletons">
            <div v-for="i in 10" :key="i" class="inv__skel" />
          </div>

          <ul v-else class="inv__watchlist" role="list">
            <li
              v-for="sym in watchlistSymbols"
              :key="sym"
              class="inv__wrow"
              :class="{ 'inv__wrow--active': selectedSymbol === sym }"
              role="button"
              @click="selectSymbol(sym)"
            >
              <div>
                <div class="inv__wrow-sym">{{ sym }}</div>
                <div class="inv__wrow-name">{{ shortName(quotes[sym]?.name, sym) }}</div>
              </div>
              <div class="inv__wrow-right">
                <div class="inv__wrow-px">{{ fmt(quotes[sym]?.current_price) }}</div>
                <div
                  v-if="quotes[sym]?.day_change_pct != null"
                  class="inv__wrow-ch"
                  :class="quotes[sym].day_change_pct >= 0 ? 'green' : 'red'"
                >{{ quotes[sym].day_change_pct >= 0 ? '+' : '' }}{{ quotes[sym].day_change_pct.toFixed(2) }}%</div>
              </div>
            </li>
          </ul>
        </div>

        <!-- ── Detail + Chart panel ─────────────────────────────────────── -->
        <div v-if="selectedSymbol" class="inv__detail">

          <!-- Price header -->
          <div class="inv__detail-top">
            <div>
              <div class="inv__detail-sym">{{ selectedSymbol }}</div>
              <div class="inv__detail-name">{{ selectedQuote?.name ?? selectedSymbol }}</div>
            </div>
            <div class="inv__detail-prices">
              <div class="inv__detail-px">{{ fmt(selectedQuote?.current_price) }}</div>
              <div
                v-if="selectedQuote?.day_change_pct != null"
                class="inv__detail-ch"
                :class="selectedQuote.day_change_pct >= 0 ? 'green' : 'red'"
              >
                {{ selectedQuote.day_change_pct >= 0 ? '▲' : '▼' }}
                {{ Math.abs(selectedQuote.day_change_pct).toFixed(2) }}% today
              </div>
            </div>
          </div>

          <!-- Key stats -->
          <div class="inv__stats" v-if="selectedQuote">
            <div v-if="selectedQuote.previous_close" class="inv__stat">
              <span class="inv__stat-l">Prev Close</span>
              <span class="inv__stat-v">{{ fmt(selectedQuote.previous_close) }}</span>
            </div>
            <div v-if="selectedQuote.day_high" class="inv__stat">
              <span class="inv__stat-l">Day High</span>
              <span class="inv__stat-v">{{ fmt(selectedQuote.day_high) }}</span>
            </div>
            <div v-if="selectedQuote.day_low" class="inv__stat">
              <span class="inv__stat-l">Day Low</span>
              <span class="inv__stat-v">{{ fmt(selectedQuote.day_low) }}</span>
            </div>
            <div v-if="selectedQuote.market_cap" class="inv__stat">
              <span class="inv__stat-l">Mkt Cap</span>
              <span class="inv__stat-v">{{ fmtCap(selectedQuote.market_cap) }}</span>
            </div>
          </div>

          <!-- StockChart -->
          <div class="inv__chart-area">
            <StockChart
              :candles="historyCandles"
              :active-period="selectedPeriod"
              :is-loading="isLoadingHistory"
              :is-up="(selectedQuote?.day_change_pct ?? 0) >= 0"
              @period="onPeriodChange"
            />
          </div>

          <!-- Buy button -->
          <button
            class="inv__buy-btn"
            :disabled="!selectedQuote?.current_price"
            @click="openBuyModal"
          >
            Buy {{ selectedSymbol }}
          </button>
        </div>

        <!-- Empty state -->
        <div v-else class="inv__detail inv__detail--empty">
          <span class="inv__empty-icon">◈</span>
          <p>Select a stock or ETF from the watchlist</p>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════ PORTFOLIO ════════════════════════ -->
    <div v-else class="inv__portfolio-tab">
      <div v-if="isLoadingPortfolio">
        <div v-for="i in 4" :key="i" class="inv__skel inv__skel--tall" />
      </div>

      <div v-else-if="!holdings.length" class="inv__port-empty">
        <span class="inv__empty-icon">◈</span>
        <p>No holdings yet. Go to <strong>Discover</strong> to start investing.</p>
        <button class="inv__buy-btn inv__buy-btn--outline" @click="activeTab = 'discover'">
          Browse Markets
        </button>
      </div>

      <div v-else class="inv__holdings">
        <div class="inv__holdings-head">
          <span>Symbol</span><span>Shares</span><span>Avg Cost</span><span>Current</span><span>Gain / Loss</span>
        </div>
        <div v-for="h in enrichedHoldings" :key="h.symbol" class="inv__hrow">
          <div>
            <div class="inv__hrow-sym">{{ h.symbol }}</div>
            <div class="inv__hrow-name">{{ shortName(quotes[h.symbol]?.name, h.symbol) }}</div>
          </div>
          <span>{{ h.shares }}</span>
          <span>{{ fmt(h.avgCost) }}</span>
          <span>{{ h.currentPrice != null ? fmt(h.currentPrice) : '—' }}</span>
          <span :class="h.gainLoss >= 0 ? 'green' : 'red'">
            {{ h.gainLoss >= 0 ? '+' : '' }}{{ fmt(Math.abs(h.gainLoss)) }}
            <small>({{ h.gainLossPct >= 0 ? '+' : '' }}{{ h.gainLossPct.toFixed(1) }}%)</small>
          </span>
        </div>

        <div class="inv__port-total">
          <span>Total Value</span>
          <strong>{{ fmt(totalPortfolioValue) }}</strong>
        </div>
      </div>
    </div>

    <!-- ── Guide card ────────────────────────────────────────────────────── -->
    <section class="inv__guide">
      <h2>Before you invest</h2>
      <ul>
        <li>Build a 3–6 month emergency fund before investing any surplus.</li>
        <li>Max out tax-advantaged accounts (401k match, Roth IRA) first.</li>
        <li>Low-cost index ETFs (VTI, VOO) beat most active funds long-term.</li>
        <li>Rebalance on a schedule — not when the market moves.</li>
      </ul>
      <NuxtLink to="/chat">Ask ARIA about the right allocation for you →</NuxtLink>
    </section>

    <!-- ════════════════════════════════ BUY MODAL ═══════════════════════ -->
    <Teleport to="body">
      <div v-if="showBuyModal" class="inv__overlay" @click.self="closeBuyModal" role="dialog" aria-modal="true">
        <div class="inv__modal">
          <div class="inv__modal-hd">
            <h2>Buy {{ selectedSymbol }}</h2>
            <button class="inv__modal-x" @click="closeBuyModal" aria-label="Close">✕</button>
          </div>

          <div class="inv__modal-price-row">
            <span class="inv__modal-qname">{{ selectedQuote?.name ?? selectedSymbol }}</span>
            <span class="inv__modal-qpx">{{ fmt(selectedQuote?.current_price) }}</span>
          </div>

          <div class="inv__modal-bal">
            <span>Available in checking</span>
            <strong>{{ fmt(checkingBalance) }}</strong>
          </div>

          <!-- Shares input -->
          <label class="inv__modal-lbl">
            Number of Shares
            <input
              v-model.number="buyShares"
              type="number"
              class="inv__modal-inp"
              min="0.001"
              step="0.001"
              placeholder="e.g. 1"
              @input="syncDollarFromShares"
            />
          </label>

          <!-- Dollar input -->
          <label class="inv__modal-lbl">
            — or — Invest Amount ($)
            <input
              v-model.number="buyDollars"
              type="number"
              class="inv__modal-inp"
              min="1"
              step="1"
              placeholder="e.g. 100"
              @input="syncSharesFromDollar"
            />
          </label>

          <div class="inv__modal-total">
            <span>Total cost</span>
            <strong>{{ fmt(buyTotal) }}</strong>
          </div>

          <p v-if="buyTotal > checkingBalance" class="inv__modal-insuf">
            Insufficient funds — need {{ fmt(buyTotal - checkingBalance) }} more.
          </p>

          <div v-if="buyError" class="inv__modal-err">{{ buyError }}</div>
          <div v-if="buySuccess" class="inv__modal-ok">{{ buySuccess }}</div>

          <button
            class="inv__buy-btn"
            :disabled="buyTotal <= 0 || buyTotal > checkingBalance || isBuying"
            @click="executeBuy"
          >
            {{ isBuying ? 'Processing…' : `Confirm — Buy ${fmt(buyTotal)}` }}
          </button>
          <button class="inv__modal-cancel" @click="closeBuyModal">Cancel</button>

          <p class="inv__modal-disc">Paper trading only. No real money is transferred.</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default', middleware: ['auth'], ssr: false })

// ── Financial data (checking balance) ────────────────────────────────────────
const { data: financialData, refreshLive } = useFinancialData()
const checkingBalance = computed(() => financialData.value?.accounts.checking ?? 0)

const config     = useRuntimeConfig()
const agentBase  = config.public.agentBase as string

// ── Symbol lists ──────────────────────────────────────────────────────────────
const watchlistSymbols = [
  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM',
  'VTI', 'VOO', 'SPY', 'QQQ', 'BND', 'SCHD', 'VXUS',
]
const tickerSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'VTI', 'SPY', 'QQQ']

// ── Quote state ───────────────────────────────────────────────────────────────
const quotes          = ref<Record<string, any>>({})
const isLoadingQuotes = ref(true)

// ── Selected stock state ──────────────────────────────────────────────────────
const selectedSymbol  = ref<string | null>(null)
const historyCandles  = ref<any[]>([])
const isLoadingHistory = ref(false)
const selectedPeriod  = ref('1M')

// ── Search state ──────────────────────────────────────────────────────────────
const searchQuery        = ref('')
const searchResults      = ref<{ symbol: string; name: string; type: string; exchange: string }[]>([])
const isSearching        = ref(false)
const showSearchDropdown = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

// ── Portfolio state ───────────────────────────────────────────────────────────
const holdings          = ref<{ symbol: string; shares: number; avgCost: number }[]>([])
const isLoadingPortfolio = ref(false)
const activeTab          = ref<'discover' | 'portfolio'>('discover')

// ── Buy modal state ───────────────────────────────────────────────────────────
const showBuyModal = ref(false)
const buyShares    = ref<number>(1)
const buyDollars   = ref<number>(0)
const isBuying     = ref(false)
const buyError     = ref<string | null>(null)
const buySuccess   = ref<string | null>(null)

// ── Computed ──────────────────────────────────────────────────────────────────
const selectedQuote = computed(() =>
  selectedSymbol.value ? quotes.value[selectedSymbol.value] : null
)

const buyTotal = computed(() =>
  Math.round(Number(buyShares.value) * (selectedQuote.value?.current_price ?? 0) * 100) / 100
)

const enrichedHoldings = computed(() =>
  holdings.value.map(h => {
    const cp = quotes.value[h.symbol]?.current_price ?? null
    const gainLoss    = cp != null ? Math.round((cp - h.avgCost) * h.shares * 100) / 100 : 0
    const gainLossPct = h.avgCost > 0 && cp != null
      ? Math.round(((cp - h.avgCost) / h.avgCost) * 1000) / 10 : 0
    return { ...h, currentPrice: cp, gainLoss, gainLossPct }
  })
)

const totalPortfolioValue = computed(() =>
  enrichedHoldings.value.reduce(
    (s, h) => s + ((h.currentPrice ?? h.avgCost) * h.shares), 0
  )
)

// ── Formatters ────────────────────────────────────────────────────────────────
function fmt(n: number | null | undefined): string {
  if (n == null) return '—'
  return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmtCap(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`
  if (n >= 1e9)  return `$${(n / 1e9).toFixed(2)}B`
  if (n >= 1e6)  return `$${(n / 1e6).toFixed(2)}M`
  return fmt(n)
}

function shortName(name: string | undefined, fallback: string): string {
  const n = name ?? fallback
  return n.length > 24 ? n.slice(0, 22) + '…' : n
}

// ── Fetch quotes ──────────────────────────────────────────────────────────────
async function fetchQuotes(extra: string[] = []) {
  isLoadingQuotes.value = true
  const syms = [...new Set([...watchlistSymbols, ...tickerSymbols, ...extra])].join(',')
  try {
    const res = await $fetch<{ quotes: Record<string, any> }>('/api/market/quotes', {
      query: { symbols: syms },
    })
    quotes.value = { ...quotes.value, ...(res.quotes ?? {}) }
  } catch { /* leave stale */ }
  finally { isLoadingQuotes.value = false }
}

// ── Fetch price history ────────────────────────────────────────────────────────
async function fetchHistory(symbol: string, period: string) {
  isLoadingHistory.value = true
  historyCandles.value   = []
  try {
    const res = await $fetch<{ candles: any[] }>(`/api/market/history/${symbol}`, {
      query: { period },
    })
    historyCandles.value = res.candles ?? []
  } catch (e) {
    console.error('[invest] fetchHistory failed:', e)
    historyCandles.value = []
  } finally {
    isLoadingHistory.value = false
  }
}

async function selectSymbol(sym: string) {
  selectedSymbol.value = sym
  searchQuery.value    = ''
  closeSearch()
  await fetchHistory(sym, selectedPeriod.value)

  // Fetch quote if we don't have it yet (e.g., came from search)
  if (!quotes.value[sym]) {
    const res = await $fetch<{ quotes: Record<string, any> }>('/api/market/quotes', {
      query: { symbols: sym },
    }).catch(() => ({ quotes: {} }))
    quotes.value = { ...quotes.value, ...(res.quotes ?? {}) }
  }
}

async function onPeriodChange(p: string) {
  selectedPeriod.value = p
  if (selectedSymbol.value) await fetchHistory(selectedSymbol.value, p)
}

// ── Search ────────────────────────────────────────────────────────────────────
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  const q = searchQuery.value.trim()
  if (!q) { closeSearch(); return }
  showSearchDropdown.value = true
  isSearching.value        = true
  searchTimer = setTimeout(() => doSearch(q), 280)
}

async function doSearch(q: string) {
  try {
    const res = await $fetch<{ results: any[] }>('/api/market/search', { query: { q } })
    searchResults.value = res.results ?? []
  } catch {
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

function closeSearch() {
  showSearchDropdown.value = false
  isSearching.value        = false
}

function pickFirst() {
  const first = searchResults.value[0]
  if (first) { selectSymbol(first.symbol); closeSearch() }
}

// ── Portfolio ─────────────────────────────────────────────────────────────────
async function fetchPortfolio() {
  isLoadingPortfolio.value = true
  try {
    const res = await $fetch<{ holdings: any[] }>(`${agentBase}/api/finance/portfolio`, {
      credentials: 'include' as RequestCredentials,
    })
    holdings.value = res.holdings ?? []

    // Fetch quotes for portfolio symbols not in watchlist
    const missing = holdings.value.map(h => h.symbol).filter(s => !quotes.value[s])
    if (missing.length) await fetchQuotes(missing)
  } catch {
    holdings.value = []
  } finally {
    isLoadingPortfolio.value = false
  }
}

// ── Buy modal ─────────────────────────────────────────────────────────────────
function syncDollarFromShares() {
  const p = selectedQuote.value?.current_price
  if (p && buyShares.value > 0) buyDollars.value = Math.round(buyShares.value * p * 100) / 100
}

function syncSharesFromDollar() {
  const p = selectedQuote.value?.current_price
  if (p && buyDollars.value > 0) buyShares.value = Math.round((buyDollars.value / p) * 1000) / 1000
}

function openBuyModal() {
  buyShares.value = 1
  buyDollars.value = selectedQuote.value?.current_price ?? 0
  buyError.value = null; buySuccess.value = null
  showBuyModal.value = true
}

function closeBuyModal() {
  showBuyModal.value = false
  buyError.value = null; buySuccess.value = null
}

async function executeBuy() {
  if (!selectedSymbol.value || buyTotal.value <= 0) return
  isBuying.value = true; buyError.value = null; buySuccess.value = null

  try {
    await $fetch(`${agentBase}/api/finance/invest`, {
      method: 'POST',
      credentials: 'include' as RequestCredentials,
      body: {
        symbol:        selectedSymbol.value,
        shares:        Number(buyShares.value),
        pricePerShare: selectedQuote.value?.current_price,
        name:          selectedQuote.value?.name,
      },
    })
    buySuccess.value = `Purchased ${buyShares.value} share(s) of ${selectedSymbol.value}`
    await refreshLive()
    await fetchPortfolio()
    setTimeout(closeBuyModal, 1800)
  } catch (e: any) {
    buyError.value = e?.data?.message ?? e?.message ?? 'Purchase failed'
  } finally {
    isBuying.value = false
  }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
let _quoteInterval: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  await fetchQuotes()
  await selectSymbol('AAPL')
  _quoteInterval = setInterval(() => fetchQuotes(), 60_000)
})

onUnmounted(() => {
  if (_quoteInterval) clearInterval(_quoteInterval)
})

useHead({
  title: 'Markets — AscendFi',
  meta: [{ name: 'description', content: 'Real-time stocks and ETFs with paper trading.' }],
})
</script>

<style scoped>
/* ── Page ────────────────────────────────────────────────────────────────── */
.inv {
  max-width: 78rem;
  margin: 0 auto;
  padding-bottom: 3rem;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.inv__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.inv__eyebrow {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-faint);
  margin: 0 0 0.3rem;
}

.inv__title {
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  color: var(--color-text);
}

.inv__balance-chip {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
  padding: 0.55rem 0.95rem;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
  flex-shrink: 0;
}

.inv__balance-label {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
}

.inv__balance-val {
  font-size: 1rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}

/* ── Ticker strip ────────────────────────────────────────────────────────── */
.inv__ticker-wrap {
  overflow: hidden;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  margin-bottom: 1rem;
}

.inv__ticker-track {
  display: flex;
  gap: 1.75rem;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 0.55rem 1rem;
  -webkit-overflow-scrolling: touch;
}

.inv__ticker-track::-webkit-scrollbar { display: none; }

.inv__tick {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.inv__tick--clickable { cursor: pointer; }
.inv__tick--clickable:hover .inv__tick-sym { color: var(--color-primary); }

.inv__tick-sym { font-weight: 800; font-size: 0.75rem; color: var(--color-text); }
.inv__tick-px  { font-size: 0.75rem; font-weight: 600; font-variant-numeric: tabular-nums; color: var(--color-text); }
.inv__tick-ch  { font-size: 0.7rem; font-weight: 700; font-variant-numeric: tabular-nums; }

/* ── Utility colours ─────────────────────────────────────────────────────── */
.green { color: #16a34a; }
.red   { color: #dc2626; }

/* ── Warning ─────────────────────────────────────────────────────────────── */
.inv__warn {
  padding: 0.55rem 0.9rem;
  border-radius: 0.65rem;
  background: color-mix(in srgb, var(--color-primary) 6%, var(--color-surface));
  border: 1px solid var(--color-border);
  font-size: 0.73rem;
  color: var(--color-text-muted);
  margin-bottom: 1.1rem;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.inv__tabs {
  display: flex;
  gap: 0.2rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.25rem;
}

.inv__tab {
  padding: 0.55rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  background: none;
  color: var(--color-text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  border-radius: 0.25rem 0.25rem 0 0;
  transition: color 0.15s, border-color 0.15s;
}

.inv__tab--active { color: var(--color-primary); border-bottom-color: var(--color-primary); }
.inv__tab:hover:not(.inv__tab--active) { color: var(--color-text); }

/* ── Search ──────────────────────────────────────────────────────────────── */
.inv__search-wrap {
  position: relative;
  margin-bottom: 1.1rem;
}

.inv__search-inner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
  padding: 0 1rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.inv__search-inner:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}

.inv__search-icon { font-size: 1.1rem; color: var(--color-text-faint); flex-shrink: 0; }

.inv__search {
  flex: 1;
  border: none;
  background: none;
  font-size: 0.9rem;
  color: var(--color-text);
  padding: 0.75rem 0;
  outline: none;
}

.inv__search::placeholder { color: var(--color-text-faint); }

.inv__search-spinner {
  font-size: 0.9rem;
  color: var(--color-primary);
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

.inv__search-drop {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  box-shadow: var(--shadow-card-hover);
  z-index: 100;
  list-style: none;
  margin: 0; padding: 0.35rem 0;
  overflow: hidden;
}

.inv__search-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 1rem;
  cursor: pointer;
  transition: background 0.1s;
}

.inv__search-item:hover { background: var(--color-bg-subtle); }

.inv__search-sym {
  font-weight: 800;
  font-size: 0.875rem;
  color: var(--color-text);
  min-width: 3.5rem;
}

.inv__search-name {
  flex: 1;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inv__search-badge {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.15rem 0.45rem;
  border-radius: 0.35rem;
  background: var(--color-surface-raised);
  color: var(--color-text-faint);
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.inv__search-empty {
  padding: 0.85rem 1rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  text-align: center;
}

/* ── Main layout ─────────────────────────────────────────────────────────── */
.inv__layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.1rem;
}

@media (min-width: 820px) {
  .inv__layout {
    grid-template-columns: 220px 1fr;
    align-items: start;
  }
}

/* ── Watchlist sidebar ───────────────────────────────────────────────────── */
.inv__sidebar {
  border-radius: 0.875rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.inv__sidebar-head {
  padding: 0.55rem 0.9rem;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--color-text-faint);
  background: var(--color-surface-raised);
  border-bottom: 1px solid var(--color-border);
}

.inv__watchlist { list-style: none; margin: 0; padding: 0; }

.inv__wrow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.9rem;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background 0.1s;
}

.inv__wrow:last-child { border-bottom: none; }
.inv__wrow:hover { background: var(--color-bg-subtle); }

.inv__wrow--active {
  background: color-mix(in srgb, var(--color-primary) 7%, var(--color-surface));
  border-left: 3px solid var(--color-primary);
}

.inv__wrow-sym  { font-weight: 800; font-size: 0.8125rem; color: var(--color-text); }
.inv__wrow-name { font-size: 0.7rem; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 9rem; }

.inv__wrow-right { text-align: right; flex-shrink: 0; }
.inv__wrow-px    { font-weight: 700; font-size: 0.8125rem; font-variant-numeric: tabular-nums; color: var(--color-text); }
.inv__wrow-ch    { font-size: 0.7rem; font-weight: 700; font-variant-numeric: tabular-nums; }

/* ── Skeletons ───────────────────────────────────────────────────────────── */
.inv__skeletons { display: flex; flex-direction: column; gap: 0.4rem; padding: 0.5rem; }

.inv__skel {
  height: 48px;
  border-radius: 0.5rem;
  background: var(--color-surface-raised);
  animation: pulse 1.5s ease-in-out infinite;
}

.inv__skel--tall { height: 64px; margin-bottom: 0.5rem; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }

/* ── Detail panel ────────────────────────────────────────────────────────── */
.inv__detail {
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.inv__detail--empty {
  align-items: center;
  justify-content: center;
  min-height: 320px;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  gap: 0.65rem;
}

.inv__empty-icon { font-size: 2.5rem; color: var(--color-text-faint); }

.inv__detail-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.inv__detail-sym { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; color: var(--color-text); }
.inv__detail-name { font-size: 0.8125rem; color: var(--color-text-muted); }

.inv__detail-prices { text-align: right; flex-shrink: 0; }

.inv__detail-px {
  font-size: 1.6rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.inv__detail-ch {
  font-size: 0.8125rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* ── Stats row ───────────────────────────────────────────────────────────── */
.inv__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem 1.25rem;
  padding: 0.65rem 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.inv__stat { display: flex; flex-direction: column; gap: 0.1rem; }
.inv__stat-l { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: var(--color-text-faint); }
.inv__stat-v { font-size: 0.875rem; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--color-text); }

/* ── Chart area ──────────────────────────────────────────────────────────── */
.inv__chart-area {
  height: 280px;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  padding: 0.5rem;
}

/* ── Buy button ──────────────────────────────────────────────────────────── */
.inv__buy-btn {
  width: 100%;
  padding: 0.8rem;
  border-radius: 0.75rem;
  border: none;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-size: 0.9375rem;
  font-weight: 700;
  cursor: pointer;
  transition: filter 0.15s, transform 0.15s;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--color-primary) 35%, transparent);
}

.inv__buy-btn:hover:not(:disabled) { filter: brightness(1.07); transform: translateY(-1px); }
.inv__buy-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.inv__buy-btn--outline { background: transparent; color: var(--color-primary); border: 1.5px solid var(--color-primary); box-shadow: none; }

/* ── Portfolio tab ───────────────────────────────────────────────────────── */
.inv__port-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; min-height: 200px; text-align: center;
  color: var(--color-text-muted); font-size: 0.9rem;
}

.inv__holdings {
  border-radius: 0.875rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.inv__holdings-head {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr 1.2fr;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  background: var(--color-surface-raised);
  font-size: 0.62rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-text-faint);
  border-bottom: 1px solid var(--color-border);
}

.inv__hrow {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr 1.2fr;
  gap: 0.5rem;
  align-items: center;
  padding: 0.7rem 1rem;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
}

.inv__hrow:last-of-type { border-bottom: none; }
.inv__hrow-sym { font-weight: 800; color: var(--color-text); }
.inv__hrow-name { font-size: 0.7rem; color: var(--color-text-muted); }

.inv__port-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background: var(--color-surface-raised);
  border-top: 1px solid var(--color-border);
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text);
}

.inv__port-total strong {
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
  color: var(--color-primary);
}

/* ── Guide card ──────────────────────────────────────────────────────────── */
.inv__guide {
  margin-top: 2rem;
  padding: 1.1rem 1.2rem;
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.inv__guide h2 { font-size: 1rem; font-weight: 750; margin: 0 0 0.55rem; color: var(--color-text); }

.inv__guide ul {
  margin: 0 0 0.8rem;
  padding-left: 1.1rem;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-text-muted);
}

.inv__guide ul li + li { margin-top: 0.3rem; }

.inv__guide a {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary-dim);
  text-decoration: none;
}

.inv__guide a:hover { text-decoration: underline; }

/* ── Buy Modal ───────────────────────────────────────────────────────────── */
.inv__overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(5px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 1rem;
}

.inv__modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1.25rem;
  box-shadow: var(--shadow-card-hover);
  padding: 1.5rem;
  width: 100%; max-width: 400px;
  display: flex; flex-direction: column; gap: 0.85rem;
}

.inv__modal-hd {
  display: flex; justify-content: space-between; align-items: center;
}

.inv__modal-hd h2 { font-size: 1.2rem; font-weight: 800; margin: 0; color: var(--color-text); }

.inv__modal-x {
  border: none; background: var(--color-surface-raised); color: var(--color-text-muted);
  width: 2rem; height: 2rem; border-radius: 9999px; cursor: pointer; font-size: 0.875rem;
  display: flex; align-items: center; justify-content: center; transition: background 0.15s;
}

.inv__modal-x:hover { background: var(--color-border); color: var(--color-text); }

.inv__modal-price-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.7rem 1rem;
  background: var(--color-surface-raised);
  border-radius: 0.75rem; border: 1px solid var(--color-border);
}

.inv__modal-qname { font-size: 0.875rem; color: var(--color-text-muted); }
.inv__modal-qpx   { font-size: 1.15rem; font-weight: 800; font-variant-numeric: tabular-nums; color: var(--color-text); }

.inv__modal-bal {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.8125rem; color: var(--color-text-muted);
}

.inv__modal-bal strong { font-variant-numeric: tabular-nums; color: var(--color-text); }

.inv__modal-lbl {
  display: flex; flex-direction: column; gap: 0.35rem;
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em;
  color: var(--color-text-faint);
}

.inv__modal-inp {
  width: 100%; padding: 0.65rem 0.9rem;
  border-radius: 0.65rem; border: 1px solid var(--color-border);
  background: var(--color-surface); font-size: 0.9375rem; font-weight: 600;
  font-variant-numeric: tabular-nums; color: var(--color-text); outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.inv__modal-inp:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-glow); }

.inv__modal-total {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.7rem 1rem;
  background: color-mix(in srgb, var(--color-primary) 7%, var(--color-surface));
  border: 1px solid color-mix(in srgb, var(--color-primary) 18%, var(--color-border));
  border-radius: 0.75rem; font-size: 0.875rem; color: var(--color-text-muted);
}

.inv__modal-total strong { font-size: 1.1rem; font-weight: 800; font-variant-numeric: tabular-nums; color: var(--color-text); }

.inv__modal-insuf { font-size: 0.75rem; color: #dc2626; font-weight: 600; margin: 0; }

.inv__modal-err {
  padding: 0.55rem 0.85rem; border-radius: 0.6rem;
  background: color-mix(in srgb,#dc2626 10%,var(--color-surface));
  border: 1px solid color-mix(in srgb,#dc2626 25%,var(--color-border));
  color: #dc2626; font-size: 0.8125rem; font-weight: 600;
}

.inv__modal-ok {
  padding: 0.55rem 0.85rem; border-radius: 0.6rem;
  background: color-mix(in srgb,#16a34a 10%,var(--color-surface));
  border: 1px solid color-mix(in srgb,#16a34a 25%,var(--color-border));
  color: #16a34a; font-size: 0.8125rem; font-weight: 600;
}

.inv__modal-cancel {
  width: 100%; padding: 0.7rem; border-radius: 0.75rem;
  border: 1.5px solid var(--color-border); background: transparent;
  color: var(--color-text-muted); font-size: 0.875rem; font-weight: 600;
  cursor: pointer; transition: background 0.15s, color 0.15s;
}

.inv__modal-cancel:hover { background: var(--color-surface-raised); color: var(--color-text); }

.inv__modal-disc { font-size: 0.68rem; color: var(--color-text-faint); text-align: center; margin: 0; }
</style>
