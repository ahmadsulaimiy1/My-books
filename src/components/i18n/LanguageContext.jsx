'use client';

/*
  LanguageContext
  ----------------
  A single, reusable EN/AR language provider used by every page and portal.
  Each page/portal supplies its own translation dictionary (see
  src/data/translations/*.js) via the `dict` prop; this context only owns
  the *current language* and the *toggle* logic, plus the <html lang/dir>
  side effect, so every page behaves identically.

  Usage:
    <LanguageProvider dict={homepageDict}>
      <YourPageContent />
    </LanguageProvider>

  Inside any child component:
    const { lang, t, toggleLang } = useLanguage();
    <h1>{t('heroTitle')}</h1>
*/

import { createContext, useContext, useEffect, useState, useCallback } from 'react';

const LanguageContext = createContext(null);

export function LanguageProvider({ dict, children, defaultLang = 'en' }) {
  const [lang, setLang] = useState(defaultLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  }, [lang]);

  const toggleLang = useCallback(() => {
    setLang((prev) => (prev === 'en' ? 'ar' : 'en'));
  }, []);

  // t(key) looks up the key in the current language's dictionary,
  // falling back to the English string (or the key itself) if missing,
  // so a missing Arabic translation never breaks the page.
  const t = useCallback(
    (key) => {
      const entry = dict?.[key];
      if (!entry) return key;
      return entry[lang] ?? entry.en ?? key;
    },
    [dict, lang]
  );

  return (
    <LanguageContext.Provider value={{ lang, setLang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error('useLanguage must be used within a <LanguageProvider>');
  }
  return ctx;
}
