'use client';

import "./App.css";
import { useState, useCallback } from "react";
import OpenAI from "openai";
import { SYSTEM_PROMPT, INITIAL_MESSAGE } from "./prompts";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessages } from "./components/ChatMessages";
import { ChatInput } from "./components/ChatInput";
import { useSpeechRecognition } from "./components/useSpeechRecognition";
import { ViewSwitcher } from "./components/ViewSwitcher";
import { AdminPortal } from "./components/AdminPortal";

const client = new OpenAI({
  apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true,
});

function App() {
  const [isAdminView, setIsAdminView] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: INITIAL_MESSAGE },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(false);

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const handleSendMessage = useCallback(async (message = inputMessage) => {
    if (message.trim() === "") return;

    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInputMessage("");

    try {
      const response = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...messages,
          { role: "user", content: message },
        ],
      });

      const assistantMessage = response.choices[0].message.content || "No response received";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: assistantMessage },
      ]);
      speak(assistantMessage);
    } catch (error) {
      console.error("Error calling OpenAI API:", error);
      const errorMessage = "I'm sorry, I encountered an error. Please try again.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMessage },
      ]);
      speak(errorMessage);
    }
  }, [inputMessage, messages]);

  const { isListening, toggleListening } = useSpeechRecognition(handleSendMessage);

  return (
    <div className={`App ${isDarkMode ? "dark-mode" : "light-mode"}`}>
      <div className="chat-container">
        <ChatHeader 
          isDarkMode={isDarkMode} 
          setIsDarkMode={setIsDarkMode}
          isAdminView={isAdminView}
          onViewChange={setIsAdminView}
        />
        
        {isAdminView ? (
          <AdminPortal />
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