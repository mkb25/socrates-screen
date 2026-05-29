<template>
  <div id="app" class="app-shell">
    <AcademyBackdrop />

    <Transition name="phase" mode="out-in">
      <OnboardingPhase
        v-if="store.phase === PHASE.ONBOARDING"
        key="onboarding"
      />

      <TapPhase
        v-else-if="isTapPhase"
        :key="store.phase"
      />

      <LoadingPhase
        v-else-if="store.phase === PHASE.LOADING"
        key="loading"
      />

      <RevealPhase
        v-else-if="store.phase === PHASE.REVEAL && store.recommendation?.length"
        key="reveal"
      />
    </Transition>

    <ErrorToast />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useSocratesStore, PHASE } from "./stores/store.js";

import AcademyBackdrop from "./components/AcademyBackdrop.vue";
import OnboardingPhase from "./components/OnboardingPhase.vue";
import TapPhase from "./components/TapPhase.vue";
import LoadingPhase from "./components/LoadingPhase.vue";
import RevealPhase from "./components/RevealPhase.vue";
import ErrorToast from "./components/ErrorToast.vue";

const store = useSocratesStore();

const isTapPhase = computed(() =>
  [PHASE.TAP_1, PHASE.TAP_2, PHASE.TAP_3].includes(store.phase)
);
</script>
