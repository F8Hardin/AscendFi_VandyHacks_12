import { useEffect } from 'react'
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, RefreshControl, Dimensions,
} from 'react-native'
import { PieChart, LineChart } from 'react-native-chart-kit'
import { useFinancialData } from '@/hooks/useFinancialData'
import { useAuth } from '@/hooks/useAuth'
import { colors } from '@/lib/colors'

const W = Dimensions.get('window').width
const CHART_W = W - 48

const chartConfig = {
  backgroundGradientFrom: colors.surfaceRaised,
  backgroundGradientTo: colors.surfaceRaised,
  color: (opacity = 1) => `rgba(99,102,241,${opacity})`,
  labelColor: () => colors.textMuted,
  propsForDots: { r: '3', strokeWidth: '1', stroke: colors.primary },
  decimalPlaces: 0,
}

export default function DashboardTab() {
  const { data, isLoading, isUsingDummyData, refresh } = useFinancialData()
  const { displayName } = useAuth()

  useEffect(() => { refresh() }, [])

  if (isLoading && !data) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={s.loadText}>ARIA is analysing your finances…</Text>
      </View>
    )
  }

  const d = data!

  // Pie chart data
  const pieData = d.spending.labels.map((label, i) => ({
    name: label,
    amount: d.spending.amounts[i] ?? 0,
    color: d.spending.colors[i] ?? colors.chart[i % colors.chart.length],
    legendFontColor: colors.textMuted,
    legendFontSize: 12,
  }))

  // Gains line chart
  const gainsDataset = d.financialGains.datasets[0]
  const gainsData = {
    labels: d.financialGains.labels,
    datasets: [{ data: gainsDataset?.data ?? [0], color: () => colors.success, strokeWidth: 2 }],
  }

  return (
    <ScrollView
      style={s.container}
      contentContainerStyle={s.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refresh} tintColor={colors.primary} />}
    >
      {/* Header */}
      <View style={s.header}>
        <Text style={s.eyebrow}>Checking & spending</Text>
        <Text style={s.heroTitle}>
          Good morning{displayName ? `, ${displayName}` : ''}
        </Text>
        <Text style={s.heroSub}>AI-computed financial snapshot</Text>
      </View>

      {/* Status badge */}
      <View style={[s.badge, { backgroundColor: isUsingDummyData ? 'rgba(245,158,11,0.12)' : 'rgba(34,197,94,0.1)' }]}>
        <View style={[s.dot, { backgroundColor: isUsingDummyData ? colors.warning : colors.success }]} />
        <Text style={[s.badgeText, { color: isUsingDummyData ? colors.warning : colors.success }]}>
          {isUsingDummyData ? 'Demo data · start the Python agent for live AI' : 'AI-powered · live calculations'}
        </Text>
      </View>

      {/* AI Risk chips */}
      <View style={s.riskRow}>
        {Object.entries(d.risks).map(([key, risk]) => (
          <View
            key={key}
            style={[s.riskChip, {
              backgroundColor: risk.level === 'high'
                ? 'rgba(239,68,68,0.1)' : risk.level === 'moderate'
                ? 'rgba(245,158,11,0.1)' : 'rgba(34,197,94,0.08)',
              borderColor: risk.level === 'high'
                ? 'rgba(239,68,68,0.3)' : risk.level === 'moderate'
                ? 'rgba(245,158,11,0.3)' : 'rgba(34,197,94,0.25)',
            }]}
          >
            <Text style={s.riskIcon}>
              {risk.level === 'high' ? '🔴' : risk.level === 'moderate' ? '🟡' : '🟢'}
            </Text>
            <Text style={[s.riskLabel, {
              color: risk.level === 'high' ? colors.danger : risk.level === 'moderate' ? colors.warning : colors.success,
            }]}>{risk.label}</Text>
            <Text style={[s.riskPct, {
              color: risk.level === 'high' ? colors.danger : risk.level === 'moderate' ? colors.warning : colors.success,
            }]}>{Math.round((risk.probability ?? 0) * 100)}%</Text>
          </View>
        ))}
      </View>

      {/* Overview stats */}
      <Text style={s.sectionTitle}>Overview</Text>
      <View style={s.statsGrid}>
        <StatCard label="Monthly income" value={`$${d.user.monthlyIncome.toLocaleString()}`} color={colors.info} emoji="💵" />
        <StatCard label="Checking" value={`$${d.accounts.checking.toLocaleString()}`} color={colors.warning} emoji="🏦" />
        <StatCard label="Savings" value={`$${d.accounts.savings.toLocaleString()}`} color={colors.primary} emoji="🛡️" />
        <StatCard label="Credit score" value={d.accounts.creditScore != null ? String(d.accounts.creditScore) : '—'} color={colors.text} emoji="⭐" />
      </View>

      {/* Spending donut */}
      <Text style={s.sectionTitle}>Spending mix</Text>
      <View style={s.card}>
        <Text style={s.cardTitle}>Category breakdown</Text>
        {pieData.length > 0 && (
          <PieChart
            data={pieData}
            width={CHART_W}
            height={180}
            chartConfig={chartConfig}
            accessor="amount"
            backgroundColor="transparent"
            paddingLeft="8"
            hasLegend
          />
        )}
      </View>

      {/* Financial gains */}
      {gainsDataset && gainsDataset.data.length > 1 && (
        <>
          <Text style={s.sectionTitle}>Financial gains</Text>
          <View style={s.card}>
            <Text style={s.cardTitle}>Net monthly gain</Text>
            <LineChart
              data={gainsData}
              width={CHART_W}
              height={160}
              chartConfig={{ ...chartConfig, color: (opacity = 1) => `rgba(34,197,94,${opacity})` }}
              bezier
              style={{ borderRadius: 8 }}
              withDots={false}
            />
          </View>
        </>
      )}

      {/* Recent activity */}
      <Text style={s.sectionTitle}>Recent activity</Text>
      <View style={s.card}>
        {d.recentActivity.slice(0, 6).map((tx, i) => (
          <View key={i} style={[s.txRow, i < d.recentActivity.length - 1 && s.txBorder]}>
            <View style={{ flex: 1 }}>
              <Text style={s.txDesc}>{tx.description}</Text>
              <Text style={s.txMeta}>{tx.date} · {tx.category}</Text>
            </View>
            <Text style={[s.txAmt, { color: tx.amount > 0 ? colors.success : colors.text }]}>
              {tx.amount > 0 ? '+' : ''}${Math.abs(tx.amount).toFixed(2)}
            </Text>
          </View>
        ))}
      </View>

      <TouchableOpacity style={s.refreshBtn} onPress={refresh} disabled={isLoading} activeOpacity={0.7}>
        <Text style={s.refreshBtnText}>⟳ Refresh AI</Text>
      </TouchableOpacity>

      <View style={{ height: 32 }} />
    </ScrollView>
  )
}

