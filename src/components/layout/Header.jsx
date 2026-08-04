'use client';

/*
  Header
  ------
  Shared sticky navigation used on every public page (Homepage, About,
  Academic Structure, Admissions, etc). Includes the functional mobile
  hamburger menu (the one earlier phases of this project had to
  back-port to older static pages by hand — here it's one component,
  so that problem structurally cannot recur).
*/

import { useState, useRef } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/components/i18n/LanguageContext';

const NAV_LINKS = [
  { href: '/academic-structure', key: 'navSchools' },
  { href: '/admissions', key: 'navAdmissions' },
  { href: '/research-innovation', key: 'navResearch' },
  { href: '/about', key: 'navAbout' },
  { href: '/#contact', key: 'navContact' },
];

const HEADER_STRINGS = {
  brand: { en: 'Albalagh', ar: 'البلاغ' },
  navSchools: { en: 'Schools', ar: 'الكليات' },
  navAdmissions: { en: 'Admissions', ar: 'القبول' },
  navResearch: { en: 'Research Centres', ar: 'مراكز البحث' },
  navAbout: { en: 'About', ar: 'عن الكلية' },
  navContact: { en: 'Contact', ar: 'تواصل' },
  applyNow: { en: 'Apply Now', ar: 'قدّم الآن' },
  langToggle: { en: 'عربي', ar: 'English' },
};

export default function Header() {
  const { t, lang, toggleLang } = useLanguage();
  const [open, setOpen] = useState(false);
  const lastFocused = useRef(null);

  function openMenu() {
    lastFocused.current = document.activeElement;
    setOpen(true);
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    setOpen(false);
    document.body.style.overflow = '';
    lastFocused.current?.focus?.();
  }

  return (
    <>
      <header className="site-header">
        <div className="container nav-inner">
          <Link href="/" className="brand">
            <BrandMark />
            <span>{HEADER_STRINGS.brand[lang]}</span>
          </Link>

          <nav className="links" aria-label="Primary">
            {NAV_LINKS.map((link) => (
              <Link key={link.key} href={link.href}>
                {HEADER_STRINGS[link.key][lang]}
              </Link>
            ))}
          </nav>

          <div className="nav-right">
            <button className="lang-toggle" onClick={toggleLang} type="button">
              {HEADER_STRINGS.langToggle[lang]}
            </button>
            <Link href="/admissions#apply" className="btn btn-primary">
              {HEADER_STRINGS.applyNow[lang]}
            </Link>
            <button
              className="hamburger"
              aria-label="Open menu"
              aria-expanded={open}
              aria-controls="mobileNav"
              onClick={openMenu}
              type="button"
            >
              ☰
            </button>
          </div>
        </div>
      </header>

      <div
        className={`mobile-nav ${open ? 'open' : ''}`}
        id="mobileNav"
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
      >
        <div className="mobile-nav-top">
          <Link href="/" className="brand" onClick={closeMenu}>
            <BrandMark />
            <span>{HEADER_STRINGS.brand[lang]}</span>
          </Link>
          <button className="mobile-nav-close" aria-label="Close menu" onClick={closeMenu} type="button">
            ✕
          </button>
        </div>
        <nav className="mobile-nav-links" aria-label="Mobile Primary">
          {NAV_LINKS.map((link) => (
            <Link key={link.key} href={link.href} onClick={closeMenu}>
              {HEADER_STRINGS[link.key][lang]}
            </Link>
          ))}
        </nav>
        <div className="mobile-nav-bottom">
          <button className="lang-toggle" style={{ width: '100%', padding: 12 }} onClick={toggleLang} type="button">
            {HEADER_STRINGS.langToggle[lang]}
          </button>
          <Link href="/admissions#apply" className="btn btn-primary" style={{ justifyContent: 'center' }} onClick={closeMenu}>
            {HEADER_STRINGS.applyNow[lang]}
          </Link>
        </div>
      </div>

      <style jsx>{`
        .site-header { position: sticky; top: 0; z-index: 100; background: var(--navy-dark); border-bottom: 1px solid var(--border-dark); }
        .nav-inner { display: flex; align-items: center; justify-content: space-between; height: 76px; }
        .brand { display: flex; align-items: center; gap: 10px; }
        .brand span { color: #fff; font-family: 'Fraunces', serif; font-size: 19px; font-weight: 600; }
        :global([dir='rtl']) .brand span { font-family: 'Amiri', serif; font-size: 20px; }
        .links { display: flex; align-items: center; gap: 32px; }
        .links a { color: #EDEEF2; font-size: 14.5px; font-weight: 500; opacity: 0.9; }
        .links a:hover { opacity: 1; }
        .nav-right { display: flex; align-items: center; gap: 20px; }
        .lang-toggle { background: transparent; border: 1px solid var(--border-dark); color: #fff; font-size: 13px; font-weight: 600; padding: 7px 14px; border-radius: var(--radius-sm); cursor: pointer; }
        .lang-toggle:hover { border-color: var(--gold); color: var(--gold); }
        .hamburger { display: none; background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; line-height: 1; padding: 4px; }
        @media (max-width: 960px) {
          .links { display: none; }
          .hamburger { display: block; }
          .nav-right :global(.btn-primary) { display: none; }
        }
        .mobile-nav { position: fixed; inset: 0; background: var(--navy-dark); z-index: 200; display: flex; flex-direction: column; padding: 24px; transform: translateX(100%); transition: transform 0.25s ease; visibility: hidden; }
        :global([dir='rtl']) .mobile-nav { transform: translateX(-100%); }
        .mobile-nav.open { transform: translateX(0); visibility: visible; }
        .mobile-nav-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 48px; }
        .mobile-nav-close { background: none; border: none; color: #fff; font-size: 28px; cursor: pointer; line-height: 1; }
        .mobile-nav-links { display: flex; flex-direction: column; gap: 8px; }
        .mobile-nav-links a { color: #fff; font-size: 22px; font-family: 'Fraunces', serif; padding: 14px 0; border-bottom: 1px solid var(--border-dark); }
        :global([dir='rtl']) .mobile-nav-links a { font-family: 'Amiri', serif; }
        .mobile-nav-bottom { margin-top: auto; display: flex; flex-direction: column; gap: 16px; }
        @media (prefers-reduced-motion: reduce) { .mobile-nav { transition: none; } }
      `}</style>
    </>
  );
}

function BrandMark() {
  return (
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none" aria-hidden="true">
      <path
        d="M24 4 L30 14 L42 14 L33 22 L37 34 L24 27 L11 34 L15 22 L6 14 L18 14 Z"
        stroke="var(--gold)"
        strokeWidth="1.6"
        fill="none"
      />
    </svg>
  );
}
