<template>
  <div class="academy-backdrop" aria-hidden="true">
    <span class="academy-backdrop__pediment"></span>
    <span class="academy-backdrop__column academy-backdrop__column--left"></span>
    <span class="academy-backdrop__column academy-backdrop__column--right"></span>
  </div>
</template>

<script setup>
// Pure presentational – no props, no state
</script>

<style scoped>
.academy-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.7;
}
.academy-backdrop::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(232, 224, 207, 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(232, 224, 207, 0.025) 1px, transparent 1px);
  background-size: 88px 88px;
  mask-image: linear-gradient(to bottom, rgba(0,0,0,0.75), transparent 72%);
}
.academy-backdrop::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 48%;
  background:
    linear-gradient(180deg, transparent, rgba(9, 10, 12, 0.9)),
    repeating-linear-gradient(90deg, transparent 0 36px, rgba(212, 175, 55, 0.035) 37px 38px);
}
.academy-backdrop__pediment {
  position: absolute;
  top: 4rem;
  left: 50%;
  width: min(860px, 92vw);
  height: 220px;
  transform: translateX(-50%);
  border-top: 1px solid rgba(212, 175, 55, 0.16);
  border-bottom: 1px solid rgba(232, 224, 207, 0.06);
  clip-path: polygon(50% 0, 100% 40%, 100% 48%, 0 48%, 0 40%);
}
.academy-backdrop__column {
  position: absolute;
  top: 19rem;
  width: 1px;
  height: 52dvh;
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.2), transparent);
  box-shadow:
    16px 0 0 rgba(232, 224, 207, 0.035),
    32px 0 0 rgba(232, 224, 207, 0.025),
    -16px 0 0 rgba(232, 224, 207, 0.035),
    -32px 0 0 rgba(232, 224, 207, 0.025);
}
.academy-backdrop__column--left { left: max(2rem, calc(50% - 380px)); }
.academy-backdrop__column--right { right: max(2rem, calc(50% - 380px)); }
</style>
