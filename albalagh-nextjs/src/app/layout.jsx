import './globals.css';

const SITE_URL = 'https://www.albalagh.edu';
const TITLE = 'Al-Balagh International Premium College';
const DESCRIPTION =
  'Al-Balagh International Premium College for Islamic Sciences and Modern Civilization — official Digital Campus.';

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: `%s | ${TITLE}` },
  description: DESCRIPTION,
  applicationName: 'Al-Balagh',
  manifest: '/site.webmanifest',
  icons: {
    icon: [{ url: '/favicon.svg', type: 'image/svg+xml' }],
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    type: 'website',
    siteName: TITLE,
    title: TITLE,
    description: DESCRIPTION,
    url: SITE_URL,
  },
  twitter: {
    card: 'summary',
    title: TITLE,
    description: DESCRIPTION,
  },
};

export const viewport = {
  themeColor: '#0F2847',
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
