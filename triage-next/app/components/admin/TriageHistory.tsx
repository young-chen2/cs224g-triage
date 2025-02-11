'use client';

interface ChatHistory {
    id: string;
    timestamp: string;
    patientName: string;
    symptoms: string;
    chatContext: string;
    currentTriage: 'Nurse' | 'PA' | 'Physician';
}

interface Props {
    isDarkMode: boolean;
    chatHistories: ChatHistory[];
}

export const TriageHistory = ({ isDarkMode, chatHistories }: Props) => {
    return (
        <div className={`${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} rounded-xl shadow-md p-6`}>
            <div className="flex items-center gap-2 mb-4">
                <span className="text-blue-600 font-bold text-2xl">📋</span>
                <h2 className="text-xl font-semibold">Recent Triage Decisions</h2>
            </div>

            <div className="space-y-4">
                {chatHistories.length > 0 ? (
                    chatHistories.map((chat) => (
                        <div
                            key={chat.id}
                            className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-medium">{chat.patientName}</h3>
                                    <p className="text-sm text-gray-500">{chat.timestamp}</p>
                                </div>
                                <span className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                                    {chat.currentTriage}
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{chat.symptoms}</p>
                            <p className="text-sm text-gray-600 mb-3 line-clamp-2">{chat.chatContext}</p>

                            <div className="flex gap-2">
                                <button className="text-sm px-3 py-1 rounded-lg bg-green-100 text-green-700 hover:bg-green-200">
                                    Triage to Nurse
                                </button>
                                <button className="text-sm px-3 py-1 rounded-lg bg-yellow-100 text-yellow-700 hover:bg-yellow-200">
                                    Triage to PA
                                </button>
                                <button className="text-sm px-3 py-1 rounded-lg bg-red-100 text-red-700 hover:bg-red-200">
                                    Triage to Physician
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="text-center text-gray-500 py-8">No triage decisions recorded yet.</p>
                )}
            </div>
        </div>
    );
}; 