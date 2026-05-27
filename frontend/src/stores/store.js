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
    label: "Stimulate Me",
    sublabel: "Cerebral, layered, morally complex. A film that lingers for days and demands a second watch.",
  },
  {
    id: "brain_off",
    label: "Entertain Me",
    sublabel: "Pure spectacle. High-octane action, sharp comedy, or masala chaos. Zero analytical effort required.",
  },
  {
    id: "feel",
    label: "Move Me",
    sublabel: "I need to feel something real tonight — grief, joy, longing. Emotionally charged, deeply human stories.",
  },
];

export const REALITY_OPTIONS = [
  {
    id: "grounded",
    label: "Keep It Real",
    sublabel: "Rooted in truth. True events, naturalistic performances, and the kind of realism that makes your chest tighten.",
  },
  {
    id: "escapism",
    label: "Take Me Away",
    sublabel: "A completely different world. Fantasy, mythology, sci-fi, surreal dreamscapes — anywhere but here.",
  },
];

export const COMMITMENT_OPTIONS = [
  {
    id: "quick",
    label: "Under Two Hours",
    sublabel: "Tight, punchy, no filler. Every scene earns its place. Under 110 minutes, sharp as a blade.",
  },
  {
    id: "epic",
    label: "I Have All Night",
    sublabel: "Sagas, sprawling epics, slow burns. 130+ minutes. I'm going nowhere and I don't want to.",
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

// ── Store definition ───────────────────────────────────────────────────────

export const useSocratesStore = defineStore("socrates", () => {
  // ── Baseline profile (persisted) ──────────────────────────────────────
  const _saved = loadBaseline();

  const baselineProfile = ref(
    _saved || {
      favorite_movies: [],      // Array<string> – up to 5 titles
      favorite_genres: [],      // Array<string>
      dealbreakers: [],         // Array<string> – e.g. ["gore", "subtitles"]
      preferred_language: "any",
    }
  );

  const hasBaseline = computed(() => {
    const bp = baselineProfile.value;
    return bp.favorite_movies.length > 0 || bp.favorite_genres.length > 0;
  });

  function saveProfile() {
    saveBaseline(baselineProfile.value);
  }

  function resetBaseline() {
    baselineProfile.value = {
      favorite_movies: [],
      favorite_genres: [],
      dealbreakers: [],
      preferred_language: "any",
    };
    localStorage.removeItem(LS_KEY);
  }

  // ── Session state (ephemeral, reset each run) ─────────────────────────
  const sessionState = ref({
    energy: null,     // "think" | "brain_off" | "feel"
    reality: null,    // "grounded" | "escapism"
    commitment: null, // "quick" | "epic"
  });

  function resetSession() {
    sessionState.value = { energy: null, reality: null, commitment: null };
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
    error.value = null;
    recommendation.value = null;

    try {
      const payload = {
        baseline_profile: baselineProfile.value,
        session_state: {
          energy: sessionState.value.energy,
          reality: sessionState.value.reality,
          commitment: sessionState.value.commitment,
        },
        seen_titles: [...seenTitles.value],  // exclude already-shown films
      };

      const { data } = await axios.post(`${API_BASE}/api/recommend`, payload, {
        timeout: 30000, // 30 s – LLM + TMDB can be slow on slow networks
        headers: { "Content-Type": "application/json" },
      });

      recommendation.value = data.films; // array of 3 MovieCards
      phase.value = PHASE.REVEAL;
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong. Please try again.";
      error.value = msg;
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
    if (recommendation.value?.length) {
      for (const film of recommendation.value) {
        if (!seenTitles.value.includes(film.title)) {
          seenTitles.value.push(film.title);
        }
      }
    }
    await fetchRecommendation();
  }

  /** Start over — pick new taps (clears seen history). */
  function startNewSession() {
    resetSession();
    recommendation.value = null;
    error.value = null;
    seenTitles.value = [];
    phase.value = PHASE.TAP_1;
  }

  /** Full reset including baseline (re-triggers onboarding). */
  function fullReset() {
    resetBaseline();
    resetSession();
    recommendation.value = null;
    error.value = null;
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
