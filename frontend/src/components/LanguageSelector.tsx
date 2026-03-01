'use client';

import { motion } from 'framer-motion';

interface LanguageSelectorProps {
    language: string;
    onLanguageChange: (lang: 'fr' | 'en' | 'darija') => void;
}

const LANGUAGES = [
    { code: 'fr' as const, label: 'FR', flag: '🇫🇷' },
    { code: 'en' as const, label: 'EN', flag: '🇬🇧' },
    { code: 'darija' as const, label: 'دارجة', flag: '🇲🇦' },
];

export default function LanguageSelector({ language, onLanguageChange }: LanguageSelectorProps) {
    return (
        <div className="language-selector">
            {LANGUAGES.map((lang) => (
                <motion.button
                    key={lang.code}
                    className={`language-option ${language === lang.code ? 'active' : ''}`}
                    onClick={() => onLanguageChange(lang.code)}
                    whileTap={{ scale: 0.95 }}
                    layout
                >
                    {lang.flag} {lang.label}
                </motion.button>
            ))}
        </div>
    );
}
