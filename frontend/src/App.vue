<template>
  <div id="app" class="app-shell">

    <!-- Ambient background orbs -->
    <div class="bg-orb bg-orb--1" aria-hidden="true"></div>
    <div class="bg-orb bg-orb--2" aria-hidden="true"></div>

    <Transition name="phase" mode="out-in">

      <!-- ═══════════════════════════════════════════════
           ONBOARDING
      ════════════════════════════════════════════════ -->
      <section v-if="store.phase === PHASE.ONBOARDING" key="onboarding" class="phase onboarding-phase">
        <header class="ob-header">
          <div class="wordmark">
            <span class="wordmark__icon">◉</span>
            <span class="wordmark__text">Socrates Screen</span>
          </div>
          <p class="ob-tagline">3 taps · The perfect film · Every time.</p>
        </header>

        <div class="ob-card">
          <div class="ob-card__eyebrow">Your Taste Profile</div>
          <h1 class="ob-card__title">Let's calibrate<br>your cinema radar.</h1>
          <p class="ob-card__sub">Saved only in your browser. Never on a server.</p>

          <!-- Favourite Movies -->
          <div class="field">
            <label class="field__label">Films you love</label>
            <div class="field__input-row">
              <input
                id="movie-input"
                v-model="movieInput"
                class="field__input"
                placeholder="Dune, Vikram, Tumbbad…"
                @keydown.enter.prevent="addMovie"
                autocomplete="off"
              />
              <button class="field__add-btn" @click="addMovie" aria-label="Add movie">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
            <div class="tag-list">
              <span v-for="(m, i) in store.baselineProfile.favorite_movies" :key="i" class="tag">
                {{ m }}
                <button class="tag__remove" @click="removeMovie(i)" :aria-label="`Remove ${m}`">
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M1 1l8 8M9 1L1 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </button>
              </span>
            </div>
          </div>

          <!-- Preferred Genres -->
          <div class="field">
            <label class="field__label">Genres you're drawn to</label>
            <div class="pill-grid">
              <button
                v-for="g in GENRE_OPTIONS" :key="g"
                class="pill"
                :class="{ 'pill--active': store.baselineProfile.favorite_genres.includes(g) }"
                @click="toggleGenre(g)"
              >{{ g }}</button>
            </div>
          </div>

          <!-- Dealbreakers -->
          <div class="field">
            <label class="field__label">Hard passes</label>
            <div class="dealbreaker-grid">
              <button
                v-for="d in DEALBREAKER_OPTIONS" :key="d.id"
                class="dealbreaker"
                :class="{ 'dealbreaker--active': store.baselineProfile.dealbreakers.includes(d.id) }"
                @click="toggleDealbreaker(d.id)"
              >
                <span class="dealbreaker__icon">{{ d.emoji }}</span>
                <span class="dealbreaker__label">{{ d.label }}</span>
              </button>
            </div>
          </div>

          <!-- Language -->
          <div class="field">
            <label class="field__label">Language preference</label>
            <div class="lang-strip">
              <button
                v-for="lang in LANG_OPTIONS" :key="lang.id"
                class="lang-chip"
                :class="{ 'lang-chip--active': store.baselineProfile.preferred_language === lang.id }"
                @click="store.baselineProfile.preferred_language = lang.id"
              >{{ lang.flag }} {{ lang.label }}</button>
            </div>
          </div>

          <button class="cta-btn" @click="store.finishOnboarding()">
            <span>Let's find your film</span>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M3 9h12M10 4l5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </section>

      <!-- ═══════════════════════════════════════════════
           TAP PHASES (1, 2, 3)
      ════════════════════════════════════════════════ -->
      <section
        v-else-if="[PHASE.TAP_1, PHASE.TAP_2, PHASE.TAP_3].includes(store.phase)"
        :key="store.phase"
        class="phase tap-phase"
      >
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

      <!-- ═══════════════════════════════════════════════
           LOADING
      ════════════════════════════════════════════════ -->
      <section v-else-if="store.phase === PHASE.LOADING" key="loading" class="phase loading-phase">
        <div class="film-loader" aria-label="Loading">
          <div class="film-loader__reel">
            <div v-for="n in 8" :key="n" class="film-loader__hole"></div>
          </div>
          <div class="film-loader__strip">
            <div v-for="n in 4" :key="n" class="film-loader__frame"></div>
          </div>
          <div class="film-loader__reel">
            <div v-for="n in 8" :key="n" class="film-loader__hole"></div>
          </div>
        </div>
        <h2 class="loading-title">Socrates is thinking<span class="loading-ellipsis"><span>.</span><span>.</span><span>.</span></span></h2>
        <p class="loading-sub">Searching all of world cinema for your perfect film</p>
      </section>

      <!-- ═══════════════════════════════════════════════
           REVEAL
      ════════════════════════════════════════════════ -->
      <section
        v-else-if="store.phase === PHASE.REVEAL && store.recommendation?.length"
        key="reveal"
        class="phase reveal-phase"
      >
        <!-- ── Primary Pick ─────────────────────────────────── -->
        <div class="reveal-poster">
          <img
            v-if="store.recommendation[0].poster_url && !posterErrors[0]"
            :src="store.recommendation[0].poster_url"
            :alt="`${store.recommendation[0].title} poster`"
            class="reveal-poster__img"
            @error="posterErrors[0] = true"
          />
          <div v-else class="reveal-poster__fallback">🎞️</div>
          <div class="reveal-poster__gradient"></div>
          <span class="reveal-poster__eyebrow">Best match</span>
        </div>

        <div class="reveal-details">
          <h2 class="reveal-title">
            <a
              v-if="store.recommendation[0].tmdb_id"
              :href="`https://www.themoviedb.org/movie/${store.recommendation[0].tmdb_id}`"
              target="_blank"
              rel="noopener noreferrer"
              class="reveal-title__link"
            >
              {{ store.recommendation[0].title }}
            </a>
            <span v-else>{{ store.recommendation[0].title }}</span>
          </h2>
          <div class="reveal-meta">
            <span class="reveal-meta__year">{{ store.recommendation[0].year }}</span>
            <span v-if="store.recommendation[0].vote_average" class="reveal-meta__rating">
              ★ {{ store.recommendation[0].vote_average.toFixed(1) }}
            </span>
            <span v-if="store.recommendation[0].original_language" class="reveal-meta__lang">
              {{ langLabel(store.recommendation[0].original_language) }}
            </span>
          </div>
          <blockquote class="reveal-reason">{{ store.recommendation[0].reason }}</blockquote>

          <!-- 3-tap recap -->
          <div class="reveal-taps">
            <span class="reveal-tap">{{ tapLabel('energy', store.sessionState.energy) }}</span>
            <span class="reveal-tap-sep">·</span>
            <span class="reveal-tap">{{ tapLabel('reality', store.sessionState.reality) }}</span>
            <span class="reveal-tap-sep">·</span>
            <span class="reveal-tap">{{ tapLabel('commitment', store.sessionState.commitment) }}</span>
          </div>
        </div>

        <!-- ── Also consider ─────────────────────────────────── -->
        <div class="also-section">
          <div class="also-section__header">
            <span class="also-section__label">Also consider</span>
            <span class="also-section__rule"></span>
          </div>
          <div class="also-list">
            <div
              v-for="(film, idx) in store.recommendation.slice(1)"
              :key="idx"
              class="also-card"
            >
              <div class="also-card__thumb">
                <img
                  v-if="film.poster_url && !posterErrors[idx + 1]"
                  :src="film.poster_url"
                  :alt="film.title"
                  class="also-card__img"
                  @error="posterErrors[idx + 1] = true"
                />
                <div v-else class="also-card__no-img">🎞</div>
                <span class="also-card__badge">{{ idx + 2 }}</span>
              </div>
              <div class="also-card__info">
                <span class="also-card__title">
                  <a
                    v-if="film.tmdb_id"
                    :href="`https://www.themoviedb.org/movie/${film.tmdb_id}`"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="also-card__title-link"
                  >
                    {{ film.title }}
                  </a>
                  <span v-else>{{ film.title }}</span>
                </span>
                <div class="also-card__meta">
                  <span>{{ film.year }}</span>
                  <span v-if="film.vote_average">★ {{ film.vote_average.toFixed(1) }}</span>
                  <span v-if="film.original_language" class="also-card__lang">{{ langLabel(film.original_language) }}</span>
                </div>
                <p class="also-card__reason">{{ film.reason }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="reveal-actions">
          <button class="cta-btn" @click="store.findMore()">
            <span>Find 3 more</span>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M14 9A5 5 0 1 1 9 4M14 4v5h-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <div class="reveal-actions__row">
            <button class="ghost-btn ghost-btn--half" @click="store.startNewSession()">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 7h12M7 1l6 6-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Change mood
            </button>
            <button class="ghost-btn ghost-btn--half" @click="store.fullReset()">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              Edit taste
            </button>
          </div>
        </div>
      </section>

    </Transition>

    <!-- Error Toast -->
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
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useSocratesStore, PHASE, ENERGY_OPTIONS, REALITY_OPTIONS, COMMITMENT_OPTIONS } from "./stores/store.js";

