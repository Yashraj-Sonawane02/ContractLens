import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT authorization bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('contractlens_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authAPI = {
  register: async (fullName, email, password) => {
    const response = await api.post('/auth/register', {
      full_name: fullName,
      email,
      password,
    });
    if (response.data.access_token) {
      localStorage.setItem('contractlens_token', response.data.access_token);
      localStorage.setItem('contractlens_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('contractlens_token', response.data.access_token);
      localStorage.setItem('contractlens_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('contractlens_token');
    localStorage.removeItem('contractlens_user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('contractlens_user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

export default api;
