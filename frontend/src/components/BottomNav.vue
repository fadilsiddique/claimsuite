<template>
  <nav class="fixed bottom-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-lg border-t border-gray-100 safe-area-bottom">
    <div class="flex items-center justify-around h-16 max-w-lg mx-auto">
      <router-link
        v-for="item in items"
        :key="item.route"
        :to="item.route"
        class="flex flex-col items-center justify-center gap-1 flex-1 h-full transition-all duration-200"
        :class="isActive(item.route) ? 'text-gray-900' : 'text-gray-400'"
      >
        <div
          class="flex items-center justify-center w-10 h-10 rounded-2xl transition-all duration-200"
          :class="isActive(item.route) ? 'bg-gray-900 text-white scale-105' : 'text-gray-400 hover:bg-gray-50'"
        >
          <FeatherIcon :name="item.icon" class="w-5 h-5" />
        </div>
        <span class="text-[10px] font-medium leading-none">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'BottomNav',
  components: { FeatherIcon },
  data() {
    return {
      items: [
        { label: 'Home', icon: 'home', route: '/' },
        { label: 'New Claim', icon: 'plus-circle', route: '/new' },
        { label: 'Claims', icon: 'file-text', route: '/claims' },
      ],
    }
  },
  methods: {
    isActive(route) {
      if (route === '/') {
        return this.$route.path === '/'
      }
      return this.$route.path.startsWith(route)
    },
  },
}
</script>
