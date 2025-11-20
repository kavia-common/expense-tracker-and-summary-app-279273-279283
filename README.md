# expense-tracker-and-summary-app-279273-279283

## Backend setup (FastAPI)

1. Create your environment file:
   - Copy `expense_tracker_backend/.env.example` to `expense_tracker_backend/.env`
   - Required keys:
     - SECRET_KEY, DATABASE_URL (optional if using default SQLite), ACCESS_TOKEN_EXPIRES_MIN, REFRESH_TOKEN_EXPIRES_DAYS
     - CORS_ORIGINS via `CORS_ALLOW_ORIGINS`
   - By default, SQLite is used at `./data/expense_tracker.db`. To use Postgres, set `DATABASE_URL` accordingly (e.g., `postgresql+psycopg2://USER:PASS@HOST:5432/DB`).

2. Install dependencies and run the API:
   - `pip install -r expense_tracker_backend/requirements.txt`
   - `uvicorn src.api.main:app --app-dir expense_tracker_backend/src --reload --host 0.0.0.0 --port 3001`

3. Initialize the database (schema + seed):
   - `python -m src.db --app-dir expense_tracker_backend/src`
   - Or from the backend src dir: `PYTHONPATH=. python -m src.db`

4. OpenAPI docs:
   - Visit `/docs` on the backend URL.

### Auth quickstart
- Register: POST /auth/register {email, password, name?}
- Login: POST /auth/login {email, password}
  - Response includes access token; a refresh token is set as httpOnly cookie.
- Refresh: POST /auth/refresh (uses refresh cookie) -> new access token (refresh cookie rotated)
- Logout: POST /auth/logout (clears refresh cookie)

Send requests with `Authorization: Bearer <access_token>` header to protected endpoints.