const store = useSocratesStore();

const movieInput = ref("");
const posterErrors = ref([false, false, false]);

watch(() => store.recommendation, () => {
  posterErrors.value = [false, false, false];
});

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

// SVG icon map – Lucide-style, 24px stroke icons
const ICONS = {
  // think – three interconnected nodes (neural network)
  think: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="4.5" r="2" stroke="currentColor" stroke-width="1.6"/>
    <circle cx="4.5" cy="18.5" r="2" stroke="currentColor" stroke-width="1.6"/>
    <circle cx="19.5" cy="18.5" r="2" stroke="currentColor" stroke-width="1.6"/>
    <path d="M12 6.5L5.6 16.8M12 6.5L18.4 16.8M6.4 18.5H17.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  </svg>`,
  // brain_off – clapperboard (film/entertainment)
  brain_off: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="8" width="20" height="13" rx="2" stroke="currentColor" stroke-width="1.6"/>
    <path d="M2 12h20" stroke="currentColor" stroke-width="1.6"/>
    <path d="M7 8V5M12 8V5M17 8V5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M5 5h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M10 15.5l5 2.5-5 2.5v-5z" fill="currentColor" opacity="0.6"/>
  </svg>`,
  // feel – EKG heartbeat pulse
  feel: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <polyline points="2,12 5,12 7,6 9,18 11,10 13,14 15,12 22,12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`,
  // grounded – compass with needle
  grounded: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"/>
    <path d="M12 3v1.5M12 19.5V21M3 12h1.5M19.5 12H21" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity="0.45"/>
    <path d="M12 12L9.5 7l5 2.5-2.5 4.5z" fill="currentColor"/>
    <path d="M12 12l2.5 5-5-2.5 2.5-2.5z" fill="currentColor" opacity="0.35"/>
  </svg>`,
  // escapism – rocket
  escapism: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2c-5 6-5 10-5 12a5 5 0 0 0 10 0c0-2 0-6-5-12z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M9 20.5S6 20 6 16M15 20.5S18 20 18 16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <circle cx="12" cy="10" r="1.8" fill="currentColor" opacity="0.5"/>
  </svg>`,
  // quick – stopwatch
  quick: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="13" r="8" stroke="currentColor" stroke-width="1.6"/>
    <path d="M12 9v4l3 2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M9.5 2h5M12 2v2.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  </svg>`,
  // epic – mountain range
  epic: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 20h20" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M3 20L9 7l4 7 3-5 5 11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`,
};

