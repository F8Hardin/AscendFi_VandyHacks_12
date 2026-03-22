import { Tabs } from 'expo-router'
import { View, Text, StyleSheet } from 'react-native'
import { colors } from '@/lib/colors'

function TabIcon({ symbol, label, focused }: { symbol: string; label: string; focused: boolean }) {
  return (
    <View style={[ts.iconWrap, focused && ts.iconWrapActive]}>
      <Text style={ts.emoji}>{symbol}</Text>
      <Text style={[ts.iconLabel, { color: focused ? colors.primary : colors.textFaint }]}>{label}</Text>
    </View>
  )
}

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          height: 68,
          paddingBottom: 8,
        },
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ focused }) => <TabIcon symbol="📊" label="Dashboard" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="debt"
        options={{
          title: 'Debt',
          tabBarIcon: ({ focused }) => <TabIcon symbol="💳" label="Debt" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="autonomous"
        options={{
          title: 'Planner',
          tabBarIcon: ({ focused }) => <TabIcon symbol="🤖" label="Planner" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="invest"
        options={{
          title: 'Invest',
          tabBarIcon: ({ focused }) => <TabIcon symbol="📈" label="Invest" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'ARIA',
          tabBarIcon: ({ focused }) => <TabIcon symbol="✨" label="ARIA" focused={focused} />,
        }}
      />
    </Tabs>
  )
}

const ts = StyleSheet.create({
  iconWrap: { alignItems: 'center', paddingTop: 4, paddingHorizontal: 6 },
  iconWrapActive: {},
  emoji: { fontSize: 20 },
  iconLabel: { fontSize: 10, marginTop: 2, fontWeight: '600' },
})
