/**
 * GET /api/market/quotes?symbols=AAPL,MSFT,...
 *
 * Fetches real-time quotes from stooq.com (no API key, no rate limits).
 * Returns current price, previous close, day change %, high/low.
 */

const STOOQ_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

/** Known company names for common symbols */
const NAME_MAP: Record<string, string> = {
  AAPL: 'Apple Inc.', MSFT: 'Microsoft Corp.', GOOGL: 'Alphabet Inc.',
  AMZN: 'Amazon.com Inc.', NVDA: 'NVIDIA Corp.', TSLA: 'Tesla Inc.',
  META: 'Meta Platforms Inc.', JPM: 'JPMorgan Chase & Co.',
  VTI: 'Vanguard Total Stock Market ETF', VOO: 'Vanguard S&P 500 ETF',
  SPY: 'SPDR S&P 500 ETF', QQQ: 'Invesco QQQ Trust',
  BND: 'Vanguard Total Bond Market ETF', SCHD: 'Schwab US Dividend Equity ETF',
  VXUS: 'Vanguard Total Intl Stock ETF', ARKK: 'ARK Innovation ETF',
  GLD: 'SPDR Gold Shares', IWM: 'iShares Russell 2000 ETF',
}

/** Convert Yahoo-style ticker to stooq format: AAPL → aapl.us */
function toStooqSym(symbol: string): string {
  return symbol.toLowerCase().replace(/[^a-z0-9]/g, '') + '.us'
}

function fmtDate(d: Date): string {
  return d.toISOString().slice(0, 10).replace(/-/g, '')
}

interface Bar {
  date: string; open: number; high: number; low: number; close: number
}

function parseCSV(csv: string): Bar[] {
  const lines = csv.trim().split('\n').filter(l => l && !l.startsWith('No data') && !l.startsWith('Warning'))
  if (lines.length < 2) return []
  const rows: Bar[] = []
  for (let i = 1; i < lines.length; i++) {
    const p = lines[i]!.split(',')
    if (p.length < 5) continue
    const bar = { date: p[0]!, open: +p[1]!, high: +p[2]!, low: +p[3]!, close: +p[4]! }
    if (!isNaN(bar.close) && bar.close > 0) rows.push(bar)
  }
  return rows
}

async function fetchStooqQuote(symbol: string): Promise<Record<string, unknown> | null> {
  const sym = toStooqSym(symbol)
  const d2 = fmtDate(new Date())
  const past = new Date(); past.setDate(past.getDate() - 14)
  const d1 = fmtDate(past)

  try {
    const url = `https://stooq.com/q/d/l/?s=${sym}&i=d&d1=${d1}&d2=${d2}`
    const csv = await $fetch<string>(url, {
      headers: STOOQ_HEADERS,
      responseType: 'text',
      timeout: 8_000,
    })

    const bars = parseCSV(csv)
    if (bars.length === 0) return null

    const latest = bars[bars.length - 1]!
    const prev   = bars.length >= 2 ? bars[bars.length - 2]! : latest
    const changePct = prev.close
      ? parseFloat(((latest.close - prev.close) / prev.close * 100).toFixed(2))
      : 0

    return {
      symbol:         symbol.toUpperCase(),
      name:           NAME_MAP[symbol.toUpperCase()] ?? symbol.toUpperCase(),
      current_price:  parseFloat(latest.close.toFixed(2)),
      previous_close: parseFloat(prev.close.toFixed(2)),
      day_change_pct: changePct,
      day_high:       parseFloat(latest.high.toFixed(2)),
      day_low:        parseFloat(latest.low.toFixed(2)),
      market_cap:     null,
      currency:       'USD',
      exchange:       'US',
    }
  } catch {
    return null
  }
}

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const raw = (query.symbols as string) || 'AAPL,MSFT,GOOGL,AMZN,NVDA,TSLA,VTI,VOO,SPY,BND,QQQ,SCHD'
  const symbols = raw.split(',').map(s => s.trim().toUpperCase()).filter(Boolean).slice(0, 20)

  const settled = await Promise.allSettled(symbols.map(fetchStooqQuote))

  const quotes: Record<string, unknown> = {}
  for (let i = 0; i < symbols.length; i++) {
    const r = settled[i]
    if (r?.status === 'fulfilled' && r.value) {
      quotes[symbols[i]!] = r.value
    }
  }

  return { quotes, timestamp: new Date().toISOString() }
})
