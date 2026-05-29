<template>
  <Transition name="toast">
    <div v-if="store.error" class="toast" role="alert">
      <span class="toast__icon">⚠</span>
      <span class="toast__msg">{{ store.error }}</span>
      <button class="toast__close" @click="store.error = null" aria-label="Dismiss">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { useSocratesStore } from "../stores/store.js";

const store = useSocratesStore();
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 1.5rem; left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(10, 10, 12, 0.92);
  border: 1px solid var(--terracotta-border);
  border-radius: var(--r-btn);
  backdrop-filter: blur(16px);
  padding: 0.75rem 1rem 0.75rem 1.1rem;
  font-size: 0.85rem;
  color: var(--text-1);
  max-width: calc(100vw - 2rem);
  z-index: 100;
  box-shadow: 0 8px 32px rgba(192, 108, 84, 0.16);
}
.toast__icon { color: var(--rose); font-size: 1rem; flex-shrink: 0; }
.toast__msg { flex: 1; }
.toast__close {
  background: none; border: none;
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  transition: color 0.15s;
}
.toast__close:hover { color: var(--rose); }

.toast-enter-active, .toast-leave-active { transition: opacity 0.25s, transform 0.25s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
</style>
