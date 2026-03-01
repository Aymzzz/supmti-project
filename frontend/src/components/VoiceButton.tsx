'use client';

import { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';

interface VoiceButtonProps {
    language: string;
    onResult: (transcript: string) => void;
    disabled?: boolean;
}

// Language codes for Web Speech API
const SPEECH_LANG_MAP: Record<string, string> = {
    fr: 'fr-FR',
    en: 'en-US',
    darija: 'ar-MA',
};

export default function VoiceButton({ language, onResult, disabled }: VoiceButtonProps) {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const recognitionRef = useRef<any>(null);

    const startRecording = useCallback(() => {
        if (disabled) return;

        // Check for Web Speech API support
        const SpeechRecognition =
            (window as any).SpeechRecognition ||
            (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = SPEECH_LANG_MAP[language] || 'fr-FR';
        recognition.interimResults = true;
        recognition.continuous = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            setIsRecording(true);
            setTranscript('');
        };

        recognition.onresult = (event: any) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                if (result.isFinal) {
                    finalTranscript += result[0].transcript;
                } else {
                    interimTranscript += result[0].transcript;
                }
            }

            setTranscript(finalTranscript || interimTranscript);

            if (finalTranscript) {
                onResult(finalTranscript);
            }
        };

        recognition.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error);
            setIsRecording(false);
        };

        recognition.onend = () => {
            setIsRecording(false);
        };

        recognitionRef.current = recognition;
        recognition.start();
    }, [language, onResult, disabled]);

    const stopRecording = useCallback(() => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
        setIsRecording(false);
    }, []);

    const toggleRecording = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    return (
        <div style={{ position: 'relative' }}>
            <motion.button
                className={`voice-btn ${isRecording ? 'recording' : ''}`}
                onClick={toggleRecording}
                disabled={disabled}
                whileTap={{ scale: 0.9 }}
                aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
                title={isRecording ? 'Stop' : 'Voice input'}
            >
                {isRecording ? (
                    // Stop icon
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="6" y="6" width="12" height="12" rx="2" />
                    </svg>
                ) : (
                    // Microphone icon
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" y1="19" x2="12" y2="23" />
                        <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                )}
            </motion.button>

            {/* Live transcript overlay */}
            {isRecording && transcript && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                        position: 'absolute',
                        bottom: '50px',
                        right: 0,
                        background: 'var(--bg-secondary)',
                        border: '1px solid var(--border-glass)',
                        borderRadius: 'var(--radius-md)',
                        padding: '8px 12px',
                        fontSize: '12px',
                        color: 'var(--text-secondary)',
                        maxWidth: '250px',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        zIndex: 10,
                    }}
                >
                    🎤 {transcript}
                </motion.div>
            )}
        </div>
    );
}
