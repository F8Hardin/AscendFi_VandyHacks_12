import { useEffect, useState, useCallback } from 'react'
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  ActivityIndicator, TextInput, Dimensions,
} from 'react-native'
import { LineChart } from 'react-native-chart-kit'
import { AGENT_ROOT, apiFetch } from '@/lib/api'
import { colors } from '@/lib/colors'

const W = Dimensions.get('window').width

interface Quote {
  symbol: string
  name: string
  current_price: number
  previous_close: number
  day_change_pct: number
  day_high: number
  day_low: number
}

interface Candle { time: string; open: number; high: number; low: number; close: number }

const DEFAULT_SYMBOLS = 'AAPL,MSFT,NVDA,TSLA,VOO,SPY,QQQ,BND'
const PERIODS = ['1D', '1W', '1M', '3M', '6M', '1Y']

export default function InvestTab() {
  const [quotes, setQuotes] = useState<Record<string, Quote>>({})
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)
  const [candles, setCandles] = useState<Candle[]>([])
  const [period, setPeriod] = useState('1M')
  const [chartLoading, setChartLoading] = useState(false)
  const [search, setSearch] = useState('')

  const fetchQuotes = useCallback(async () => {
    try {
      const res = await apiFetch<{ quotes: Record<string, Quote> }>(
        `${AGENT_ROOT}/api/market/quotes?symbols=${DEFAULT_SYMBOLS}`
      )
      setQuotes(res.quotes)
    } catch { /* agent may be offline */ } finally {
      setLoading(false)
    }
  }, [])

  const fetchChart = useCallback(async (symbol: string, p: string) => {
    setChartLoading(true)
    try {
      const res = await apiFetch<{ candles: Candle[] }>(
        `${AGENT_ROOT}/api/market/history/${symbol}?period=${p}`
      )
      setCandles(res.candles ?? [])
    } catch {
      setCandles([])
    } finally {
      setChartLoading(false)
    }
  }, [])

  useEffect(() => { fetchQuotes() }, [])

  function selectSymbol(sym: string) {
    setSelected(sym)
    fetchChart(sym, period)
  }

  function changePeriod(p: string) {
    setPeriod(p)
    if (selected) fetchChart(selected, p)
  }

  const filteredSymbols = Object.keys(quotes).filter(sym => {
    if (!search) return true
    const q = search.toUpperCase()
    return sym.includes(q) || quotes[sym]?.name.toUpperCase().includes(q)
  })

  const selectedQuote = selected ? quotes[selected] : null
  const chartData = candles.map(c => c.close)
  const chartLabels = candles
    .filter((_, i) => i === 0 || i === Math.floor(candles.length / 2) || i === candles.length - 1)
    .map(c => c.time.slice(5)) // MM-DD

  return (
    <ScrollView style={s.container} contentContainerStyle={s.content}>
      <View style={s.header}>
        <Text style={s.eyebrow}>Market</Text>
        <Text style={s.heroTitle}>Invest</Text>
        <Text style={s.heroSub}>Live prices via stooq.com · no key required</Text>
      </View>

      {/* Search */}
      <TextInput
        style={s.searchInput}
        placeholder="Search symbol or name…"
        placeholderTextColor={colors.textFaint}
        autoCapitalize="characters"
        value={search}
        onChangeText={setSearch}
        onSubmitEditing={() => {
          const sym = search.trim().toUpperCase()
          if (sym) selectSymbol(sym)
        }}
      />

      {/* Selected chart */}
      {selected && (
        <View style={s.chartCard}>
          {selectedQuote && (
            <View style={s.chartHeader}>
              <View>
                <Text style={s.chartSym}>{selected}</Text>
                <Text style={s.chartName}>{selectedQuote.name}</Text>
              </View>
              <View style={s.chartPrices}>
                <Text style={s.chartPrice}>${selectedQuote.current_price.toFixed(2)}</Text>
                <Text style={[s.chartChange, { color: selectedQuote.day_change_pct >= 0 ? colors.success : colors.danger }]}>
                  {selectedQuote.day_change_pct >= 0 ? '+' : ''}{selectedQuote.day_change_pct.toFixed(2)}%
                </Text>
              </View>
            </View>
          )}

          {/* Period selector */}
          <View style={s.periods}>
            {PERIODS.map(p => (
              <TouchableOpacity
                key={p}
                style={[s.periodBtn, period === p && s.periodBtnActive]}
                onPress={() => changePeriod(p)}
                activeOpacity={0.7}
              >
                <Text style={[s.periodText, period === p && s.periodTextActive]}>{p}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {chartLoading ? (
            <View style={s.chartLoader}>
              <ActivityIndicator color={colors.primary} />
            </View>
          ) : chartData.length > 1 ? (
            <LineChart
              data={{
                labels: chartLabels.length > 0 ? chartLabels : ['', '', ''],
                datasets: [{
                  data: chartData,
                  color: () => chartData[chartData.length - 1] >= chartData[0] ? colors.success : colors.danger,
                  strokeWidth: 2,
                }],
              }}
              width={W - 48}
              height={180}
              chartConfig={{
                backgroundGradientFrom: colors.surfaceRaised,
                backgroundGradientTo: colors.surfaceRaised,
                color: (opacity = 1) => `rgba(99,102,241,${opacity})`,
                labelColor: () => colors.textFaint,
                decimalPlaces: 2,
                propsForDots: { r: '0' },
              }}
              bezier
              withDots={false}
              style={{ borderRadius: 8, marginTop: 8 }}
            />
          ) : (
            <View style={s.chartLoader}>
              <Text style={s.noData}>No price data · Python agent may be offline</Text>
            </View>
          )}
        </View>
      )}

      {/* Watchlist */}
      <Text style={s.sectionTitle}>Watchlist</Text>
      {loading ? (
        <ActivityIndicator color={colors.primary} style={{ marginTop: 16 }} />
      ) : (
        <View style={s.card}>
          {filteredSymbols.length === 0 && (
            <Text style={s.emptyText}>No quotes yet · Python agent may be offline</Text>
          )}
          {filteredSymbols.map((sym, i) => {
            const q = quotes[sym]!
            const up = q.day_change_pct >= 0
            return (
              <TouchableOpacity
                key={sym}
                style={[s.quoteRow, i < filteredSymbols.length - 1 && s.quoteBorder, selected === sym && s.quoteSelected]}
                onPress={() => selectSymbol(sym)}
                activeOpacity={0.7}
              >
                <View style={{ flex: 1 }}>
                  <Text style={s.quoteSym}>{sym}</Text>
                  <Text style={s.quoteName} numberOfLines={1}>{q.name}</Text>
                </View>
                <View style={s.quoteRight}>
                  <Text style={s.quotePrice}>${q.current_price.toFixed(2)}</Text>
                  <View style={[s.changeBadge, { backgroundColor: up ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)' }]}>
                    <Text style={[s.changeText, { color: up ? colors.success : colors.danger }]}>
                      {up ? '+' : ''}{q.day_change_pct.toFixed(2)}%
                    </Text>
                  </View>
                </View>
              </TouchableOpacity>
            )
          })}
        </View>
      )}

      <TouchableOpacity style={s.refreshBtn} onPress={fetchQuotes} activeOpacity={0.7}>
        <Text style={s.refreshBtnText}>⟳ Refresh quotes</Text>
      </TouchableOpacity>

      <View style={{ height: 32 }} />
    </ScrollView>
  )
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 16, paddingTop: 60 },
  header: { marginBottom: 16 },
  eyebrow: { fontSize: 12, fontWeight: '600', color: colors.success, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  heroTitle: { fontSize: 26, fontWeight: '800', color: colors.text, marginBottom: 4 },
  heroSub: { fontSize: 13, color: colors.textMuted },
  searchInput: {
    backgroundColor: colors.surface, borderRadius: 12, borderWidth: 1,
    borderColor: colors.border, color: colors.text, fontSize: 15,
    padding: 12, marginBottom: 16,
  },
  chartCard: {
    backgroundColor: colors.surface, borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: colors.border, marginBottom: 16,
  },
  chartHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 },
  chartSym: { fontSize: 20, fontWeight: '800', color: colors.text },
  chartName: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  chartPrices: { alignItems: 'flex-end' },
  chartPrice: { fontSize: 20, fontWeight: '700', color: colors.text },
  chartChange: { fontSize: 14, fontWeight: '700', marginTop: 2 },
  periods: { flexDirection: 'row', gap: 6, marginBottom: 4 },
  periodBtn: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 6,
    borderWidth: 1, borderColor: colors.border,
  },
  periodBtnActive: { borderColor: colors.primary, backgroundColor: colors.primaryGlow },
  periodText: { fontSize: 12, color: colors.textMuted, fontWeight: '600' },
  periodTextActive: { color: colors.primary },
  chartLoader: { height: 100, justifyContent: 'center', alignItems: 'center' },
  noData: { color: colors.textMuted, fontSize: 13 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 10 },
  card: {
    backgroundColor: colors.surface, borderRadius: 16,
    borderWidth: 1, borderColor: colors.border, marginBottom: 16,
    overflow: 'hidden',
  },
  emptyText: { color: colors.textMuted, fontSize: 14, padding: 16 },
  quoteRow: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 8 },
  quoteBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  quoteSelected: { backgroundColor: colors.primaryGlow },
  quoteSym: { fontSize: 15, fontWeight: '700', color: colors.text, marginBottom: 2 },
  quoteName: { fontSize: 11, color: colors.textMuted },
  quoteRight: { alignItems: 'flex-end', gap: 4 },
  quotePrice: { fontSize: 15, fontWeight: '700', color: colors.text },
  changeBadge: { borderRadius: 6, paddingHorizontal: 6, paddingVertical: 2 },
  changeText: { fontSize: 12, fontWeight: '700' },
  refreshBtn: {
    alignSelf: 'center', borderWidth: 1, borderColor: colors.primary,
    borderRadius: 999, paddingHorizontal: 20, paddingVertical: 8,
  },
  refreshBtnText: { color: colors.primary, fontWeight: '600', fontSize: 13 },
})
