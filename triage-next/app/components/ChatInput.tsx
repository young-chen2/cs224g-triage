interface ChatInputProps {
    inputMessage: string;
    setInputMessage: (message: string) => void;
    handleSendMessage: (message?: string) => void;
    isListening: boolean;
    toggleListening: () => void;
}

export function ChatInput({
    inputMessage,
    setInputMessage,
    handleSendMessage,
    isListening,
    toggleListening,
}: ChatInputProps) {
    return (
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
    );
}