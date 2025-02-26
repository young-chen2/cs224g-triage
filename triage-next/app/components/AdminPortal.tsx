'use client';

import { useState, useEffect } from 'react';
import { GuidelinesUpload } from './admin/GuidelinesUpload';
import { TriageHistory } from './admin/TriageHistory';
import { AccountManagement } from './admin/AccountManagement';
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

interface Account {
    id: string;
    username: string;
    role: string;
    email: string;
}

export const AdminPortal = ({ 
    isDarkMode, 
    providerId 
}: { 
    isDarkMode: boolean;
    providerId: string;
}) => {
    const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
    const [accountList, setAccountList] = useState<Account[]>([]);
    const [isLoadingCases, setIsLoadingCases] = useState(true);
    const [isLoadingAccounts, setIsLoadingAccounts] = useState(true);
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

    // Fetch provider accounts (for admin users only)
    useEffect(() => {
        const fetchAccounts = async () => {
            setIsLoadingAccounts(true);
            try {
                // First check if current user is admin/physician
                const { data: currentProvider } = await supabase
                    .from('providers')
                    .select('role')
                    .eq('id', providerId)
                    .single();
                    
                if (currentProvider?.role === 'physician') {
                    // Only physicians can see all accounts
                    const { data: providersData, error: providersError } = await supabase
                        .from('providers')
                        .select(`
                            id,
                            name,
                            role,
                            user_id
                        `)
                        .order('name');
                        
                    if (providersError) throw providersError;
                    
                    // Get emails from auth
                    const accounts: Account[] = [];
                    
                    for (const provider of providersData || []) {
                        const { data: userData } = await supabase
                            .auth.admin.getUserById(provider.user_id);
                            
                        accounts.push({
                            id: provider.id,
                            username: provider.name,
                            role: provider.role,
                            email: userData?.user?.email || 'N/A'
                        });
                    }
                    
                    setAccountList(accounts);
                } else {
                    // Non-physicians only see their own account
                    setAccountList([]);
                }
            } catch (error) {
                console.error('Error fetching accounts:', error);
            } finally {
                setIsLoadingAccounts(false);
            }
        };

        if (providerId) {
            fetchAccounts();
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
                    c.id === caseId ? {...c, status: newStatus} : c
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
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <GuidelinesUpload isDarkMode={isDarkMode} />
                <TriageHistory 
                    isDarkMode={isDarkMode} 
                    chatHistories={chatHistories}
                    isLoading={isLoadingCases}
                    onUpdateStatus={updateCaseStatus}
                />
            </div>
            
            {accountList.length > 0 && (
                <AccountManagement 
                    isDarkMode={isDarkMode} 
                    accountList={accountList}
                    setAccountList={setAccountList}
                    isLoading={isLoadingAccounts}
                />
            )}
        </div>
    );
};