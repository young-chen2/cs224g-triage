'use client';

import "./App.css";
import { useState, useEffect } from "react";
import OpenAI from "openai";
import { SYSTEM_PROMPT, INITIAL_MESSAGE } from "./prompts";

const client = new OpenAI({
  apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true,
});

function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: INITIAL_MESSAGE },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (message.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { role: "user", content: message },
    ]);
    setInputMessage("");

    try {
      // // Call your Python backend API
      // const response = await fetch("http://localhost:8000/triage", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ symptoms: message }),
      // });

      // if (!response.ok) throw new Error("API call failed");

      // const data = await response.json();
      // const assistantMessage = data.recommendation;

      const response = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...messages,
          { role: "user", content: message },
        ],
      });

      const assistantMessage = response.choices[0].message.content;
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "assistant", content: assistantMessage },
      ]);
      speak(assistantMessage);
    } catch (error) {
      console.error("Error calling OpenAI API:", error);
      const errorMessage =
        "I'm sorry, I encountered an error. Please try again.";
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);
      speak(errorMessage);
    }
  };

  useEffect(() => {
    if ("webkitSpeechRecognition" in window) {
      const recognitionInstance = new window.webkitSpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
        // ensure state is updated before sending
        setTimeout(() => handleSendMessage(transcript), 100);
      };

      recognitionInstance.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, []);

  const toggleListening = () => {
    if (!recognition) {
      console.error("Speech recognition not supported");
      return;
    }

    if (isListening) {
      recognition.stop();
    } else {
      try {
        recognition.start();
        setIsListening(true);
      } catch (error) {
        console.error("Error starting recognition:", error);
      }
    }
  };

  return (
    <div className={`App ${isDarkMode ? "dark-mode" : "light-mode"}`}>
      <div className="chat-container">
        <header className="chat-header">
          <h1>Triage</h1>
          <button
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? "☀️" : "🌙"}
          </button>
        </header>

        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              {message.content}
            </div>
          ))}
        </div>

        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Describe your symptoms..."
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
          />
          <button onClick={() => handleSendMessage()}>Send</button>
          <button
            onClick={toggleListening}
            className={`mic-button ${isListening ? "listening" : ""}`}
          >
            {isListening ? "🎤 (Recording...)" : "🎤"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
