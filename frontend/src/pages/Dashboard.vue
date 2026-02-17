<template>
  <div class="dashboard-page">
    <!-- Hero Header -->
    <div class="dashboard-header px-4 pt-20 pb-16 rounded-b-3xl">
      <div class="mb-5">
        <h2 class="text-2xl font-bold text-white">
          {{ greeting }}<span v-if="firstName">, {{ firstName }}</span>
        </h2>
        <p class="text-sm text-white/70 mt-1">{{ todayFormatted }}</p>
      </div>

      <!-- Summary Stats Row -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-white/15 backdrop-blur-sm rounded-2xl p-4">
          <p class="text-xs font-medium text-white/70 mb-1">Total Claims</p>
          <p class="text-2xl font-bold text-white tabular-nums">{{ stats?.total_claims ?? '—' }}</p>
        </div>
        <div class="bg-white/15 backdrop-blur-sm rounded-2xl p-4">
          <p class="text-xs font-medium text-white/70 mb-1">Total Amount</p>
          <p class="text-2xl font-bold text-white tabular-nums">
            <span class="text-sm font-medium text-white/70">AED</span>
            {{ stats ? formatCurrency(stats.total_amount) : '—' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Floating Stats Cards (overlapping the header) -->
    <div class="px-4 -mt-6">
      <div v-if="stats" class="grid grid-cols-2 gap-3 mb-5">
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-amber-50">
              <FeatherIcon name="clock" class="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p class="text-xl font-bold text-gray-900 tabular-nums">{{ stats.draft_count }}</p>
              <p class="text-xs text-gray-500">Pending</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-green-50">
              <FeatherIcon name="check-circle" class="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p class="text-xl font-bold text-gray-900 tabular-nums">{{ stats.submitted_count }}</p>
              <p class="text-xs text-gray-500">Approved</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Skeleton -->
      <div v-else class="grid grid-cols-2 gap-3 mb-5">
        <div v-for="i in 2" :key="i" class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 animate-pulse">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gray-100"></div>
            <div class="flex-1">
              <div class="h-6 bg-gray-100 rounded w-12 mb-1"></div>
              <div class="h-3 bg-gray-50 rounded w-16"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Action -->
      <router-link
        to="/new"
        class="quick-action-btn flex items-center gap-4 text-white rounded-2xl p-5 mb-6 active:scale-[0.98] transition-all duration-100 shadow-lg"
      >
        <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/20">
          <FeatherIcon name="plus" class="w-6 h-6" />
        </div>
        <div>
          <p class="text-base font-semibold">New Expense Claim</p>
          <p class="text-xs text-white/70">Submit a new expense</p>
        </div>
        <FeatherIcon name="chevron-right" class="w-5 h-5 text-white/60 ml-auto" />
      </router-link>

      <!-- Recent Claims -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-base font-semibold text-gray-900">Recent Claims</h3>
          <router-link
            to="/claims"
            class="text-xs font-medium text-gray-500 hover:text-gray-700"
          >
            View all
          </router-link>
        </div>

        <div v-if="statsResource.loading && !stats" class="space-y-3">
          <div
            v-for="i in 3"
            :key="i"
            class="bg-white rounded-2xl p-4 border border-gray-100 animate-pulse"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-gray-100"></div>
              <div class="flex-1">
                <div class="h-4 bg-gray-100 rounded w-24 mb-2"></div>
                <div class="h-3 bg-gray-50 rounded w-32"></div>
              </div>
              <div class="h-5 bg-gray-100 rounded w-20"></div>
            </div>
          </div>
        </div>

        <div v-else-if="recentClaims.length" class="space-y-3">
          <ClaimCard
            v-for="claim in recentClaims"
            :key="claim.name"
            :claim="claim"
          />
        </div>

        <EmptyState
          v-else
          icon="file-text"
          title="No claims yet"
          message="Create your first expense claim to get started"
        >
          <template #action>
            <router-link to="/new" class="mt-4">
              <button class="btn-primary h-8 px-3 text-sm font-medium rounded-lg text-white inline-flex items-center gap-1.5">
                <FeatherIcon name="plus" class="w-4 h-4" />
                New Claim
              </button>
            </router-link>
          </template>
        </EmptyState>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui'
import { FeatherIcon } from 'frappe-ui'
import ClaimCard from '@/components/ClaimCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'Dashboard',
  components: { ClaimCard, EmptyState, FeatherIcon },
  setup() {
    const { userInfo } = useAuth()

    const statsResource = createResource({
      url: 'claimsuite.api.get_dashboard_stats',
      auto: true,
    })

    return { statsResource, userInfo }
  },
  methods: {
    formatCurrency(val) {
      return Number(val || 0).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
  },
  computed: {
    stats() {
      return this.statsResource.data
    },
    recentClaims() {
      return this.stats?.recent_claims || []
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
  },
}
</script>

<style scoped>
.dashboard-header {
  background: linear-gradient(135deg, #29A38B 0%, #1e8a74 100%);
}
.quick-action-btn {
  background: linear-gradient(135deg, #29A38B 0%, #1e8a74 100%);
  box-shadow: 0 8px 24px rgba(41, 163, 139, 0.3);
}
</style>
