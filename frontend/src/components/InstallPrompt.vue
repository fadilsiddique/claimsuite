<template>
  <transition name="slide-up">
    <div
      v-if="canInstall"
      class="fixed left-4 right-4 z-30"
      style="bottom: 84px"
    >
      <div class="bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
        <!-- Top accent bar -->
        <div class="h-1 w-full" style="background: linear-gradient(90deg, #29A38B 0%, #1e8a74 100%)"></div>

        <div class="p-4">
          <div class="flex items-start gap-3">
            <!-- Icon -->
            <div
              class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
              style="background: linear-gradient(135deg, #29A38B 0%, #1e8a74 100%)"
            >
              <FeatherIcon name="download" class="w-5 h-5 text-white" />
            </div>

            <!-- Text -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900">Add to Home Screen</p>
              <p class="text-xs text-gray-500 mt-0.5 leading-relaxed">
                Install ClaimSuite for faster access and a native app experience.
              </p>
            </div>

            <!-- Dismiss X -->
            <button
              class="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors shrink-0 -mr-1 -mt-1"
              @click="dismiss"
            >
              <FeatherIcon name="x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <!-- Buttons -->
          <div class="flex gap-2 mt-4">
            <button
              class="btn-primary flex-1 h-10 text-sm font-semibold rounded-xl text-white flex items-center justify-center gap-1.5 active:scale-[0.98] transition-transform"
              @click="install"
            >
              <FeatherIcon name="download" class="w-3.5 h-3.5" />
              Install App
            </button>
            <button
              class="flex-1 h-10 text-sm font-medium text-gray-600 bg-gray-100 rounded-xl hover:bg-gray-200 active:scale-[0.98] transition-all"
              @click="dismiss"
            >
              Maybe Later
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { useInstallPrompt } from '@/composables/useInstallPrompt'

export default {
  name: 'InstallPrompt',
  components: { FeatherIcon },
  setup() {
    const { canInstall, install, dismiss } = useInstallPrompt()
    return { canInstall, install, dismiss }
  },
}
</script>

<style scoped>
.slide-up-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.slide-up-leave-active {
  transition: all 0.2s ease-in;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(120%);
  opacity: 0;
}
</style>
