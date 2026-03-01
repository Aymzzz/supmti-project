'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatWindow from '@/components/ChatWindow';
import VoiceButton from '@/components/VoiceButton';
import LanguageSelector from '@/components/LanguageSelector';
import Sidebar from '@/components/Sidebar';

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    language?: string;
    sources?: Array<{ source: string; category: string; score: number }>;
}

const SUGGESTED_QUESTIONS = {
    fr: [
        "Quelles filières proposez-vous ?",
        "Suis-je éligible avec un Bac Sciences Maths ?",
        "Quels sont les frais de scolarité ?",
        "Comment s'inscrire ?",
        "Quels sont les débouchés en informatique ?",
    ],
    en: [
        "What programs do you offer?",
        "Am I eligible with a Science Bac?",
        "What are the tuition fees?",
        "How to apply?",
        "What career paths in computer engineering?",
    ],
    darija: [
        "شنو هما الفيليارات اللي عندكم؟",
        "واش نقدر ندخل بالباك ديال العلوم؟",
        "شحال الثمن ديال الدراسة؟",
        "كيفاش نتسجل؟",
        "شنو المستقبل ديال المعلوميات؟",
    ],
};

export default function HomePage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [language, setLanguage] = useState<'fr' | 'en' | 'darija'>('fr');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const inputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const sendMessage = async (text: string) => {
        if (!text.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: text.trim(),
            timestamp: new Date(),
            language,
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text.trim(),
                    session_id: sessionId,
                    language,
                }),
            });

            if (!response.ok) throw new Error('Failed to get response');

            const data = await response.json();

            if (data.session_id) setSessionId(data.session_id);

            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.answer,
                timestamp: new Date(),
                language: data.language,
                sources: data.sources,
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: language === 'fr'
                    ? 'Désolé, une erreur est survenue. Veuillez réessayer.'
                    : language === 'darija'
                        ? 'سمحلي، كاين مشكل. عاود جرب من بعد.'
                        : 'Sorry, an error occurred. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            inputRef.current?.focus();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputValue);
        }
    };

    const handleVoiceResult = (transcript: string) => {
        if (transcript) {
            sendMessage(transcript);
        }
    };

    const handleNewChat = () => {
        setMessages([]);
        setSessionId(null);
        inputRef.current?.focus();
    };

    const currentSuggestions = SUGGESTED_QUESTIONS[language] || SUGGESTED_QUESTIONS.fr;

    return (
        <div className="chat-container">
            {/* Sidebar */}
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        initial={{ x: -280, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: -280, opacity: 0 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    >
                        <Sidebar
                            onNewChat={handleNewChat}
                            language={language}
                        />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Chat Area */}
            <div className="chat-main">
                {/* Header */}
                <header className="chat-header glass-strong">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <button
                            className="btn-icon"
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            aria-label="Toggle sidebar"
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <line x1="3" y1="12" x2="21" y2="12" />
                                <line x1="3" y1="6" x2="21" y2="6" />
                                <line x1="3" y1="18" x2="21" y2="18" />
                            </svg>
                        </button>
                        <div>
                            <h1 style={{ fontSize: '16px', fontWeight: 700 }}>
                                <span className="gradient-text">SupMTI</span> Assistant
                            </h1>
                            <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                {language === 'fr' ? 'Assistant d\'orientation intelligent' :
                                    language === 'darija' ? 'مساعد التوجيه الذكي' :
                                        'Intelligent orientation assistant'}
                            </p>
                        </div>
                    </div>

                    <LanguageSelector
                        language={language}
                        onLanguageChange={setLanguage}
                    />
                </header>

                {/* Messages or Welcome */}
                {messages.length === 0 ? (
                    <div className="welcome-container">
                        <motion.div
                            className="welcome-logo"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: 'spring', damping: 10, stiffness: 100 }}
                        >
                            🎓
                        </motion.div>
                        <motion.h2
                            className="welcome-title"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            {language === 'fr' ? (
                                <>Bienvenue à <span className="gradient-text">SupMTI</span></>
                            ) : language === 'darija' ? (
                                <>مرحبا بيك ف <span className="gradient-text">SupMTI</span></>
                            ) : (
                                <>Welcome to <span className="gradient-text">SupMTI</span></>
                            )}
                        </motion.h2>
                        <motion.p
                            className="welcome-subtitle"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                        >
                            {language === 'fr'
                                ? 'Je suis votre assistant intelligent. Posez-moi vos questions sur les filières, l\'admission, ou l\'éligibilité.'
                                : language === 'darija'
                                    ? 'أنا المساعد الذكي ديالك. سولني على الفيليارات، التسجيل، ولا الأهلية.'
                                    : 'I\'m your intelligent assistant. Ask me about programs, admissions, or eligibility.'}
                        </motion.p>
                        <motion.div
                            className="suggested-questions"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 }}
                        >
                            {currentSuggestions.map((q, i) => (
                                <motion.button
                                    key={i}
                                    className="suggested-question"
                                    onClick={() => sendMessage(q)}
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.97 }}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.5 + i * 0.08 }}
                                >
                                    {q}
                                </motion.button>
                            ))}
                        </motion.div>
                    </div>
                ) : (
                    <ChatWindow
                        messages={messages}
                        isLoading={isLoading}
                        messagesEndRef={messagesEndRef}
                    />
                )}

                {/* Input Area */}
                <div className="chat-input-area">
                    <div className="input-container">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={
                                language === 'fr' ? 'Posez votre question...' :
                                    language === 'darija' ? '...كتب السؤال ديالك' :
                                        'Ask your question...'
                            }
                            dir={language === 'darija' ? 'rtl' : 'ltr'}
                            disabled={isLoading}
                        />
                        <VoiceButton
                            language={language}
                            onResult={handleVoiceResult}
                            disabled={isLoading}
                        />
                        <button
                            className="send-btn"
                            onClick={() => sendMessage(inputValue)}
                            disabled={!inputValue.trim() || isLoading}
                            aria-label="Send message"
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="22" y1="2" x2="11" y2="13" />
                                <polygon points="22 2 15 22 11 13 2 9 22 2" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
