import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'SupMTI – Assistant Intelligent d\'Orientation',
    description: 'Chatbot IA vocal et textuel pour l\'orientation scolaire à SupMTI. Découvrez nos filières, vérifiez votre éligibilité, et trouvez votre voie en Darija, Français ou Anglais.',
    keywords: ['SupMTI', 'chatbot', 'orientation', 'école', 'ingénieur', 'Maroc', 'IA'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="fr">
            <body>{children}</body>
        </html>
    );
}
