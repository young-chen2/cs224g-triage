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
    const [searchQuery, setSearchQuery] = useState('');
    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [filterTriage, setFilterTriage] = useState<string>('all');

    const handleStatusChange = async (newStatus: string) => {
        if (!selectedCase) return;

        setIsUpdating(true);
        try {
            const success = await onUpdateStatus(selectedCase.id, newStatus);
            if (success) {
                setSelectedCase({ ...selectedCase, status: newStatus });
            }
        } finally {
            setIsUpdating(false);
        }
    };

    // Filter functions
    const filteredCases = chatHistories.filter(chat => {
        const matchesSearch =
            searchQuery === '' ||
            chat.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
            chat.symptoms.toLowerCase().includes(searchQuery.toLowerCase());

        const matchesStatus =
            filterStatus === 'all' ||
            chat.status === filterStatus;

        const matchesTriage =
            filterTriage === 'all' ||
            chat.currentTriage === filterTriage;

        return matchesSearch && matchesStatus && matchesTriage;
    });

    return (
        <div className={`border p-4 rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
            <h2 className={`text-xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                Triage Cases
            </h2>

            {isLoading ? (
                <div className="flex justify-center items-center h-60">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            ) : (
                <div className="space-y-4">
                    {!selectedCase && (
                        <div className="space-y-3">
                            {/* Search and filters */}
                            <div className="flex flex-col sm:flex-row gap-2">
                                <div className="flex-1">
                                    <input
                                        type="text"
                                        placeholder="Search patients or symptoms..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className={`w-full px-3 py-2 rounded border ${isDarkMode
                                                ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
                                                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                                            }`}
                                    />
                                </div>
                                <select
                                    value={filterStatus}
                                    onChange={(e) => setFilterStatus(e.target.value)}
                                    className={`px-3 py-2 rounded border ${isDarkMode
                                            ? 'bg-gray-700 border-gray-600 text-white'
                                            : 'bg-white border-gray-300 text-gray-900'
                                        }`}
                                >
                                    <option value="all">All Status</option>
                                    <option value="pending">Pending</option>
                                    <option value="in_progress">In Progress</option>
                                    <option value="completed">Completed</option>
                                </select>
                                <select
                                    value={filterTriage}
                                    onChange={(e) => setFilterTriage(e.target.value)}
                                    className={`px-3 py-2 rounded border ${isDarkMode
                                            ? 'bg-gray-700 border-gray-600 text-white'
                                            : 'bg-white border-gray-300 text-gray-900'
                                        }`}
                                >
                                    <option value="all">All Levels</option>
                                    <option value="nurse">Nurse</option>
                                    <option value="pa">PA</option>
                                    <option value="physician">Physician</option>
                                </select>
                            </div>

                            {/* Stats summary */}
                            <div className={`grid grid-cols-3 gap-2 p-3 rounded ${isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
                                }`}>
                                <div className="text-center">
                                    <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Pending</div>
                                    <div className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                        {chatHistories.filter(c => c.status === 'pending').length}
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>In Progress</div>
                                    <div className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                        {chatHistories.filter(c => c.status === 'in_progress').length}
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Completed</div>
                                    <div className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                        {chatHistories.filter(c => c.status === 'completed').length}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

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
                                    <span className={`font-semibold capitalize ${selectedCase.currentTriage === 'physician' ? 'text-red-500' :
                                            selectedCase.currentTriage === 'pa' ? 'text-yellow-500' : 'text-green-500'
                                        }`}>
                                        {selectedCase.currentTriage}
                                    </span>
                                </div>

                                <div className="mt-4">
                                    <div className="mb-2">Status:
                                        <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${selectedCase.status === 'pending' ? 'bg-yellow-200 text-yellow-800' :
                                                selectedCase.status === 'in_progress' ? 'bg-blue-200 text-blue-800' :
                                                    selectedCase.status === 'completed' ? 'bg-green-200 text-green-800' :
                                                        'bg-gray-200 text-gray-800'
                                            }`}>
                                            {selectedCase.status === 'pending' ? 'Pending' :
                                                selectedCase.status === 'in_progress' ? 'In Progress' :
                                                    selectedCase.status === 'completed' ? 'Completed' : selectedCase.status}
                                        </span>
                                    </div>

                                    <div className="flex space-x-2">
                                        {selectedCase.status === 'pending' && (
                                            <button
                                                onClick={() => handleStatusChange('in_progress')}
                                                disabled={isUpdating}
                                                className={`px-3 py-1 rounded text-white bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed`}
                                            >
                                                {isUpdating ? 'Updating...' : 'Start Case'}
                                            </button>
                                        )}

                                        {selectedCase.status === 'in_progress' && (
                                            <button
                                                onClick={() => handleStatusChange('completed')}
                                                disabled={isUpdating}
                                                className={`px-3 py-1 rounded text-white bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed`}
                                            >
                                                {isUpdating ? 'Updating...' : 'Complete Case'}
                                            </button>
                                        )}

                                        {selectedCase.status === 'completed' && (
                                            <button
                                                onClick={() => handleStatusChange('in_progress')}
                                                disabled={isUpdating}
                                                className={`px-3 py-1 rounded text-white bg-yellow-500 hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed`}
                                            >
                                                {isUpdating ? 'Updating...' : 'Reopen Case'}
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Case Notes - This could be expanded with actual notes functionality */}
                                <div className={`mt-6 p-3 border rounded ${isDarkMode ? 'border-gray-600 bg-gray-800' : 'border-gray-300 bg-white'}`}>
                                    <h4 className={`font-medium mb-2 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                                        Case Notes
                                    </h4>
                                    <textarea
                                        className={`w-full p-2 rounded border ${isDarkMode
                                                ? 'bg-gray-700 border-gray-600 text-white'
                                                : 'bg-white border-gray-200 text-gray-800'
                                            }`}
                                        rows={3}
                                        placeholder="Add notes about this case..."
                                    />
                                    <button className={`mt-2 px-3 py-1 rounded text-white bg-blue-500 hover:bg-blue-600`}>
                                        Save Notes
                                    </button>
                                </div>

                                {/* View Full Chat option */}
                                <div className="mt-4 text-center">
                                    <button className={`px-4 py-2 rounded ${isDarkMode
                                            ? 'bg-gray-600 text-gray-200 hover:bg-gray-500'
                                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}>
                                        View Full Chat History
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div>
                            {filteredCases.length === 0 ? (
                                <div className={`text-center py-10 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                    {chatHistories.length === 0
                                        ? 'No triage cases found'
                                        : 'No cases match your current filters'
                                    }
                                </div>
                            ) : (
                                <div className="space-y-2 max-h-96 overflow-y-auto">
                                    {filteredCases.map((chat) => (
                                        <div
                                            key={chat.id}
                                            onClick={() => setSelectedCase(chat)}
                                            className={`border p-3 rounded cursor-pointer transition-colors ${isDarkMode
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
                                                <span className={`text-xs capitalize px-2 py-0.5 rounded ${chat.currentTriage === 'physician' ? 'bg-red-100 text-red-800' :
                                                        chat.currentTriage === 'pa' ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-green-100 text-green-800'
                                                    }`}>
                                                    {chat.currentTriage}
                                                </span>

                                                <span className={`text-xs px-2 py-0.5 rounded ${chat.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                        chat.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                                            chat.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                                'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {chat.status === 'pending' ? 'Pending' :
                                                        chat.status === 'in_progress' ? 'In Progress' :
                                                            chat.status === 'completed' ? 'Completed' : chat.status}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};