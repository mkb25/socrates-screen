/**
 * icons.js – Classical Greek antiquity themed SVG icon map
 *
 * Each key corresponds to an energy/reality/commitment option ID.
 * Values are raw SVG markup strings rendered via v-html.
 */

// Owl of Athena (Logos) – think
const think = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3c-3 0-5.5 1.5-6.5 3.5C5 7.5 5 9.5 5.5 11c0 0 .5.5 1 .5M12 3c3 0 5.5 1.5 6.5 3.5.5 1 .5 3 0 4.5 0 0-.5.5-1 .5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <circle cx="8.5" cy="9.5" r="2.5" stroke="currentColor" stroke-width="1.6"/>
  <circle cx="15.5" cy="9.5" r="2.5" stroke="currentColor" stroke-width="1.6"/>
  <circle cx="8.5" cy="9.5" r="0.8" fill="currentColor"/>
  <circle cx="15.5" cy="9.5" r="0.8" fill="currentColor"/>
  <path d="M12 9.5v3l-1.5-1.5H13.5L12 12.5" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M7.5 13.5c-.5.8-1 2.3-1 4.5 0 2 1.5 3.5 5.5 3.5s5.5-1.5 5.5-3.5c0-2.2-.5-3.7-1-4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M10 16.5l2 1.5 2-1.5M9.5 18.5l2.5 1.5 2.5-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
</svg>`;

// Greek Theater Masks (Catharsis) – brain_off
const brain_off = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 13.5c0-3.5 2-6 5-6s5 2.5 5 6-1.5 5.5-4 5.5S3 17 3 13.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
  <circle cx="6.5" cy="11.5" r="1" fill="currentColor"/>
  <circle cx="9.5" cy="11.5" r="1" fill="currentColor"/>
  <path d="M6.5 15.5c.5-.5 1.5-.5 2 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M11 10.5c0-3.5 2-6 5-6s5 2.5 5 6-1.5 5.5-4 5.5s-6-2-6-5.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" fill="rgba(6, 6, 10, 0.9)"/>
  <circle cx="14.5" cy="8.5" r="1" fill="currentColor"/>
  <circle cx="17.5" cy="8.5" r="1" fill="currentColor"/>
  <path d="M14.5 11c.5.8 1.5.8 2 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
</svg>`;

// Lyre of Apollo (Pathos) – feel
const feel = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 5h12M4 5.5h2M18 5.5h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M6 5c-.5 3-1.5 5.5-1.5 9 0 4.5 3.5 7.5 7.5 7.5s7.5-3 7.5-7.5c0-3.5-1-6-1.5-9" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M9 5v14.5M12 5v16M15 5v14.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M8 18.5h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>`;

// Balance Scales (Mimesis) – grounded
const grounded = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3v16M8 21h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M5 7h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M5 7l-2 6.5h4L5 7z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M2.5 13.5c0 1.5 1.5 2.5 2.5 2.5s2.5-1 2.5-2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M19 7l-2 6.5h4L19 7z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M16.5 13.5c0 1.5 1.5 2.5 2.5 2.5s2.5-1 2.5-2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  <circle cx="12" cy="7" r="1" fill="currentColor"/>
</svg>`;

// Temple in the Clouds (Phantasia) – escapism
const escapism = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 8l8-4.5L20 8H4z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M5 8.5h14v1.5H5v-1.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M7 10v6M10 10v6M14 10v6M17 10v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M5 16.5h14v1.5H5v-1.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M2 19.5c1.5-1 3.5-.5 4.5.5.8-1.2 2.5-1.5 3.5-.5.8-1 2.5-1.2 3.5 0 1-1.2 2.8-1 3.5.5s2 1.5 3.5.5M2 20.5h20" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
</svg>`;

// Winged Hourglass (Kairos) – quick
const quick = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M8 5h8M8 19h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M9 5c0 3.5 1.5 5.5 3 7-1.5 1.5-3 3.5-3 7M15 5c0 3.5-1.5 5.5-3 7 1.5 1.5 3 3.5 3 7" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M10 7.5h4M11 16.5h2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M12 12v3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.6"/>
  <path d="M7.5 9C6.5 8 4.5 8 3.5 9s-1.5 3 1.5 4c2.5.8 2.5-1 2.5-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M16.5 9c1-1 3-1 4 0s1.5 3-1.5 4c-2.5.8-2.5-1-2.5-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
</svg>`;

// Classical Greek Temple / Sprawling Monument (Aion) – epic
const epic = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 7l10-5 10 5H2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M3 7.5h18v1.8H3V7.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M5 9.5v8.5M8 9.5v8.5M11 9.5v8.5M14 9.5v8.5M17 9.5v8.5M20 9.5v8.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M3 18.5h18v1.5H3v-1.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M1.5 20.2h21v1.8h-21v-1.8z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
</svg>`;

export const ICONS = {
  think,
  brain_off,
  feel,
  grounded,
  escapism,
  quick,
  epic,
};

export default ICONS;
