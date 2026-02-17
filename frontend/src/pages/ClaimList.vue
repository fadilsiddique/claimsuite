<template>
  <div class="px-4 py-5">
    <!-- Filter Tabs -->
    <div class="flex gap-2 mb-5 overflow-x-auto no-scrollbar">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        class="shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-150"
        :class="activeTab === tab.value
          ? 'bg-gray-900 text-white'
          : 'bg-white text-gray-600 border border-gray-100 hover:bg-gray-50'"
      >
        {{ tab.label }}
        <span
          v-if="tab.count !== undefined"
          class="ml-1.5 text-xs opacity-70"
        >{{ tab.count }}</span>
      </button>
    </div>

    <!-- Claims List -->
    <div v-if="claimsResource.loading && !claims.length" class="space-y-3">
      <div
        v-for="i in 5"
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

    <div v-else-if="claims.length" class="space-y-3">
      <ClaimCard
        v-for="claim in claims"
        :key="claim.name"
        :claim="claim"
      />

      <!-- Infinite scroll sentinel -->
      <div ref="sentinel" class="h-1" />

      <!-- Loading more indicator -->
      <div v-if="loadingMore" class="flex justify-center py-3">
        <div class="w-6 h-6 border-2 border-gray-200 border-t-gray-600 rounded-full animate-spin"></div>
      </div>

      <!-- End of list -->
      <p v-if="!hasMore && claims.length > PAGE_SIZE" class="text-center text-xs text-gray-400 py-3">
        All claims loaded
      </p>
    </div>

    <EmptyState
      v-else
      icon="file-text"
      :title="emptyTitle"
      :message="emptyMessage"
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
</template>

<script>
import { createResource } from 'frappe-ui'
import { FeatherIcon } from 'frappe-ui'
import ClaimCard from '@/components/ClaimCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const PAGE_SIZE = 20

export default {
  name: 'ClaimList',
  components: { ClaimCard, EmptyState, FeatherIcon },
  setup() {
    const claimsResource = createResource({
      url: 'claimsuite.api.get_claims',
    })

    return { claimsResource }
  },
  data() {
    return {
      PAGE_SIZE,
      activeTab: 'all',
      claims: [],
      start: 0,
      hasMore: false,
      loadingMore: false,
      observer: null,
      tabs: [
        { label: 'All', value: 'all' },
        { label: 'Draft', value: 'draft' },
        { label: 'Submitted', value: 'submitted' },
        { label: 'Cancelled', value: 'cancelled' },
      ],
    }
  },
  computed: {
    emptyTitle() {
      if (this.activeTab === 'all') return 'No claims yet'
      return `No ${this.activeTab} claims`
    },
    emptyMessage() {
      if (this.activeTab === 'all') return 'Create your first expense claim to get started'
      return `You don't have any ${this.activeTab} claims`
    },
  },
  watch: {
    activeTab() {
      this.claims = []
      this.start = 0
      this.hasMore = false
      this.fetchClaims()
    },
  },
  mounted() {
    this.fetchClaims()
    this.setupObserver()
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect()
    }
  },
  methods: {
    setupObserver() {
      this.observer = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && this.hasMore && !this.loadingMore) {
            this.loadMore()
          }
        },
        { rootMargin: '200px' }
      )
      this.$nextTick(() => {
        if (this.$refs.sentinel) {
          this.observer.observe(this.$refs.sentinel)
        }
      })
    },
    async fetchClaims() {
      const isLoadMore = this.start > 0
      if (isLoadMore) this.loadingMore = true

      await this.claimsResource.submit({
        status: this.activeTab,
        start: this.start,
        limit: PAGE_SIZE,
      })

      const data = this.claimsResource.data || []
      if (this.start === 0) {
        this.claims = data
      } else {
        this.claims.push(...data)
      }
      this.hasMore = data.length === PAGE_SIZE
      this.loadingMore = false

      // Re-observe sentinel after DOM update
      this.$nextTick(() => {
        if (this.$refs.sentinel && this.observer) {
          this.observer.observe(this.$refs.sentinel)
        }
      })
    },
    loadMore() {
      this.start += PAGE_SIZE
      this.fetchClaims()
    },
  },
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
