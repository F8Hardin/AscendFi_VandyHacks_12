import { useEffect, useState } from 'react'
import {
  View, Text, ScrollView, StyleSheet, RefreshControl,
  ActivityIndicator, TouchableOpacity, Dimensions,
} from 'react-native'
import { LineChart } from 'react-native-chart-kit'
import { useFinancialData } from '@/hooks/useFinancialData'
import { colors } from '@/lib/colors'

const W = Dimensions.get('window').width

export default function DebtTab() {
  const { data, isLoading, refresh } = useFinancialData()
  const [extraPayment, setExtraPayment] = useState(100)

  useEffect(() => { refresh() }, [])

  if (isLoading && !data) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={s.loadText}>Loading debt analysis…</Text>
      </View>
    )
  }

  const d = data!
  const sortedDebts = [...d.debts].sort((a, b) => b.rate - a.rate)
  const totalDebt = d.debts.reduce((sum, debt) => sum + debt.balance, 0)
  const totalMin = d.debts.reduce((sum, debt) => sum + debt.min, 0)
  const weightedApr = d.debts.reduce((sum, debt) => sum + debt.rate * (debt.balance / totalDebt), 0)

  // Accelerated payoff estimate (rough)
  const monthsSavedRough = extraPayment > 0 ? Math.round((totalDebt / (totalMin + extraPayment)) * 0.15) : 0

  const debtTimeline = d.debtTimeline
  const timelineDataset = debtTimeline.datasets[0]

  return (
    <ScrollView
      style={s.container}
      contentContainerStyle={s.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refresh} tintColor={colors.primary} />}
    >
      <View style={s.header}>
        <Text style={s.eyebrow}>Debt & payoff</Text>
        <Text style={s.heroTitle}>Debt overview</Text>
        <Text style={s.heroSub}>Avalanche strategy — highest APR first</Text>
      </View>

      {/* Summary stats */}
      <View style={s.statsRow}>
        <View style={s.statBox}>
          <Text style={s.statVal}>${totalDebt.toLocaleString()}</Text>
          <Text style={s.statLabel}>Total balance</Text>
        </View>
        <View style={s.statBox}>
          <Text style={[s.statVal, { color: colors.danger }]}>{weightedApr.toFixed(1)}%</Text>
          <Text style={s.statLabel}>Weighted APR</Text>
        </View>
        <View style={s.statBox}>
          <Text style={s.statVal}>${totalMin.toLocaleString()}</Text>
          <Text style={s.statLabel}>Min/month</Text>
        </View>
      </View>

      {/* Debt timeline */}
      {timelineDataset && timelineDataset.data.length > 1 && (
        <>
          <Text style={s.sectionTitle}>Paydown trajectory</Text>
          <View style={s.card}>
            <Text style={s.cardTitle}>AI-projected balance over time</Text>
            <LineChart
              data={{
                labels: debtTimeline.labels.filter((_, i) => i % 2 === 0),
                datasets: [{ data: timelineDataset.data, color: () => colors.danger, strokeWidth: 2 }],
              }}
              width={W - 48}
              height={160}
              chartConfig={{
                backgroundGradientFrom: colors.surfaceRaised,
                backgroundGradientTo: colors.surfaceRaised,
                color: (opacity = 1) => `rgba(239,68,68,${opacity})`,
                labelColor: () => colors.textMuted,
                decimalPlaces: 0,
              }}
              bezier
              withDots={false}
              style={{ borderRadius: 8 }}
            />
          </View>
        </>
      )}

      {/* Extra payment accelerator */}
      <Text style={s.sectionTitle}>Payoff accelerator</Text>
      <View style={s.card}>
        <Text style={s.cardTitle}>Extra monthly payment</Text>
        <View style={s.presets}>
          {[50, 100, 200, 500].map(amt => (
            <TouchableOpacity
              key={amt}
              style={[s.preset, extraPayment === amt && s.presetActive]}
              onPress={() => setExtraPayment(amt)}
              activeOpacity={0.7}
            >
              <Text style={[s.presetText, extraPayment === amt && s.presetTextActive]}>+${amt}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <View style={s.accelStats}>
          <View style={s.accelRow}>
            <Text style={s.accelLabel}>Monthly payment</Text>
            <Text style={s.accelVal}>${(totalMin + extraPayment).toLocaleString()}</Text>
          </View>
          <View style={s.accelRow}>
            <Text style={s.accelLabel}>Months saved (est.)</Text>
            <Text style={[s.accelVal, { color: colors.success }]}>{monthsSavedRough} months</Text>
          </View>
        </View>
      </View>

      {/* Debt list */}
      <Text style={s.sectionTitle}>Your debts</Text>
      <View style={s.card}>
        {sortedDebts.map((debt, i) => {
          const pct = totalDebt > 0 ? (debt.balance / totalDebt) * 100 : 0
          const aprColor = debt.rate >= 20 ? colors.danger : debt.rate >= 10 ? colors.warning : colors.success
          return (
            <View key={i} style={[s.debtRow, i < sortedDebts.length - 1 && s.debtBorder]}>
              <View style={s.debtLeft}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                  <Text style={s.debtName}>{debt.name}</Text>
                  {i === 0 && (
                    <View style={s.firstBadge}>
                      <Text style={s.firstBadgeText}>Pay first</Text>
                    </View>
                  )}
                </View>
                <Text style={s.debtMeta}>Due in {debt.dueInDays}d · min ${debt.min}/mo</Text>
                {/* Progress bar */}
                <View style={s.bar}>
                  <View style={[s.barFill, { width: `${pct}%`, backgroundColor: aprColor }]} />
                </View>
              </View>
              <View style={s.debtRight}>
                <Text style={s.debtBalance}>${debt.balance.toLocaleString()}</Text>
                <Text style={[s.debtRate, { color: aprColor }]}>{debt.rate.toFixed(1)}%</Text>
              </View>
            </View>
          )
        })}
      </View>

      <View style={{ height: 32 }} />
    </ScrollView>
  )
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 16, paddingTop: 60 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.bg, gap: 16 },
  loadText: { color: colors.textMuted, fontSize: 14 },
  header: { marginBottom: 16 },
  eyebrow: { fontSize: 12, fontWeight: '600', color: colors.danger, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  heroTitle: { fontSize: 26, fontWeight: '800', color: colors.text, marginBottom: 4 },
  heroSub: { fontSize: 13, color: colors.textMuted },
  statsRow: { flexDirection: 'row', gap: 8, marginBottom: 20 },
  statBox: {
    flex: 1, backgroundColor: colors.surface, borderRadius: 12,
    padding: 12, borderWidth: 1, borderColor: colors.border, alignItems: 'center',
  },
  statVal: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 4 },
  statLabel: { fontSize: 11, color: colors.textMuted, textAlign: 'center' },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 10, marginTop: 4 },
  card: {
    backgroundColor: colors.surface, borderRadius: 16,
    padding: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 16,
  },
  cardTitle: { fontSize: 14, fontWeight: '600', color: colors.text, marginBottom: 10 },
  presets: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  preset: {
    flex: 1, paddingVertical: 8, borderRadius: 8,
    borderWidth: 1, borderColor: colors.border,
    backgroundColor: colors.surfaceRaised, alignItems: 'center',
  },
  presetActive: { borderColor: colors.primary, backgroundColor: colors.primaryGlow },
  presetText: { fontSize: 13, color: colors.textMuted, fontWeight: '600' },
  presetTextActive: { color: colors.primary },
  accelStats: { gap: 8 },
  accelRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  accelLabel: { fontSize: 14, color: colors.textMuted },
  accelVal: { fontSize: 15, fontWeight: '700', color: colors.text },
  debtRow: { paddingVertical: 12, flexDirection: 'row', gap: 12, alignItems: 'flex-start' },
  debtBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  debtLeft: { flex: 1 },
  debtName: { fontSize: 14, fontWeight: '600', color: colors.text, marginBottom: 2 },
  debtMeta: { fontSize: 11, color: colors.textMuted, marginBottom: 6 },
  debtRight: { alignItems: 'flex-end' },
  debtBalance: { fontSize: 15, fontWeight: '700', color: colors.text, marginBottom: 2 },
  debtRate: { fontSize: 12, fontWeight: '700' },
  bar: { height: 4, backgroundColor: colors.border, borderRadius: 2, overflow: 'hidden' },
  barFill: { height: '100%', borderRadius: 2 },
  firstBadge: { backgroundColor: colors.primaryGlow, borderRadius: 4, paddingHorizontal: 5, paddingVertical: 2 },
  firstBadgeText: { fontSize: 10, color: colors.primary, fontWeight: '700' },
})
