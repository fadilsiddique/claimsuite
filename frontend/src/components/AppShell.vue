<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <TopBar
      :title="pageTitle"
      :show-back="showBack"
      :show-brand="isDashboard && !scrolledPastHeader"
      :show-avatar="!showBack"
      :user-image="userImage"
      :transparent="isDashboard && !scrolledPastHeader"
      @avatar-click="showProfileMenu = true"
    />

    <!-- Pull-to-refresh indicator (fixed, below top bar) -->
    <div class="fixed left-0 right-0 z-20 flex justify-center pointer-events-none" style="top: 56px">
      <div
        class="flex items-center justify-center w-9 h-9 rounded-full bg-white shadow-md"
        :style="{
          transform: isPulling
            ? `translateY(${pullDistance - 4}px)`
            : isRefreshing
            ? 'translateY(20px)'
            : 'translateY(-48px)',
          transition: isPulling ? 'none' : 'transform 0.3s ease',
          opacity: isPulling || isRefreshing ? 1 : 0,
        }"
      >
        <div
          class="w-5 h-5 border-2 rounded-full"
          :class="isRefreshing ? 'border-gray-200 border-t-[#29A38B] animate-spin' : 'border-gray-400'"
          :style="!isRefreshing ? { transform: `rotate(${pullDistance * 3}deg)` } : {}"
        ></div>
      </div>
    </div>

    <main ref="mainContent" class="flex-1 pb-24 overflow-y-auto" style="overscroll-behavior-y: none" :class="{ '-mt-14': isDashboard }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <InstallPrompt />
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
import InstallPrompt from './InstallPrompt.vue'
import { Dialog, FeatherIcon, Button } from 'frappe-ui'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'AppShell',
  components: { TopBar, BottomNav, InstallPrompt, Dialog, FeatherIcon, Button },
  setup() {
    const { userInfo, user, logout } = useAuth()
    return { userInfo, user, logout }
  },
  data() {
    return {
      showProfileMenu: false,
      scrolledPastHeader: false,
      isPulling: false,
      pullDistance: 0,
      isRefreshing: false,
    }
  },
  mounted() {
    const el = this.$refs.mainContent
    if (!el) return
    el.addEventListener('scroll', this.handleScroll, { passive: true })
    el.addEventListener('touchstart', this._ptrTouchStart, { passive: true })
    el.addEventListener('touchmove', this._ptrTouchMove, { passive: true })
    el.addEventListener('touchend', this._ptrTouchEnd, { passive: true })
  },
  beforeUnmount() {
    const el = this.$refs.mainContent
    if (!el) return
    el.removeEventListener('scroll', this.handleScroll)
    el.removeEventListener('touchstart', this._ptrTouchStart)
    el.removeEventListener('touchmove', this._ptrTouchMove)
    el.removeEventListener('touchend', this._ptrTouchEnd)
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
    handleScroll() {
      const el = this.$refs.mainContent
      if (!el) return
      this.scrolledPastHeader = el.scrollTop > 120
      this._lastScrollTime = Date.now()
    },
    handleLogout() {
      this.showProfileMenu = false
      this.logout()
    },

    // Pull-to-refresh
    _ptrTouchStart(e) {
      this._ptrActive = false
      if (this.$refs.mainContent?.scrollTop !== 0) return
      // Require 800ms of stillness so momentum scrolls landing at top don't arm PTR
      if (Date.now() - (this._lastScrollTime || 0) < 800) return
      this._ptrStartY = e.touches[0].clientY
      this._ptrLastY = e.touches[0].clientY
      this._ptrActive = true
    },
    _ptrTouchMove(e) {
      if (!this._ptrActive) return
      const currentY = e.touches[0].clientY
      const dy = currentY - this._ptrStartY      // cumulative from start
      const step = currentY - this._ptrLastY     // movement since last frame

      // Cancel if content scrolled away from top
      if (this.$refs.mainContent?.scrollTop > 0) {
        this._ptrActive = false
        this.isPulling = false
        this.pullDistance = 0
        return
      }

      // Cancel if finger is moving upward or total pull is negative —
      // this catches scroll gestures that start at the top
      if (dy <= 0 || step < 0) {
        this._ptrActive = false
        this.isPulling = false
        this.pullDistance = 0
        return
      }

      this._ptrLastY = currentY

      // Dead zone — require an intentional 30px pull before showing anything
      if (dy < 30) return

      this.isPulling = true
      this.pullDistance = Math.min((dy - 30) * 0.5, 80)
    },
    _ptrTouchEnd() {
      if (!this._ptrActive) return
      this._ptrActive = false
      if (this.pullDistance >= 60) {
        this.isRefreshing = true
        this.isPulling = false
        this.pullDistance = 0
        window.dispatchEvent(new Event('app:refresh'))
        setTimeout(() => { this.isRefreshing = false }, 1500)
      } else {
        this.isPulling = false
        this.pullDistance = 0
      }
    },
  },

}
</script>
