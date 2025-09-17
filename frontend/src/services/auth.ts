// API service for authentication
const API_BASE_URL = 'http://localhost:8000';

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password1: string;
  password2: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: {
    pk: number;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export interface AuthError {
  [key: string]: string[];
}

class AuthService {
  async login(data: LoginData): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    const result = await response.json();
    
    // Store tokens in localStorage - handle both formats
    const accessToken = result.access_token || result.access;
    const refreshToken = result.refresh_token || result.refresh;
    
    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
    }
    
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }

    return result;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/registration/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    const result = await response.json();
    
    // Store tokens in localStorage - handle both formats
    const accessToken = result.access_token || result.access;
    const refreshToken = result.refresh_token || result.refresh;
    
    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
    }
    
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }

    return result;
  }

  async logout(): Promise<void> {
    const token = localStorage.getItem('access_token');
    
    try {
      await fetch(`${API_BASE_URL}/auth/logout/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  async getCurrentUser() {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE_URL}/auth/user/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return response.json();
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

export const authService = new AuthService();
