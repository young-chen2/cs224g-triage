import { useState, useEffect, useCallback } from "react";

export function useSpeechRecognition(onTranscript: (message: string) => void) {
const [isListening, setIsListening] = useState(false);
const [recognition, setRecognition] = useState<any>(null);

useEffect(() => {
    if ("webkitSpeechRecognition" in window && !recognition) {
    const recognitionInstance = new (window as any).webkitSpeechRecognition();
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = false;

    recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setIsListening(false);
        onTranscript(transcript);
    };

    recognitionInstance.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
    };

    recognitionInstance.onend = () => {
        setIsListening(false);
    };

    setRecognition(recognitionInstance);
    }
}, []); // Empty dependency array since we only want to initialize once

const toggleListening = useCallback(() => {
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
}, [recognition, isListening]);

return { isListening, toggleListening };
}
