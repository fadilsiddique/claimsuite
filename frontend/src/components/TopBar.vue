<template>
  <header
    class="sticky top-0 z-30 transition-all duration-300"
    :class="transparent ? 'bg-gradient-to-b from-black/20 to-transparent' : 'bg-white/80 backdrop-blur-lg border-b border-gray-100'"
  >
    <div class="flex items-center justify-between px-4 h-14">
      <div class="flex items-center gap-2.5">
        <button
          v-if="showBack"
          @click="$router.back()"
          class="flex items-center justify-center w-9 h-9 -ml-1 rounded-xl hover:bg-gray-100 transition-colors"
        >
          <FeatherIcon name="arrow-left" class="w-5 h-5" :class="transparent ? 'text-white' : 'text-gray-700'" />
        </button>
        <div
          v-if="showBrand && !showBack"
          class="flex items-center justify-center w-7 h-7 rounded-lg"
          style="background: rgba(255,255,255,0.2)"
        >
          <FeatherIcon name="file-text" class="w-4 h-4 text-white" />
        </div>
        <h1 class="text-lg font-semibold truncate" :class="transparent ? 'text-white' : 'text-gray-900'">{{ title }}</h1>
      </div>
      <div class="flex items-center gap-2">
        <slot name="actions" />
        <button
          v-if="showAvatar"
          @click="$emit('avatar-click')"
          class="flex items-center justify-center w-9 h-9 rounded-full overflow-hidden ring-2"
          :class="transparent ? 'bg-white/20 ring-white/20' : 'bg-gray-100 ring-gray-50'"
        >
          <img
            v-if="userImage"
            :src="userImage"
            class="w-full h-full object-cover"
          />
          <FeatherIcon v-else name="user" class="w-4 h-4" :class="transparent ? 'text-white' : 'text-gray-500'" />
        </button>
      </div>
    </div>
  </header>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'TopBar',
  components: { FeatherIcon },
  props: {
    title: { type: String, default: '' },
    showBack: { type: Boolean, default: false },
    showBrand: { type: Boolean, default: false },
    showAvatar: { type: Boolean, default: true },
    userImage: { type: String, default: null },
    transparent: { type: Boolean, default: false },
  },
  emits: ['avatar-click'],
}
</script>
