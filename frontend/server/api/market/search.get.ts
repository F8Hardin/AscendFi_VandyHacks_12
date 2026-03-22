/**
 * GET /api/market/search?q=Apple
 *
 * Local fuzzy search over a curated index of popular US stocks and ETFs.
 * No external API calls — instant, always available.
 */

interface StockEntry {
  symbol:   string
  name:     string
  type:     string   // 'EQUITY' | 'ETF'
  exchange: string
}

const STOCK_INDEX: StockEntry[] = [
  // ── Mega-cap US equities ─────────────────────────────────────────────────
  { symbol: 'AAPL',  name: 'Apple Inc.',                          type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'MSFT',  name: 'Microsoft Corporation',               type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'GOOGL', name: 'Alphabet Inc. (Class A)',              type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'GOOG',  name: 'Alphabet Inc. (Class C)',              type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'AMZN',  name: 'Amazon.com Inc.',                      type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'NVDA',  name: 'NVIDIA Corporation',                   type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'META',  name: 'Meta Platforms Inc.',                  type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'TSLA',  name: 'Tesla Inc.',                           type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'BRK',   name: 'Berkshire Hathaway Inc.',              type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'JPM',   name: 'JPMorgan Chase & Co.',                 type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'V',     name: 'Visa Inc.',                            type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'MA',    name: 'Mastercard Incorporated',              type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'LLY',   name: 'Eli Lilly and Company',               type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'UNH',   name: 'UnitedHealth Group Incorporated',      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'XOM',   name: 'Exxon Mobil Corporation',              type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'JNJ',   name: 'Johnson & Johnson',                    type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'WMT',   name: 'Walmart Inc.',                         type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'PG',    name: 'Procter & Gamble Co.',                 type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'HD',    name: 'The Home Depot Inc.',                  type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'ORCL',  name: 'Oracle Corporation',                   type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'COST',  name: 'Costco Wholesale Corporation',         type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'ABBV',  name: 'AbbVie Inc.',                          type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'MRK',   name: 'Merck & Co. Inc.',                     type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'CVX',   name: 'Chevron Corporation',                  type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'BAC',   name: 'Bank of America Corporation',          type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'PFE',   name: 'Pfizer Inc.',                          type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'AVGO',  name: 'Broadcom Inc.',                        type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'KO',    name: 'The Coca-Cola Company',                type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'NFLX',  name: 'Netflix Inc.',                         type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'DIS',   name: 'The Walt Disney Company',              type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'AMD',   name: 'Advanced Micro Devices Inc.',          type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'INTC',  name: 'Intel Corporation',                    type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'CSCO',  name: 'Cisco Systems Inc.',                   type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'ADBE',  name: 'Adobe Inc.',                           type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'CRM',   name: 'Salesforce Inc.',                      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'QCOM',  name: 'QUALCOMM Incorporated',                type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'PEP',   name: 'PepsiCo Inc.',                         type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'AMGN',  name: 'Amgen Inc.',                           type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'TXN',   name: 'Texas Instruments Incorporated',       type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'INTU',  name: 'Intuit Inc.',                          type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'SBUX',  name: 'Starbucks Corporation',                type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'IBM',   name: 'IBM Corporation',                      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'GE',    name: 'GE Aerospace',                         type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'CAT',   name: 'Caterpillar Inc.',                     type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'BA',    name: 'The Boeing Company',                   type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'GS',    name: 'Goldman Sachs Group Inc.',             type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'MS',    name: 'Morgan Stanley',                       type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'WFC',   name: 'Wells Fargo & Company',                type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'C',     name: 'Citigroup Inc.',                       type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'AXP',   name: 'American Express Company',             type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'BLK',   name: 'BlackRock Inc.',                       type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'SPGI',  name: 'S&P Global Inc.',                      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'RTX',   name: 'RTX Corporation',                      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'DE',    name: 'Deere & Company',                      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'TMO',   name: 'Thermo Fisher Scientific Inc.',        type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'ABT',   name: 'Abbott Laboratories',                  type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'DHR',   name: 'Danaher Corporation',                  type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'ISRG',  name: 'Intuitive Surgical Inc.',              type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'BKNG',  name: 'Booking Holdings Inc.',                type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'NOW',   name: 'ServiceNow Inc.',                      type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'SPOT',  name: 'Spotify Technology S.A.',              type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'UBER',  name: 'Uber Technologies Inc.',               type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'LYFT',  name: 'Lyft Inc.',                            type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'SNAP',  name: 'Snap Inc.',                            type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'PINS',  name: 'Pinterest Inc.',                       type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'PLTR',  name: 'Palantir Technologies Inc.',           type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'COIN',  name: 'Coinbase Global Inc.',                 type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'HOOD',  name: 'Robinhood Markets Inc.',               type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'SOFI',  name: 'SoFi Technologies Inc.',               type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'SHOP',  name: 'Shopify Inc.',                         type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'SQ',    name: 'Block Inc.',                           type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'PYPL',  name: 'PayPal Holdings Inc.',                 type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'ROKU',  name: 'Roku Inc.',                            type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'ZM',    name: 'Zoom Video Communications Inc.',       type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'ABNB',  name: 'Airbnb Inc.',                          type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'DASH',  name: 'DoorDash Inc.',                        type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'RBLX',  name: 'Roblox Corporation',                   type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'RIVN',  name: 'Rivian Automotive Inc.',               type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'LCID',  name: 'Lucid Group Inc.',                     type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'NIO',   name: 'NIO Inc.',                             type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'F',     name: 'Ford Motor Company',                   type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'GM',    name: 'General Motors Company',               type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'T',     name: 'AT&T Inc.',                            type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'VZ',    name: 'Verizon Communications Inc.',          type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'TMUS',  name: 'T-Mobile US Inc.',                     type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'NFLX',  name: 'Netflix Inc.',                         type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'WMT',   name: 'Walmart Inc.',                         type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'TGT',   name: 'Target Corporation',                   type: 'EQUITY', exchange: 'NYSE'   },
  { symbol: 'AMZN',  name: 'Amazon.com Inc.',                      type: 'EQUITY', exchange: 'NASDAQ' },
  { symbol: 'EBAY',  name: 'eBay Inc.',                            type: 'EQUITY', exchange: 'NASDAQ' },
  // ── Popular ETFs ─────────────────────────────────────────────────────────
  { symbol: 'SPY',   name: 'SPDR S&P 500 ETF Trust',              type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'VOO',   name: 'Vanguard S&P 500 ETF',                type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'VTI',   name: 'Vanguard Total Stock Market ETF',     type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'QQQ',   name: 'Invesco QQQ Trust (NASDAQ-100)',      type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'IWM',   name: 'iShares Russell 2000 ETF',            type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'DIA',   name: 'SPDR Dow Jones Industrial Average ETF', type: 'ETF', exchange: 'NYSE'   },
  { symbol: 'VEA',   name: 'Vanguard FTSE Developed Markets ETF', type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'VXUS',  name: 'Vanguard Total Intl Stock Market ETF', type: 'ETF',   exchange: 'NASDAQ' },
  { symbol: 'VWO',   name: 'Vanguard FTSE Emerging Markets ETF',  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'BND',   name: 'Vanguard Total Bond Market ETF',      type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'AGG',   name: 'iShares Core US Aggregate Bond ETF',  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'TLT',   name: 'iShares 20+ Year Treasury Bond ETF',  type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'SCHD',  name: 'Schwab US Dividend Equity ETF',       type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'VIG',   name: 'Vanguard Dividend Appreciation ETF',  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'DVY',   name: 'iShares Select Dividend ETF',         type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'GLD',   name: 'SPDR Gold Shares',                    type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'SLV',   name: 'iShares Silver Trust',                type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'IAU',   name: 'iShares Gold Trust',                  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'ARKK',  name: 'ARK Innovation ETF',                  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'ARKG',  name: 'ARK Genomic Revolution ETF',          type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'XLK',   name: 'Technology Select Sector SPDR Fund',  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'XLF',   name: 'Financial Select Sector SPDR Fund',   type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'XLV',   name: 'Health Care Select Sector SPDR Fund', type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'XLE',   name: 'Energy Select Sector SPDR Fund',      type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'XLY',   name: 'Consumer Discret. Select Sector SPDR', type: 'ETF',   exchange: 'NYSE'   },
  { symbol: 'VGT',   name: 'Vanguard Information Technology ETF', type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'SOXX',  name: 'iShares Semiconductor ETF',           type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'SMH',   name: 'VanEck Semiconductor ETF',            type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'ICLN',  name: 'iShares Global Clean Energy ETF',     type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'JEPI',  name: 'JPMorgan Equity Premium Income ETF',  type: 'ETF',    exchange: 'NYSE'   },
  { symbol: 'JEPQ',  name: 'JPMorgan Nasdaq Equity Premium ETF',  type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'SQQQ',  name: 'ProShares UltraPro Short QQQ',        type: 'ETF',    exchange: 'NASDAQ' },
  { symbol: 'TQQQ',  name: 'ProShares UltraPro QQQ',              type: 'ETF',    exchange: 'NASDAQ' },
]

export default defineEventHandler((event) => {
  const query = getQuery(event)
  const q = ((query.q as string) ?? '').trim().toUpperCase()

  if (!q || q.length < 1) return { results: [] }

  // Exact symbol match first, then name match
  const exactSym = STOCK_INDEX.filter(s => s.symbol === q)
  const startsSym = STOCK_INDEX.filter(s => s.symbol !== q && s.symbol.startsWith(q))
  const nameMatch = STOCK_INDEX.filter(s =>
    !s.symbol.startsWith(q) &&
    s.name.toUpperCase().includes(q)
  )

  const results = [...exactSym, ...startsSym, ...nameMatch].slice(0, 8)
  return { results }
})
