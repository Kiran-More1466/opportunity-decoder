# Opportunity Decoder

Opportunity Decoder helps students organize a job or internship listing, compare its stated requirements with their profile, and prepare focused next steps. The frontend is React + Vite; the API is FastAPI and uses Gemini for real analysis. The API validates Gemini's structured response with Pydantic before returning it.

## Features

- Evidence-grounded mandatory and preferred requirement assessments (`Met`, `Not met`, or `Unknown`).
- Demonstrated skills, potential skill gaps, prioritized preparation actions, and details to clarify.
- Optional daily preparation time for a bounded seven-day plan.
- Safe provider error handling. The Gemini key is read by the backend only.

## Project structure

```text
.
├── backend/
│   ├── app/                 # FastAPI app, route, settings, schemas, Gemini service
│   └── tests/               # API tests and mocked personalization tests
├── src/
│   ├── components/          # Shared React components
│   ├── pages/               # Landing and opportunity-input pages
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── package.json             # Frontend scripts and dependencies
├── package-lock.json        # Reproducible npm dependency tree
├── requirements.txt         # Backend runtime dependencies
├── requirements-dev.txt     # Backend test dependency
├── .env.example
├── render.yaml              # Render API service configuration
└── vercel.json              # Vercel SPA route fallback
```

## Requirements

- Node.js `^20.19.0` or `>=22.12.0`.
- Python 3.12.14 available as `python` on your PATH (also recorded in `.python-version`).
- A Gemini API key for real analysis. Never put it in a `VITE_` variable or Vercel settings.

## Local setup (Windows PowerShell)

From the repository root:

```powershell
npm ci
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` and set `GEMINI_API_KEY`. Keep `.env` private; Git ignores it. `VITE_API_BASE_URL` is blank locally, so the browser uses a relative `/api` URL and Vite proxies it to the local backend. `API_PROXY_TARGET` can override the Vite development proxy target if needed.

Start the API in one PowerShell window:

```powershell
Set-Location -LiteralPath '<repository-root>'
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in a second window:

```powershell
Set-Location -LiteralPath '<repository-root>'
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). The Vite proxy is development-only. The browser sends `POST /api/analyze`; the FastAPI server calls Gemini using the server-side `GEMINI_API_KEY`. `GET /health` is available for service checks.

## Environment variables

| Variable | Used by | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | FastAPI only | Secret key for the Gemini API. |
| `GEMINI_MODEL` | FastAPI only | Gemini model; defaults to `gemini-3.8-flash`. |
| `GEMINI_HTTP_TIMEOUT_SECONDS` | FastAPI only | Gemini HTTP request timeout; defaults to 55 seconds. |
| `GEMINI_TIMEOUT_SECONDS` | FastAPI only | Overall analysis timeout; defaults to 60 seconds. |
| `FRONTEND_ORIGINS` | FastAPI only | Comma-separated browser origins allowed by CORS. Set this to the deployed Vercel origin(s) in production. |
| `VITE_API_BASE_URL` | Vite build | Public API origin, with no trailing slash (for example `https://<service>.onrender.com`). Leave blank for local Vite proxy use. This is an API URL, never a secret. |
| `API_PROXY_TARGET` | Vite dev server only | Optional local backend proxy target; defaults to `http://127.0.0.1:8000`. |

## API

- `GET /health` returns `{"status":"ok"}`.
- `POST /api/analyze` accepts the opportunity description and student profile. Optional fields include company, source URL, graduation year, projects/experience, and daily preparation time.
- The response schema is defined in `backend/app/schemas.py`. Provider output is validated before the API returns it. The source URL is metadata; the server does not fetch it.
- Interactive API docs are available at `/docs` while FastAPI is running.

## Tests and production build

Run backend tests (Gemini is mocked in tests):

```powershell
python -m pytest backend/tests -q
```

Create the frontend production bundle:

```powershell
npm run build
```

No frontend lint or type-check script is configured; the frontend is JavaScript/JSX, not TypeScript.

## Deploy the frontend to Vercel

1. Import the GitHub repository into Vercel and select the repository root as the project root.
2. Use the Vite defaults: install `npm ci`, build `npm run build`, output directory `dist`.
3. Set `VITE_API_BASE_URL` in the Vercel project environment to the Render API's HTTPS origin, for example `https://<service-name>.onrender.com` (no trailing slash). Redeploy after changing it because Vite embeds this public setting at build time.
4. Do not add `GEMINI_API_KEY` to Vercel. It belongs only in the Render backend environment.

`vercel.json` rewrites deep links such as `/analyze` to the SPA entry point on page refresh. This configuration follows [Vercel's Vite SPA guidance](https://vercel.com/docs/frameworks/frontend/vite).

## Deploy the backend to Render

The included `render.yaml` defines a Python web service with:

- Build command: `pip install -r requirements.txt`.
- Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
- Health check path: `/health`.
- Python version: 3.12.14.

Create the Render service from the repository Blueprint. In the Render dashboard, provide the prompted secret `GEMINI_API_KEY` and set `FRONTEND_ORIGINS` to the exact production Vercel origin(s), comma-separated if needed. Keep the local localhost origins only for development. Render supplies the service port through `$PORT`; do not hardcode the local development port for deployment. See [Render's Python version configuration](https://render.com/docs/python-version) and [web service setup](https://render.com/docs/web-services).

## Security and repository hygiene

- `.env`, `.env.*` (except `.env.example`), credentials, virtual environments, caches, logs, `node_modules/`, `dist/`, and local editor artifacts are ignored by Git.
- `.env.example` contains placeholders only.
- Only the backend reads `GEMINI_API_KEY`; no key is exposed to the browser bundle.
- Before deploying, rotate any API key previously shared in chat or another public place, then set the replacement only in Render's secret environment settings.
