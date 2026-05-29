/**
 * options.js – UI option arrays for Socrates Screen
 *
 * Shared across Onboarding and other components.
 */

export const ONBOARDING_QUESTIONS = [
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

export const GENRE_OPTIONS = [
  "Thriller",
  "Drama",
  "Comedy",
  "Action",
  "Romance",
  "Sci-Fi",
  "Horror",
  "Mystery",
  "Fantasy",
  "Historical",
  "Documentary",
  "Masala",
  "Biographical",
  "Animation",
];

export const DEALBREAKER_OPTIONS = [
  { id: "gore", emoji: "🩸", label: "Gore" },
  { id: "subtitles", emoji: "📝", label: "No Subtitles" },
  { id: "sexual_content", emoji: "🔞", label: "Sexual Content" },
  { id: "slow_burn", emoji: "🐢", label: "No Slow Burns" },
  { id: "sad_endings", emoji: "😢", label: "No Sad Endings" },
  { id: "animals_harmed", emoji: "🐾", label: "No Animal Harm" },
];

export const LANG_OPTIONS = [
  { id: "any", flag: "🌐", label: "Any" },
  { id: "Hindi", flag: "🇮🇳", label: "Hindi" },
  { id: "Telugu", flag: "🎬", label: "Telugu" },
  { id: "Tamil", flag: "🎭", label: "Tamil" },
  { id: "Malayalam", flag: "🌴", label: "Malayalam" },
  { id: "English", flag: "🇬🇧", label: "English" },
];
