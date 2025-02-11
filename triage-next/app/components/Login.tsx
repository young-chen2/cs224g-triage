'use client';

import { useState } from 'react';

interface LoginProps {
  onLogin: (username: string, password: string) => void;
  onPatientAccess: () => void;
}

export const Login = ({ onLogin, onPatientAccess }: LoginProps) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }
    onLogin(username, password);
    setError('Invalid username or password');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0f172a] to-[#1e293b]">
      <div className="max-w-md w-full space-y-8 p-8 bg-white/5 backdrop-blur-lg rounded-xl shadow-lg border border-white/10">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Triage
          </h2>
          <p className="mt-2 text-center text-sm text-gray-300">
            Please sign in to continue or continue as a patient
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none rounded-lg relative block w-full px-3 py-2 bg-white/10 border border-white/20 placeholder-gray-400 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Username (e.g., doctor1, nurse1, pa1)"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
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
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Sign in as Staff
            </button>
            
            <button
              type="button"
              onClick={onPatientAccess}
              className="group relative w-full flex justify-center py-2 px-4 border border-green-500 text-sm font-medium rounded-md text-green-400 bg-transparent hover:bg-green-500/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Continue as Patient
            </button>
          </div>
        </form>
        
        <div className="mt-4 text-sm text-gray-300">
          <p className="font-semibold">Available staff accounts:</p>
          <ul className="list-disc list-inside">
            <li>doctor1 - Physician</li>
            <li>nurse1 - Nurse</li>
            <li>pa1 - PA</li>
            <li>Password for all: password123</li>
          </ul>
        </div>
      </div>
    </div>
  );
}; 