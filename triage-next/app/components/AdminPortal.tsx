'use client';

import { useState, useEffect } from 'react';
import { GuidelinesUpload } from './admin/GuidelinesUpload';
import { TriageHistory } from './admin/TriageHistory';
import supabase from './supabaseClient';

interface ChatHistory {
    id: string;
    timestamp: string;
    patientName: string;
    symptoms: string;
    chatContext: string;
    currentTriage: 'nurse' | 'pa' | 'physician';
    status: string;
}

export const AdminPortal = ({
    isDarkMode,
    providerId
}: {
    isDarkMode: boolean;
    providerId: string;
}) => {
    const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
    const [isLoadingCases, setIsLoadingCases] = useState(true);
    const [error, setError] = useState('');

    // Fetch triage cases
    useEffect(() => {
        const fetchTriageCases = async () => {
            setIsLoadingCases(true);
            try {
                // Get all cases for this provider
                const { data: casesData, error: casesError } = await supabase
                    .from('triage_cases')
                    .select(`
                        id,
                        status,
                        triage_level,
                        created_at,
                        patients (
                            name
                        )
                    `)
                    .eq('assigned_provider_id', providerId)
                    .order('created_at', { ascending: false });

                if (casesError) throw casesError;

                // For each case, get the first message to display symptoms
                const formattedCases: ChatHistory[] = [];

                for (const caseItem of casesData || []) {
                    // Get first patient message
                    const { data: messagesData } = await supabase
                        .from('chat_messages')
                        .select('message')
                        .eq('triage_case_id', caseItem.id)
                        .eq('sender_type', 'patient')
                        .order('timestamp', { ascending: true })
                        .limit(1);

                    const firstMessage = messagesData && messagesData.length > 0
                        ? messagesData[0].message
                        : 'No symptom information available';

                    formattedCases.push({
                        id: caseItem.id,
                        timestamp: new Date(caseItem.created_at).toLocaleString(),
                        patientName: caseItem.patients?.name || 'Unknown Patient',
                        symptoms: firstMessage,
                        chatContext: 'Click to view full conversation',
                        currentTriage: caseItem.triage_level as 'nurse' | 'pa' | 'physician',
                        status: caseItem.status
                    });
                }

                setChatHistories(formattedCases);
            } catch (error) {
                console.error('Error fetching triage cases:', error);
                setError('Failed to load triage cases');
            } finally {
                setIsLoadingCases(false);
            }
        };

        if (providerId) {
            fetchTriageCases();
        }
    }, [providerId]);

    // Function to update triage case status
    const updateCaseStatus = async (caseId: string, newStatus: string) => {
        try {
            await supabase
                .from('triage_cases')
                .update({ status: newStatus })
                .eq('id', caseId);

            // Refresh the case list
            setChatHistories(prevCases =>
                prevCases.map(c =>
                    c.id === caseId ? { ...c, status: newStatus } : c
                )
            );

            return true;
        } catch (error) {
            console.error('Error updating case status:', error);
            return false;
        }
    };

    return (
        <div className="max-w-7xl mx-auto p-4 space-y-6">
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <span className="block sm:inline">{error}</span>
                </div>
            )}

            <div>
                <GuidelinesUpload isDarkMode={isDarkMode} />
            </div>

            <div>
                <TriageHistory
                    isDarkMode={isDarkMode}
                    chatHistories={chatHistories}
                    isLoading={isLoadingCases}
                    onUpdateStatus={updateCaseStatus}
                />
            </div>
        </div>
    );
};