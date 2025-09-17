import React, { useState, useEffect } from 'react';
import { authService } from '../services/auth';

interface DashboardProps {
  onLogout: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await authService.getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error('Error loading user:', error);
        onLogout();
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [onLogout]);

  const handleLogout = async () => {
    try {
      await authService.logout();
      onLogout();
    } catch (error) {
      console.error('Logout error:', error);
      onLogout();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                AFP V2 - Personal Finance
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                Welcome, {user?.email || 'User'}
              </span>
              <button
                onClick={handleLogout}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to your Dashboard!
              </h2>
              
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">User Information</h3>
                <div className="space-y-2 text-left">
                  <p><strong>Email:</strong> {user?.email}</p>
                  <p><strong>User ID:</strong> {user?.pk}</p>
                  <p><strong>First Name:</strong> {user?.first_name || 'Not set'}</p>
                  <p><strong>Last Name:</strong> {user?.last_name || 'Not set'}</p>
                  <p><strong>Staff Status:</strong> {user?.is_staff ? 'Yes' : 'No'}</p>
                  <p><strong>Joined:</strong> {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'Unknown'}</p>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-blue-900 mb-2">
                  🎉 Authentication Working!
                </h3>
                <p className="text-blue-700">
                  You have successfully logged in with JWT authentication. 
                  Next step: Connect your email accounts for transaction processing.
                </p>
              </div>

              <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-100 rounded-lg p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Email Connections</h4>
                  <p className="text-gray-600 text-sm mb-4">Connect your Gmail or Outlook accounts</p>
                  <button className="bg-gray-300 text-gray-500 px-4 py-2 rounded-md text-sm cursor-not-allowed">
                    Coming Soon
                  </button>
                </div>
                
                <div className="bg-gray-100 rounded-lg p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Transactions</h4>
                  <p className="text-gray-600 text-sm mb-4">View your processed transactions</p>
                  <button className="bg-gray-300 text-gray-500 px-4 py-2 rounded-md text-sm cursor-not-allowed">
                    Coming Soon
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