function goBack() {
  if (store.phase === PHASE.TAP_2) store.goToPhase(PHASE.TAP_1);
  else if (store.phase === PHASE.TAP_3) store.goToPhase(PHASE.TAP_2);
}

function addMovie() {
  const val = movieInput.value.trim();
  if (!val || store.baselineProfile.favorite_movies.length >= 5) return;
  if (!store.baselineProfile.favorite_movies.includes(val))
    store.baselineProfile.favorite_movies.push(val);
  movieInput.value = "";
}
function removeMovie(idx) { store.baselineProfile.favorite_movies.splice(idx, 1); }
function toggleGenre(g) {
  const genres = store.baselineProfile.favorite_genres;
  const i = genres.indexOf(g);
  if (i === -1) genres.push(g); else genres.splice(i, 1);
}
function toggleDealbreaker(id) {
  const db = store.baselineProfile.dealbreakers;
  const i = db.indexOf(id);
  if (i === -1) db.push(id); else db.splice(i, 1);
}

function tapLabel(axis, id) {
  const map = {
    energy: { think: "Cerebral", brain_off: "Entertainment", feel: "Emotional" },
    reality: { grounded: "Grounded", escapism: "Escapism" },
    commitment: { quick: "Quick watch", epic: "Full journey" },
  };
  return map[axis]?.[id] || id;
}

