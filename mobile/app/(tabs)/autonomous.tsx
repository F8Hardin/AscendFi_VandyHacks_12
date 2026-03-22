import { useEffect } from 'react'
import {
  View, Text, ScrollView, StyleSheet, RefreshControl, ActivityIndicator,
} from 'react-native'
import { PieChart } from 'react-native-chart-kit'
import { Dimensions } from 'react-native'
import { useFinancialData } from '@/hooks/useFinancialData'
import { colors } from '@/lib/colors'

const W = Dimensions.get('window').width

export default function AutonomousTab() {
  const { data, isLoading, refresh } = useFinancialData()

  useEffect(() => { refresh() }, [])

  if (isLoading && !data) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={s.loadText}>Building your autonomous finance plan…</Text>
      </View>
    )
  }

  const d = data!
  const b = d.behavior

  const recs = b?.recommendations ?? []
  const priorityColor = (p: string) =>
    p === 'high' ? colors.danger : p === 'medium' ? colors.warning : colors.success

  // Paycheck split pie
  const pieData = d.paycheckSplit.labels.map((label, i) => ({
    name: label,
    amount: d.paycheckSplit.amounts[i] ?? 0,
    color: d.paycheckSplit.colors[i] ?? colors.chart[i % colors.chart.length],
    legendFontColor: colors.textMuted,
    legendFontSize: 11,
  }))

  return (
    <ScrollView
      style={s.container}
      contentContainerStyle={s.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refresh} tintColor={colors.primary} />}
    >
      <View style={s.header}>
        <Text style={s.eyebrow}>Autonomous finance</Text>
        <Text style={s.heroTitle}>Your AI plan</Text>
        <Text style={s.heroSub}>Paycheck split, next steps, and behavior profile</Text>
      </View>

      {/* Behavior profile */}
      {b && (
        <>
          <Text style={s.sectionTitle}>AI behavior profile</Text>
          <View style={s.profileCard}>
            <View style={s.profileTop}>
              {b.profile?.emoji && <Text style={s.profileEmoji}>{b.profile.emoji}</Text>}
              <View style={{ flex: 1 }}>
                <Text style={s.profileArchetype}>{b.profile?.archetype ?? 'Financial Profile'}</Text>
                {b.scoreBand && <Text style={s.profileBand}>{b.scoreBand}</Text>}
              </View>
              {b.score != null && (
                <View style={s.scoreBox}>
                  <Text style={s.scoreNum}>{b.score}</Text>
                  <Text style={s.scoreDenom}>/100</Text>
                </View>
              )}
            </View>
            {b.trend && (
              <View style={s.trendRow}>
                <Text style={s.trendLabel}>Trend: </Text>
                <Text style={[s.trendVal, {
                  color: b.trend === 'improving' ? colors.success : b.trend === 'declining' ? colors.danger : colors.textMuted,
                }]}>
                  {b.trend === 'improving' ? '↑ Improving' : b.trend === 'declining' ? '↓ Declining' : '→ Stable'}
                </Text>
              </View>
            )}
            {b.aiSummary && <Text style={s.aiSummary}>{b.aiSummary}</Text>}
          </View>
        </>
      )}

      {/* AI Next Steps */}
      <Text style={s.sectionTitle}>AI next steps</Text>
      <View style={s.card}>
        {recs.length > 0
          ? recs.map((rec, i) => (
            <View key={i} style={[s.stepRow, i < recs.length - 1 && s.stepBorder]}>
              <View style={[s.stepNum, { backgroundColor: priorityColor(rec.priority) + '20', borderColor: priorityColor(rec.priority) + '50' }]}>
                <Text style={[s.stepNumText, { color: priorityColor(rec.priority) }]}>{i + 1}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={s.stepTitle}>{rec.title}</Text>
                <Text style={s.stepDesc}>{rec.description}</Text>
                {rec.impact && <Text style={s.stepImpact}>{rec.impact}</Text>}
              </View>
            </View>
          ))
          : (
            <Text style={s.emptyText}>AI next steps will appear after analysis runs.</Text>
          )}
      </View>

      {/* Paycheck split */}
      <Text style={s.sectionTitle}>Paycheck split</Text>
      <View style={s.card}>
        <Text style={s.cardTitle}>
          Suggested allocation from ${d.user.monthlyIncome.toLocaleString()}/mo
        </Text>
        {pieData.length > 0 && (
          <PieChart
            data={pieData}
            width={W - 48}
            height={200}
            chartConfig={{
              backgroundGradientFrom: colors.surfaceRaised,
              backgroundGradientTo: colors.surfaceRaised,
              color: () => colors.primary,
              labelColor: () => colors.textMuted,
            }}
            accessor="amount"
            backgroundColor="transparent"
            paddingLeft="8"
            hasLegend
          />
        )}
        {/* Bucket detail */}
        <View style={{ marginTop: 8 }}>
          {d.paycheckSplit.labels.map((label, i) => (
            <View key={label} style={s.bucketRow}>
              <View style={[s.bucketDot, { backgroundColor: d.paycheckSplit.colors[i] ?? colors.primary }]} />
              <Text style={s.bucketLabel}>{label}</Text>
              <Text style={s.bucketAmt}>${(d.paycheckSplit.amounts[i] ?? 0).toLocaleString()}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Emergency fund */}
      <Text style={s.sectionTitle}>Emergency fund</Text>
      <View style={s.card}>
        {(() => {
          const monthly = d.user.monthlyIncome
          const savings = d.accounts.savings
          const expenses = d.paycheckSplit.amounts[0] ?? monthly * 0.5
          const monthsCovered = expenses > 0 ? (savings / expenses) : 0
          const target3mo = expenses * 3
          const pct = Math.min((savings / target3mo) * 100, 100)
          return (
            <>
              <View style={s.efHeader}>
                <Text style={s.efMonths}>{monthsCovered.toFixed(1)}</Text>
                <Text style={s.efUnit}>months covered</Text>
              </View>
              <View style={s.efBar}>
                <View style={[s.efFill, { width: `${pct}%`, backgroundColor: pct >= 100 ? colors.success : pct >= 50 ? colors.warning : colors.danger }]} />
              </View>
              <Text style={s.efText}>
                ${savings.toLocaleString()} saved · target ${target3mo.toLocaleString()} (3 months)
              </Text>
              {pct < 100 && (
                <Text style={s.efNeeded}>
                  ${(target3mo - savings).toLocaleString()} more needed to reach 3-month goal
                </Text>
              )}
            </>
          )
        })()}
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
  eyebrow: { fontSize: 12, fontWeight: '600', color: colors.primary, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  heroTitle: { fontSize: 26, fontWeight: '800', color: colors.text, marginBottom: 4 },
  heroSub: { fontSize: 13, color: colors.textMuted },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 10, marginTop: 4 },
  card: {
    backgroundColor: colors.surface, borderRadius: 16,
    padding: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 16,
  },
  cardTitle: { fontSize: 14, fontWeight: '600', color: colors.text, marginBottom: 12 },
  profileCard: {
    backgroundColor: colors.surface, borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: colors.border, borderLeftWidth: 4,
    borderLeftColor: colors.primary, marginBottom: 16,
  },
  profileTop: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 10 },
  profileEmoji: { fontSize: 32 },
  profileArchetype: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 2 },
  profileBand: { fontSize: 12, color: colors.textMuted },
  scoreBox: { alignItems: 'center' },
  scoreNum: { fontSize: 32, fontWeight: '800', color: colors.primary, lineHeight: 36 },
  scoreDenom: { fontSize: 11, color: colors.textMuted },
  trendRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  trendLabel: { fontSize: 13, color: colors.textMuted },
  trendVal: { fontSize: 13, fontWeight: '700' },
  aiSummary: { fontSize: 14, color: colors.text, lineHeight: 20, opacity: 0.9 },
  stepRow: { flexDirection: 'row', gap: 12, paddingVertical: 12, alignItems: 'flex-start' },
  stepBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  stepNum: {
    width: 28, height: 28, borderRadius: 14, alignItems: 'center',
    justifyContent: 'center', borderWidth: 1, flexShrink: 0,
  },
  stepNumText: { fontSize: 13, fontWeight: '800' },
  stepTitle: { fontSize: 14, fontWeight: '600', color: colors.text, marginBottom: 3 },
  stepDesc: { fontSize: 13, color: colors.textMuted, lineHeight: 18, marginBottom: 3 },
  stepImpact: { fontSize: 12, color: colors.primary, fontWeight: '600' },
  emptyText: { color: colors.textMuted, fontSize: 14 },
  bucketRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6, gap: 10 },
  bucketDot: { width: 10, height: 10, borderRadius: 5 },
  bucketLabel: { flex: 1, fontSize: 13, color: colors.text },
  bucketAmt: { fontSize: 13, fontWeight: '700', color: colors.text },
  efHeader: { flexDirection: 'row', alignItems: 'baseline', gap: 6, marginBottom: 10 },
  efMonths: { fontSize: 36, fontWeight: '800', color: colors.primary },
  efUnit: { fontSize: 14, color: colors.textMuted },
  efBar: { height: 8, backgroundColor: colors.border, borderRadius: 4, overflow: 'hidden', marginBottom: 8 },
  efFill: { height: '100%', borderRadius: 4 },
  efText: { fontSize: 12, color: colors.textMuted, marginBottom: 4 },
  efNeeded: { fontSize: 12, color: colors.warning, fontWeight: '600' },
})
