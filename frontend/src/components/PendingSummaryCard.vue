<template>
  <router-link
    to="/claims"
    class="summary-card relative block overflow-hidden rounded-3xl p-5 text-white
           active:scale-[0.98] transition-transform duration-100
           lg:p-6 lg:transition-all lg:hover:-translate-y-0.5 lg:hover:brightness-105"
    :class="`is-${state}`"
  >
    <!-- Soft light -->
    <div class="absolute -top-24 -right-16 w-56 h-56 rounded-full bg-white/10 blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-20 -left-12 w-44 h-44 rounded-full bg-white/[0.07] blur-3xl pointer-events-none"></div>
    <div class="sheen pointer-events-none"></div>

    <!-- Header -->
    <div class="relative flex items-start justify-between gap-3">
      <span
        class="inline-flex items-center gap-1.5 rounded-full bg-white/15 backdrop-blur-sm
               pl-1.5 pr-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em]"
      >
        <span class="relative flex w-1.5 h-1.5">
          <span
            v-if="state !== 'settled'"
            class="absolute inline-flex w-full h-full rounded-full bg-white opacity-70 animate-ping"
          ></span>
          <span class="relative inline-flex w-1.5 h-1.5 rounded-full bg-white"></span>
        </span>
        {{ badge }}
      </span>

      <span class="flex items-center justify-center w-7 h-7 rounded-full bg-white/15 shrink-0">
        <FeatherIcon name="arrow-up-right" class="w-4 h-4 text-white/90" />
      </span>
    </div>

    <!-- Amount -->
    <div class="relative mt-5">
      <p class="text-[10px] font-medium uppercase tracking-[0.2em] text-white/60">
        {{ label }}
      </p>
      <p class="mt-1.5 flex items-baseline gap-1.5 leading-none">
        <span class="text-sm font-semibold text-white/70">AED</span>
        <span class="text-[2.125rem] font-bold tabular-nums tracking-tight">{{ formattedAmount }}</span>
      </p>
    </div>

    <!-- Footer facts -->
    <div class="relative mt-5 pt-3.5 border-t border-white/15 flex items-center gap-5">
      <div class="flex items-center gap-2 min-w-0">
        <FeatherIcon :name="footerIcon" class="w-4 h-4 text-white/60 shrink-0" />
        <p class="text-xs text-white/80 truncate">
          <template v-if="state === 'pending'">
            <span class="font-semibold tabular-nums">{{ count }}</span>
            {{ count === 1 ? 'claim' : 'claims' }} in queue
          </template>
          <template v-else>{{ footerText }}</template>
        </p>
      </div>
      <div class="flex items-center gap-2 min-w-0 ml-auto">
        <FeatherIcon name="clock" class="w-4 h-4 text-white/60 shrink-0" />
        <p class="text-xs text-white/80 truncate">{{ formattedDate }}</p>
      </div>
    </div>
  </router-link>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'PendingSummaryCard',
  components: { FeatherIcon },
  props: {
    amount: { type: Number, required: true },
    count: { type: Number, required: true },
    updatedAt: { type: [String, Date], default: () => new Date() },
  },
  computed: {
    // amount is the ledger position: positive means the company owes the
    // employee, negative means the employee owes the company back.
    state() {
      if (this.amount > 0) return 'pending'
      if (this.amount < 0) return 'due'
      return 'settled'
    },
    badge() {
      return { pending: 'Awaiting payout', due: 'Balance due', settled: 'All settled' }[this.state]
    },
    label() {
      return {
        pending: 'Pending reimbursement',
        due: 'You owe the company',
        settled: 'Pending reimbursement',
      }[this.state]
    },
    footerIcon() {
      return { pending: 'file-text', due: 'alert-circle', settled: 'check-circle' }[this.state]
    },
    footerText() {
      return this.state === 'due' ? 'Settle with finance' : 'Nothing awaiting payout'
    },
    formattedAmount() {
      return Math.abs(Number(this.amount || 0)).toLocaleString('en-AE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    },
    formattedDate() {
      const d = this.updatedAt instanceof Date ? this.updatedAt : new Date(this.updatedAt)
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    },
  },
}
</script>

<style scoped>
.summary-card.is-pending {
  background: linear-gradient(135deg, #2fb89c 0%, #29a38b 45%, #10604f 100%);
  box-shadow: 0 12px 32px -10px rgba(16, 96, 79, 0.55);
}

.summary-card.is-settled {
  background: linear-gradient(135deg, #3c4a56 0%, #2b363f 55%, #1b232a 100%);
  box-shadow: 0 12px 32px -10px rgba(27, 35, 42, 0.5);
}

/* Employee owes the company back — warm, needs attention, not an error */
.summary-card.is-due {
  background: linear-gradient(135deg, #e0913a 0%, #c9702a 50%, #8f4715 100%);
  box-shadow: 0 12px 32px -10px rgba(143, 71, 21, 0.5);
}

/* Diagonal gloss sweeping across the face */
.sheen {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    102deg,
    transparent 38%,
    rgba(255, 255, 255, 0.09) 48%,
    rgba(255, 255, 255, 0.02) 56%,
    transparent 64%
  );
}
</style>
