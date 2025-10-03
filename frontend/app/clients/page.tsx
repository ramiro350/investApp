'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '../../components/button';
import { Users, Plus, ArrowLeft, Mail, User, Activity } from 'lucide-react';
import { useAuth } from '../../hooks/use-auth';
import ProtectedRoute from '../../components/protected-route';

function ClientsContent() {
  const { 
    clientsMutation, 
    clientsMutationIsLoading, 
    clientsMutationError,
    clients // Add this to get the clients data from useAuth
  } = useAuth();

  useEffect(() => {
    // Fetch clients when component mounts
    clientsMutation();
  }, [clientsMutation]);

  const handleRetry = () => {
    clientsMutation();
  };

  if (clientsMutationIsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center mb-6">
            <Link 
              href="#" 
              className="flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>

          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading clients...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center mb-6">
          <Link 
            href="#" 
            className="flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>

        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
            <p className="text-gray-600 mt-2">
              {clients && clients.length > 0 
                ? `Managing ${clients.length} client${clients.length !== 1 ? 's' : ''}` 
                : 'Manage your clients'
              }
            </p>
          </div>
          <Link href="/clients/register">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="h-4 w-4 mr-2" />
              Add Client
            </Button>
          </Link>
        </div>

        {clientsMutationError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="text-red-800 text-sm">{clientsMutationError.message}</span>
              </div>
              <Button 
                onClick={handleRetry}
                variant="outline" 
                size="sm"
                className="border-red-300 text-red-700 hover:bg-red-100"
              >
                Retry
              </Button>
            </div>
          </div>
        )}

        {/* Show clients data if we have it, otherwise show empty state */}
        {clients && clients.length > 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h3 className="text-lg font-medium text-gray-900">Your Clients</h3>
            </div>
            
            <div className="divide-y divide-gray-200">
              {clients.map((client) => (
                <div key={client.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-gray-400" />
                          <h4 className="text-lg font-medium text-gray-900">{client.name}</h4>
                        </div>
                        
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          client.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          <Activity className="h-3 w-3 mr-1" />
                          {client.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2 text-gray-600">
                        <Mail className="h-4 w-4" />
                        <span className="text-sm">{client.email}</span>
                      </div>
                      
                      <div className="mt-2">
                        <span className="text-xs text-gray-500">
                          Created: {new Date(client.created_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          })}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Client Statistics */}
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span>Total: {clients.length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-green-500" />
                  <span>Active: {clients.filter(client => client.is_active).length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-gray-400" />
                  <span>Inactive: {clients.filter(client => !client.is_active).length}</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No clients yet</h3>
            <p className="text-gray-600 mb-4">Get started by registering your first client.</p>
            <Link href="/clients/register">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                Register First Client
              </Button>
            </Link>
          </div>
        )}

        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Client Management</h3>
          <p className="text-blue-700 text-sm">
            Welcome back! You can register new clients and manage existing ones from this dashboard.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function ClientsPage() {
  return (
    <ProtectedRoute>
      <ClientsContent />
    </ProtectedRoute>
  );
}