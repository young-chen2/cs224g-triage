import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
    role: "user" | "assistant";
    content: string;
    guidelines?: string[];
    is_gathering_info?: boolean;
}

interface ChatMessagesProps {
    messages: Message[];
}

export function ChatMessages({ messages }: ChatMessagesProps) {
    const [expandedMessage, setExpandedMessage] = useState<number | null>(null);

    // Function to format triage message content
    const formatTriageContent = (content: string) => {
        // If it looks like a triage assessment (contains numbered sections)
        if (content.includes("**Patient Profile:**") || 
            content.includes("**Assessment:**") || 
            content.includes("**Triage Recommendation:**")) {
            
            // Convert the format to markdown for better rendering
            return content
                // Ensure proper line breaks between sections
                .replace(/(\d+\.\s+\*\*[^*]+\*\*:)/g, '\n\n$1\n')
                // Add bullet points for items separated by dashes
                .replace(/(\s+-\s+)([^-]+)/g, '\n* $2')
                // Ensure sections are well separated
                .replace(/\*\*([^*]+)\*\*:/g, '### **$1**:');
        }
        
        return content;
    };

    return (
        <div className="messages-container">
            {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                    {message.role === 'assistant' && (
                        <div className="message-content">
                            <ReactMarkdown className="markdown-content">
                                {formatTriageContent(message.content)}
                            </ReactMarkdown>
                        </div>
                    )}
                    
                    {message.role === 'user' && (
                        <div className="message-content">{message.content}</div>
                    )}

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