function langLabel(code) {
  const MAP = { hi: "Hindi", te: "Telugu", ta: "Tamil", ml: "Malayalam", kn: "Kannada", en: "English", fr: "French", ko: "Korean", ja: "Japanese", es: "Spanish", de: "German", it: "Italian" };
  return MAP[code] || code?.toUpperCase();
}

const GENRE_OPTIONS = ["Thriller","Drama","Comedy","Action","Romance","Sci-Fi","Horror","Mystery","Fantasy","Historical","Documentary","Masala","Biographical","Animation"];
const DEALBREAKER_OPTIONS = [
  { id: "gore", emoji: "🩸", label: "Gore" },
  { id: "subtitles", emoji: "📝", label: "No Subtitles" },
  { id: "sexual_content", emoji: "🔞", label: "Sexual Content" },
  { id: "slow_burn", emoji: "🐢", label: "No Slow Burns" },
  { id: "sad_endings", emoji: "😢", label: "No Sad Endings" },
  { id: "animals_harmed", emoji: "🐾", label: "No Animal Harm" },
];
const LANG_OPTIONS = [
  { id: "any", flag: "🌐", label: "Any" },
  { id: "Hindi", flag: "🇮🇳", label: "Hindi" },
  { id: "Telugu", flag: "🎬", label: "Telugu" },
  { id: "Tamil", flag: "🎭", label: "Tamil" },
  { id: "Malayalam", flag: "🌴", label: "Malayalam" },
  { id: "English", flag: "🇬🇧", label: "English" },
];
</script>

<style>
/* ─── Fonts ───────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');

/* ─── Tokens ──────────────────────────────────────────────────────────────── */
:root {
  --bg:          #06060A;
  --surface:     rgba(255,255,255,0.045);
  --surface-hov: rgba(255,255,255,0.08);
  --border:      rgba(255,255,255,0.08);
  --border-hov:  rgba(255,255,255,0.18);

  --amber:       #F59E0B;
  --amber-dim:   rgba(245,158,11,0.15);
  --violet:      #7C3AED;
  --violet-dim:  rgba(124,58,237,0.18);
  --rose:        #F43F5E;

  --text-1:  #F1F5F9;
  --text-2:  #94A3B8;
  --text-3:  #475569;

  --r-card:  18px;
  --r-btn:   12px;
  --r-pill:  999px;

  --sans:    'Inter', system-ui, sans-serif;
  --serif:   'DM Serif Display', Georgia, serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text-1);
  font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* ─── App shell ───────────────────────────────────────────────────────────── */
.app-shell {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 1rem 2rem;
  position: relative;
  overflow: hidden;
}

/* Ambient background orbs */
.bg-orb {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(80px);
  opacity: 0.35;
}
.bg-orb--1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, #7C3AED 0%, transparent 70%);
  top: -200px; left: -150px;
}
.bg-orb--2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #F59E0B 0%, transparent 70%);
  bottom: -150px; right: -100px;
}

