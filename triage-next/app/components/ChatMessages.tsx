import { useState } from 'react';

interface Message {
    role: "user" | "assistant";
    content: string;
    guidelines?: string[];
}

interface ChatMessagesProps {
    messages: Message[];
}

export function ChatMessages({ messages }: ChatMessagesProps) {
    const [expandedMessage, setExpandedMessage] = useState<number | null>(null);

    return (
        <div className="messages-container">
            {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                    <div className="message-content">{message.content}</div>

                    {message.role === 'assistant' && message.guidelines && message.guidelines.length > 0 && (
                        <div className="guidelines-section">
                            <button
                                className="guidelines-toggle"
                                onClick={() => setExpandedMessage(expandedMessage === index ? null : index)}
                            >
                                {expandedMessage === index ? '▼ Hide Guidelines' : '▶ Show Guidelines'}
                            </button>

                            {expandedMessage === index && (
                                <div className="guidelines-content">
                                    <h4>Reference Guidelines:</h4>
                                    {message.guidelines.map((guideline, idx) => (
                                        <div key={idx} className="guideline-item">
                                            {guideline}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}