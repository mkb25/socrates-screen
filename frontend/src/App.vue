<template>
  <div id="app" class="app-shell">

    <div class="academy-backdrop" aria-hidden="true">
      <span class="academy-backdrop__pediment"></span>
      <span class="academy-backdrop__column academy-backdrop__column--left"></span>
      <span class="academy-backdrop__column academy-backdrop__column--right"></span>
    </div>

    <Transition name="phase" mode="out-in">

      <!-- ═══════════════════════════════════════════════
           ONBOARDING
      ════════════════════════════════════════════════ -->
      <section v-if="store.phase === PHASE.ONBOARDING" key="onboarding" class="phase onboarding-phase">
        <header class="ob-header">
          <img
            class="socrates-portrait"
            src="/socrates-logo.png"
            alt="Gold Socrates profile coin"
            width="128"
            height="128"
          />

          <div class="wordmark">
            <span class="wordmark__text">Socrates Screen</span>
          </div>
          <p class="ob-tagline">Question taste. Find the film.</p>
        </header>

        <div class="ob-card">
          <div class="dialogue-progress" aria-label="Taste setup progress">
            <span
              v-for="(_, i) in ONBOARDING_QUESTIONS"
              :key="i"
              class="dialogue-progress__dot"
              :class="{ 'dialogue-progress__dot--active': i <= onboardingStep }"
            ></span>
          </div>

          <div class="ob-card__eyebrow">Question {{ onboardingStep + 1 }} / {{ ONBOARDING_QUESTIONS.length }}</div>
          <h1 class="ob-card__title">{{ currentOnboardingQuestion.title }}</h1>
          <p class="ob-card__sub">{{ currentOnboardingQuestion.sub }}</p>

          <Transition name="question" mode="out-in">
            <div :key="onboardingStep" class="question-panel">
              <div v-if="onboardingStep === 0" class="field">
                <label class="field__label" for="movie-input">Your answer</label>
                <div class="field__input-row">
                  <input
                    id="movie-input"
                    v-model="movieInput"
                    class="field__input"
                    placeholder="Dune, Vikram, Tumbbad..."
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

              <div v-else-if="onboardingStep === 1" class="field">
                <label class="field__label">Choose all that answer honestly</label>
                <div class="pill-grid">
                  <button
                    v-for="g in GENRE_OPTIONS" :key="g"
                    class="pill"
                    :class="{ 'pill--active': store.baselineProfile.favorite_genres.includes(g) }"
                    @click="toggleGenre(g)"
                  >{{ g }}</button>
                </div>
              </div>

              <div v-else-if="onboardingStep === 2" class="field">
                <label class="field__label">What should Socrates avoid?</label>
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

              <div v-else class="field">
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
            </div>
          </Transition>

          <div class="dialogue-actions">
            <button class="ghost-btn" :disabled="onboardingStep === 0" @click="previousOnboardingQuestion">
              Back
            </button>
            <button class="ghost-btn" @click="nextOnboardingQuestion(true)">
              Skip
            </button>
          </div>

          <button class="cta-btn" @click="nextOnboardingQuestion(false)">
            <span>{{ onboardingStep === ONBOARDING_QUESTIONS.length - 1 ? "Begin the search" : "Continue" }}</span>
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
const onboardingStep = ref(0);
const posterErrors = ref([false, false, false]);

const ONBOARDING_QUESTIONS = [
  {
    title: "Which films have already persuaded you?",
    sub: "Name up to five films Socrates should treat as evidence of your taste.",
  },
  {
    title: "What kind of stories call to you?",
    sub: "Select the genres you return to when the evening is yours.",
  },
  {
    title: "What should be kept outside the city gates?",
    sub: "Mark anything that would ruin the recommendation for you.",
  },
  {
    title: "In what tongue should the oracle speak?",
    sub: "Pick a language preference, or leave the field open to the wider world.",
  },
];

watch(() => store.recommendation, () => {
  posterErrors.value = [false, false, false];
});

const currentOnboardingQuestion = computed(() => ONBOARDING_QUESTIONS[onboardingStep.value]);

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

