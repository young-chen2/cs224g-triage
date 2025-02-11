'use client';

import "./App.css";
import { useState, useCallback } from "react";
import { INITIAL_MESSAGE } from "./prompts";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessages } from "./components/ChatMessages";
import { ChatInput } from "./components/ChatInput";
import { useSpeechRecognition } from "./components/useSpeechRecognition";
import { AdminPortal } from "./components/AdminPortal";
import { Login } from "./components/Login";

// Define types for the API response
interface TriageResponse {
  symptoms_received: string;
  raw_llm_response: string;
  relevant_guidelines: string[];
}

// Add interface for user
interface User {
  username: string;
  role: string;
}

function App() {
  const [isAdminView, setIsAdminView] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: INITIAL_MESSAGE },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const handleSendMessage = useCallback(async (message = inputMessage) => {
    if (message.trim() === "") return;

    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInputMessage("");

    try {
      const response = await fetch('http://127.0.0.1:8000/triage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          symptoms: message  // This is already correct as it's sending a string
        }),
      });

      if (!response.ok) {
        console.error('API Error:', response.status, await response.text());
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data: TriageResponse = await response.json();
      console.log('API Response:', data); // Debug log

      const assistantMessage = {
        role: "assistant" as const,
        content: data.raw_llm_response,
        guidelines: data.relevant_guidelines
      };

      setMessages((prev) => [...prev, assistantMessage]);
      speak(data.raw_llm_response);
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
  }, [inputMessage]);

  const { isListening, toggleListening } = useSpeechRecognition(handleSendMessage);

  // Add mock authentication
  const handleLogin = (username: string, password: string) => {
    const mockUsers = [
      { username: 'doctor1', role: 'Physician', password: 'password123' },
      { username: 'nurse1', role: 'Nurse', password: 'password123' },
      { username: 'pa1', role: 'PA', password: 'password123' },
    ];

    const user = mockUsers.find(u => u.username === username && u.password === password);
    if (user) {
      setUser({ username: user.username, role: user.role });
    }
  };

  // Add patient access handler
  const handlePatientAccess = () => {
    setUser({ username: 'Patient', role: 'Patient' });
  };

  // Add logout handler
  const handleLogout = () => {
    setUser(null);
    setIsAdminView(false); // Reset admin view on logout
  };

  // If not logged in, show login screen
  if (!user) {
    return <Login onLogin={handleLogin} onPatientAccess={handlePatientAccess} />;
  }

  return (
    <div className={`App ${isDarkMode ? "dark-mode" : "light-mode"}`}>
      <div className="chat-container">
        <ChatHeader 
          isDarkMode={isDarkMode} 
          setIsDarkMode={setIsDarkMode}
          isAdminView={isAdminView}
          onViewChange={setIsAdminView}
          user={user}
          onLogout={handleLogout}
        />
        
        {isAdminView ? (
          <AdminPortal isDarkMode={isDarkMode} />
        ) : (
          <>
            <ChatMessages messages={messages} />
            <ChatInput
              inputMessage={inputMessage}
              setInputMessage={setInputMessage}
              handleSendMessage={handleSendMessage}
              isListening={isListening}
              toggleListening={toggleListening}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;