<template>
  <div class="min-h-screen flex flex-col" style="background: linear-gradient(150deg, #29A38B 0%, #1e8a74 100%)">
    <!-- Branding -->
    <div class="flex flex-col items-center justify-center flex-1 px-6 pb-4 pt-16">
      <div
        class="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 shadow-lg"
        style="background: rgba(255,255,255,0.2); backdrop-filter: blur(10px)"
      >
        <FeatherIcon name="file-text" class="w-8 h-8 text-white" />
      </div>
      <h1 class="text-3xl font-bold text-white tracking-tight">ClaimSuite</h1>
      <p class="text-white/70 text-sm mt-1">Expense Management</p>
    </div>

    <!-- Login card (rounded-top sheet) -->
    <div class="bg-white rounded-t-3xl px-6 pt-8 pb-10 shadow-2xl">
      <h2 class="text-xl font-bold text-gray-900">Welcome back 👋</h2>
      <p class="text-sm text-gray-500 mt-1 mb-6">Sign in to continue</p>

      <!-- Error -->
      <transition name="fade">
        <div
          v-if="error"
          class="mb-5 px-4 py-3 bg-red-50 border border-red-100 rounded-xl flex items-start gap-2"
        >
          <FeatherIcon name="alert-circle" class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>
      </transition>

      <!-- Username -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Email or Username</label>
        <input
          v-model="form.usr"
          type="email"
          autocomplete="username"
          placeholder="you@company.com"
          class="w-full h-12 px-4 bg-gray-50 border-2 border-gray-100 rounded-xl text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:ring-0 outline-none transition-colors"
          @keyup.enter="handleLogin"
        />
      </div>

      <!-- Password -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
        <div class="relative">
          <input
            v-model="form.pwd"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full h-12 px-4 pr-12 bg-gray-50 border-2 border-gray-100 rounded-xl text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:ring-0 outline-none transition-colors"
            @keyup.enter="handleLogin"
          />
          <button
            type="button"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            @click="showPassword = !showPassword"
          >
            <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Sign In button -->
      <button
        class="btn-primary w-full h-12 text-base font-semibold rounded-xl text-white flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="loading || !form.usr || !form.pwd"
        @click="handleLogin"
      >
        <span
          v-if="loading"
          class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"
        ></span>
        {{ loading ? 'Signing in…' : 'Sign In' }}
      </button>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'Login',
  components: { FeatherIcon },
  setup() {
    const { login } = useAuth()
    return { login }
  },
  data() {
    return {
      form: { usr: '', pwd: '' },
      showPassword: false,
      loading: false,
      error: '',
    }
  },
  methods: {
    async handleLogin() {
      if (!this.form.usr || !this.form.pwd || this.loading) return
      this.error = ''
      this.loading = true
      try {
        await this.login(this.form.usr, this.form.pwd)
        // App.vue reactively shows AppShell — no explicit navigation needed
      } catch (err) {
        this.error = err.message || 'Something went wrong. Please try again.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
