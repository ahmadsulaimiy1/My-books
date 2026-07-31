import './globals.css';

export const metadata = {
  title: 'Al-Balagh International Premium College',
  description:
    'Al-Balagh International Premium College for Islamic Sciences and Modern Civilization — official Digital Campus.',
};

// Root layout: intentionally minimal. Language direction (lang/dir) is set
// client-side per-page by LanguageProvider, since the language toggle is an
// instant client-side switch rather than a route change (see
// src/components/i18n/LanguageContext.jsx).
export default function RootLayout({ children }) {
  return (
    <html lang="en" dir="ltr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&family=Amiri:wght@400;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
