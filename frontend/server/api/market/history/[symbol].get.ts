/**
 * GET /api/market/history/:symbol?period=1D|1W|1M|3M|6M|1Y
 *
 * Returns OHLCV price history from stooq.com for the StockChart component.
 * All periods use daily bars (stooq does not provide intraday data).
 */

const STOOQ_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

/** How many calendar days back to fetch for each period */
const PERIOD_DAYS: Record<string, number> = {
  '1D':  7,    // last ~5 trading days
  '1W':  14,
  '1M':  45,
  '3M':  100,
  '6M':  190,
  '1Y':  375,
}

const NAME_MAP: Record<string, string> = {
  AAPL: 'Apple Inc.', MSFT: 'Microsoft Corp.', GOOGL: 'Alphabet Inc.',
  AMZN: 'Amazon.com Inc.', NVDA: 'NVIDIA Corp.', TSLA: 'Tesla Inc.',
  META: 'Meta Platforms Inc.', JPM: 'JPMorgan Chase & Co.',
  VTI: 'Vanguard Total Stock Market ETF', VOO: 'Vanguard S&P 500 ETF',
  SPY: 'SPDR S&P 500 ETF', QQQ: 'Invesco QQQ Trust',
  BND: 'Vanguard Total Bond Market ETF', SCHD: 'Schwab US Dividend Equity ETF',
  VXUS: 'Vanguard Total Intl Stock ETF',
}

function toStooqSym(symbol: string): string {
  return symbol.toLowerCase().replace(/[^a-z0-9]/g, '') + '.us'
}

function fmtDate(d: Date): string {
  return d.toISOString().slice(0, 10).replace(/-/g, '')
}

interface Bar {
  date: string; open: number; high: number; low: number; close: number; volume: number
}

function parseCSV(csv: string): Bar[] {
  const lines = csv.trim().split('\n').filter(l => l && !l.startsWith('No data') && !l.startsWith('Warning'))
  if (lines.length < 2) return []
  const rows: Bar[] = []
  for (let i = 1; i < lines.length; i++) {
    const p = lines[i]!.split(',')
    if (p.length < 5) continue
    const bar: Bar = {
      date:   p[0]!,
      open:   parseFloat(parseFloat(p[1]!).toFixed(4)),
      high:   parseFloat(parseFloat(p[2]!).toFixed(4)),
      low:    parseFloat(parseFloat(p[3]!).toFixed(4)),
      close:  parseFloat(parseFloat(p[4]!).toFixed(4)),
      volume: parseInt(p[5] ?? '0'),
    }
    if (!isNaN(bar.close) && bar.close > 0) rows.push(bar)
  }
  return rows
}

export default defineEventHandler(async (event) => {
  const symbol = (getRouterParam(event, 'symbol') ?? '').toUpperCase()
  if (!symbol) throw createError({ statusCode: 400, message: 'symbol required' })

  const query  = getQuery(event)
  const period = ((query.period as string) || '1M').toUpperCase()
  const days   = PERIOD_DAYS[period] ?? PERIOD_DAYS['1M']!

  const d2 = fmtDate(new Date())
  const past = new Date(); past.setDate(past.getDate() - days)
  const d1 = fmtDate(past)

  try {
    const sym = toStooqSym(symbol)
    const url = `https://stooq.com/q/d/l/?s=${sym}&i=d&d1=${d1}&d2=${d2}`
    const csv = await $fetch<string>(url, {
      headers: STOOQ_HEADERS,
      responseType: 'text',
      timeout: 12_000,
    })

    const bars = parseCSV(csv)
    if (bars.length === 0) {
      return { candles: [], symbol, name: NAME_MAP[symbol] ?? symbol, currentPrice: null }
    }

    const candles = bars.map(b => ({
      time:  b.date,   // 'YYYY-MM-DD' — perfect for lightweight-charts daily bars
      open:  b.open,
      high:  b.high,
      low:   b.low,
      close: b.close,
      value: b.close,
    }))

    const latest = bars[bars.length - 1]!
    const prev   = bars.length >= 2 ? bars[bars.length - 2] : null

    return {
      candles,
      symbol,
      name:          NAME_MAP[symbol] ?? symbol,
      currentPrice:  latest.close,
      previousClose: prev?.close ?? null,
    }
  } catch (err) {
    return { candles: [], symbol, name: NAME_MAP[symbol] ?? symbol, currentPrice: null, error: String(err) }
  }
})
