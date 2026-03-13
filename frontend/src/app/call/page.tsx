'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { WavRecorder } from '../../utils/audioEncoder';

type CallState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

export default function CallPage() {
    const [callState, setCallState] = useState<CallState>('idle');
    const [transcript, setTranscript] = useState<string>('');
    const [response, setResponse] = useState<string>('');
    const [language, setLanguage] = useState<'fr' | 'en' | 'darija'>('fr');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const recorderRef = useRef<WavRecorder | null>(null);
    const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

    // Stop speaking if unmounted or leaving page
    useEffect(() => {
        return () => {
            if (audioPlayerRef.current) {
                audioPlayerRef.current.pause();
                audioPlayerRef.current = null;
            }
            if (recorderRef.current) {
                // If unmounted, force stop without awaiting to release mic
                recorderRef.current.stop().catch(() => {});
            }
        };
    }, []);

    const startRecording = async () => {
        try {
            setCallState('listening');
            setTranscript('');
            setResponse('');

            if (audioPlayerRef.current) {
                audioPlayerRef.current.pause();
                audioPlayerRef.current = null;
            }

            const recorder = new WavRecorder();
            recorderRef.current = recorder;
            await recorder.start();

        } catch (error) {
            console.error('Error accessing microphone:', error);
            setCallState('error');
            setTimeout(() => setCallState('idle'), 2000);
        }
    };

    const stopRecording = async () => {
        if (recorderRef.current && callState === 'listening') {
            const wavBlob = await recorderRef.current.stop();
            // A valid WAV file always has a 44-byte header. If it's 44 or 0 bytes, no audio recorded.
            if (wavBlob.size <= 44) {
                setCallState('idle');
                return;
            }
            await processAudio(wavBlob);
        }
    };

    const processAudio = async (audioBlob: Blob) => {
        setCallState('thinking');
        try {
            // 1. Transcribe
            const formData = new FormData();
            formData.append('audio', audioBlob, 'speech.wav');
            formData.append('language', language);

            const sttRes = await fetch('/api/voice/transcribe', {
                method: 'POST',
                body: formData,
            });

            if (!sttRes.ok) throw new Error('Transcription failed');
            const sttData = await sttRes.json();
            const userText = sttData.transcript;

            if (!userText) {
                setCallState('idle');
                setTranscript("Désolé, je n'ai rien entendu.");
                setTimeout(() => setTranscript(''), 2000);
                return;
            }

            setTranscript(userText);

            // 2. Chat (LLM via RAG)
            const chatRes = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userText,
                    session_id: sessionId,
                    language,
                }),
            });

            if (!chatRes.ok) throw new Error('Chat generation failed');
            const chatData = await chatRes.json();
            setResponse(chatData.answer);
            if (chatData.session_id) setSessionId(chatData.session_id);

            // 3. TTS
            setCallState('speaking');
            const ttsRes = await fetch('/api/voice/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: chatData.answer,
                    language: chatData.language || language,
                }),
            });

            if (!ttsRes.ok) throw new Error('TTS failed');
            const audioBlobTTS = await ttsRes.blob();
            const audioUrl = URL.createObjectURL(audioBlobTTS);

            const audio = new Audio(audioUrl);
            audioPlayerRef.current = audio;
            
            audio.onended = () => {
                setCallState('idle');
            };

            audio.play().catch(e => {
                console.error("Audio playback prevented:", e);
                setCallState('idle');
            });

        } catch (error) {
            console.error('Processing error:', error);
            setCallState('error');
            setTimeout(() => setCallState('idle'), 3000);
        }
    };

    return (
        <div style={{
            display: 'flex', flexDirection: 'column', height: '100vh', 
            justifyContent: 'center', alignItems: 'center', 
            background: 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%)',
            color: 'var(--text-primary)', fontFamily: 'system-ui, sans-serif'
        }}>
            <div style={{ position: 'absolute', top: '20px', left: '20px' }}>
                <Link href="/" style={{
                    padding: '10px 15px', background: 'rgba(255,255,255,0.1)', 
                    borderRadius: '8px', textDecoration: 'none', color: 'inherit',
                    display: 'flex', alignItems: 'center', gap: '8px',
                    backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.2)'
                }}>
                    ⬅️ Retour / 🔙
                </Link>
            </div>

            <div style={{ position: 'absolute', top: '20px', right: '20px' }}>
                <select 
                    value={language} 
                    onChange={(e) => setLanguage(e.target.value as any)}
                    style={{
                        padding: '10px 15px', background: 'rgba(255,255,255,0.1)',
                        borderRadius: '8px', color: 'inherit', border: '1px solid rgba(255,255,255,0.2)',
                        appearance: 'none', cursor: 'pointer', outline: 'none'
                    }}
                >
                    <option value="fr">Français 🇫🇷</option>
                    <option value="darija">Darija 🇲🇦</option>
                    <option value="en">English 🇬🇧</option>
                </select>
            </div>

            <motion.div
                animate={{
                    scale: callState === 'listening' ? [1, 1.1, 1] : 
                           callState === 'speaking' ? [1, 1.05, 1] : 1,
                }}
                transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
                style={{
                    width: '180px', height: '180px', borderRadius: '50%',
                    background: callState === 'idle' ? 'linear-gradient(135deg, #4f46e5, #3b82f6)' :
                                callState === 'listening' ? 'linear-gradient(135deg, #ef4444, #f97316)' :
                                callState === 'thinking' ? 'linear-gradient(135deg, #8b5cf6, #d946ef)' :
                                callState === 'speaking' ? 'linear-gradient(135deg, #10b981, #3b82f6)' :
                                'linear-gradient(135deg, #64748b, #94a3b8)',
                    display: 'flex', justifyContent: 'center', alignItems: 'center',
                    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                    cursor: 'pointer', border: '4px solid rgba(255,255,255,0.1)',
                    marginBottom: '40px'
                }}
                onClick={() => {
                    if (callState === 'idle') startRecording();
                    else if (callState === 'listening') stopRecording();
                }}
            >
                <span style={{ fontSize: '4rem' }}>
                    {callState === 'idle' ? '📞' : 
                     callState === 'listening' ? '🎙️' : 
                     callState === 'thinking' ? '⏳' : 
                     callState === 'speaking' ? '🔊' : '❌'}
                </span>
            </motion.div>

            <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '8px', textAlign: 'center' }}>
                {callState === 'idle' ? (language === 'fr' ? 'Cliquez pour parler' : language === 'darija' ? 'كليكي و هضر' : 'Click to speak') :
                 callState === 'listening' ? (language === 'fr' ? 'Je vous écoute... (Cliquez pour arrêter)' : language === 'darija' ? 'كنسمعك... (كليكي باش تحبس)' : 'Listening... (Click to stop)') :
                 callState === 'thinking' ? (language === 'fr' ? 'Je réfléchis...' : language === 'darija' ? 'كنفكر...' : 'Thinking...') :
                 callState === 'speaking' ? 'SupMTI Assistant' : 'Erreur'}
            </h2>

            <p style={{ 
                color: 'var(--text-secondary)', fontSize: '16px', maxWidth: '400px', 
                textAlign: 'center', minHeight: '60px', opacity: 0.8
            }}>
                {callState === 'speaking' && response ? `"${response}"` : 
                 callState === 'listening' ? '...' : 
                 transcript ? `"${transcript}"` : ''}
            </p>
        </div>
    );
}
