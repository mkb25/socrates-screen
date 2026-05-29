<template>
  <section class="phase onboarding-phase">
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
          <!-- Step 0: Favorite movies -->
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

          <!-- Step 1: Genres -->
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

          <!-- Step 2: Dealbreakers -->
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

          <!-- Step 3: Language preference -->
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
</template>

<script setup>
import { useSocratesStore } from "../stores/store.js";
import { useOnboarding } from "../composables/useOnboarding.js";
import {
  ONBOARDING_QUESTIONS,
  GENRE_OPTIONS,
  DEALBREAKER_OPTIONS,
  LANG_OPTIONS,
} from "../constants/options.js";

const store = useSocratesStore();

const {
  movieInput,
  onboardingStep,
  currentOnboardingQuestion,
  addMovie,
  removeMovie,
  nextOnboardingQuestion,
  previousOnboardingQuestion,
  toggleGenre,
  toggleDealbreaker,
} = useOnboarding(store);
</script>

<style scoped>
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
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--text-2);
  letter-spacing: 0.04em;
  font-family: var(--serif);
  text-transform: uppercase;
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
</style>
