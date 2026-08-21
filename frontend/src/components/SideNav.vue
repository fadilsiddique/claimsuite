<template>
  <!-- Desktop only: the mobile shell keeps using BottomNav -->
  <aside class="w-60 shrink-0 bg-white border-r border-gray-100 flex-col">
    <!-- Brand -->
    <div class="flex items-center gap-2.5 h-14 px-5 border-b border-gray-50">
      <div class="w-7 h-7 rounded-lg overflow-hidden bg-white shadow-sm shrink-0">
        <img
          :src="'/assets/claimsuite/frontend/icon-source.png'"
          alt="ClaimSuite"
          class="w-full h-full object-contain"
        />
      </div>
      <span class="text-base font-semibold text-gray-900">ClaimSuite</span>
    </div>

    <div class="flex-1 overflow-y-auto p-3">
      <!-- Primary action -->
      <router-link
        to="/new"
        class="new-claim-btn flex items-center gap-2.5 rounded-xl px-3 h-11 mb-4 text-white
               text-sm font-semibold hover:brightness-105 transition"
      >
        <FeatherIcon name="plus" class="w-4 h-4" />
        New Claim
      </router-link>

      <p class="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-gray-400">
        Menu
      </p>
      <nav class="space-y-0.5">
        <router-link
          v-for="item in items"
          :key="item.route"
          :to="item.route"
          class="flex items-center gap-3 rounded-xl px-3 h-10 text-sm font-medium transition-colors"
          :class="isActive(item.route)
            ? 'bg-gray-900 text-white'
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
        >
          <FeatherIcon :name="item.icon" class="w-4 h-4 shrink-0" />
          {{ item.label }}
        </router-link>
      </nav>
    </div>

    <!-- Profile -->
    <button
      type="button"
      @click="$emit('profile-click')"
      class="flex items-center gap-3 w-full p-3 border-t border-gray-50 hover:bg-gray-50 transition-colors text-left"
    >
      <div class="w-9 h-9 rounded-full overflow-hidden bg-gray-100 ring-2 ring-gray-50 shrink-0">
        <img v-if="userImage" :src="userImage" class="w-full h-full object-cover" />
        <div v-else class="w-full h-full flex items-center justify-center">
          <FeatherIcon name="user" class="w-4 h-4 text-gray-400" />
        </div>
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium text-gray-900 truncate">{{ fullName || 'Account' }}</p>
        <p class="text-xs text-gray-500 truncate">{{ userEmail }}</p>
      </div>
      <FeatherIcon name="more-vertical" class="w-4 h-4 text-gray-400 shrink-0" />
    </button>
  </aside>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'SideNav',
  components: { FeatherIcon },
  props: {
    userImage: { type: String, default: null },
    fullName: { type: String, default: '' },
    userEmail: { type: String, default: '' },
  },
  emits: ['profile-click'],
  data() {
    return {
      items: [
        { label: 'Home', icon: 'home', route: '/' },
        { label: 'Claims', icon: 'file-text', route: '/claims' },
        { label: 'Insights', icon: 'bar-chart-2', route: '/insights' },
      ],
    }
  },
  methods: {
    isActive(route) {
      if (route === '/') return this.$route.path === '/'
      return this.$route.path.startsWith(route)
    },
  },
}
</script>

<style scoped>
.new-claim-btn {
  background: linear-gradient(135deg, #29a38b 0%, #1e8a74 100%);
  box-shadow: 0 4px 12px -4px rgba(41, 163, 139, 0.5);
}
</style>
