// app/register/page.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../../hooks/use-auth';
import { registerSchema, RegisterFormData } from '../../lib/validation';
import { Button } from '../../components/button';
import { Input } from '../../components/input';
import { Label } from '../../components/label';
import { Checkbox } from '../../components/ui/checkbox';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function RegisterPage() {
  const { register: registerUser, registerIsLoading, registerError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      is_active: true,
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    // Remove confirmPassword before sending to API
    const { confirmPassword, ...userData } = data;
    registerUser(userData);
  };

  const password = watch('password');

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-6">
          <Link 
            href="/login" 
            className="flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to login
          </Link>
        </div>

        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Create your account</h2>
          <p className="text-sm text-gray-600 mt-2">
            Enter your details to create a new account
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {registerError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-red-800 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{registerError.detail || 'Erro ao criar conta'}</span>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-sm font-medium text-gray-900">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                required
                {...register('email')}
                className={`mt-1 w-full ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="password" className="text-sm font-medium text-gray-900">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                required
                {...register('password')}
                className={`mt-1 w-full ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
              {password && !errors.password && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-gray-600">A senha deve conter:</p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    <li className={`flex items-center ${password.length >= 6 ? 'text-green-600' : ''}`}>
                      {password.length >= 6 ? '✓' : '•'} Pelo menos 6 caracteres
                    </li>
                    <li className={`flex items-center ${/(?=.*[a-z])/.test(password) ? 'text-green-600' : ''}`}>
                      {/(?=.*[a-z])/.test(password) ? '✓' : '•'} Uma letra minúscula
                    </li>
                    <li className={`flex items-center ${/(?=.*[A-Z])/.test(password) ? 'text-green-600' : ''}`}>
                      {/(?=.*[A-Z])/.test(password) ? '✓' : '•'} Uma letra maiúscula
                    </li>
                    <li className={`flex items-center ${/(?=.*\d)/.test(password) ? 'text-green-600' : ''}`}>
                      {/(?=.*\d)/.test(password) ? '✓' : '•'} Um número
                    </li>
                  </ul>
                </div>
              )}
            </div>

            <div>
              <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-900">
                Confirm Password
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                required
                {...register('confirmPassword')}
                className={`mt-1 w-full ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
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
                Activate account immediately
              </Label>
            </div>

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={registerIsLoading}
            >
              {registerIsLoading ? 'Creating account...' : 'Create account'}
            </Button>
          </div>

          <div className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{" "}
            <Link href="/login" className="text-blue-600 hover:text-blue-500 underline">
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}