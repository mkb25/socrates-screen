/**
 * store.js – Pinia State Store for Socrates Screen
 *
 * Responsibilities:
 *  1. Persist the user's BaselineProfile in localStorage (survives page reloads).
 *  2. Track ephemeral 3-tap session state (reset after each recommendation).
 *  3. Manage UI phase transitions: onboarding → tapping → loading → reveal.
 *  4. Call the FastAPI backend and store the resulting MovieCard.
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

// ── API base URL (Vite proxy in dev; absolute URL in prod) ─────────────────
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// ── Constants ──────────────────────────────────────────────────────────────

export const ENERGY_OPTIONS = [
  {
    id: "think",
    label: "Logos (Cerebral)",
    sublabel: "Stimulate the intellect. Layered, morally complex, and thought-provoking cinema that lingers for days.",
  },
  {
    id: "brain_off",
    label: "Catharsis (Spectacle)",
    sublabel: "Pure emotional release. High-octane action, sharp comedy, or spectacular chaos. Let the mind rest.",
  },
  {
    id: "feel",
    label: "Pathos (Emotional)",
    sublabel: "Deeply moving human stories. Explore raw empathy, grief, joy, and the depth of human experience.",
  },
];

export const REALITY_OPTIONS = [
  {
    id: "grounded",
    label: "Mimesis (Realism)",
    sublabel: "Mirror of reality. True events, naturalistic acting, and authentic slice-of-life drama.",
  },
  {
    id: "escapism",
    label: "Phantasia (Fantasy)",
    sublabel: "Journeys to imaginary realms. Mythological epics, science fiction, and surreal dreamscapes.",
  },
];

export const COMMITMENT_OPTIONS = [
  {
    id: "quick",
    label: "Kairos (Under 2 Hours)",
    sublabel: "The opportune moment. Tight, punchy, under 110 minutes with zero wasted scenes.",
  },
  {
    id: "epic",
    label: "Aion (Sprawling Epic)",
    sublabel: "Eternal narratives. Sprawling sagas, slow burns, and grand journeys that take all night.",
  },
];

// ── Phases ─────────────────────────────────────────────────────────────────

export const PHASE = {
  ONBOARDING: "onboarding",
  TAP_1: "tap_1",      // Energy
  TAP_2: "tap_2",      // Reality
  TAP_3: "tap_3",      // Commitment
  LOADING: "loading",
  REVEAL: "reveal",
};

// ── Local storage key ──────────────────────────────────────────────────────

const LS_KEY = "socrates_baseline_v1";

function createBaselineProfile() {
  return {
    favorite_movies: [],
    favorite_genres: [],
    dealbreakers: [],
    preferred_language: "any",
  };
}

function createSessionState() {
  return {
    energy: null,
    reality: null,
    commitment: null,
  };
}

function loadBaseline() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveBaseline(profile) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(profile));
  } catch {
    /* storage quota exceeded – silently ignore */
  }
}

function hasTasteProfile(profile) {
  return profile.favorite_movies.length > 0 || profile.favorite_genres.length > 0;
}

function parseRecommendationError(err) {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }
  return (
    detail ||
    (err?.response?.status
      ? `Request failed with status ${err.response.status}`
      : "") ||
    err?.message ||
    "Something went wrong. Please try again."
  );
}

// ── Store definition ───────────────────────────────────────────────────────

