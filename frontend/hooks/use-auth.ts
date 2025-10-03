// hooks/use-auth.ts
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authApi } from '../lib/api';
import { LoginRequest, ApiError, RegisterRequest, RegisterClientRequest, GetClientsRequest, Client } from '../types/api';
import { useState } from 'react';

export const useAuth = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [clients, setClients] = useState<Client[]>([]);

  const loginMutation = useMutation<
    { access_token: string; token_type: string },
    ApiError,
    LoginRequest
  >({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.access_token);
      router.push('/clients');
    },
  });

  const registerMutation = useMutation<
    { id: number; email: string; is_active: boolean },
    ApiError,
    RegisterRequest
  >({
    mutationFn: authApi.register,
    onSuccess: (data) => {
      // After successful registration, redirect to login
      router.push('/login?message=Registration successful');
    },
  });

  const registerClientMutation = useMutation<
    { name: string; email: string; is_active: boolean },
    ApiError,
    RegisterClientRequest
  >({
    mutationFn: authApi.registerClient,
    onSuccess: (data) => {
      // After successful registration, redirect to clients page
      router.push('/clients?message=Client registration successful');
    },
  });

  const clientsMutation = useMutation<
    Client[], // This should return an array of Client objects
    ApiError,
    GetClientsRequest
  >({
    mutationFn: authApi.getClients,
    onSuccess: (data) => {
      // Store the clients data in state
      setClients(data);
    },
  });

  // Alternative: You could also use useQuery for automatic fetching
  // const clientsQuery = useQuery({
  //   queryKey: ['clients'],
  //   queryFn: () => authApi.getClients({ skip: 0, limit: 100 }),
  //   enabled: isAuthenticated(), // Only fetch if authenticated
  // });

  const logout = () => {
    localStorage.removeItem('auth_token');
    queryClient.clear();
    setClients([]); // Clear clients on logout
    router.push('/login');
  };

  const isAuthenticated = () => {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem('auth_token');
  };

  return {
    login: loginMutation.mutate,
    isLoading: loginMutation.isPending,
    error: loginMutation.error,

    register: registerMutation.mutate,
    registerIsLoading: registerMutation.isPending,
    registerError: registerMutation.error,

    registerClient: registerClientMutation.mutate,
    registerClientIsLoading: registerClientMutation.isPending,
    registerClientError: registerClientMutation.error,

    // Clients mutation and data
    clientsMutation: clientsMutation.mutate,
    clientsMutationIsLoading: clientsMutation.isPending,
    clientsMutationError: clientsMutation.error,
    clients, // Return the clients data

    logout,
    isAuthenticated: isAuthenticated(),
  };
};