/* ─── Phase wrapper ───────────────────────────────────────────────────────── */
.phase {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 480px;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  padding-bottom: 2rem;
}

/* ─── Phase transitions ───────────────────────────────────────────────────── */
.phase-enter-active, .phase-leave-active {
  transition: opacity 0.28s ease, transform 0.28s cubic-bezier(0.4,0,0.2,1);
}
.phase-enter-from { opacity: 0; transform: translateY(24px); }
.phase-leave-to   { opacity: 0; transform: translateY(-16px); }

/* ══════════════════════════════════════════════════════════════════
   ONBOARDING
══════════════════════════════════════════════════════════════════ */
.ob-header {
  padding: 2.5rem 0 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.wordmark {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.wordmark__icon {
  font-size: 1.4rem;
  color: var(--amber);
  animation: spin-slow 8s linear infinite;
}
@keyframes spin-slow { to { transform: rotate(360deg); } }

.wordmark__text {
  font-family: var(--serif);
  font-size: 1.5rem;
  color: var(--text-1);
  letter-spacing: -0.01em;
}

.ob-tagline {
  font-size: 0.8rem;
  color: var(--text-3);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* Onboarding card */
.ob-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  padding: 1.75rem 1.5rem;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  display: flex;
  flex-direction: column;
  gap: 1.6rem;
}

.ob-card__eyebrow {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--amber);
}

.ob-card__title {
  font-family: var(--serif);
  font-size: 2rem;
  line-height: 1.15;
  color: var(--text-1);
}

.ob-card__sub {
  font-size: 0.8rem;
  color: var(--text-3);
  margin-top: -0.8rem;
}

/* Fields */
.field { display: flex; flex-direction: column; gap: 0.6rem; }

.field__label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-2);
  letter-spacing: 0.02em;
}

.field__input-row {
  display: flex;
  gap: 0.5rem;
}

.field__input {
  flex: 1;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  border-radius: var(--r-btn);
  color: var(--text-1);
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  font-family: var(--sans);
  outline: none;
  transition: border-color 0.2s;
}
.field__input:focus { border-color: var(--violet); }
.field__input::placeholder { color: var(--text-3); }

.field__add-btn {
  width: 42px; height: 42px;
  background: var(--violet);
  border: none;
  border-radius: var(--r-btn);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.1s;
}
.field__add-btn:hover { background: #6d28d9; }
.field__add-btn:active { transform: scale(0.94); }

/* Tags */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-height: 20px;
}
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--violet-dim);
  border: 1px solid rgba(124,58,237,0.3);
  border-radius: var(--r-pill);
  padding: 0.22rem 0.65rem 0.22rem 0.75rem;
  font-size: 0.8rem;
  color: var(--text-1);
}
.tag__remove {
  background: none; border: none;
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: color 0.15s;
}
.tag__remove:hover { color: var(--rose); }

