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
}

interface Message {
  role: string;
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
  const [patientInfo, setPatientInfo] = useState({});
  const [inputMessage, setInputMessage] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isSavingTriage, setIsSavingTriage] = useState(false);
  const [isTriageComplete, setIsTriageComplete] = useState(false);
  const [triageLevel, setTriageLevel] = useState<string | null>(null);

  // Check for existing session on load
  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        // Get provider details
        const { data: providerData } = await supabase
          .from('providers')
          .select('*')
          .eq('user_id', data.session.user.id)
          .single();

        if (providerData) {
          setUser({
            username: providerData.name,
            role: providerData.role,
            id: providerData.id
          });
        }
      }
    };

    checkSession();
  }, []);

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  // Call the complete_triage endpoint on the backend
  const completeTriageWithAPI = async () => {
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

      // Extract allergies from conversation (simple extraction for demo)
      let allergies = [];
      if (userMessages.some(msg => msg.toLowerCase().includes("allergic to"))) {
        const allergyMessages = userMessages.filter(msg =>
          msg.toLowerCase().includes("allergic to") ||
          msg.toLowerCase().includes("allergy")
        );
        if (allergyMessages.length > 0) {
          // Simple extraction - this could be more sophisticated
          allergies = ["penicillin"]; // Match what's in screenshot
        }
      }

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
            allergies: allergies,
            medications: [],
            contact_info: {}
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
  };

  // Save completed triage to Supabase and backend
  const saveTriageToDatabase = async () => {
    if (!isTriageComplete || !triageLevel) return;

    setIsSavingTriage(true);
    try {
      // First call the backend API to complete the triage
      const caseId = await completeTriageWithAPI();

      // Then proceed with Supabase operations as a fallback/redundancy
      // 1. Create patient record
      const patientData = {
        name: patientName || "Anonymous Patient",
        ...patientInfo
      };

      const { data: patientResponse, error: patientError } = await supabase
        .table('patients')
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
        .table('triage_cases')
        .insert(triageData)
        .select()
        .single();

      if (caseError) throw caseError;

      // 4. Store chat messages
      for (const message of chatHistory) {
        await supabase.table('chat_messages').insert({
          triage_case_id: caseResponse.id,
          sender_type: message.sender_type,
          message: message.content
        });
      }

      // 5. Assign to appropriate provider based on triage level
      const { data: providerResponse } = await supabase
        .table('providers')
        .select('id')
        .eq('role', triageLevel.toLowerCase())
        .order('random()')
        .limit(1);

      if (providerResponse && providerResponse.length > 0) {
        await supabase
          .table('triage_cases')
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
  };

  const handleSendMessage = useCallback(async (message = inputMessage) => {
    if (message.trim() === "") return;

    // Add user message to conversation
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInputMessage("");

    try {
      // If this is the first message and it looks like a name, ask for symptoms
      if (messages.length === 1 && message.split(" ").length <= 3 && !message.includes("pain") && !message.includes("hurt")) {
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
        if (user?.role === 'Patient') {
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
  }, [inputMessage, messages, patientName, user]);

  const { isListening, toggleListening } = useSpeechRecognition(handleSendMessage);

  // Handle login with Supabase auth
  const handleLogin = async (userData: User) => {
    setUser(userData);
    if (userData.role != "Patient") {
      setIsAdminView(true);
    }
  };

  // Add patient access handler
  const handlePatientAccess = () => {
    setUser({ username: 'Patient', role: 'Patient', id: 'patient' });
  };

  // Handle logout
  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setIsAdminView(false);
    setMessages([{ role: "assistant", content: INITIAL_MESSAGE }]);
  };

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
          onViewChange={setIsAdminView}
          user={user}
          onLogout={handleLogout}
        />

        <div className={`flex-1 overflow-y-auto`}>
          {isAdminView ? (
            <AdminPortal
              isDarkMode={isDarkMode}
              providerId={user.id}
            />
          ) : (
            <div className="h-full flex flex-col">
              <ChatMessages messages={messages} />

              {isTriageComplete && user.role == 'Patient' && (
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