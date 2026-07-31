'use client';

/*
  Homepage (App Router: this file = the "/" route)
  --------------------------------------------------
  A real, working conversion of homepage.html into componentized Next.js —
  demonstrating the target architecture the rest of the site is migrating
  toward. See /docs/MIGRATION.md for what's converted vs. still static HTML.
*/

import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import { LanguageProvider, useLanguage } from '@/components/i18n/LanguageContext';
import homepageDict from '@/data/translations/homepage';

export default function HomePage() {
  return (
    <LanguageProvider dict={homepageDict}>
      <Header />
      <main id="main">
        <Hero />
        <WhySection />
        <SchoolsSection />
        <CtaSection />
        <ContactSection />
      </main>
      <Footer />
    </LanguageProvider>
  );
}

function Hero() {
  const { t } = useLanguage();
  return (
    <section className="hero">
      <div className="container">
        <span className="eyebrow">{t('heroEyebrow')}</span>
        <h1>{t('heroTitle')}</h1>
        <p className="lead">{t('heroLead')}</p>
        <div className="hero-ctas">
          <a href="/admissions#apply" className="btn btn-primary">{t('heroCta1')}</a>
          <a href="/academic-structure" className="btn btn-outline-light">{t('heroCta2')}</a>
        </div>
      </div>
      <style jsx>{`
        .hero { background: var(--navy-dark); padding: 96px 0 88px; }
        h1 { color: #fff; font-size: 44px; max-width: 760px; margin-bottom: 18px; }
        [dir='rtl'] h1 { font-size: 38px; line-height: 1.4; }
        @media (max-width: 600px) { h1 { font-size: 28px; } }
        .lead { color: #C7CEDC; font-size: 17px; max-width: 640px; margin-bottom: 32px; }
        .hero-ctas { display: flex; gap: 14px; flex-wrap: wrap; }
        .btn-outline-light { border: 1.5px solid rgba(255,255,255,0.5); color: #fff; display: inline-flex; align-items: center; padding: 13px 28px; border-radius: var(--radius-md); font-weight: 600; }
      `}</style>
    </section>
  );
}

function WhySection() {
  const { t } = useLanguage();
  const items = [
    ['why1Title', 'why1Body'],
    ['why2Title', 'why2Body'],
    ['why3Title', 'why3Body'],
    ['why4Title', 'why4Body'],
  ];
  return (
    <section className="why">
      <div className="container">
        <span className="eyebrow">{t('whyEyebrow')}</span>
        <h2>{t('whyTitle')}</h2>
        <div className="grid">
          {items.map(([titleKey, bodyKey]) => (
            <div className="tile" key={titleKey}>
              <h3>{t(titleKey)}</h3>
              <p>{t(bodyKey)}</p>
            </div>
          ))}
        </div>
      </div>
      <style jsx>{`
        .why { padding: 88px 0; background: var(--surface); }
        h2 { font-size: 32px; margin-bottom: 44px; max-width: 600px; }
        [dir='rtl'] h2 { font-size: 28px; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        @media (max-width: 960px) { .grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }
        .tile { background: var(--manuscript); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 26px; }
        .tile h3 { font-size: 16.5px; margin-bottom: 8px; }
        .tile p { font-size: 13.5px; }
      `}</style>
    </section>
  );
}

function SchoolsSection() {
  const { t } = useLanguage();
  const schools = [
    { key: 's1', href: '/academic-structure#schools' },
    { key: 's2', href: '/academic-structure#schools' },
    { key: 's3', href: '/academic-structure#schools' },
    { key: 's4', href: '/academic-structure#schools' },
  ];
  return (
    <section className="schools">
      <div className="container">
        <span className="eyebrow">{t('schoolsEyebrow')}</span>
        <h2>{t('schoolsTitle')}</h2>
        <div className="grid">
          {schools.map((s) => (
            <a className="card" href={s.href} key={s.key}>
              <h3>{t(s.key)}</h3>
              <span>{t('learnMore')} →</span>
            </a>
          ))}
        </div>
      </div>
      <style jsx>{`
        .schools { padding: 88px 0; background: var(--manuscript); }
        h2 { font-size: 32px; margin-bottom: 44px; }
        [dir='rtl'] h2 { font-size: 28px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }
        .card { display: block; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 28px; transition: box-shadow 0.15s, transform 0.15s; }
        .card:hover { box-shadow: var(--shadow-2); transform: translateY(-2px); }
        .card h3 { font-size: 18px; margin-bottom: 10px; }
        .card span { font-size: 13px; font-weight: 600; color: var(--gold); }
      `}</style>
    </section>
  );
}

function CtaSection() {
  const { t } = useLanguage();
  return (
    <section className="cta-section">
      <div className="container">
        <div className="cta-final">
          <h2>{t('ctaTitle')}</h2>
          <p>{t('ctaBody')}</p>
          <a href="/admissions#apply" className="btn btn-primary">{t('ctaBtn')}</a>
        </div>
      </div>
      <style jsx>{`
        .cta-section { padding: 88px 0; background: var(--surface); }
        .cta-final { background: linear-gradient(135deg, var(--navy) 0%, var(--navy-dark) 100%); border-radius: var(--radius-lg); padding: 56px 48px; text-align: center; }
        .cta-final h2 { color: #fff; font-size: 30px; margin-bottom: 14px; }
        .cta-final p { color: #C7CEDC; max-width: 560px; margin: 0 auto 28px; }
      `}</style>
    </section>
  );
}

function ContactSection() {
  const { t } = useLanguage();
  return (
    <section id="contact" className="contact">
      <div className="container">
        <h2>{t('contactHeading')}</h2>
        <p>{t('contactBody')}</p>
      </div>
      <style jsx>{`
        .contact { padding: 88px 0; background: var(--manuscript); text-align: center; }
        h2 { font-size: 28px; margin-bottom: 12px; }
      `}</style>
    </section>
  );
}
