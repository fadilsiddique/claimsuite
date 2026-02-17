<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <TopBar
      :title="pageTitle"
      :show-back="showBack"
      :show-avatar="!showBack"
      :user-image="userImage"
      :transparent="isDashboard && !scrolledPastHeader"
      @avatar-click="showProfileMenu = true"
    />
    <main ref="mainContent" class="flex-1 pb-24 overflow-y-auto" :class="{ '-mt-14': isDashboard }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <BottomNav />

    <Dialog
      v-model="showProfileMenu"
      :options="{ title: 'Profile', size: 'sm' }"
    >
      <template #body-content>
        <div class="flex flex-col items-center gap-4 py-4">
          <div class="w-16 h-16 rounded-full overflow-hidden bg-gray-100 ring-4 ring-gray-50">
            <img
              v-if="userImage"
              :src="userImage"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <FeatherIcon name="user" class="w-8 h-8 text-gray-400" />
            </div>
          </div>
          <div class="text-center">
            <p class="text-base font-semibold text-gray-900">{{ fullName }}</p>
            <p class="text-sm text-gray-500">{{ userEmail }}</p>
          </div>
          <Button
            theme="red"
            variant="solid"
            class="w-full"
            @click="handleLogout"
            icon-left="log-out"
            label="Sign Out"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script>
import TopBar from './TopBar.vue'
import BottomNav from './BottomNav.vue'
import { Dialog, FeatherIcon, Button } from 'frappe-ui'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'AppShell',
  components: { TopBar, BottomNav, Dialog, FeatherIcon, Button },
  setup() {
    const { userInfo, user, logout } = useAuth()
    return { userInfo, user, logout }
  },
  data() {
    return {
      showProfileMenu: false,
      scrolledPastHeader: false,
    }
  },
  mounted() {
    this.$refs.mainContent?.addEventListener('scroll', this.handleScroll, { passive: true })
  },
  beforeUnmount() {
    this.$refs.mainContent?.removeEventListener('scroll', this.handleScroll)
  },
  computed: {
    pageTitle() {
      return this.$route.meta.title || 'ClaimSuite'
    },
    showBack() {
      return !!this.$route.meta.showBack
    },
    isDashboard() {
      return this.$route.name === 'Dashboard'
    },
    userImage() {
      return this.userInfo?.user_image || null
    },
    fullName() {
      return this.userInfo?.full_name || ''
    },
    userEmail() {
      return this.user || ''
    },
  },
  methods: {
    handleLogout() {
      this.showProfileMenu = false
      this.logout()
    },
  },
}
</script>
