<template>
  <section :key="store.phase" class="phase tap-phase">
    <!-- Progress bar -->
    <div class="tap-progress">
      <div class="tap-progress__bar" :style="{ width: (currentStep / 3 * 100) + '%' }"></div>
    </div>

    <!-- Header -->
    <div class="tap-header">
      <div class="tap-header__step">Step {{ currentStep }} / 3</div>
      <h2 class="tap-header__title">{{ currentStepTitle }}</h2>
    </div>

    <!-- Cards for Tap 1 (Energy – 3 choices, stacked) -->
    <div v-if="store.phase === PHASE.TAP_1" class="tap-stack">
      <button
        v-for="opt in ENERGY_OPTIONS" :key="opt.id"
        class="tap-tile"
        @click="store.selectEnergy(opt.id)"
        :aria-label="opt.label"
      >
        <span class="tap-tile__icon" v-html="ICONS[opt.id]"></span>
        <div class="tap-tile__body">
          <span class="tap-tile__label">{{ opt.label }}</span>
          <span class="tap-tile__sub">{{ opt.sublabel }}</span>
        </div>
        <svg class="tap-tile__arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M5 10h10M11 6l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- Cards for Tap 2 (Reality – 2 options, side by side) -->
    <div v-else-if="store.phase === PHASE.TAP_2" class="tap-duo">
      <button
        v-for="opt in REALITY_OPTIONS" :key="opt.id"
        class="tap-block"
        @click="store.selectReality(opt.id)"
        :aria-label="opt.label"
      >
        <span class="tap-block__icon" v-html="ICONS[opt.id]"></span>
        <span class="tap-block__label">{{ opt.label }}</span>
        <span class="tap-block__sub">{{ opt.sublabel }}</span>
      </button>
    </div>

    <!-- Cards for Tap 3 (Commitment – 2 options, side by side) -->
    <div v-else-if="store.phase === PHASE.TAP_3" class="tap-duo">
      <button
        v-for="opt in COMMITMENT_OPTIONS" :key="opt.id"
        class="tap-block"
        @click="store.selectCommitment(opt.id)"
        :aria-label="opt.label"
      >
        <span class="tap-block__icon" v-html="ICONS[opt.id]"></span>
        <span class="tap-block__label">{{ opt.label }}</span>
        <span class="tap-block__sub">{{ opt.sublabel }}</span>
      </button>
    </div>

    <div class="tap-footer">
      <button v-if="currentStep > 1" class="back-btn" @click="goBack">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Back
      </button>
      <span v-else></span>
      <button class="ghost-btn" @click="store.fullReset()">Edit taste</button>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useSocratesStore, PHASE, ENERGY_OPTIONS, REALITY_OPTIONS, COMMITMENT_OPTIONS } from "../stores/store.js";
import { ICONS } from "../constants/icons.js";

const store = useSocratesStore();

const currentStep = computed(() => {
  if (store.phase === PHASE.TAP_1) return 1;
  if (store.phase === PHASE.TAP_2) return 2;
  if (store.phase === PHASE.TAP_3) return 3;
  return 0;
});

const currentStepTitle = computed(() => {
  if (store.phase === PHASE.TAP_1) return "Where's your head at tonight?";
  if (store.phase === PHASE.TAP_2) return "What world do you want to step into?";
  if (store.phase === PHASE.TAP_3) return "How far are you willing to travel?";
  return "";
});

function goBack() {
  if (store.phase === PHASE.TAP_2) store.goToPhase(PHASE.TAP_1);
  else if (store.phase === PHASE.TAP_3) store.goToPhase(PHASE.TAP_2);
}
</script>

<style scoped>
/* Progress bar */
.tap-progress {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: rgba(212, 175, 55, 0.08);
  z-index: 10;
}
.tap-progress__bar {
  height: 100%;
  background: linear-gradient(90deg, var(--laurel), var(--gold));
  transition: width 0.4s cubic-bezier(0.4,0,0.2,1);
  box-shadow: 0 0 12px var(--gold-glow);
}

