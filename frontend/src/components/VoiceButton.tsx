'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { WavRecorder } from '../utils/audioEncoder';

interface VoiceButtonProps {
    language: string;
    onResult: (transcript: string) => void;
    disabled?: boolean;
}

export default function VoiceButton({ language, onResult, disabled }: VoiceButtonProps) {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const recorderRef = useRef<WavRecorder | null>(null);

    const startRecording = useCallback(async () => {
        if (disabled) return;

        try {
            const recorder = new WavRecorder();
            recorderRef.current = recorder;
            await recorder.start();

            setIsRecording(true);
            setTranscript('Listening...');
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Microphone access is denied or unavailable. Please check your permissions.');
            setIsRecording(false);
        }
    }, [disabled]);

    const sendAudioToBackend = async (audioBlob: Blob) => {
        setTranscript('Processing...');
        try {
            const formData = new FormData();
            // Google STT free API relies heavily on this filename having a correct extension
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('language', language);

            const response = await fetch('/api/voice/transcribe', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Transcription failed');

            const data = await response.json();
            if (data.transcript) {
                setTranscript(data.transcript);
                onResult(data.transcript);
            } else {
                setTranscript('Could not understand audio.');
            }
        } catch (error) {
            console.error('Transcription error:', error);
            setTranscript('Error processing audio.');
        }

        setTimeout(() => setTranscript(''), 2000);
    };

    const stopRecording = useCallback(async () => {
        if (recorderRef.current && isRecording) {
            setIsRecording(false);
            const audioBlob = await recorderRef.current.stop();
            if (audioBlob.size <= 44) return;
            await sendAudioToBackend(audioBlob);
        }
    }, [isRecording, language]);

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
                        boxShadow: 'var(--shadow-sm)',
                    }}
                >
                    🎤 {transcript}
                </motion.div>
            )}
        </div>
    );
}
