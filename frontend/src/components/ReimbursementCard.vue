<template>
  <div
    class="reimbursement-card relative overflow-hidden rounded-2xl shadow-xl
           aspect-[1.586/1] max-w-md mx-auto
           text-white p-5 flex flex-col justify-between"
  >
    <!-- Decorative shine orbs -->
    <div class="absolute -top-20 -right-20 w-48 h-48 rounded-full bg-white/10 blur-2xl pointer-events-none"></div>
    <div class="absolute -bottom-16 -left-16 w-40 h-40 rounded-full bg-white/5 blur-2xl pointer-events-none"></div>

    <!-- Top: brand + icon -->
    <div class="relative flex items-start justify-between">
      <div>
        <p class="text-sm font-semibold tracking-wide">ClaimSuite</p>
        <p class="text-[10px] uppercase tracking-[0.2em] text-white/60 mt-0.5">
          Reimbursement Card
        </p>
      </div>
      <FeatherIcon name="credit-card" class="w-5 h-5 text-white/80" />
    </div>

    <!-- Middle: chip + label + amount -->
    <div class="relative">
      <div
        class="w-10 h-7 rounded-md bg-gradient-to-br from-amber-200 to-amber-400/80 shadow-inner mb-3
               flex flex-col justify-center gap-[2px] px-1"
      >
        <span class="block h-px bg-amber-700/30"></span>
        <span class="block h-px bg-amber-700/30"></span>
      </div>
      <p class="text-[10px] uppercase tracking-[0.2em] text-white/60 mb-1">
        {{ amount > 0 ? 'Pending Reimbursement' : 'No Pending' }}
      </p>
      <p class="text-3xl font-bold tabular-nums leading-none">
        <span class="text-base font-medium text-white/70 mr-1">AED</span>{{ formattedAmount }}
      </p>
    </div>

    <!-- Bottom: holder + count + date + QR placeholder -->
    <div class="relative">
      <div class="border-t border-white/15 pt-2.5 flex items-end justify-between gap-3">
        <div class="min-w-0 flex-1">
          <p class="text-[9px] uppercase tracking-[0.2em] text-white/50">Cardholder</p>
          <p class="text-sm font-semibold truncate">{{ holderDisplay }}</p>
          <p class="text-[10px] text-white/60 mt-0.5">
            {{ amount > 0 ? `Updated ${formattedDate}` : 'All caught up · No pending claims' }}
          </p>
        </div>
        <div class="flex flex-col items-end gap-1.5">
          <div class="text-right">
            <p class="text-[9px] uppercase tracking-[0.2em] text-white/50">Claims</p>
            <p class="text-sm font-semibold tabular-nums">{{ count }}</p>
          </div>
          <!-- QR placeholder (real Wallet QR slots in here later) -->
          <div class="w-9 h-9 rounded bg-white/15 flex items-center justify-center">
            <FeatherIcon name="maximize" class="w-3 h-3 text-white/50" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'ReimbursementCard',
  components: { FeatherIcon },
  props: {
    amount: { type: Number, required: true },
    count: { type: Number, required: true },
    holder: { type: String, default: '' },
    updatedAt: { type: [String, Date], default: () => new Date() },
  },
  computed: {
    formattedAmount() {
      return Number(this.amount || 0).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
    formattedDate() {
      const d = this.updatedAt instanceof Date ? this.updatedAt : new Date(this.updatedAt)
      return d.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    },
    holderDisplay() {
      return (this.holder || 'ClaimSuite User').toUpperCase()
    },
  },
}
</script>

<style scoped>
.reimbursement-card {
  background: linear-gradient(135deg, #29A38B 0%, #1e8a74 55%, #0f5f50 100%);
}
</style>
