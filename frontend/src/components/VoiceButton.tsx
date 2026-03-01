'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';

interface VoiceButtonProps {
    language: string;
    onResult: (transcript: string) => void;
    disabled?: boolean;
}

// In-Browser Audio Encoder: Converts MediaStream to pure standard PCM WAV (.wav)
class WavRecorder {
    private audioContext: AudioContext | null = null;
    private mediaStream: MediaStream | null = null;
    private scriptProcessor: ScriptProcessorNode | null = null;
    private audioBuffers: Float32Array[] = [];

    async start() {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const source = this.audioContext.createMediaStreamSource(this.mediaStream);

        // 4096 buffer size, 1 input channel, 1 output channel
        this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
        this.audioBuffers = [];

        this.scriptProcessor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            this.audioBuffers.push(new Float32Array(inputData));
        };

        source.connect(this.scriptProcessor);
        this.scriptProcessor.connect(this.audioContext.destination);
    }

    async stop(): Promise<Blob> {
        return new Promise((resolve) => {
            if (this.scriptProcessor && this.mediaStream && this.audioContext) {
                this.scriptProcessor.disconnect();
                this.mediaStream.getTracks().forEach(track => track.stop());

                const sampleRate = this.audioContext.sampleRate;
                const wavBlob = this.encodeWAV(this.audioBuffers, sampleRate);

                this.audioContext.close().then(() => resolve(wavBlob));
            } else {
                resolve(new Blob());
            }
        });
    }

    private encodeWAV(buffers: Float32Array[], sampleRate: number): Blob {
        let bufferLength = 0;
        for (let i = 0; i < buffers.length; i++) {
            bufferLength += buffers[i].length;
        }

        const result = new Float32Array(bufferLength);
        let offset = 0;
        for (let i = 0; i < buffers.length; i++) {
            result.set(buffers[i], offset);
            offset += buffers[i].length;
        }

        const buffer = new ArrayBuffer(44 + result.length * 2);
        const view = new DataView(buffer);

        const writeString = (view: DataView, offset: number, string: string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + result.length * 2, true);
        writeString(view, 8, 'WAVE');
        writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true); // PCM encoding
        view.setUint16(22, 1, true); // 1 channel
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(view, 36, 'data');
        view.setUint32(40, result.length * 2, true);

        let writeOffset = 44;
        for (let i = 0; i < result.length; i++, writeOffset += 2) {
            const s = Math.max(-1, Math.min(1, result[i]));
            view.setInt16(writeOffset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }

        return new Blob([view], { type: 'audio/wav' });
    }
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
