# Run Guide

## Backend (FastAPI)
1) Copy env and edit:
   cp expense_tracker_backend/.env.example expense_tracker_backend/.env
   - Ensure CORS_ALLOW_ORIGINS includes your frontend URL (e.g., http://localhost:3000)
   - Set COOKIE_SECURE=false for local http
2) Install and start:
   pip install -r expense_tracker_backend/requirements.txt
   uvicorn src.api.main:app --app-dir expense_tracker_backend/src --reload --host 0.0.0.0 --port 3001
3) Initialize DB (schema + seed demo data):
   python -m src.db --app-dir expense_tracker_backend/src
4) Health:
   GET http://localhost:3001/ or GET http://localhost:3001/health

## Frontend (React)
- Ensure .env in frontend project:
  REACT_APP_API_BASE_URL=http://localhost:3001
- Use credentials: 'include' for auth endpoints (login/refresh/logout) to handle httpOnly cookies.

Notes:
- All protected API calls must send Authorization: Bearer <access_token>.
- The refresh cookie is httpOnly; access token must be stored client-side with secure handling.
