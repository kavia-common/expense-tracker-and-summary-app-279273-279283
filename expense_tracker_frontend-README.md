# Frontend integration notes

- Create `.env` in the frontend project with:
  - `REACT_APP_API_BASE_URL=http://localhost:3001`
- Use this base URL for all HTTP requests to the backend.
- For auth-related endpoints that rely on httpOnly cookies (login, refresh, logout), use:
  - `credentials: 'include'` in fetch/axios to send and receive cookies.
- Send `Authorization: Bearer <access_token>` for protected endpoints (categories, transactions, reports, users/me).

Example fetch:
```js
const API = process.env.REACT_APP_API_BASE_URL;

async function login(email, password) {
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // required for refresh cookie
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json();
}
```
