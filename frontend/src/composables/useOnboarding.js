/**
 * useOnboarding.js – Composable for the onboarding wizard
 *
 * Encapsulates step navigation, movie input management,
 * genre toggling, and dealbreaker toggling.
 */

import { ref, computed } from "vue";
import { ONBOARDING_QUESTIONS } from "../constants/options.js";

export function useOnboarding(store) {
  const movieInput = ref("");
  const onboardingStep = ref(0);

  const currentOnboardingQuestion = computed(
    () => ONBOARDING_QUESTIONS[onboardingStep.value]
  );

  function addMovie() {
    const val = movieInput.value.trim();
    if (!val || store.baselineProfile.favorite_movies.length >= 5) return;
    if (!store.baselineProfile.favorite_movies.includes(val)) {
      store.baselineProfile.favorite_movies.push(val);
    }
    movieInput.value = "";
  }

  function removeMovie(idx) {
    store.baselineProfile.favorite_movies.splice(idx, 1);
  }

  function nextOnboardingQuestion(skipInput) {
    if (!skipInput && onboardingStep.value === 0 && movieInput.value.trim()) {
      addMovie();
    }

    if (onboardingStep.value < ONBOARDING_QUESTIONS.length - 1) {
      onboardingStep.value += 1;
      return;
    }

    store.finishOnboarding();
  }

  function previousOnboardingQuestion() {
    onboardingStep.value = Math.max(0, onboardingStep.value - 1);
  }

  function toggleGenre(g) {
    const genres = store.baselineProfile.favorite_genres;
    const i = genres.indexOf(g);
    if (i === -1) genres.push(g);
    else genres.splice(i, 1);
  }

  function toggleDealbreaker(id) {
    const db = store.baselineProfile.dealbreakers;
    const i = db.indexOf(id);
    if (i === -1) db.push(id);
    else db.splice(i, 1);
  }

  return {
    movieInput,
    onboardingStep,
    currentOnboardingQuestion,
    addMovie,
    removeMovie,
    nextOnboardingQuestion,
    previousOnboardingQuestion,
    toggleGenre,
    toggleDealbreaker,
  };
}
