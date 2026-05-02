<template>
  <div class="insights-page pb-8">
    <!-- Hero Header (greeting + period totals) -->
    <div class="insights-header px-4 pt-6 pb-16 rounded-b-3xl">
      <div class="mb-5">
        <h2 class="text-2xl font-bold text-white">
          {{ greeting }}<span v-if="firstName">, {{ firstName }}</span>
        </h2>
        <p class="text-sm text-white/70 mt-1">{{ todayFormatted }}</p>
      </div>

      <!-- Summary Stats Row (period-scoped) -->
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="bg-white/15 backdrop-blur-sm rounded-2xl p-4">
          <p class="text-xs font-medium text-white/70 mb-1">Total Claims</p>
          <p class="text-2xl font-bold text-white tabular-nums">
            {{ insights ? insights.claim_count : '—' }}
          </p>
        </div>
        <div class="bg-white/15 backdrop-blur-sm rounded-2xl p-4">
          <p class="text-xs font-medium text-white/70 mb-1">Total Amount</p>
          <p class="text-2xl font-bold text-white tabular-nums">
            <span class="text-sm font-medium text-white/70">AED</span>
            {{ insights ? formatCurrency(insights.total_amount) : '—' }}
          </p>
        </div>
      </div>

      <!-- Delta vs prev period -->
      <div v-if="deltaPct !== null" class="flex items-center gap-1.5 text-xs mb-4">
        <FeatherIcon
          :name="deltaPct >= 0 ? 'trending-up' : 'trending-down'"
          class="w-3.5 h-3.5"
          :class="deltaPct >= 0 ? 'text-emerald-200' : 'text-rose-200'"
        />
        <span :class="deltaPct >= 0 ? 'text-emerald-200' : 'text-rose-200'" class="font-semibold">
          {{ deltaPct >= 0 ? '+' : '' }}{{ deltaPct.toFixed(0) }}%
        </span>
        <span class="text-white/70">vs previous {{ period }}</span>
      </div>

      <!-- Period Toggle -->
      <div class="flex bg-white/15 backdrop-blur-sm rounded-2xl p-1">
        <button
          v-for="opt in periodOptions"
          :key="opt.value"
          type="button"
          class="flex-1 py-2 text-xs font-semibold rounded-xl transition-all duration-150"
          :class="period === opt.value
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-white/70 hover:text-white'"
          @click="setPeriod(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div class="px-4 -mt-6 space-y-5">
      <!-- Loading skeletons -->
      <template v-if="insightsResource.loading && !insights">
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 animate-pulse">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="h-3 bg-gray-100 rounded w-20 mb-2"></div>
              <div class="h-6 bg-gray-100 rounded w-24"></div>
            </div>
            <div>
              <div class="h-3 bg-gray-100 rounded w-20 mb-2"></div>
              <div class="h-6 bg-gray-100 rounded w-24"></div>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 animate-pulse">
          <div class="h-4 bg-gray-100 rounded w-32 mb-4"></div>
          <div class="flex justify-center mb-4">
            <div class="w-40 h-40 rounded-full bg-gray-100"></div>
          </div>
          <div v-for="i in 3" :key="i" class="flex items-center gap-2 mb-2">
            <div class="w-2.5 h-2.5 rounded-full bg-gray-100"></div>
            <div class="h-3 bg-gray-100 rounded flex-1"></div>
          </div>
        </div>
      </template>

      <template v-else-if="insights && insights.claim_count > 0">
        <!-- Paid-by Split Card -->
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-semibold text-gray-900">Who paid?</h3>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <div class="flex items-center gap-2 mb-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <p class="text-xs font-medium text-gray-500">Paid by me</p>
              </div>
              <p class="text-xl font-bold text-gray-900 tabular-nums">
                <span class="text-xs font-medium text-gray-400">AED</span>
                {{ formatCurrency(insights.paid_by_me.amount) }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5">
                {{ insights.paid_by_me.count }} claims
              </p>
              <div v-if="insights.paid_by_me.amount > 0" class="mt-2 text-[11px] text-gray-500 leading-tight space-y-0.5">
                <p>
                  <span class="text-amber-700 font-medium">Awaiting</span>
                  AED {{ formatCurrency(insights.paid_by_me.pending_amount) }}
                </p>
                <p>
                  <span class="text-emerald-700 font-medium">Reimbursed</span>
                  AED {{ formatCurrency(insights.paid_by_me.reimbursed_amount) }}
                </p>
              </div>
            </div>
            <div>
              <div class="flex items-center gap-2 mb-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <p class="text-xs font-medium text-gray-500">Paid by company</p>
              </div>
              <p class="text-xl font-bold text-gray-900 tabular-nums">
                <span class="text-xs font-medium text-gray-400">AED</span>
                {{ formatCurrency(insights.paid_by_company.amount) }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5">
                {{ insights.paid_by_company.count }} claims
              </p>
            </div>
          </div>

          <div class="h-1.5 rounded-full bg-gray-100 overflow-hidden flex">
            <div
              class="bg-amber-500 h-full transition-all duration-500"
              :style="{ width: mePct + '%' }"
            ></div>
            <div
              class="bg-emerald-500 h-full transition-all duration-500"
              :style="{ width: companyPct + '%' }"
            ></div>
          </div>
        </div>

        <!-- By Expense Type Card -->
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 class="text-base font-semibold text-gray-900 mb-1">By expense type</h3>
          <p class="text-xs text-gray-500 mb-4">
            {{ insights.by_type.length }} {{ insights.by_type.length === 1 ? 'category' : 'categories' }}
          </p>

          <div class="flex justify-center mb-5">
            <svg :width="donutSize" :height="donutSize" :viewBox="`0 0 ${donutSize} ${donutSize}`">
              <template v-if="donutSlices.length === 1">
                <circle
                  :cx="donutSize / 2"
                  :cy="donutSize / 2"
                  :r="(donutSize - 24) / 2"
                  :fill="donutSlices[0].color"
                />
                <circle
                  :cx="donutSize / 2"
                  :cy="donutSize / 2"
                  :r="(donutSize - 24) / 2 - 28"
                  fill="white"
                />
              </template>
              <path
                v-for="slice in donutSlices.length > 1 ? donutSlices : []"
                :key="slice.claim_type"
                :d="slice.path"
                :fill="slice.color"
              />
              <text
                :x="donutSize / 2"
                :y="donutSize / 2 - 6"
                text-anchor="middle"
                class="fill-gray-400 text-[10px] font-medium uppercase tracking-wide"
              >
                Total
              </text>
              <text
                :x="donutSize / 2"
                :y="donutSize / 2 + 14"
                text-anchor="middle"
                class="fill-gray-900 text-base font-bold tabular-nums"
              >
                {{ formatCompact(insights.total_amount) }}
              </text>
            </svg>
          </div>

          <div class="space-y-2.5">
            <div
              v-for="(slice, i) in donutSlices"
              :key="slice.claim_type"
              class="flex items-center gap-3"
            >
              <span
                class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                :style="{ backgroundColor: slice.color }"
              ></span>
              <span class="text-sm text-gray-900 flex-1 truncate">{{ slice.claim_type }}</span>
              <span class="text-xs text-gray-500 tabular-nums">{{ slice.count }}</span>
              <span class="text-sm font-semibold text-gray-900 tabular-nums w-20 text-right">
                {{ formatCurrency(slice.amount) }}
              </span>
              <span class="text-xs text-gray-400 tabular-nums w-10 text-right">
                {{ slice.pct.toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty state -->
      <div
        v-else-if="insights"
        class="bg-white rounded-2xl shadow-sm border border-gray-100"
      >
        <EmptyState
          icon="bar-chart-2"
          title="No data for this period"
          message="Try a longer time range or create a claim"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { createResource, FeatherIcon } from 'frappe-ui'
import EmptyState from '@/components/EmptyState.vue'
import { useAuth } from '@/composables/useAuth'

const PALETTE = ['#29A38B', '#f59e0b', '#6366f1', '#f43f5e', '#0ea5e9']
const DONUT_SIZE = 180
const DONUT_OUTER = (DONUT_SIZE - 24) / 2
const DONUT_INNER = DONUT_OUTER - 28

function polarToCartesian(cx, cy, r, angle) {
  const rad = ((angle - 90) * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

function arcPath(cx, cy, rOuter, rInner, startAngle, endAngle) {
  const largeArc = endAngle - startAngle > 180 ? 1 : 0
  const o1 = polarToCartesian(cx, cy, rOuter, startAngle)
  const o2 = polarToCartesian(cx, cy, rOuter, endAngle)
  const i1 = polarToCartesian(cx, cy, rInner, endAngle)
  const i2 = polarToCartesian(cx, cy, rInner, startAngle)
  return [
    `M ${o1.x} ${o1.y}`,
    `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${o2.x} ${o2.y}`,
    `L ${i1.x} ${i1.y}`,
    `A ${rInner} ${rInner} 0 ${largeArc} 0 ${i2.x} ${i2.y}`,
    'Z',
  ].join(' ')
}

export default {
  name: 'Insights',
  components: { EmptyState, FeatherIcon },
  data() {
    return {
      period: 'month',
      periodOptions: [
        { value: 'month', label: 'Month' },
        { value: 'quarter', label: 'Quarter' },
        { value: 'year', label: 'Year' },
        { value: 'all', label: 'All' },
      ],
      donutSize: DONUT_SIZE,
    }
  },
  setup() {
    const insightsResource = createResource({
      url: 'claimsuite.api.get_insights',
      params: { period: 'month' },
      auto: true,
    })
    const { userInfo } = useAuth()
    return { insightsResource, userInfo }
  },
  mounted() {
    window.addEventListener('app:refresh', this._onRefresh)
  },
  beforeUnmount() {
    window.removeEventListener('app:refresh', this._onRefresh)
  },
  computed: {
    insights() {
      return this.insightsResource.data
    },
    firstName() {
      const full = this.userInfo?.full_name || ''
      return full.split(' ')[0]
    },
    greeting() {
      const hour = new Date().getHours()
      if (hour < 12) return 'Good morning'
      if (hour < 17) return 'Good afternoon'
      return 'Good evening'
    },
    todayFormatted() {
      return new Date().toLocaleDateString('en-GB', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      })
    },
    periodLabel() {
      const map = {
        month: 'This month',
        quarter: 'This quarter',
        year: 'This year',
        all: 'All time',
      }
      return map[this.period]
    },
    deltaPct() {
      if (!this.insights) return null
      const prev = this.insights.prev_total_amount
      if (prev == null || prev === 0) return null
      return ((this.insights.total_amount - prev) / prev) * 100
    },
    mePct() {
      if (!this.insights || this.insights.total_amount === 0) return 0
      return (this.insights.paid_by_me.amount / this.insights.total_amount) * 100
    },
    companyPct() {
      if (!this.insights || this.insights.total_amount === 0) return 0
      return (this.insights.paid_by_company.amount / this.insights.total_amount) * 100
    },
    donutSlices() {
      if (!this.insights || !this.insights.by_type.length) return []
      const total = this.insights.total_amount || 1
      const cx = DONUT_SIZE / 2
      const cy = DONUT_SIZE / 2
      let cursor = 0
      return this.insights.by_type.map((item, i) => {
        const pct = (item.amount / total) * 100
        const angle = (item.amount / total) * 360
        const start = cursor
        // Subtract a tiny gap for visual separation when there are multiple slices
        const end = cursor + angle - (this.insights.by_type.length > 1 ? 0.5 : 0)
        cursor += angle
        return {
          ...item,
          pct,
          color: PALETTE[i % PALETTE.length],
          path: arcPath(cx, cy, DONUT_OUTER, DONUT_INNER, start, Math.max(start + 0.01, end)),
        }
      })
    },
  },
  methods: {
    _onRefresh() {
      this.insightsResource.reload()
    },
    setPeriod(value) {
      if (this.period === value) return
      this.period = value
      this.insightsResource.update({ params: { period: value } })
      this.insightsResource.reload()
    },
    formatCurrency(val) {
      return Number(val || 0).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
    formatCompact(val) {
      const n = Number(val || 0)
      if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
      if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
      return n.toFixed(0)
    },
  },
}
</script>

<style scoped>
.insights-header {
  background: linear-gradient(135deg, #29A38B 0%, #1e8a74 100%);
}
</style>
