'use client';

/*
  Branded 404 (App Router: this file handles every unmatched route)
  --------------------------------------------------------------------
  Bilingual and styled consistently with the rest of the real Next.js
  shell, rather than falling back to the framework's default error page.
*/

import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import { LanguageProvider, useLanguage } from '@/components/i18n/LanguageContext';
import notFoundDict from '@/data/translations/notFound';

export default function NotFound() {
  return (
    <LanguageProvider dict={notFoundDict}>
      <Header />
      <main id="main">
        <NotFoundContent />
      </main>
      <Footer />
    </LanguageProvider>
  );
}

function NotFoundContent() {
  const { t } = useLanguage();
  return (
    <section className="not-found">
      <div className="container">
        <span className="code" aria-hidden="true">404</span>
        <span className="eyebrow">{t('eyebrow')}</span>
        <h1>{t('title')}</h1>
        <p className="lead">{t('body')}</p>
        <div className="ctas">
          <a href="/" className="btn btn-primary">{t('homeCta')}</a>
          <a href="/academic-structure" className="btn btn-outline">{t('exploreCta')}</a>
        </div>
        <div className="links">
          <span className="links-heading">{t('linksHeading')}</span>
          <nav aria-label="Top-level pages">
            <a href="/about">{t('about')}</a>
            <a href="/admissions">{t('admissions')}</a>
            <a href="/academic-structure">{t('academics')}</a>
            <a href="/research-innovation">{t('research')}</a>
          </nav>
        </div>
      </div>
      <style jsx>{`
        .not-found { background: var(--manuscript); padding: 96px 0 104px; text-align: center; }
        .container { max-width: 640px; }
        .code {
          display: block;
          font-family: 'Fraunces', serif;
          font-size: 96px;
          font-weight: 600;
          color: var(--navy);
          opacity: 0.14;
          line-height: 1;
          margin-bottom: 8px;
        }
        .eyebrow { display: block; margin-bottom: 16px; }
        h1 { font-size: 30px; margin-bottom: 16px; }
        [dir='rtl'] h1 { font-size: 26px; }
        .lead { font-size: 15.5px; margin-bottom: 32px; }
        .ctas { display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; margin-bottom: 56px; }
        .links {
          border-top: 1px solid var(--border);
          padding-top: 32px;
        }
        .links-heading {
          display: block;
          font-size: 12px;
          font-weight: 600;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: var(--ink-muted);
          margin-bottom: 16px;
        }
        .links nav { display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; }
        .links nav a { font-size: 14.5px; font-weight: 600; color: var(--navy); }
        .links nav a:hover { color: var(--gold); }
      `}</style>
    </section>
  );
}