export const useSocratesStore = defineStore("socrates", () => {
  // ── Baseline profile (persisted) ──────────────────────────────────────
  const _saved = loadBaseline();

  const baselineProfile = ref(_saved || createBaselineProfile());

  const hasBaseline = computed(() => hasTasteProfile(baselineProfile.value));

  function saveProfile() {
    saveBaseline(baselineProfile.value);
  }

  function resetBaseline() {
    baselineProfile.value = createBaselineProfile();
    localStorage.removeItem(LS_KEY);
  }

  // ── Session state (ephemeral, reset each run) ─────────────────────────
  const sessionState = ref(createSessionState());

  function resetSession() {
    sessionState.value = createSessionState();
  }

  // ── UI Phase ──────────────────────────────────────────────────────────
  const phase = ref(_saved ? PHASE.TAP_1 : PHASE.ONBOARDING);

  function goToPhase(p) {
    phase.value = p;
  }

  // ── Recommendation result ─────────────────────────────────────────────
  const recommendation = ref(null); // array of 3 MovieCards
  const error = ref(null);           // Error string shown to user

  /**
   * Titles the user has already been shown in the current tap session.
   * Sent to the LLM so it never repeats the same film.
   */
  const seenTitles = ref([]);

  // ── Actions ───────────────────────────────────────────────────────────

  function buildRecommendationPayload() {
    return {
      baseline_profile: baselineProfile.value,
      session_state: { ...sessionState.value },
      seen_titles: [...seenTitles.value],
    };
  }

  function rememberCurrentRecommendations() {
    for (const film of recommendation.value || []) {
      if (!seenTitles.value.includes(film.title)) {
        seenTitles.value.push(film.title);
      }
    }
  }

  function clearRecommendationState() {
    recommendation.value = null;
    error.value = null;
  }

  /** Called when user completes the onboarding form. */
  function finishOnboarding() {
    saveProfile();
    phase.value = PHASE.TAP_1;
  }

  /** Called when user taps an Energy option (Tap 1). */
  function selectEnergy(energyId) {
    sessionState.value.energy = energyId;
    phase.value = PHASE.TAP_2;
  }

  /** Called when user taps a Reality option (Tap 2). */
  function selectReality(realityId) {
    sessionState.value.reality = realityId;
    phase.value = PHASE.TAP_3;
  }

  /**
   * Called when user taps a Commitment option (Tap 3).
   * Immediately fires the API call.
   */
  async function selectCommitment(commitmentId) {
    sessionState.value.commitment = commitmentId;
    await fetchRecommendation();
  }

  /** Core API call. Transitions to LOADING then REVEAL (or error). */
  async function fetchRecommendation() {
    phase.value = PHASE.LOADING;
    clearRecommendationState();

    try {
      const { data } = await axios.post(
        `${API_BASE}/api/recommend`,
        buildRecommendationPayload(),
        {
          timeout: 30000, // 30 s – LLM + TMDB can be slow on slow networks
          headers: { "Content-Type": "application/json" },
        }
      );

      recommendation.value = data.films; // array of 3 MovieCards
      phase.value = PHASE.REVEAL;
    } catch (err) {
      error.value = parseRecommendationError(err);
      // Regress to Tap 1 so user can retry with different taps
      phase.value = PHASE.TAP_1;
      resetSession();
    }
  }

  /**
   * Re-run with the same 3 taps but request 3 DIFFERENT films.
   * Adds the currently shown titles to seenTitles so the LLM excludes them.
   */
  async function findMore() {
    rememberCurrentRecommendations();
    await fetchRecommendation();
  }

  /** Start over — pick new taps (clears seen history). */
  function startNewSession() {
    resetSession();
    clearRecommendationState();
    seenTitles.value = [];
    phase.value = PHASE.TAP_1;
  }

  /** Full reset including baseline (re-triggers onboarding). */
  function fullReset() {
    resetBaseline();
    resetSession();
    clearRecommendationState();
    seenTitles.value = [];
    phase.value = PHASE.ONBOARDING;
  }

  return {
    // State
    baselineProfile,
    sessionState,
    phase,
    recommendation,
    error,
    hasBaseline,
    // Baseline actions
    saveProfile,
    resetBaseline,
    finishOnboarding,
    // Session actions
    selectEnergy,
    selectReality,
    selectCommitment,
    findMore,
    startNewSession,
    fullReset,
    // Misc
    goToPhase,
    // Constants (re-exported for convenience in components)
    PHASE,
  };
});
