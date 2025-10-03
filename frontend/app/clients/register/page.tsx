'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../../../hooks/use-auth';
import { ClientSchema, ClientFormData } from '../../../lib/validation';
import { Button } from '../../../components/button';
import { Input } from '../../../components/input';
import { Label } from '../../../components/label';
import { Checkbox } from '../../../components/ui/checkbox';
import { AlertCircle, ArrowLeft, UserPlus } from 'lucide-react';
import Link from 'next/link';
import ProtectedRoute from '../../../components/protected-route';

export default function ClientRegisterPage() {
  const { registerClient, registerClientIsLoading, registerClientError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ClientFormData>({
    resolver: zodResolver(ClientSchema),
    defaultValues: {
      is_active: true,
    },
  });

  const onSubmit = (data: ClientFormData) => {
    registerClient(data);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
        <div className="w-full max-w-md bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Link 
              href="/clients" 
              className="flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Clients
            </Link>
          </div>

          <div className="text-center mb-6">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
              <UserPlus className="h-6 w-6 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Register New Client</h2>
            <p className="text-sm text-gray-600 mt-2">
              Add a new client to your system
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            {registerClientError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-red-800 text-sm">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span>{registerClientError.detail || 'Error creating client'}</span>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-sm font-medium text-gray-900">
                  Client Name
                </Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter client name"
                  required
                  {...register('name')}
                  className={`mt-1 w-full ${errors.name ? 'border-red-500' : 'border-gray-300'}`}
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="email" className="text-sm font-medium text-gray-900">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="client@example.com"
                  required
                  {...register('email')}
                  className={`mt-1 w-full ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  {...register('is_active')}
                />
                <Label
                  htmlFor="is_active"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Activate client immediately
                </Label>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                disabled={registerClientIsLoading}
              >
                {registerClientIsLoading ? 'Creating client...' : 'Create client'}
              </Button>
            </div>

            <div className="mt-6 text-center text-sm text-gray-600">
              Back to{" "}
              <Link href="/clients" className="text-blue-600 hover:text-blue-500 underline">
                Clients list
              </Link>
            </div>
          </form>
        </div>
      </div>
    </ProtectedRoute>
  );
}