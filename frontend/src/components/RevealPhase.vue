<template>
  <section class="phase reveal-phase">
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
</template>

<script setup>
import { ref, watch } from "vue";
import { useSocratesStore } from "../stores/store.js";

const store = useSocratesStore();

const posterErrors = ref([false, false, false]);

watch(() => store.recommendation, () => {
  posterErrors.value = [false, false, false];
});

function tapLabel(axis, id) {
  const map = {
    energy: { think: "Logos", brain_off: "Catharsis", feel: "Pathos" },
    reality: { grounded: "Mimesis", escapism: "Phantasia" },
    commitment: { quick: "Kairos", epic: "Aion" },
  };
  return map[axis]?.[id] || id;
}

function langLabel(code) {
  const MAP = {
    hi: "Hindi", te: "Telugu", ta: "Tamil", ml: "Malayalam", kn: "Kannada",
    en: "English", fr: "French", ko: "Korean", ja: "Japanese",
    es: "Spanish", de: "German", it: "Italian",
  };
  return MAP[code] || code?.toUpperCase();
}
</script>

<style scoped>
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
</style>
