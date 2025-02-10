'use client';

import { useState } from 'react';

interface ChatHeaderProps {
    isDarkMode: boolean;
    setIsDarkMode: (value: boolean) => void;
    isAdminView: boolean;
    onViewChange: (isAdmin: boolean) => void;
}

export const ChatHeader = ({ isDarkMode, setIsDarkMode, isAdminView, onViewChange }: ChatHeaderProps) => {
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleViewChange = () => {
        if (!isAdminView) {
            setShowPasswordModal(true);
        } else {
            onViewChange(false);
        }
    };

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
            <div className="header-buttons">
                <button
                    onClick={handleViewChange}
                    className={`view-toggle ${isDarkMode ? 'dark' : 'light'}`}
                >
                    {isAdminView ? '👨‍⚕️ Admin' : '🏥 Patient'}
                </button>
                <button
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className="theme-toggle"
                    aria-label="Toggle theme"
                >
                    {isDarkMode ? '☀️' : '🌙'}
                </button>
            </div>
            <h1>Triage</h1>

            {
                showPasswordModal && (
                    <div className="modal-overlay">
                        <div className={`modal-container ${isDarkMode ? 'dark' : 'light'}`}>
                            <div className="modal-header">
                                <h2>Admin Access</h2>
                                <button
                                    className="close-btn"
                                    onClick={() => {
                                        setShowPasswordModal(false);
                                        setPassword('');
                                        setError('');
                                    }}
                                >
                                    ×
                                </button>
                            </div>
                            <div className="modal-body">
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter admin password"
                                    className="password-input"
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                            handleAdminAccess();
                                        }
                                    }}
                                />
                                {error && <p className="error-message">{error}</p>}
                                <button
                                    className="submit-btn"
                                    onClick={handleAdminAccess}
                                >
                                    Login
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </header >
    );
};