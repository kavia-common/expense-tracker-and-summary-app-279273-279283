# expense-tracker-and-summary-app-279273-279283

## Backend setup (FastAPI)

1. Environment
   - Copy `expense_tracker_backend/.env.example` to `expense_tracker_backend/.env`
   - Set at minimum:
     - SECRET_KEY
     - CORS_ALLOW_ORIGINS to include your frontend URL (e.g., http://localhost:3000)
     - COOKIE_SECURE=false for local http, true for production https
     - DATABASE_URL (optional; defaults to SQLite file)
   - SQLite default: `sqlite:///./data/expense_tracker.db`
   - For Postgres: `postgresql+psycopg2://USER:PASS@HOST:5432/DB`

2. Install and run API
   - `pip install -r expense_tracker_backend/requirements.txt`
   - Run API (port 3001):
     - `uvicorn src.api.main:app --app-dir expense_tracker_backend/src --reload --host 0.0.0.0 --port 3001`
   - Health endpoints:
     - `GET /` returns `{ "message": "Healthy" }`
     - `GET /health` returns `{ "status": "ok" }`

3. Initialize the database (schema + seed)
   - From repo root:
     - `python -m src.db --app-dir expense_tracker_backend/src`
   - Or from backend src dir:
     - `PYTHONPATH=. python -m src.db`
   - Notes:
     - The initializer creates tables and inserts demo data (demo user + sample categories/transactions).
     - Safe to run multiple times (idempotent seed).

4. OpenAPI docs
   - Visit `/docs` on the backend URL.

### Auth quickstart
- Register: `POST /auth/register` { email, password, name? }
- Login: `POST /auth/login` { email, password }
  - Response includes access token; a refresh token is set as httpOnly cookie.
  - Set `fetch(..., { credentials: 'include' })` on the frontend to send/receive cookies.
- Refresh: `POST /auth/refresh` (uses refresh cookie) -> new access token (refresh cookie rotated)
- Logout: `POST /auth/logout` (clears refresh cookie)
- Protected endpoints require header: `Authorization: Bearer <access_token>`

### CORS and Cookies
- CORS is configured via environment:
  - `CORS_ALLOW_ORIGINS=http://localhost:3000` for local React app
  - `CORS_ALLOW_CREDENTIALS=true` to allow cookies
- Ensure frontend requests that need cookies use `credentials: 'include'`.

## Frontend integration quick notes
- Frontend should read API base from `REACT_APP_API_BASE_URL` (e.g., `http://localhost:3001`).
- Use this base for all API calls.
- For endpoints that set/read the refresh cookie (login/refresh/logout), use `credentials: 'include'` in fetch/axios.