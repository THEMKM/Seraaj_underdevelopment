export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}

export interface Opportunity {
  id: string;
  title: string;
  description: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

let token: string | null = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

function buildHeaders(hasBody = false): HeadersInit {
  const headers: HeadersInit = {};
  if (hasBody) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(res: Response): Promise<ApiResponse<T>> {
  let payload: any = null;
  try {
    payload = await res.json();
  } catch {}
  if (!res.ok) {
    const message = payload?.detail || payload?.message || res.statusText;
    return { success: false, error: message };
  }
  return { success: true, data: payload };
}

export const auth = {
  isAuthenticated(): boolean {
    return !!token;
  },
  async login(credentials: LoginCredentials): Promise<ApiResponse<{access_token: string}>> {
    const res = await fetch(`${API_BASE_URL}/v1/auth/login`, {
      method: 'POST',
      headers: buildHeaders(true),
      body: JSON.stringify(credentials),
    });
    const result = await handleResponse<{access_token: string}>(res);
    if (result.success && result.data?.access_token) {
      token = result.data.access_token;
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', token);
      }
    }
    return result;
  },
  async register(data: RegisterData): Promise<ApiResponse<any>> {
    const res = await fetch(`${API_BASE_URL}/v1/auth/register`, {
      method: 'POST',
      headers: buildHeaders(true),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  async logout(): Promise<ApiResponse<any>> {
    const res = await fetch(`${API_BASE_URL}/v1/auth/logout`, {
      method: 'POST',
      headers: buildHeaders(),
    });
    const result = await handleResponse(res);
    token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
    return result;
  },
  async getCurrentUser(): Promise<ApiResponse<User>> {
    const res = await fetch(`${API_BASE_URL}/v1/auth/me`, {
      headers: buildHeaders(),
    });
    return handleResponse<User>(res);
  },
};

export const opportunities = {
  async getAll(params: Record<string, any> = {}): Promise<ApiResponse<Opportunity[]>> {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`${API_BASE_URL}/v1/opportunities/${query ? `?${query}` : ''}`, {
      headers: buildHeaders(),
    });
    return handleResponse<Opportunity[]>(res);
  },
  async apply(id: string): Promise<ApiResponse<any>> {
    const res = await fetch(`${API_BASE_URL}/v1/opportunities/${id}/apply`, {
      method: 'POST',
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },
};
