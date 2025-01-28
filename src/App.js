import './App.css';
import { useState } from 'react';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hello! I'm your medical assistant. I'll help assess your symptoms and direct you to the appropriate healthcare professional. Could you please describe what brings you in today?" }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;
    
    setMessages([...messages, { role: 'user', content: inputMessage }]);
    setInputMessage('');
    // Here you would typically make an API call to your LLM service
    // and handle the response in a proper way
  };

  return (
    <div className={`App ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
      <div className="chat-container">
        <header className="chat-header">
          <h1>Triage</h1>
          <button 
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? '☀️' : '🌙'}
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
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
