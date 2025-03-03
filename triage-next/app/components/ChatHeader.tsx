'use client';

import { useState } from 'react';

interface ChatHeaderProps {
    isDarkMode: boolean;
    setIsDarkMode: (value: boolean) => void;
    isAdminView: boolean;
    onViewChange: (value: boolean) => void;
    user: { username: string; role: string } | null;
    onLogout: () => void;
}

export const ChatHeader = ({
    isDarkMode,
    setIsDarkMode,
    isAdminView,
    onViewChange,
    user,
    onLogout
}: ChatHeaderProps) => {
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleAdminAccess = () => {
        if (password === '2025') {
            setShowPasswordModal(false);
            onViewChange(true);
            setError('');
            setPassword('');
        } else {
            setError('Incorrect password');
        }
    };

    return (
        <header className="chat-header">
            <div className="header-buttons flex justify-between items-center p-4">
                <div className="flex items-center gap-4">
                    {user && (
                        <div className="text-sm">
                            Logged in as: {user.username} ({user.role})
                        </div>
                    )}
                    <button
                        onClick={() => setIsDarkMode(!isDarkMode)}
                        className="p-2 rounded-full hover:bg-gray-200"
                    >
                        {isDarkMode ? '☀️' : '🌙'}
                    </button>
                    {user?.role === 'Physician' && (
                        <button
                            onClick={() => onViewChange(!isAdminView)}
                            className="px-3 py-1 rounded-lg bg-blue-100 text-blue-800 hover:bg-blue-200"
                        >
                            {isAdminView ? 'Chat View' : 'Admin View'}
                        </button>
                    )}
                    <button
                        onClick={onLogout}
                        className="px-3 py-1 rounded-lg bg-red-100 text-red-800 hover:bg-red-200"
                    >
                        Logout
                    </button>
                </div>
            </div>
            <h1 className="text-center text-3xl font-bold">Triage</h1>

            {showPasswordModal && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
                    <div className={`w-80 ${
                        isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
                    } p-6 rounded-lg shadow-lg`}>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-semibold">Admin Access</h2>
                            <button
                                className="text-gray-500 dark:text-gray-300 text-2xl leading-none"
                                onClick={() => {
                                    setShowPasswordModal(false);
                                    setPassword('');
                                    setError('');
                                }}
                            >
                                &times;
                            </button>
                        </div>
                        <div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter admin password"
                                className={`w-full p-2 mb-2 border rounded-md focus:outline-none focus:ring ${
                                    isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
                                }`}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        handleAdminAccess();
                                    }
                                }}
                            />
                            {error && <p className="text-red-500 mb-2">{error}</p>}
                            <button
                                className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
                                onClick={handleAdminAccess}
                            >
                                Login
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
};