/* Genre pills */
.pill-grid { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.pill {
  padding: 0.35rem 0.85rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  font-size: 0.8rem;
  font-family: var(--sans);
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.15s;
}
.pill:hover { border-color: var(--border-hov); color: var(--text-1); }
.pill--active {
  background: var(--violet-dim);
  border-color: rgba(124,58,237,0.5);
  color: #c4b5fd;
  font-weight: 500;
}

/* Dealbreakers */
.dealbreaker-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.45rem;
}
.dealbreaker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.75rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-btn);
  cursor: pointer;
  font-family: var(--sans);
  transition: all 0.15s;
  text-align: left;
}
.dealbreaker:hover { border-color: var(--border-hov); }
.dealbreaker--active {
  background: rgba(244,63,94,0.12);
  border-color: rgba(244,63,94,0.4);
}
.dealbreaker__icon { font-size: 1rem; }
.dealbreaker__label { font-size: 0.8rem; color: var(--text-2); }
.dealbreaker--active .dealbreaker__label { color: #fda4af; }

/* Language chips */
.lang-strip { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.lang-chip {
  padding: 0.35rem 0.8rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  font-size: 0.8rem;
  font-family: var(--sans);
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.15s;
}
.lang-chip:hover { border-color: var(--border-hov); }
.lang-chip--active {
  background: var(--amber-dim);
  border-color: rgba(245,158,11,0.45);
  color: var(--amber);
  font-weight: 500;
}

/* CTA button */
.cta-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.95rem 1.5rem;
  background: linear-gradient(135deg, var(--violet) 0%, #5b21b6 100%);
  border: none;
  border-radius: var(--r-btn);
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  font-family: var(--sans);
  cursor: pointer;
  letter-spacing: 0.01em;
  box-shadow: 0 4px 24px rgba(124,58,237,0.35);
  transition: transform 0.15s, box-shadow 0.15s;
}
.cta-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(124,58,237,0.5); }
.cta-btn:active { transform: translateY(0); }

/* ══════════════════════════════════════════════════════════════════
   TAP PHASES
══════════════════════════════════════════════════════════════════ */

/* Progress bar */
.tap-progress {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: rgba(255,255,255,0.06);
  z-index: 10;
}
.tap-progress__bar {
  height: 100%;
  background: linear-gradient(90deg, var(--violet), var(--amber));
  transition: width 0.4s cubic-bezier(0.4,0,0.2,1);
}

/* Header */
.tap-header {
  padding: 4rem 0 1.5rem;
  text-align: center;
}
.tap-header__step {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--amber);
  margin-bottom: 0.75rem;
}
.tap-header__title {
  font-family: var(--serif);
  font-size: 1.9rem;
  line-height: 1.2;
  color: var(--text-1);
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
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  cursor: pointer;
  text-align: left;
  font-family: var(--sans);
  transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1);
  position: relative;
  overflow: hidden;
}
.tap-tile::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--violet-dim) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.2s;
}
.tap-tile:hover { border-color: var(--border-hov); transform: translateX(4px); box-shadow: 0 8px 32px rgba(0,0,0,0.25); }
.tap-tile:hover::before { opacity: 1; }
.tap-tile:active { transform: scale(0.98); }

.tap-tile__icon {
  flex-shrink: 0;
  width: 44px; height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--violet-dim);
  border-radius: 12px;
  color: #a78bfa;
  transition: transform 0.2s, background 0.2s;
}
.tap-tile:hover .tap-tile__icon {
  transform: scale(1.1);
  background: rgba(124,58,237,0.28);
}

.tap-tile__body { flex: 1; display: flex; flex-direction: column; gap: 0.2rem; }
.tap-tile__label { font-size: 1.05rem; font-weight: 600; color: var(--text-1); }
.tap-tile__sub { font-size: 0.78rem; color: var(--text-2); }

.tap-tile__arrow { color: var(--text-3); flex-shrink: 0; transition: transform 0.2s, color 0.2s; }
.tap-tile:hover .tap-tile__arrow { transform: translateX(4px); color: var(--text-1); }

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
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  cursor: pointer;
  font-family: var(--sans);
  transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1);
  min-height: 180px;
  position: relative;
  overflow: hidden;
}
.tap-block::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, var(--violet-dim) 100%);
  opacity: 0;
  transition: opacity 0.2s;
}
.tap-block:hover { border-color: var(--border-hov); transform: translateY(-4px); box-shadow: 0 16px 40px rgba(0,0,0,0.3); }
.tap-block:hover::after { opacity: 1; }
.tap-block:active { transform: scale(0.97); }

.tap-block__icon {
  width: 52px; height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--violet-dim);
  border-radius: 14px;
  color: #a78bfa;
  transition: transform 0.2s, background 0.2s;
}
.tap-block:hover .tap-block__icon {
  transform: scale(1.12) rotate(-3deg);
  background: rgba(124,58,237,0.28);
}

