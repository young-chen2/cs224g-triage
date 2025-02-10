interface Message {
    role: string;
    content: string;
}

interface ChatMessagesProps {
    messages: Message[];
}

export function ChatMessages({ messages }: ChatMessagesProps) {
    return (
        <div className="messages-container">
            {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                    {message.content}
                </div>
            ))}
        </div>
    );
}