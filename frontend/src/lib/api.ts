import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// attach JWT on every request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// redirect to /login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  },
);

/* ── helper to send form-urlencoded login (OAuth2 spec) ── */

export async function loginRequest(email: string, password: string) {
  const form = new URLSearchParams();
  form.set('username', email);
  form.set('password', password);

  const res = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return res.data as { access_token: string; token_type: string };
}

/* ── AI task poller ── */

export async function pollTaskUntilDone(taskId: string, intervalMs = 1500, maxPolls = 30) {
  for (let i = 0; i < maxPolls; i++) {
    await new Promise((r) => setTimeout(r, intervalMs));
    const res = await api.get(`/ai/tasks/${taskId}`);
    const data = res.data as { status: string; result?: unknown };
    if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
      return data;
    }
  }
  return { status: 'TIMEOUT', result: null };
}
