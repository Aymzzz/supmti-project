'use client';

import { motion } from 'framer-motion';

interface SidebarProps {
    onNewChat: () => void;
    language: string;
}

const LABELS = {
    fr: {
        newChat: 'Nouvelle conversation',
        features: 'Fonctionnalités',
        chat: 'Chat textuel',
        voice: 'Interaction vocale',
        eligibility: 'Vérification d\'éligibilité',
        recommend: 'Recommandation de filière',
        multilingual: 'Multilingue (FR/EN/دارجة)',
        poweredBy: 'Propulsé par IA',
    },
    en: {
        newChat: 'New conversation',
        features: 'Features',
        chat: 'Text chat',
        voice: 'Voice interaction',
        eligibility: 'Eligibility check',
        recommend: 'Program recommendation',
        multilingual: 'Multilingual (FR/EN/دارجة)',
        poweredBy: 'Powered by AI',
    },
    darija: {
        newChat: 'محادثة جديدة',
        features: 'المميزات',
        chat: 'الدردشة النصية',
        voice: 'التفاعل الصوتي',
        eligibility: 'التحقق من الأهلية',
        recommend: 'اقتراح الفيليار',
        multilingual: 'متعدد اللغات',
        poweredBy: 'مدعوم بالذكاء الاصطناعي',
    },
};

export default function Sidebar({ onNewChat, language }: SidebarProps) {
    const labels = LABELS[language as keyof typeof LABELS] || LABELS.fr;

    return (
        <div className="chat-sidebar">
            {/* Logo */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--gradient-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '22px',
                }}>
                    🎓
                </div>
                <div>
                    <h2 style={{ fontSize: '16px', fontWeight: 700 }} className="gradient-text">SupMTI</h2>
                    <p style={{ fontSize: '10px', color: 'var(--text-muted)' }}>AI Chatbot</p>
                </div>
            </div>

            {/* New Chat Button */}
            <motion.button
                className="btn-primary"
                onClick={onNewChat}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{ width: '100%', justifyContent: 'center', marginBottom: '24px' }}
            >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                {labels.newChat}
            </motion.button>

            {/* Features List */}
            <div style={{ flex: 1 }}>
                <h3 style={{
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    color: 'var(--text-muted)',
                    marginBottom: '12px',
                }}>
                    {labels.features}
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {[
                        { icon: '💬', label: labels.chat },
                        { icon: '🎙️', label: labels.voice },
                        { icon: '✅', label: labels.eligibility },
                        { icon: '🎯', label: labels.recommend },
                        { icon: '🌍', label: labels.multilingual },
                    ].map((feature, i) => (
                        <div
                            key={i}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                padding: '8px 10px',
                                borderRadius: 'var(--radius-sm)',
                                fontSize: '13px',
                                color: 'var(--text-secondary)',
                            }}
                        >
                            <span style={{ fontSize: '14px' }}>{feature.icon}</span>
                            {feature.label}
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <div style={{
                paddingTop: '16px',
                borderTop: '1px solid var(--border-subtle)',
                fontSize: '11px',
                color: 'var(--text-muted)',
                textAlign: 'center',
            }}>
                <span style={{ fontSize: '12px' }}>⚡</span> {labels.poweredBy}
                <br />
                <span style={{ fontSize: '10px', opacity: 0.6 }}>RAG + OpenRouter</span>
            </div>
        </div>
    );
}
