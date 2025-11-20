# expense-tracker-and-summary-app-279273-279283

## Backend setup (FastAPI)

1. Create your environment file:
   - Copy `expense_tracker_backend/.env.example` to `expense_tracker_backend/.env`
   - By default, SQLite is used at `./data/expense_tracker.db`. To use Postgres, set `DATABASE_URL` accordingly (e.g., `postgresql+psycopg2://USER:PASS@HOST:5432/DB`).

2. Install dependencies and run the API:
   - `pip install -r expense_tracker_backend/requirements.txt`
   - `uvicorn src.api.main:app --app-dir expense_tracker_backend/src --reload --host 0.0.0.0 --port 3001`

3. Initialize the database (schema + seed):
   - `python -m src.db --app-dir expense_tracker_backend/src`
   - Or from the backend src dir: `PYTHONPATH=. python -m src.db`

4. OpenAPI docs:
   - Visit `/docs` on the backend URL.