.tap-block__label { font-size: 1rem; font-weight: 700; color: var(--text-1); }
.tap-block__sub { font-size: 0.75rem; color: var(--text-2); text-align: center; line-height: 1.4; }

/* Footer row */
.tap-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.25rem;
  margin-top: auto;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: none;
  border: none;
  color: var(--text-2);
  font-size: 0.88rem;
  font-family: var(--sans);
  cursor: pointer;
  padding: 0.5rem 0;
  transition: color 0.15s;
}
.back-btn:hover { color: var(--text-1); }

.ghost-btn {
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  color: var(--text-2);
  font-size: 0.8rem;
  font-family: var(--sans);
  padding: 0.4rem 1rem;
  cursor: pointer;
  transition: all 0.15s;
}
.ghost-btn:hover { border-color: var(--border-hov); color: var(--text-1); }
.ghost-btn--full { width: 100%; }

/* ══════════════════════════════════════════════════════════════════
   LOADING
══════════════════════════════════════════════════════════════════ */
.loading-phase {
  justify-content: center;
  align-items: center;
  gap: 2rem;
  text-align: center;
}

/* Film strip loader */
.film-loader {
  display: flex;
  align-items: center;
  gap: 0;
  animation: film-roll 1.2s linear infinite;
}
@keyframes film-roll { to { transform: translateX(-8px); } }

.film-loader__reel {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 4px;
  background: #1a1a2e;
  border-radius: 4px;
}
.film-loader__hole {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--bg);
}

.film-loader__strip {
  display: flex;
  gap: 2px;
}
.film-loader__frame {
  width: 44px; height: 56px;
  background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1a 100%);
  border-radius: 2px;
  border: 1px solid rgba(255,255,255,0.06);
  animation: frame-flicker 0.8s ease-in-out infinite;
}
.film-loader__frame:nth-child(1) { animation-delay: 0s; background: linear-gradient(135deg, #1e1b4b 0%, #0f0f1a 100%); }
.film-loader__frame:nth-child(2) { animation-delay: 0.2s; background: linear-gradient(135deg, #1a1a2e 0%, #1e1b4b 100%); }
.film-loader__frame:nth-child(3) { animation-delay: 0.4s; background: linear-gradient(135deg, #1e1b4b 0%, #0f0f1a 100%); }
.film-loader__frame:nth-child(4) { animation-delay: 0.6s; }

@keyframes frame-flicker {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.loading-title {
  font-family: var(--serif);
  font-size: 1.8rem;
  color: var(--text-1);
}
.loading-ellipsis span {
  display: inline-block;
  animation: ellipsis-bounce 1.2s ease-in-out infinite;
  color: var(--amber);
}
.loading-ellipsis span:nth-child(2) { animation-delay: 0.2s; }
.loading-ellipsis span:nth-child(3) { animation-delay: 0.4s; }
@keyframes ellipsis-bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-8px); opacity: 1; }
}

.loading-sub {
  font-size: 0.88rem;
  color: var(--text-3);
  max-width: 260px;
  line-height: 1.6;
}

/* ══════════════════════════════════════════════════════════════════
   REVEAL
══════════════════════════════════════════════════════════════════ */
.reveal-phase {
  padding: 0 0 2rem;
  gap: 0;
}

/* Poster */
.reveal-poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  max-height: 55dvh;
  overflow: hidden;
  border-radius: 0 0 28px 28px;
  flex-shrink: 0;
}
.reveal-poster__img {
  width: 100%; height: 100%;
  object-fit: cover;
  object-position: top;
  display: block;
  animation: poster-reveal 0.6s cubic-bezier(0.4,0,0.2,1) forwards;
}
@keyframes poster-reveal {
  from { transform: scale(1.08); opacity: 0.6; }
  to   { transform: scale(1);    opacity: 1; }
}
.reveal-poster__fallback {
  width: 100%; height: 100%;
  background: linear-gradient(160deg, #1a1030 0%, #06060a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 5rem;
}
.reveal-poster__gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 40%, var(--bg) 100%);
}
.reveal-poster__eyebrow {
  position: absolute;
  top: 1rem; left: 1rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--amber);
  background: rgba(6,6,10,0.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(245,158,11,0.25);
  border-radius: var(--r-pill);
  padding: 0.25rem 0.7rem;
}

/* Details panel */
.reveal-details {
  padding: 1.25rem 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reveal-title {
  font-family: var(--serif);
  font-size: 2.1rem;
  line-height: 1.1;
  color: var(--text-1);
}
.reveal-title__link {
  color: inherit;
  text-decoration: none;
  background: linear-gradient(to right, var(--text-1), var(--text-1));
  background-size: 0% 1.5px;
  background-position: 0 100%;
  background-repeat: no-repeat;
  transition: background-size 0.3s ease, color 0.2s;
  display: inline-block;
}
.reveal-title__link:hover {
  color: #fff;
  background-size: 100% 1.5px;
}

.reveal-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.reveal-meta__year { font-size: 0.88rem; color: var(--text-3); }
.reveal-meta__rating { font-size: 0.88rem; color: var(--amber); font-weight: 600; }
.reveal-meta__lang {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  padding: 0.15rem 0.55rem;
  color: var(--text-2);
}

.reveal-reason {
  font-size: 0.95rem;
  color: var(--text-2);
  line-height: 1.65;
  font-style: italic;
  border-left: 2px solid var(--violet);
  padding-left: 1rem;
  margin-left: 0.1rem;
}

/* 3-tap recap */
.reveal-taps {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}
.reveal-tap {
  font-size: 0.78rem;
  color: var(--text-2);
}
.reveal-tap-sep {
  font-size: 0.78rem;
  color: var(--text-3);
}

/* Reveal actions */
.reveal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding: 0 1rem 0;
  margin-top: 0.25rem;
}
.reveal-actions__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}
.ghost-btn--half {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  width: 100%;
}

/* ── Also consider section ──────────────────────────────────────── */
.also-section {
  padding: 0 1rem;
  margin-top: 0.5rem;
}
.also-section__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.also-section__label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-3);
  white-space: nowrap;
}
.also-section__rule {
  flex: 1;
  height: 1px;
  background: var(--border);
}

