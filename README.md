# 🎬 Socrates Screen

> **3 taps. The perfect film. Every time.**
>
> A mobile-first movie recommendation app built for the Indian market — powered by Llama 3 (Groq), TMDB, and a Cloudflare Worker image proxy that bypasses Jio/ACT/BSNL ISP blocks on `image.tmdb.org`.

---

## Project Structure

```
socrates-screen/
│
├── frontend/                  ← Vue 3 + Vite frontend
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue            ← Full UI: onboarding → 3-tap → reveal
│   │   └── stores/
│   │       └── store.js       ← Pinia store (state, API calls, localStorage)
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json           ← Vue/Vite deps only
│   └── .env.example           ← VITE_API_BASE template
│
├── backend/                   ← Python FastAPI server
│   ├── main.py                ← Router + TMDB integration
│   ├── llm_service.py         ← Groq/Cerebras LLM + system prompt
│   ├── requirements.txt
│   ├── .env                   ← Your local secrets (git-ignored)
│   └── .env.example           ← Template
│
├── worker/                    ← Cloudflare Worker (TMDB image proxy)
│   ├── index.js               ← Worker entry point
│   └── wrangler.toml          ← Deploy with: npm run worker:deploy
│
├── package.json               ← Root orchestrator (run scripts for all 3)
├── .gitignore
└── README.md
```

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.12** | `py install 3.12` (Windows Python Launcher) |
| **Node.js 18+** | [nodejs.org](https://nodejs.org) |
| **Groq API key** | Free at [console.groq.com](https://console.groq.com/keys) |
| **TMDB API key** | Free v3 key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) |
| **Cloudflare account** | Free at [cloudflare.com](https://cloudflare.com) – 100k req/day free tier |

---

## Step 1 — Deploy the Cloudflare Worker

This is the image proxy that bypasses Indian ISP blocks on TMDB. **Do this first** so you have the URL for the backend config.

```bash
# Log in to Cloudflare (one-time)
npm run worker:login

# Deploy the worker
npm run worker:deploy
```

After deploying, Wrangler will print a URL like:
```
https://socrates-image-proxy.<your-name>.workers.dev
```
Copy this — you'll need it in Step 2.

---

## Step 2 — Configure & Start the Backend

```bash
# Create the Python 3.12 virtual environment and install all packages
npm run backend:install
```

Then open `backend/.env` and fill in your keys:

```env
GROQ_API_KEY=gsk_...              # From console.groq.com
TMDB_API_KEY=6507e1bc...          # 32-char v3 key from TMDB settings
CLOUDFLARE_WORKER_URL=https://socrates-image-proxy.<your-name>.workers.dev
```

> **Note on TMDB keys:** The backend auto-detects which type you have:
> - **v3 key** (32-char hex like `6507e1bc...`) → sent as `?api_key=` query param
> - **v4 token** (long JWT starting with `eyJ...`) → sent as `Authorization: Bearer` header

Then start the server:
```bash
npm run backend
# API running at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

---

## Step 3 — Run the Frontend

```bash
# Install frontend dependencies (only needed once)
npm run install:frontend

# Start the dev server
npm run dev
# Open http://localhost:5173
```

---

## The 3-Tap Flow

```
Tap 1 – Energy      Tap 2 – Reality     Tap 3 – Commitment
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  🧠 Think    │    │  🌍 Grounded │    │  ⚡ Quick    │
│  🍿 Brain Off│ →  │  🚀 Escapism │ →  │  🏔️ Epic    │  → Recommendation
│  ❤️ Feel    │    └──────────────┘    └──────────────┘
└──────────────┘
```

On **Tap 3**, the app fires `POST /api/recommend` which:
1. Sends the 3-tap state + baseline profile to **Llama 3.3-70B** via Groq
2. Searches **TMDB** server-side for the title's poster
3. Rewrites the poster URL through the **Cloudflare Worker** to bypass ISP blocks
4. Returns the complete `MovieCard` to the frontend

---

## npm Scripts Reference

| Script | What it does |
|--------|-------------|
| `npm run dev` | Start Vite frontend dev server |
| `npm run build` | Build frontend for production (`frontend/dist/`) |
| `npm run install:frontend` | Install frontend npm dependencies |
| `npm run backend` | Start the FastAPI backend server |
| `npm run backend:install` | Create venv + install Python deps |
| `npm run worker:login` | Authenticate Wrangler with Cloudflare |
| `npm run worker:deploy` | Deploy `worker/index.js` to Cloudflare |
| `npm run worker:dev` | Run the worker locally for testing |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key (get from console.groq.com) |
| `TMDB_API_KEY` | Yes | TMDB v3 key or v4 JWT token |
| `CLOUDFLARE_WORKER_URL` | Yes | Your deployed worker URL |
| `ALLOWED_ORIGINS` | Optional | CORS origins (default: localhost ports) |
| `GROQ_MODEL` | Optional | Override model (default: llama-3.3-70b-versatile) |
| `CEREBRAS_API_KEY` | Optional | Alternative to Groq |

### Frontend (`.env.local`, optional)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE` | Backend URL override (default: `http://localhost:8000`) |

---

## Indian Cinema Support

The LLM system prompt explicitly instructs the model to be fluent in:

- **Bollywood** / Hindi cinema (Golden Era, New Wave, modern blockbusters)
- **Tollywood** / Telugu (RRR, Baahubali, Arjun Reddy, Pushpa)
- **Kollywood** / Tamil (Mani Ratnam, Pa. Ranjith, Lokesh Kanagaraj)
- **Mollywood** / Malayalam (Jallikattu, Kumbalangi Nights, the New Wave)
- Kannada, Marathi, Bengali, Punjabi regional cinema

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 (Composition API) + Pinia |
| Styling | Vanilla CSS (glassmorphism, CSS animations) |
| Build | Vite 8 |
| Backend | Python 3.12 · FastAPI · Pydantic v2 |
| AI Engine | Groq SDK (Llama 3.3-70B) |
| Movie Data | TMDB API v3 (server-side only) |
| Image Proxy | Cloudflare Workers |

---

*Built for the Indian market. Works on 4G. Feels like cinema.*
