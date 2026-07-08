# RepoMind Space

**RepoMind Space** is an AI-powered repository intelligence platform. Import any GitHub repository or ZIP archive, automatically analyze the codebase, generate rich documentation artifacts, and have real-time AI-assisted conversations about your code — all from a clean, modern web interface.

🔗 **Live Demo:** [https://repomind-space.onrender.com]
🔗 **Demo Video:** [https://drive.google.com/file/d/1Nkzj09wCHtBTlNmQsEhAmoR3QpkmYQM1/view?usp=sharing]

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Running Locally](#running-locally)
- [Deploying to Render](#deploying-to-render)
- [API Reference](#api-reference)
- [Key Design Decisions](#key-design-decisions)

---

## Features

- **Google OAuth 2.0 Sign-In** — Secure one-click authentication via Google Identity Services
- **Email / Password Auth** — Standard registration and login with bcrypt-hashed passwords and JWT sessions
- **Workspace Management** — Create named workspaces linked to a GitHub repo URL or uploaded ZIP archive. Each workspace is isolated with its own parsed codebase, artifacts, and chat history
- **Repository Ingestion** — Clones public/private GitHub repositories or extracts ZIP uploads
- **AI Artifact Generation** — Uses Google Gemini to produce structured documentation:
  - `README.md`, Architecture Overview, API Reference, Data Flow Diagram, Changelog, Custom prompts
- **AI Repository Chat** — Stream-based conversational interface (Server-Sent Events) powered by Gemini — ask anything about your codebase
- **Artifact Management** — View, edit (Markdown editor), and delete generated artifacts per workspace
- **Dashboard** — Real-time stats: total workspaces, repositories, artifacts, AI chats, and a weekly activity chart
- **User Profile** — Update display name, view account info, delete account
- **Dark / Light Theme** — Persisted via `localStorage`
- **Workspace Deduplication** — Server-side guard prevents double workspace creation from browser double-submit race conditions

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Runtime |
| **Flask 3.0** | REST API + static file server |
| **Gunicorn** | Production WSGI server |
| **flask-cors** | Cross-origin request handling |
| **pymongo 4.6** | MongoDB Atlas driver |
| **bcrypt** | Password hashing |
| **PyJWT** | JWT session tokens |
| **google-auth** | Google ID Token verification |
| **google-generativeai** | Gemini AI SDK (artifact generation + chat) |
| **python-dotenv** | Environment variable management |
| **pathspec** | `.gitignore`-aware file parsing |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5 / Vanilla CSS** | Structure and styling |
| **Vanilla JavaScript** | UI logic, API calls, SSE streaming |
| **Google Identity Services (GIS)** | Google OAuth button |
| **Chart.js** (CDN) | Dashboard activity chart |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Render** | Full-stack hosting (backend + frontend on one service) |
| **MongoDB Atlas** | Cloud database (users, workspaces, artifacts, chats) |
| **Google Gemini API** | AI generation with model fallback chain |
| **GitHub API / git CLI** | Repository cloning |

---

## Project Structure

```
RepoMindSpace/
│
├── app.py                    # Flask entry point — serves API + static frontend
├── requirements.txt          # Python dependencies (incl. gunicorn)
├── Procfile                  # Render/Gunicorn start command
├── render.yaml               # Render Blueprint config
├── .env                      # Secret keys (never commit — see .env.example)
├── .env.example              # Template for environment variables
├── .gitignore
├── index.html                # Landing page
│
├── routes/
│   ├── auth.py               # /api/auth/* — register, login, Google OAuth, profile
│   ├── workspace.py          # /api/workspace/* — CRUD, stats, dedup guard
│   ├── artifact.py           # /api/artifacts/* — Gemini generation, CRUD
│   └── chat.py               # /api/chat/* — SSE streaming chat, history
│
├── models/
│   └── user.py               # MongoDB user schema helpers
│
├── utils/
│   ├── parser.py             # LocalParser — walks workspace dir, extracts file content
│   ├── ignore_handler.py     # .gitignore-aware file filter
│   └── auth_middleware.py    # token_required JWT decorator
│
├── pages/                    # All HTML pages
│   ├── login.html
│   ├── register.html
│   ├── onboarding.html
│   ├── dashboard.html
│   ├── workspaces.html
│   ├── create-workspace.html
│   ├── workspace-detail.html
│   ├── repository-chat.html
│   ├── generate-artifact.html
│   ├── edit-artifact.html
│   ├── artifacts.html
│   ├── profile.html
│   ├── forgot-password.html
│   └── mfa-verify.html
│
├── js/                       # Client-side JavaScript
│   ├── config.js             # API_BASE URL (empty = relative, works on any host)
│   ├── auth.js               # Login, register, Google GIS, logout
│   ├── workspace.js          # Workspace create, list, stats
│   ├── artifacts.js          # Artifact list, delete
│   ├── analysis.js           # Workspace detail — file stats
│   ├── chat.js               # SSE streaming chat
│   ├── generation.js         # Artifact generation form
│   ├── user-profile.js       # Profile page data
│   └── theme.js              # Dark/Light theme
│
├── css/
│   └── style.css             # Global design system
│
└── data/
    └── workspaces/           # Cloned repos (auto-created at runtime, gitignored)
```

---

## Prerequisites

- **Python 3.10+**
- **Git** (must be in PATH — used to clone repositories)
- **MongoDB Atlas** account (free tier works fine)
- **Google Cloud Console** project with OAuth 2.0 Client ID
- **Google Gemini API Key** — from [Google AI Studio](https://aistudio.google.com/)
- *(Optional)* **GitHub Personal Access Token** for private repo cloning

---

## Environment Setup

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env`.**

```env
# MongoDB Atlas
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/?appName=RepoMindCluster
MONGO_DB_NAME=repomind_space

# JWT — use any long random string
JWT_SECRET=your_super_secret_jwt_key_here

# Flask
FLASK_APP=app.py
FLASK_ENV=development
PORT=5000

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Google OAuth (from Google Cloud Console → Credentials)
GOOGLE_CLIENT_ID=your_google_client_id_here

# GitHub (optional — needed only for private repo cloning)
GITHUB_TOKEN=your_github_personal_access_token_here
```

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services → Credentials**
2. Create an **OAuth 2.0 Client ID** (Web application)
3. Add `http://localhost:5000` to **Authorized JavaScript origins**
4. Copy the **Client ID** into `GOOGLE_CLIENT_ID` in `.env`
5. Also update the `data-client_id` attribute in `pages/login.html` and `pages/register.html`

---

## Running Locally

Flask serves both the **backend API** and the **frontend static files** from the same server. One terminal is all you need.

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Start everything
python app.py
```

Open your browser at **`http://localhost:5000`**

> No more `python -m http.server 8000` — everything runs from Flask on port 5000.

---

## Deploying to Render

The entire app is deployed as **one single Render Web Service** — Flask handles both the API and serves the static frontend.

### Step-by-step

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo (`alt8d360/RepoMindSpace`)
4. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add **Environment Variables**:

| Key | Value |
|-----|-------|
| `MONGO_URI` | Your MongoDB Atlas connection string |
| `MONGO_DB_NAME` | `repomind_space` |
| `JWT_SECRET` | Any long random string |
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GITHUB_TOKEN` | Your GitHub PAT *(optional)* |
| `FLASK_ENV` | `production` |

6. Click **Deploy** 🚀

Your app will be live at `https://repomindspace.onrender.com` (or your chosen name).

> **After deploying:** Add your Render URL to **Authorized JavaScript origins** in Google Cloud Console → APIs & Services → Credentials.

> **Cold starts:** Render free tier spins down after 15 mins of inactivity. First request after sleep takes ~30s. Upgrade to Render Starter ($7/mo) to eliminate this.

---

## API Reference

All endpoints are under `/api/`. Protected routes require the header: `Authorization: Bearer <jwt_token>`

### Authentication — `/api/auth/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/register` | ❌ | Register with email + password |
| `POST` | `/login` | ❌ | Login, returns JWT |
| `POST` | `/google` | ❌ | Google OAuth — verify ID token, return JWT |
| `POST` | `/forgot-password` | ❌ | Send password reset email |
| `POST` | `/reset-password` | ❌ | Reset password with token |
| `GET` | `/me` | ✅ | Get current user info |
| `PUT` | `/profile` | ✅ | Update display name |
| `DELETE` | `/me` | ✅ | Permanently delete account and all data |

### Workspaces — `/api/workspace/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/create` | ✅ | Create workspace (GitHub clone or ZIP). 30s dedup guard. |
| `GET` | `/list` | ✅ | All workspaces with real artifact/chat counts |
| `GET` | `/recent` | ✅ | Most recently accessed workspace |
| `GET` | `/stats` | ✅ | Dashboard stats + weekly chart data |
| `GET` | `/<workspace_id>` | ✅ | Single workspace details |
| `DELETE` | `/<workspace_id>` | ✅ | Delete workspace and all data |

### Artifacts — `/api/artifacts/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/generate` | ✅ | Generate artifact via Gemini (model fallback chain) |
| `GET` | `/workspace/<workspace_id>` | ✅ | List all artifacts for a workspace |
| `GET` | `/<artifact_id>` | ✅ | Get artifact content |
| `PUT` | `/<artifact_id>` | ✅ | Update artifact content |
| `DELETE` | `/<artifact_id>` | ✅ | Delete artifact |

### Chat — `/api/chat/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/stream` | ✅ | SSE streaming Gemini chat response |
| `GET` | `/history/<workspace_id>` | ✅ | Chat message history |

---

## Key Design Decisions

### Single-Server Architecture
Flask serves both the API (`/api/*`) and the static frontend (everything else). This means same-origin requests — no CORS headaches in production. `js/config.js` sets `API_BASE = ''` so all API calls use relative URLs that work identically on localhost and Render.

### AI Model Fallback Chain
Gemini free tier has per-model daily quotas. Both generation and chat endpoints try models in order:
1. `gemini-2.0-flash`
2. `gemini-2.0-flash-lite`
3. `gemma-4-26b-a4b-it`
4. `gemini-2.5-flash`

If all models are quota-exhausted, a clear `429` error is returned to the user.

### Workspace Deduplication
`POST /api/workspace/create` checks if a workspace with the same `user_id + name + repo_url` was created within the last 30 seconds before inserting. Prevents duplicate workspaces from browser double-submit race conditions.

### Repository Parsing
`utils/parser.py` (`LocalParser`) walks the cloned workspace directory, respects `.gitignore` rules via `pathspec`, and extracts file content grouped by language. This context is sent to Gemini for both artifact generation and chat.

### Authentication Flow
- **Email/Password:** bcrypt hash stored, JWT returned on login
- **Google:** Frontend gets Google ID Token via GIS → sends to `/api/auth/google` → backend verifies with `google-auth` → creates/finds user in MongoDB → returns app JWT
