// types/api.ts
export interface User {
  id: number;
  email: string;
  password: string;
  is_active: boolean;
}

export interface Client {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  is_active?: boolean;
}

export interface RegisterClientRequest {
  name: string;
  email: string;
  is_active?: boolean;
}

export interface GetClientsRequest {
  skip: number;
  limit: number;
}