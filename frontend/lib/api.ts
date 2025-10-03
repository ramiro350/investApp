// lib/api.ts
import axios from 'axios';
import { LoginRequest, LoginResponse, ApiError, RegisterRequest, RegisterClientRequest, GetClientsRequest } from '../types/api';
import { User, Client } from '../types/api'; 

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  },

  registerClient: async (clientData: RegisterClientRequest): Promise<Client> => {
    console.log(clientData)
    const response = await api.post<Client>('/clients', clientData);
    return response.data;
  },

  getClients: async (clientData: GetClientsRequest): Promise<Client> => {
    const response = await api.get<Client>('/clients', clientData);
    return response.data;
  }
};