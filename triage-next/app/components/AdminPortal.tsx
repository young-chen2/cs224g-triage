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
    const [providerRole, setProviderRole] = useState<'nurse' | 'pa' | 'physician'>('nurse');

    // Fetch provider role
    useEffect(() => {
        const fetchProviderRole = async () => {
            try {
                const { data, error } = await supabase
                    .from('providers')
                    .select('role')
                    .eq('id', providerId)
                    .single();

                if (error) throw error;
                setProviderRole(data.role as 'nurse' | 'pa' | 'physician');
            } catch (error) {
                console.error('Error fetching provider role:', error);
            }
        };

        if (providerId) {
            fetchProviderRole();
        }
    }, [providerId]);

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

    // Function to reassign a case to another provider type
    const handleCaseReassignment = async (caseId: string, newProviderType: 'nurse' | 'pa' | 'physician') => {
        try {
            if (!caseId || !newProviderType) {
                setError('Missing case ID or provider type for reassignment');
                return false;
            }

            // First, find a provider of the specified type to reassign to
            const { data: newProviders, error: providerError } = await supabase
                .from('providers')
                .select('id')
                .eq('role', newProviderType)
                .limit(1);

            if (providerError) {
                console.error('Provider query error:', providerError);
                throw new Error(`Failed to find ${newProviderType} provider: ${providerError.message}`);
            }

            if (!newProviders || newProviders.length === 0) {
                setError(`No ${newProviderType} provider available for reassignment`);
                return false;
            }

            const newProviderId = newProviders[0].id;

            // Update only the fields that exist in your database
            const { error: updateError } = await supabase
                .from('triage_cases')
                .update({
                    assigned_provider_id: newProviderId,
                    triage_level: newProviderType
                })
                .eq('id', caseId);

            if (updateError) {
                console.error('Case update error:', updateError);
                throw new Error(`Failed to update case: ${updateError.message}`);
            }

            // Add a note to the case about the reassignment
            const { error: messageError } = await supabase
                .from('chat_messages')
                .insert({
                    triage_case_id: caseId,
                    sender_type: 'system',
                    message: `Case reassigned from ${providerRole} to ${newProviderType}`,
                    timestamp: new Date().toISOString()
                });

            if (messageError) {
                console.error('Message insert error:', messageError);
                // Don't throw here, the reassignment was successful even if the message failed
            }

            // Remove this case from the current view since it's been reassigned
            setChatHistories(prevCases =>
                prevCases.filter(c => c.id !== caseId)
            );

            return true;
        } catch (error) {
            // Ensure error is a proper Error object with a message
            const errorMessage = error instanceof Error
                ? error.message
                : 'Unknown error during reassignment';

            console.error('Error reassigning case:', errorMessage);
            setError(`Failed to reassign case: ${errorMessage}`);
            return false;
        }
    };
    
    return (
        <div className="max-w-7xl mx-auto p-4 space-y-6">
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <span className="block sm:inline">{error}</span>
                    <button
                        className="absolute top-0 right-0 px-4 py-3"
                        onClick={() => setError('')}
                    >
                        <span className="sr-only">Dismiss</span>
                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
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
                    onReassignCase={handleCaseReassignment}
                    currentUserRole={providerRole}
                />
            </div>
        </div>
    );
};