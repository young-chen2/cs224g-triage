'use client';

import { useState } from 'react';
import config from '../config';

interface LoginProps {
  onLogin: (user: { username: string, role: string, id: string }) => void;
  onPatientAccess: () => void;
}

export const Login = ({ onLogin, onPatientAccess }: LoginProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const [role, setRole] = useState('physician');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (!email || !password) {
      setError('Please enter both email and password');
      setIsLoading(false);
      return;
    }

    try {
      // Login via backend instead of directly to Supabase
      const response = await fetch(`${config.api.baseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      if (data.user) {
        // Get provider details
        const providerResponse = await fetch(`${config.api.baseUrl}/providers/by-user-id/${data.user.id}`);
        
        if (!providerResponse.ok) {
          throw new Error('Failed to get provider details');
        }
        
        const providerData = await providerResponse.json();
        
        // Login successful
        onLogin({
          username: providerData.name,
          role: providerData.role,
          id: providerData.id
        });
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (!email || !password || !name || !role) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    try {
      // Register via backend
      const response = await fetch(`${config.api.baseUrl}/auth/providers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email, 
          password,
          name,
          role 
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      // Registration successful, now login
      setIsRegistering(false);
      setIsLoading(false);
      setError('');
      alert('Account created successfully! You can now log in.');

    } catch (error) {
      console.error('Registration error:', error);
      setError('Registration failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0f172a] to-[#1e293b]">
      <div className="max-w-md w-full space-y-8 p-8 bg-white/5 backdrop-blur-lg rounded-xl shadow-lg border border-white/10">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Triage
          </h2>
          <p className="mt-2 text-center text-sm text-gray-300">
            {isRegistering 
              ? 'Create a new provider account' 
              : 'Please sign in to continue or continue as a patient'}
          </p>
        </div>
        
        {isRegistering ? (
          // Registration form
          <form className="mt-8 space-y-6" onSubmit={handleRegister}>
            <div className="rounded-md shadow-sm space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-1">
                  Full Name
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="reg-email" className="block text-sm font-medium text-gray-300 mb-1">
                  Email Address
                </label>
                <input
                  id="reg-email"
                  name="email"
                  type="email"
                  required
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="reg-password" className="block text-sm font-medium text-gray-300 mb-1">
                  Password
                </label>
                <input
                  id="reg-password"
                  name="password"
                  type="password"
                  required
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-300 mb-1">
                  Role
                </label>
                <select
                  id="role"
                  name="role"
                  required
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="patient">Patient</option>
                  <option value="physician">Physician</option>
                  <option value="nurse">Nurse</option>
                  <option value="pa">Physician Assistant</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            <div className="space-y-3">
              <button
                type="submit"
                disabled={isLoading}
                className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </button>
              
              <button
                type="button"
                onClick={() => setIsRegistering(false)}
                disabled={isLoading}
                className="group relative w-full flex justify-center py-2 px-4 border border-blue-500 text-sm font-medium rounded-md text-blue-400 bg-transparent hover:bg-blue-500/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Back to Login
              </button>
            </div>
          </form>
        ) : (
          // Login form
          <form className="mt-8 space-y-6" onSubmit={handleLogin}>
            <div className="rounded-md shadow-sm space-y-4">
              <div>
                <label htmlFor="email" className="sr-only">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            <div className="space-y-3">
              <button
                type="submit"
                disabled={isLoading}
                className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
              >
                {isLoading ? 'Signing in...' : 'Sign in 🔑'}
              </button>
              
              <button
                type="button"
                onClick={() => setIsRegistering(true)}
                className="group relative w-full flex justify-center py-2 px-4 border border-purple-500 text-sm font-medium rounded-md text-purple-400 bg-transparent hover:bg-purple-500/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                Register
              </button>
              
              <button
                type="button"
                onClick={onPatientAccess}
                disabled={isLoading}
                className="group relative w-full flex justify-center py-2 px-4 border border-green-500 text-sm font-medium rounded-md text-green-400 bg-transparent hover:bg-green-500/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Continue as Guest Patient
              </button>
            </div>
          </form>
        )}
        
        <div className="mt-4 text-sm text-gray-300">
          <p className="font-semibold">Test accounts:</p>
          <ul className="list-disc list-inside">
            <li>doctor@example.com - Physician</li>
            <li>nurse@example.com - Nurse</li>
            <li>pa@example.com - PA</li>
            <li>patient1@example.com - Patient</li>
            <li>Password for all: password123</li>
          </ul>
        </div>
      </div>
    </div>
  );
};