// SVG icon map – Classical Greek antiquity themed icons
const ICONS = {
  // think – Owl of Athena (Logos)
  think: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 3c-3 0-5.5 1.5-6.5 3.5C5 7.5 5 9.5 5.5 11c0 0 .5.5 1 .5M12 3c3 0 5.5 1.5 6.5 3.5.5 1 .5 3 0 4.5 0 0-.5.5-1 .5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <circle cx="8.5" cy="9.5" r="2.5" stroke="currentColor" stroke-width="1.6"/>
    <circle cx="15.5" cy="9.5" r="2.5" stroke="currentColor" stroke-width="1.6"/>
    <circle cx="8.5" cy="9.5" r="0.8" fill="currentColor"/>
    <circle cx="15.5" cy="9.5" r="0.8" fill="currentColor"/>
    <path d="M12 9.5v3l-1.5-1.5H13.5L12 12.5" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M7.5 13.5c-.5.8-1 2.3-1 4.5 0 2 1.5 3.5 5.5 3.5s5.5-1.5 5.5-3.5c0-2.2-.5-3.7-1-4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M10 16.5l2 1.5 2-1.5M9.5 18.5l2.5 1.5 2.5-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  </svg>`,
  // brain_off – Greek Theater Masks (Catharsis)
  brain_off: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 13.5c0-3.5 2-6 5-6s5 2.5 5 6-1.5 5.5-4 5.5S3 17 3 13.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="6.5" cy="11.5" r="1" fill="currentColor"/>
    <circle cx="9.5" cy="11.5" r="1" fill="currentColor"/>
    <path d="M6.5 15.5c.5-.5 1.5-.5 2 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M11 10.5c0-3.5 2-6 5-6s5 2.5 5 6-1.5 5.5-4 5.5s-6-2-6-5.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" fill="rgba(6, 6, 10, 0.9)"/>
    <circle cx="14.5" cy="8.5" r="1" fill="currentColor"/>
    <circle cx="17.5" cy="8.5" r="1" fill="currentColor"/>
    <path d="M14.5 11c.5.8 1.5.8 2 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  </svg>`,
  // feel – Lyre of Apollo (Pathos)
  feel: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 5h12M4 5.5h2M18 5.5h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M6 5c-.5 3-1.5 5.5-1.5 9 0 4.5 3.5 7.5 7.5 7.5s7.5-3 7.5-7.5c0-3.5-1-6-1.5-9" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M9 5v14.5M12 5v16M15 5v14.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    <path d="M8 18.5h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </svg>`,
  // grounded – Balance Scales (Mimesis)
  grounded: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 3v16M8 21h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M5 7h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M5 7l-2 6.5h4L5 7z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M2.5 13.5c0 1.5 1.5 2.5 2.5 2.5s2.5-1 2.5-2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    <path d="M19 7l-2 6.5h4L19 7z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M16.5 13.5c0 1.5 1.5 2.5 2.5 2.5s2.5-1 2.5-2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    <circle cx="12" cy="7" r="1" fill="currentColor"/>
  </svg>`,
  // escapism – Temple in the Clouds (Phantasia)
  escapism: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 8l8-4.5L20 8H4z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M5 8.5h14v1.5H5v-1.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M7 10v6M10 10v6M14 10v6M17 10v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M5 16.5h14v1.5H5v-1.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M2 19.5c1.5-1 3.5-.5 4.5.5.8-1.2 2.5-1.5 3.5-.5.8-1 2.5-1.2 3.5 0 1-1.2 2.8-1 3.5.5s2 1.5 3.5.5M2 20.5h20" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  </svg>`,
  // quick – Winged Hourglass (Kairos)
  quick: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 5h8M8 19h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M9 5c0 3.5 1.5 5.5 3 7-1.5 1.5-3 3.5-3 7M15 5c0 3.5-1.5 5.5-3 7 1.5 1.5 3 3.5 3 7" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M10 7.5h4M11 16.5h2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    <path d="M12 12v3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.6"/>
    <path d="M7.5 9C6.5 8 4.5 8 3.5 9s-1.5 3 1.5 4c2.5.8 2.5-1 2.5-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    <path d="M16.5 9c1-1 3-1 4 0s1.5 3-1.5 4c-2.5.8-2.5-1-2.5-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  </svg>`,
  // epic – Classical Greek Temple / Sprawling Monument (Aion)
  epic: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 7l10-5 10 5H2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
    <path d="M3 7.5h18v1.8H3V7.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M5 9.5v8.5M8 9.5v8.5M11 9.5v8.5M14 9.5v8.5M17 9.5v8.5M20 9.5v8.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M3 18.5h18v1.5H3v-1.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M1.5 20.2h21v1.8h-21v-1.8z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
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
  if (i === -1) genres.push(g); else genres.splice(i, 1);
}
function toggleDealbreaker(id) {
  const db = store.baselineProfile.dealbreakers;
  const i = db.indexOf(id);
  if (i === -1) db.push(id); else db.splice(i, 1);
}

function tapLabel(axis, id) {
  const map = {
    energy: { think: "Logos", brain_off: "Catharsis", feel: "Pathos" },
    reality: { grounded: "Mimesis", escapism: "Phantasia" },
    commitment: { quick: "Kairos", epic: "Aion" },
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
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

/* ─── Tokens ──────────────────────────────────────────────────────────────── */
:root {
  --bg:          #090A0C;
  --bg-2:        #101219;
  --surface:     rgba(235, 225, 199, 0.055);
  --surface-hov: rgba(235, 225, 199, 0.09);
  --border:      rgba(212, 175, 55, 0.14);
  --border-hov:  rgba(212, 175, 55, 0.28);

  --gold:        #D4AF37;
  --gold-2:      #E7C76B;
  --gold-dim:    rgba(212, 175, 55, 0.18);
  --gold-glow:   rgba(212, 175, 55, 0.4);
  
  --laurel:      #8FA87C;
  --laurel-dim:  rgba(143, 168, 124, 0.18);
  --laurel-border: rgba(143, 168, 124, 0.4);
  
  --terracotta:  #C06C54;
  --terracotta-dim: rgba(192, 108, 84, 0.15);
  --terracotta-border: rgba(192, 108, 84, 0.45);

  --marble:      #E8E0CF;
  --marble-dim:  rgba(232, 224, 207, 0.12);
  --ink:         #060608;

  --text-1:  #F4EFE4;
  --text-2:  #B6AD9B;
  --text-3:  #746F66;

  --r-card:  8px;
  --r-btn:   12px;
  --r-pill:  999px;

  --sans:    'Inter', system-ui, sans-serif;
  --serif:   'Cinzel', Georgia, serif;
  --body-serif: 'Lora', Georgia, serif;

  /* Compatibility redirections for existing styles */
  --amber:       var(--gold);
  --amber-dim:   var(--gold-dim);
  --violet:      var(--laurel);
  --violet-dim:  var(--laurel-dim);
  --rose:        var(--terracotta);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  height: 100%;
  background:
    linear-gradient(180deg, rgba(212, 175, 55, 0.08), transparent 30%),
    radial-gradient(circle at 50% -20%, rgba(232, 224, 207, 0.12), transparent 34%),
    var(--bg);
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
  padding: 1.75rem 0 1.35rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
}

.socrates-portrait {
  width: 128px;
  height: 128px;
  object-fit: contain;
  border-radius: 50%;
  animation: pulse-glow 4s ease-in-out infinite;
  filter: drop-shadow(0 0 14px rgba(212, 175, 55, 0.22)) drop-shadow(0 18px 28px rgba(0, 0, 0, 0.34));
}

.wordmark {
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 4px var(--gold-glow)); opacity: 0.9; }
  50% { filter: drop-shadow(0 0 12px var(--gold-glow)); opacity: 1; }
}

.wordmark__text {
  font-family: var(--serif);
  font-size: 1.5rem;
  color: var(--text-1);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.ob-tagline {
  font-size: 0.78rem;
  color: var(--text-3);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: var(--body-serif);
  font-style: italic;
}

/* Onboarding card */
.ob-card {
  background:
    linear-gradient(180deg, rgba(232, 224, 207, 0.07), rgba(232, 224, 207, 0.025)),
    rgba(8, 9, 11, 0.82);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  padding: 1.75rem 1.5rem;
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  display: flex;
  flex-direction: column;
  gap: 1.6rem;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(232, 224, 207, 0.08);
  position: relative;
}
.ob-card::before {
  content: '';
  position: absolute;
  inset: 0.55rem;
  border: 1px solid rgba(212, 175, 55, 0.08);
  border-radius: 5px;
  pointer-events: none;
}

.ob-card__eyebrow {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  font-family: var(--serif);
}

.ob-card__title {
  font-family: var(--serif);
  font-size: 1.9rem;
  line-height: 1.2;
  color: var(--text-1);
  letter-spacing: 0.02em;
}

.ob-card__sub {
  font-size: 0.8rem;
  color: var(--text-2);
  margin-top: -0.8rem;
  font-family: var(--body-serif);
  font-style: italic;
}

.dialogue-progress {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.4rem;
}

.dialogue-progress__dot {
  height: 3px;
  border-radius: var(--r-pill);
  background: rgba(232, 224, 207, 0.12);
  transition: background 0.25s, box-shadow 0.25s;
}

.dialogue-progress__dot--active {
  background: linear-gradient(90deg, var(--laurel), var(--gold));
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.22);
}

.question-panel {
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.question-enter-active,
.question-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.question-enter-from { opacity: 0; transform: translateX(18px); }
.question-leave-to { opacity: 0; transform: translateX(-18px); }

.dialogue-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
  margin-top: -0.3rem;
}

/* Fields */
.field { display: flex; flex-direction: column; gap: 0.6rem; }

.field__label {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-2);
  letter-spacing: 0.04em;
  font-family: var(--serif);
  text-transform: uppercase;
  font-size: 0.68rem;
}

.field__input-row {
  display: flex;
  gap: 0.5rem;
}

.field__input {
  flex: 1;
  background: rgba(5, 6, 8, 0.52);
  border: 1px solid var(--border);
  border-radius: var(--r-btn);
  color: var(--text-1);
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  font-family: var(--body-serif);
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.field__input:focus {
  border-color: var(--gold);
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.15);
}
.field__input::placeholder { color: var(--text-3); }

.field__add-btn {
  width: 42px; height: 42px;
  background: linear-gradient(135deg, var(--gold-2) 0%, var(--gold) 100%);
  border: none;
  border-radius: var(--r-btn);
  color: #080A10;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
  box-shadow: 0 2px 12px rgba(212, 175, 55, 0.25);
}
.field__add-btn:hover { background: linear-gradient(135deg, #F0D883 0%, var(--gold) 100%); box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4); }
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
  background: var(--laurel-dim);
  border: 1px solid var(--laurel-border);
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
.tag__remove:hover { color: var(--terracotta); }

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
  transition: all 0.2s;
}
.pill:hover { border-color: var(--border-hov); color: var(--text-1); }
.pill--active {
  background: var(--laurel-dim);
  border-color: var(--laurel-border);
  color: #B8D4A0;
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
  transition: all 0.2s;
  text-align: left;
}
.dealbreaker:hover { border-color: var(--border-hov); }
.dealbreaker--active {
  background: var(--terracotta-dim);
  border-color: var(--terracotta-border);
}
.dealbreaker__icon { font-size: 1rem; }
.dealbreaker__label { font-size: 0.8rem; color: var(--text-2); }
.dealbreaker--active .dealbreaker__label { color: #E8A090; }

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
  transition: all 0.2s;
}
.lang-chip:hover { border-color: var(--border-hov); }
.lang-chip--active {
  background: var(--gold-dim);
  border-color: var(--gold-glow);
  color: var(--gold);
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
  background: linear-gradient(135deg, var(--gold-2) 0%, var(--gold) 58%, #9A7B15 100%);
  border: none;
  border-radius: var(--r-btn);
  color: #080A10;
  font-size: 0.95rem;
  font-weight: 700;
  font-family: var(--serif);
  cursor: pointer;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  box-shadow: 0 4px 24px rgba(212, 175, 55, 0.3);
  transition: transform 0.15s, box-shadow 0.15s;
  position: relative;
  overflow: hidden;
}
.cta-btn::before {
  content: '';
  position: absolute;
  top: 0; left: -75%;
  width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: skewX(-25deg);
  transition: left 0.6s ease;
}
.cta-btn:hover::before { left: 125%; }
.cta-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 36px rgba(212, 175, 55, 0.45); }
.cta-btn:active { transform: translateY(0); }

/* ══════════════════════════════════════════════════════════════════
   TAP PHASES
══════════════════════════════════════════════════════════════════ */

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
  background: rgba(232, 224, 207, 0.025);
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
.ghost-btn:disabled {
  cursor: not-allowed;
  opacity: 0.38;
}
.ghost-btn:disabled:hover {
  border-color: var(--border);
  color: var(--text-2);
}
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
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.36), rgba(116, 111, 102, 0.22));
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
  background: linear-gradient(135deg, rgba(232, 224, 207, 0.12) 0%, rgba(6, 6, 8, 0.88) 100%);
  border-radius: 2px;
  border: 1px solid rgba(212, 175, 55, 0.12);
  animation: frame-flicker 0.8s ease-in-out infinite;
}
.film-loader__frame:nth-child(1) { animation-delay: 0s; background: linear-gradient(135deg, rgba(143, 168, 124, 0.22) 0%, rgba(6, 6, 8, 0.88) 100%); }
.film-loader__frame:nth-child(2) { animation-delay: 0.2s; background: linear-gradient(135deg, rgba(212, 175, 55, 0.18) 0%, rgba(6, 6, 8, 0.88) 100%); }
.film-loader__frame:nth-child(3) { animation-delay: 0.4s; background: linear-gradient(135deg, rgba(192, 108, 84, 0.18) 0%, rgba(6, 6, 8, 0.88) 100%); }
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
  color: var(--gold);
}
.loading-ellipsis span:nth-child(2) { animation-delay: 0.2s; }
.loading-ellipsis span:nth-child(3) { animation-delay: 0.4s; }
@keyframes ellipsis-bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-8px); opacity: 1; }
}

.loading-sub {
  font-size: 0.88rem;
  color: var(--text-2);
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
  border: 1px solid rgba(212, 175, 55, 0.12);
  border-top: 0;
  border-radius: 0 0 var(--r-card) var(--r-card);
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
  background:
    linear-gradient(160deg, rgba(143, 168, 124, 0.18) 0%, rgba(6, 6, 8, 0.96) 100%),
    repeating-linear-gradient(90deg, rgba(212, 175, 55, 0.12) 0 1px, transparent 1px 16px);
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
  color: var(--gold);
  background: rgba(6, 6, 8, 0.74);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(212, 175, 55, 0.28);
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
  color: var(--gold-2);
  background-size: 100% 1.5px;
}

.reveal-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.reveal-meta__year { font-size: 0.88rem; color: var(--text-3); }
.reveal-meta__rating { font-size: 0.88rem; color: var(--gold); font-weight: 600; }
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
  border-left: 2px solid var(--laurel);
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
  color: var(--gold);
  font-family: var(--serif);
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
  background:
    linear-gradient(180deg, rgba(232, 224, 207, 0.052), rgba(232, 224, 207, 0.018)),
    rgba(8, 9, 11, 0.78);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  padding: 0.75rem;
  transition: border-color 0.15s;
}
.also-card:hover { border-color: var(--border-hov); }

.also-card__thumb {
  position: relative;
  flex-shrink: 0;
  width: 56px; height: 80px;
  border-radius: 5px;
  overflow: hidden;
  background: var(--ink);
  border: 1px solid rgba(212, 175, 55, 0.12);
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
  background: linear-gradient(160deg, rgba(143, 168, 124, 0.22), rgba(6, 6, 8, 0.96));
}
.also-card__badge {
  position: absolute;
  top: 3px; right: 3px;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: var(--gold);
  color: var(--ink);
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
  color: var(--gold);
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

/* ──────────────────────────────────────────────────────────────── */
@media (min-width: 480px) {
  .ob-card__title { font-size: 2.3rem; }
  .tap-header__title { font-size: 2.2rem; }
  .reveal-poster { max-height: 60dvh; }
}

@media (max-width: 380px) {
  .socrates-portrait {
    width: 112px;
    height: 112px;
  }
  .wordmark__text { font-size: 1.35rem; }
}
</style>
