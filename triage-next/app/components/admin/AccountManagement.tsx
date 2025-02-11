'use client';

import { useState } from 'react';

interface Account {
    username: string;
    role: string;
    password: string;
}

interface Props {
    isDarkMode: boolean;
    accountList: Account[];
    setAccountList: (accounts: Account[]) => void;
}

export const AccountManagement = ({ isDarkMode, accountList, setAccountList }: Props) => {
    const [newUsername, setNewUsername] = useState('');
    const [newRole, setNewRole] = useState('Physician');
    const [newPassword, setNewPassword] = useState('');

    const handleCreateAccount = () => {
        if (!newUsername || !newPassword) return;
        const newAccount: Account = {
            username: newUsername,
            role: newRole,
            password: newPassword,
        };
        setAccountList([...accountList, newAccount]);
        setNewUsername('');
        setNewRole('Physician');
        setNewPassword('');
    };

    return (
        <div className={`${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} rounded-xl shadow-md p-6`}>
            <div className="flex items-center gap-2 mb-4">
                <span className="text-blue-600 font-bold text-2xl">👤</span>
                <h2 className="text-xl font-semibold">Manage Accounts</h2>
            </div>

            <div className="mb-6">
                <h3 className="font-medium mb-2">Existing Accounts:</h3>
                <ul className="list-disc list-inside">
                    {accountList.map((acc, index) => (
                        <li key={index} className="text-sm">
                            {acc.username} - {acc.role}
                        </li>
                    ))}
                </ul>
            </div>

            <div className="space-y-4">
                <h3 className="font-medium">Create New Account</h3>
                <div className="flex flex-col gap-2">
                    <label className="text-sm">
                        Username:
                        <input
                            type="text"
                            value={newUsername}
                            onChange={(e) => setNewUsername(e.target.value)}
                            className={`w-full p-2 border rounded-md focus:outline-none focus:ring ${
                                isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
                            }`}
                            placeholder="Enter username"
                        />
                    </label>
                    <label className="text-sm">
                        Role:
                        <select
                            value={newRole}
                            onChange={(e) => setNewRole(e.target.value)}
                            className={`w-full p-2 border rounded-md focus:outline-none focus:ring ${
                                isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
                            }`}
                        >
                            <option value="Physician">Physician</option>
                            <option value="PA">PA</option>
                            <option value="Nurse">Nurse</option>
                            <option value="ER">ER</option>
                        </select>
                    </label>
                    <label className="text-sm">
                        Password:
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            className={`w-full p-2 border rounded-md focus:outline-none focus:ring ${
                                isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
                            }`}
                            placeholder="Enter password"
                        />
                    </label>
                </div>
                <button
                    onClick={handleCreateAccount}
                    className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition"
                >
                    Create Account
                </button>
            </div>
        </div>
    );
}; 