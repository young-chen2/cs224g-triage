import { useState, useEffect, useCallback, useRef } from "react";

// Define proper types for the WebkitSpeechRecognition API
interface SpeechRecognitionEvent extends Event {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

// Define the SpeechRecognition interface
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: SpeechRecognitionErrorEvent) => void;
  onend: () => void;
}

type WebkitWindow = Window & {
  webkitSpeechRecognition: new () => SpeechRecognition;
};

export function useSpeechRecognition(onTranscript: (message: string) => void) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Stable reference to onTranscript
  const onTranscriptRef = useRef(onTranscript);
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => {
    // Check if the browser supports webkitSpeechRecognition
    if ("webkitSpeechRecognition" in window && !recognitionRef.current) {
      const recognitionInstance = new (
        window as unknown as WebkitWindow
      ).webkitSpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;

      recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript;
        setIsListening(false);
        onTranscriptRef.current(transcript);
      };

      recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognitionInstance;
    }
  }, []); // Empty dependency array is fine here as we're using refs

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current) {
      console.error("Speech recognition not supported");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (error) {
        console.error("Error starting recognition:", error);
      }
    }
  }, [isListening]);

  return { isListening, toggleListening };
}