.also-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.also-card {
  display: flex;
  gap: 0.85rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0.75rem;
  transition: border-color 0.15s;
}
.also-card:hover { border-color: var(--border-hov); }

.also-card__thumb {
  position: relative;
  flex-shrink: 0;
  width: 56px; height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #1a1030;
}
.also-card__img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}
.also-card__no-img {
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  background: linear-gradient(160deg, #1a1030, #06060a);
}
.also-card__badge {
  position: absolute;
  top: 3px; right: 3px;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: var(--violet);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.also-card__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
.also-card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.also-card__title-link {
  color: inherit;
  text-decoration: none;
  transition: color 0.15s;
}
.also-card__title-link:hover {
  color: var(--amber);
}
.also-card__meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-3);
}
.also-card__lang {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  padding: 0 0.35rem;
  font-size: 0.65rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-2);
}
.also-card__reason {
  font-size: 0.8rem;
  color: var(--text-2);
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* ══════════════════════════════════════════════════════════════════
   ERROR TOAST
══════════════════════════════════════════════════════════════════ */
.toast {
  position: fixed;
  bottom: 1.5rem; left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(15,15,25,0.9);
  border: 1px solid rgba(244,63,94,0.4);
  border-radius: var(--r-btn);
  backdrop-filter: blur(16px);
  padding: 0.75rem 1rem 0.75rem 1.1rem;
  font-size: 0.85rem;
  color: var(--text-1);
  max-width: calc(100vw - 2rem);
  z-index: 100;
  box-shadow: 0 8px 32px rgba(244,63,94,0.15);
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

/* ──────────────────────────────────────────────────────────────── */
@media (min-width: 480px) {
  .ob-card__title { font-size: 2.3rem; }
  .tap-header__title { font-size: 2.2rem; }
  .reveal-poster { max-height: 60dvh; }
}
</style>
