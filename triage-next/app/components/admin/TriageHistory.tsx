'use client';

import { useState } from 'react';

interface ChatHistory {
    id: string;
    timestamp: string;
    patientName: string;
    symptoms: string;
    chatContext: string;
    currentTriage: 'nurse' | 'pa' | 'physician';
    status: string;
}

interface TriageHistoryProps {
    isDarkMode: boolean;
    chatHistories: ChatHistory[];
    isLoading: boolean;
    onUpdateStatus: (caseId: string, newStatus: string) => Promise<boolean>;
}

export const TriageHistory = ({ 
    isDarkMode, 
    chatHistories, 
    isLoading,
    onUpdateStatus 
}: TriageHistoryProps) => {
    const [selectedCase, setSelectedCase] = useState<ChatHistory | null>(null);
    const [isUpdating, setIsUpdating] = useState(false);

    const handleStatusChange = async (newStatus: string) => {
        if (!selectedCase) return;
        
        setIsUpdating(true);
        try {
            const success = await onUpdateStatus(selectedCase.id, newStatus);
            if (success) {
                setSelectedCase({...selectedCase, status: newStatus});
            }
        } finally {
            setIsUpdating(false);
        }
    };

    return (
        <div className={`border p-4 rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
            <h2 className={`text-xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                Triage History
            </h2>
            
            {isLoading ? (
                <div className="flex justify-center items-center h-60">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            ) : chatHistories.length === 0 ? (
                <div className={`text-center py-10 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    No triage cases found
                </div>
            ) : (
                <div className="space-y-4">
                    {selectedCase ? (
                        <div className="space-y-4">
                            <button 
                                onClick={() => setSelectedCase(null)}
                                className={`px-2 py-1 rounded text-sm ${isDarkMode ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                            >
                                ← Back to list
                            </button>
                            
                            <div className={`border p-4 rounded ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'}`}>
                                <div className="flex justify-between items-start">
                                    <h3 className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                        {selectedCase.patientName}
                                    </h3>
                                    <span className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                        {selectedCase.timestamp}
                                    </span>
                                </div>
                                
                                <p className={`mt-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                                    <span className="font-semibold">Symptoms:</span> {selectedCase.symptoms}
                                </p>
                                
                                <div className="mt-4 flex items-center">
                                    <span className={`mr-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                                        Triaged to:
                                    </span>
                                    <span className={`font-semibold capitalize ${
                                        selectedCase.currentTriage === 'physician' ? 'text-red-500' : 
                                        selectedCase.currentTriage === 'pa' ? 'text-yellow-500' : 'text-green-500'
                                    }`}>
                                        {selectedCase.currentTriage}
                                    </span>
                                </div>
                                
                                <div className="mt-4">
                                    <div className="mb-2">Status: 
                                        <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
                                            selectedCase.status === 'pending' ? 'bg-yellow-200 text-yellow-800' :
                                            selectedCase.status === 'in_progress' ? 'bg-blue-200 text-blue-800' :
                                            selectedCase.status === 'completed' ? 'bg-green-200 text-green-800' :
                                            'bg-gray-200 text-gray-800'
                                        }`}>
                                            {selectedCase.status}
                                        </span>
                                    </div>
                                    
                                    <div className="flex space-x-2">
                                        <button 
                                            onClick={() => handleStatusChange('in_progress')}
                                            disabled={isUpdating || selectedCase.status === 'in_progress'}
                                            className={`px-3 py-1 rounded text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed`}
                                        >
                                            Start
                                        </button>
                                        <button 
                                            onClick={() => handleStatusChange('completed')}
                                            disabled={isUpdating || selectedCase.status === 'completed'}
                                            className={`px-3 py-1 rounded text-white bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed`}
                                        >
                                            Complete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                            {chatHistories.map((chat) => (
                                <div 
                                    key={chat.id}
                                    onClick={() => setSelectedCase(chat)}
                                    className={`border p-3 rounded cursor-pointer transition-colors ${
                                        isDarkMode 
                                            ? 'bg-gray-700 border-gray-600 hover:bg-gray-600' 
                                            : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                                    }`}
                                >
                                    <div className="flex justify-between items-start">
                                        <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                            {chat.patientName}
                                        </h3>
                                        <span className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                            {chat.timestamp}
                                        </span>
                                    </div>
                                    
                                    <p className={`mt-1 text-sm truncate ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                                        {chat.symptoms}
                                    </p>
                                    
                                    <div className="mt-2 flex justify-between items-center">
                                        <span className={`text-xs capitalize px-2 py-0.5 rounded ${
                                            chat.currentTriage === 'physician' ? 'bg-red-100 text-red-800' : 
                                            chat.currentTriage === 'pa' ? 'bg-yellow-100 text-yellow-800' : 
                                            'bg-green-100 text-green-800'
                                        }`}>
                                            {chat.currentTriage}
                                        </span>
                                        
                                        <span className={`text-xs px-2 py-0.5 rounded ${
                                            chat.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                            chat.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                            chat.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {chat.status}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};