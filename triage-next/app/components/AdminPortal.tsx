'use client';

import { useState } from 'react';
import { GuidelinesUpload } from './admin/GuidelinesUpload';
import { TriageHistory } from './admin/TriageHistory';
import { AccountManagement } from './admin/AccountManagement';

interface ChatHistory {
    id: string;
    timestamp: string;
    patientName: string;
    symptoms: string;
    chatContext: string;
    currentTriage: 'Nurse' | 'PA' | 'Physician';
}

interface Account {
    username: string;
    role: string;
    password: string;
}

export const AdminPortal = ({ isDarkMode }: { isDarkMode: boolean }) => {
    const [chatHistories] = useState<ChatHistory[]>([
        {
            id: '1',
            timestamp: '2024-03-20 14:30',
            patientName: 'John D.',
            symptoms: 'Chest pain, shortness of breath',
            chatContext: 'Patient reported sudden onset chest pain...',
            currentTriage: 'Nurse'
        }
    ]);

    const [accountList, setAccountList] = useState<Account[]>([
        { username: 'doctor1', role: 'Physician', password: 'password123' },
        { username: 'nurse1', role: 'Nurse', password: 'password123' },
        { username: 'pa1', role: 'PA', password: 'password123' },
    ]);

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <GuidelinesUpload isDarkMode={isDarkMode} />
                <TriageHistory isDarkMode={isDarkMode} chatHistories={chatHistories} />
            </div>
            <AccountManagement 
                isDarkMode={isDarkMode} 
                accountList={accountList}
                setAccountList={setAccountList}
            />
        </div>
    );
}; 