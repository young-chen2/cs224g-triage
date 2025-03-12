'use client';

import "./App.css";
import { useState, useCallback, useEffect } from "react";
import { INITIAL_MESSAGE } from "./prompts";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessages } from "./components/ChatMessages";
import { ChatInput } from "./components/ChatInput";
import { useSpeechRecognition } from "./components/useSpeechRecognition";
import { AdminPortal } from "./components/AdminPortal";
import { Login } from "./components/Login";
import supabase from './components/supabaseClient';

// Define types for the API response
interface TriageResponse {
  symptoms_received: string;
  raw_llm_response: string;
  relevant_guidelines: string[];
  is_gathering_info: boolean;
  triage_level?: string;
}

// Add interface for user
interface User {
  username: string;
  role: string;
  id: string;
  // Add account_id for patient users
  account_id?: string;
}

interface Message {
  role: "assistant" | "user";
  content: string;
  guidelines?: string[];
  is_gathering_info?: boolean;
}

function App() {
  const [isAdminView, setIsAdminView] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: INITIAL_MESSAGE },
  ]);
  const [patientName, setPatientName] = useState("");
  const [patientInfo] = useState({});
  const [inputMessage, setInputMessage] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isSavingTriage, setIsSavingTriage] = useState(false);
  const [isTriageComplete, setIsTriageComplete] = useState(false);
  const [triageLevel, setTriageLevel] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing user session in localStorage
  useEffect(() => {
    setIsLoading(true);
    try {
      // Check for any stored user data in localStorage
      const storedUser = localStorage.getItem('user');
      const storedAdminView = localStorage.getItem('isAdminView');

      if (storedUser) {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        
        // Set patient name from username if it's a patient
        if (userData.role === "patient" || userData.role === "Patient") {
          setPatientName(userData.username);
        }

        // If admin view state was stored, restore it
        if (storedAdminView) {
          setIsAdminView(storedAdminView === 'true');
        } else if (userData.role !== "patient" && userData.role !== "Patient") {
          // Default to admin view for non-patient users
          setIsAdminView(true);
        } else {
          // Ensure patients always see chat view, not admin
          setIsAdminView(false);
        }
      }
    } catch (error) {
      console.error("Error checking localStorage session:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Store user data to localStorage whenever it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('isAdminView', isAdminView.toString());
    }
  }, [user, isAdminView]);

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  // Call the complete_triage endpoint on the backend
  const completeTriageWithAPI = useCallback(async () => {
    if (!isTriageComplete || !triageLevel) return;

    try {
      // Extract all user messages to collect symptoms
      const userMessages = messages
        .filter(msg => msg.role === 'user')
        .map(msg => msg.content);

      const allSymptoms = userMessages.join(' ');

      // Format chat history for API
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Call the API endpoint
      const response = await fetch('http://127.0.0.1:8000/triage/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_info: {
            name: patientName || "Anonymous Patient",
            dob: null,
            gender: null,
            allergies: [],
            medications: [],
            contact_info: {},
            // Include account_id for registered patients
            account_id: user?.account_id || user?.id
          },
          symptoms: allSymptoms,
          chat_history: chatHistory,
          triage_level: triageLevel.toLowerCase(),
          summary: "Triage completed via AI assistant"
        }),
      });

      if (!response.ok) {
        console.error('API Error:', response.status, await response.text());
        throw new Error(`API request failed with status ${response.status}`);
      }

      const result = await response.json();
      console.log('Triage completed successfully:', result);

      return result.case_id;
    } catch (error) {
      console.error("Error completing triage with API:", error);
      throw error;
    }
  }, [isTriageComplete, triageLevel, messages, patientName, user]);

  // Save completed triage to Supabase and backend
  const saveTriageToDatabase = useCallback(async () => {
    if (!isTriageComplete || !triageLevel) return;

    setIsSavingTriage(true);
    try {
      // First call the backend API to complete the triage
      const caseId = await completeTriageWithAPI();

      // Then proceed with Supabase operations as a fallback/redundancy
      // 1. Create patient record
      const patientData = {
        name: patientName || "Anonymous Patient",
        account_id: user?.account_id || user?.id, // Store account_id
        ...patientInfo
      };

      const { data: patientResponse, error: patientError } = await supabase
        .from('patients')
        .upsert(patientData)
        .select()
        .single();

      if (patientError) throw patientError;

      // 2. Format chat history
      const chatHistory = messages.map(msg => ({
        sender_type: msg.role === 'assistant' ? 'system' : 'patient',
        content: msg.content
      }));

      // 3. Create triage case
      const triageData = {
        patient_id: patientResponse.id,
        triage_level: triageLevel.toLowerCase(),
        summary: "Triage completed via AI assistant",
        status: "pending",
        api_case_id: caseId // Store the case ID from our API
      };

      const { data: caseResponse, error: caseError } = await supabase
        .from('triage_cases')
        .insert(triageData)
        .select()
        .single();

      if (caseError) throw caseError;

      // 4. Store chat messages
      for (const message of chatHistory) {
        await supabase.from('chat_messages').insert({
          triage_case_id: caseResponse.id,
          sender_type: message.sender_type,
          message: message.content
        });
      }

      // 5. Assign to appropriate provider based on triage level
      const { data: providerResponse } = await supabase
        .from('providers')
        .select('id')
        .eq('role', triageLevel.toLowerCase())
        .order('random()')
        .limit(1);

      if (providerResponse && providerResponse.length > 0) {
        await supabase
          .from('triage_cases')
          .update({ assigned_provider_id: providerResponse[0].id })
          .eq('id', caseResponse.id);
      }

      alert("Triage case saved successfully!");
      // Reset conversation
      setMessages([{ role: "assistant", content: INITIAL_MESSAGE }]);
      setIsTriageComplete(false);
      setTriageLevel(null);
    } finally {
      setIsSavingTriage(false);
    }
  }, [isTriageComplete, triageLevel, completeTriageWithAPI, patientName, patientInfo, messages, user]);

  const handleSendMessage = useCallback(async (message = inputMessage) => {
    if (message.trim() === "") return;

    // Add user message to conversation
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInputMessage("");

    try {
      // If this is the first message and it looks like a name, ask for symptoms
      // Skip name detection if we already know the user
      if (messages.length === 1 && !patientName && message.split(" ").length <= 3 && !message.includes("pain") && !message.includes("hurt")) {
        setPatientName(message);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Hello ${message}, I'm here to help triage your medical concerns. Please describe your symptoms or what's bothering you today.`
          }
        ]);
        return;
      }

      // Inside handleSendMessage function
      const response = await fetch('http://127.0.0.1:8000/triage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symptoms: message,
          conversation_history: messages.slice(-5).map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        }),
      });

      if (!response.ok) {
        console.error('API Error:', response.status, await response.text());
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data: TriageResponse = await response.json();
      console.log('API Response:', data);

      const assistantMessage = {
        role: "assistant" as const,
        content: data.raw_llm_response,
        guidelines: data.relevant_guidelines,
        is_gathering_info: data.is_gathering_info
      };

      setMessages((prev) => [...prev, assistantMessage]);
      speak(data.raw_llm_response);

      // Check if triage is complete and set the triage level
      if (data.triage_level && !data.is_gathering_info) {
        setIsTriageComplete(true);
        setTriageLevel(data.triage_level);

        // If patient is logged in, save automatically
        if (user?.role === 'patient' || user?.role === 'Patient') {
          await completeTriageWithAPI();  // Send to backend API
          saveTriageToDatabase();  // Also save to Supabase as backup
        }
      }

    } catch (error) {
      console.error("Error calling Triage API:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I apologize, but I'm having trouble connecting to the medical knowledge base. Please ensure the API server is running and try again."
        },
      ]);
    }
  }, [inputMessage, messages, patientName, user, completeTriageWithAPI, saveTriageToDatabase]);

  const { isListening, toggleListening } = useSpeechRecognition(handleSendMessage);

  // Handle login (no longer dependent on Supabase auth)
  const handleLogin = async (userData: User) => {
    setUser(userData);
    
    // Set patient name if it's a patient user
    if (userData.role.toLowerCase() === "patient") {
      setPatientName(userData.username);
    }
    
    // Set admin view for non-patient users
    const shouldBeAdminView = userData.role.toLowerCase() !== "patient";
    setIsAdminView(shouldBeAdminView);

    // Store in localStorage for persistence
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('isAdminView', shouldBeAdminView.toString());
  };

  // Add patient access handler
  const handlePatientAccess = () => {
    const patientUser = { 
      username: 'Guest Patient', 
      role: 'Patient', 
      id: 'guest-' + Math.random().toString(36).substring(2, 9) // Generate random ID for guests
    };
    setUser(patientUser);
    setIsAdminView(false);
    setPatientName('Guest Patient');

    // Store in localStorage for persistence
    localStorage.setItem('user', JSON.stringify(patientUser));
    localStorage.setItem('isAdminView', 'false');
  };

  // Handle logout
  const handleLogout = async () => {
    // Clear user data from localStorage
    localStorage.removeItem('user');
    localStorage.removeItem('isAdminView');

    // Still call Supabase signOut for completeness if using Supabase elsewhere
    try {
      await supabase.auth.signOut();
    } catch (error) {
      console.error("Error signing out from Supabase:", error);
    }

    // Reset application state
    setUser(null);
    setIsAdminView(false);
    setMessages([{ role: "assistant", content: INITIAL_MESSAGE }]);
    setPatientName("");
  };

  // If still loading, show a loading indicator
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading your session...</p>
        </div>
      </div>
    );
  }

  // If not logged in, show login screen
  if (!user) {
    return <Login onLogin={handleLogin} onPatientAccess={handlePatientAccess} />;
  }

  return (
    <div className={`App min-h-screen ${isDarkMode ? "dark-mode" : "light-mode"}`}>
      <div className="chat-container h-screen flex flex-col">
        <ChatHeader
          isDarkMode={isDarkMode}
          setIsDarkMode={setIsDarkMode}
          isAdminView={isAdminView}
          onViewChange={(value) => {
            // Prevent patients from accessing admin view
            if (user.role.toLowerCase() === "patient" && value === true) {
              return;
            }
            setIsAdminView(value);
          }}
          user={user}
          onLogout={handleLogout}
        />

        <div className={`flex-1 overflow-y-auto`}>
          {isAdminView && user.role.toLowerCase() !== "patient" ? (
            <AdminPortal
              isDarkMode={isDarkMode}
              providerId={user.id}
            />
          ) : (
            <div className="h-full flex flex-col">
              <ChatMessages messages={messages} />

              {isTriageComplete && (
                <div className="p-4 bg-green-100 dark:bg-green-900 border-t border-green-200 dark:border-green-800">
                  <p className="text-green-800 dark:text-green-200 font-medium">
                    Triage complete! Recommended provider type: <span className="font-bold">{triageLevel}</span>
                  </p>
                  <button
                    className="mt-2 bg-green-500 hover:bg-green-600 text-white py-1 px-4 rounded"
                    onClick={saveTriageToDatabase}
                    disabled={isSavingTriage}
                  >
                    {isSavingTriage ? 'Saving...' : 'Save Triage Case'}
                  </button>
                </div>
              )}

              <ChatInput
                inputMessage={inputMessage}
                setInputMessage={setInputMessage}
                handleSendMessage={handleSendMessage}
                isListening={isListening}
                toggleListening={toggleListening}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;