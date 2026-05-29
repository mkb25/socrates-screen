<template>
  <section class="phase loading-phase" key="loading">
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
</template>

<script setup>
// Pure presentational – no props, no store interaction
</script>

<style scoped>
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
</style>