function StatCard({ label, value, color, emoji }: { label: string; value: string; color: string; emoji: string }) {
  return (
    <View style={sc.card}>
      <Text style={sc.emoji}>{emoji}</Text>
      <Text style={[sc.value, { color }]}>{value}</Text>
      <Text style={sc.label}>{label}</Text>
    </View>
  )
}

const sc = StyleSheet.create({
  card: {
    flex: 1, backgroundColor: colors.surface, borderRadius: 12,
    padding: 12, borderWidth: 1, borderColor: colors.border, margin: 4, alignItems: 'center',
  },
  emoji: { fontSize: 20, marginBottom: 6 },
  value: { fontSize: 16, fontWeight: '700', marginBottom: 4 },
  label: { fontSize: 11, color: colors.textMuted, textAlign: 'center' },
})

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 16, paddingTop: 60 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.bg, gap: 16 },
  loadText: { color: colors.textMuted, fontSize: 14 },
  header: { marginBottom: 16 },
  eyebrow: { fontSize: 12, fontWeight: '600', color: colors.primary, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  heroTitle: { fontSize: 26, fontWeight: '800', color: colors.text, marginBottom: 4 },
  heroSub: { fontSize: 13, color: colors.textMuted },
  badge: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    padding: 10, borderRadius: 10, marginBottom: 16,
  },
  dot: { width: 7, height: 7, borderRadius: 4 },
  badgeText: { fontSize: 12, fontWeight: '600' },
  riskRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 20 },
  riskChip: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    paddingHorizontal: 10, paddingVertical: 6, borderRadius: 999, borderWidth: 1,
  },
  riskIcon: { fontSize: 12 },
  riskLabel: { fontSize: 12, fontWeight: '600' },
  riskPct: { fontSize: 11, opacity: 0.8 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 10, marginTop: 4 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -4, marginBottom: 20 },
  card: {
    backgroundColor: colors.surface, borderRadius: 16,
    padding: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 16,
  },
  cardTitle: { fontSize: 14, fontWeight: '600', color: colors.text, marginBottom: 10 },
  txRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10 },
  txBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  txDesc: { fontSize: 14, color: colors.text, fontWeight: '500', marginBottom: 2 },
  txMeta: { fontSize: 11, color: colors.textMuted },
  txAmt: { fontSize: 14, fontWeight: '700' },
  refreshBtn: {
    alignSelf: 'center', borderWidth: 1, borderColor: colors.primary,
    borderRadius: 999, paddingHorizontal: 20, paddingVertical: 8,
  },
  refreshBtnText: { color: colors.primary, fontWeight: '600', fontSize: 13 },
})