/* Header */
.tap-header {
  padding: 4rem 0 1.5rem;
  text-align: center;
}
.tap-header__step {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.75rem;
  font-family: var(--serif);
}
.tap-header__title {
  font-family: var(--serif);
  font-size: 1.9rem;
  line-height: 1.2;
  color: var(--text-1);
  letter-spacing: 0.02em;
}

/* ── Stacked tiles (Tap 1 – 3 choices) ───────────────────────── */
.tap-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.tap-tile {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  padding: 1.25rem 1.25rem 1.25rem 1.5rem;
  background:
    linear-gradient(180deg, rgba(232, 224, 207, 0.055), rgba(232, 224, 207, 0.018)),
    rgba(8, 9, 11, 0.82);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  cursor: pointer;
  text-align: left;
  font-family: var(--sans);
  transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(16px);
}
.tap-tile::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--gold-dim) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.25s;
}
.tap-tile:hover { border-color: var(--gold-glow); transform: translateX(4px); box-shadow: 0 8px 32px rgba(212, 175, 55, 0.1); }
.tap-tile:hover::before { opacity: 1; }
.tap-tile:active { transform: scale(0.98); }

.tap-tile__icon {
  flex-shrink: 0;
  width: 48px; height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gold-dim);
  border-radius: 14px;
  color: var(--gold);
  transition: transform 0.2s, background 0.2s, box-shadow 0.2s;
}
.tap-tile:hover .tap-tile__icon {
  transform: scale(1.1);
  background: rgba(212, 175, 55, 0.25);
  box-shadow: 0 0 16px rgba(212, 175, 55, 0.2);
}

.tap-tile__body { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }
.tap-tile__label { font-size: 1.05rem; font-weight: 600; color: var(--text-1); font-family: var(--serif); letter-spacing: 0.01em; }
.tap-tile__sub { font-size: 0.78rem; color: var(--text-2); font-family: var(--body-serif); line-height: 1.45; }

.tap-tile__arrow { color: var(--text-3); flex-shrink: 0; transition: transform 0.2s, color 0.2s; }
.tap-tile:hover .tap-tile__arrow { transform: translateX(4px); color: var(--gold); }

/* ── Duo blocks (Tap 2 & 3 – 2 choices) ─────────────────────── */
.tap-duo {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  flex: 1;
}

.tap-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem 1rem;
  background:
    linear-gradient(180deg, rgba(232, 224, 207, 0.055), rgba(232, 224, 207, 0.018)),
    rgba(8, 9, 11, 0.82);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  cursor: pointer;
  font-family: var(--sans);
  transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
  min-height: 180px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(16px);
}
.tap-block::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, var(--gold-dim) 100%);
  opacity: 0;
  transition: opacity 0.25s;
}
.tap-block:hover { border-color: var(--gold-glow); transform: translateY(-4px); box-shadow: 0 16px 40px rgba(212, 175, 55, 0.08); }
.tap-block:hover::after { opacity: 1; }
.tap-block:active { transform: scale(0.97); }

.tap-block__icon {
  width: 56px; height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gold-dim);
  border-radius: 16px;
  color: var(--gold);
  transition: transform 0.2s, background 0.2s, box-shadow 0.2s;
}
.tap-block:hover .tap-block__icon {
  transform: scale(1.12) rotate(-3deg);
  background: rgba(212, 175, 55, 0.25);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
}

.tap-block__label { font-size: 1rem; font-weight: 700; color: var(--text-1); font-family: var(--serif); letter-spacing: 0.02em; }
.tap-block__sub { font-size: 0.75rem; color: var(--text-2); text-align: center; line-height: 1.4; font-family: var(--body-serif); }

/* Footer row */
.tap-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.25rem;
  margin-top: auto;
}
</style>
