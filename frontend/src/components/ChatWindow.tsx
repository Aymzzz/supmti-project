'use client';

import { RefObject } from 'react';
import { motion } from 'framer-motion';
import type { Message } from '@/app/page';
import ReactMarkdown from 'react-markdown';

interface ChatWindowProps {
    messages: Message[];
    isLoading: boolean;
    messagesEndRef: RefObject<HTMLDivElement | null>;
}

export default function ChatWindow({ messages, isLoading, messagesEndRef }: ChatWindowProps) {
    return (
        <div className="chat-messages">
            {messages.map((msg, index) => (
                <motion.div
                    key={msg.id}
                    className={`message message-${msg.role === 'user' ? 'user' : 'bot'}`}
                    initial={{ opacity: 0, y: 15, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.05 }}
                >
                    <div className="message-avatar">
                        {msg.role === 'user' ? '👤' : '🎓'}
                    </div>
                    <div
                        className="message-content"
                        dir={msg.language === 'darija' ? 'rtl' : 'ltr'}
                    >
                        {msg.role === 'assistant' ? (
                            <ReactMarkdown
                                components={{
                                    p: ({ children }) => <p style={{ margin: '4px 0' }}>{children}</p>,
                                    ul: ({ children }) => <ul style={{ paddingLeft: '16px', margin: '4px 0' }}>{children}</ul>,
                                    ol: ({ children }) => <ol style={{ paddingLeft: '16px', margin: '4px 0' }}>{children}</ol>,
                                    li: ({ children }) => <li style={{ margin: '2px 0' }}>{children}</li>,
                                    strong: ({ children }) => <strong style={{ color: 'var(--accent-cyan)' }}>{children}</strong>,
                                    h1: ({ children }) => <h3 style={{ margin: '8px 0 4px', fontSize: '16px' }}>{children}</h3>,
                                    h2: ({ children }) => <h3 style={{ margin: '8px 0 4px', fontSize: '15px' }}>{children}</h3>,
                                    h3: ({ children }) => <h4 style={{ margin: '8px 0 4px', fontSize: '14px' }}>{children}</h4>,
                                }}
                            >
                                {msg.content}
                            </ReactMarkdown>
                        ) : (
                            msg.content
                        )}

                        {/* Source badges */}
                        {msg.sources && msg.sources.length > 0 && (
                            <div style={{
                                display: 'flex',
                                flexWrap: 'wrap',
                                gap: '4px',
                                marginTop: '8px',
                                paddingTop: '8px',
                                borderTop: '1px solid var(--border-subtle)',
                            }}>
                                {msg.sources.slice(0, 3).map((src, i) => (
                                    <span
                                        key={i}
                                        style={{
                                            fontSize: '10px',
                                            padding: '2px 8px',
                                            borderRadius: 'var(--radius-full)',
                                            background: 'var(--bg-tertiary)',
                                            color: 'var(--text-muted)',
                                        }}
                                    >
                                        📄 {src.source}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>
            ))}

            {/* Typing indicator */}
            {isLoading && (
                <motion.div
                    className="message message-bot"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className="message-avatar">🎓</div>
                    <div className="message-content">
                        <div className="typing-indicator">
                            <span className="dot" />
                            <span className="dot" />
                            <span className="dot" />
                        </div>
                    </div>
                </motion.div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}
