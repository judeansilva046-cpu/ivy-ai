import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

interface AuthResponse {
  user: User;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  };
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

class AuthService {
  private apiClient: AxiosInstance;

  constructor() {
    this.apiClient = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.apiClient.interceptors.request.use((config) => {
      const token = this.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token refresh on 401
    this.apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          try {
            await this.refreshToken();
            return this.apiClient(error.config);
          } catch {
            this.logout();
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  private setTokens(accessToken: string, refreshToken: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  // Auth endpoints
  async register(email: string, username: string, password: string, fullName?: string): Promise<AuthResponse> {
    const response = await this.apiClient.post<AuthResponse>('/auth/register', {
      email,
      username,
      password,
      full_name: fullName,
    });

    this.setTokens(
      response.data.tokens.access_token,
      response.data.tokens.refresh_token
    );

    return response.data;
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await this.apiClient.post<AuthResponse>('/auth/login', {
      username,
      password,
    });

    this.setTokens(
      response.data.tokens.access_token,
      response.data.tokens.refresh_token
    );

    return response.data;
  }

  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    this.setTokens(
      response.data.access_token,
      response.data.refresh_token
    );

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.apiClient.get<User>('/auth/me');
    return response.data;
  }

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }
}

export const authService = new AuthService();
