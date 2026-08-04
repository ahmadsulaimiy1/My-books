'use client';

/*
  Footer
  ------
  Shared site footer. Same pattern as Header: one component, one place
  to fix things, instead of hand-editing the same markup across every page.
*/

import Link from 'next/link';
import { useLanguage } from '@/components/i18n/LanguageContext';

const FOOTER_STRINGS = {
  motto: { en: 'Knowledge • Character • Innovation • Service to Humanity', ar: 'العلم • الأخلاق • الابتكار • خدمة الإنسانية' },
  schoolsHeading: { en: 'Schools', ar: 'الكليات' },
  s1: { en: 'School of Islamic Sciences', ar: 'كلية العلوم الإسلامية' },
  s2: { en: 'School of Media, Journalism & Digital Communication', ar: 'كلية الإعلام والصحافة والاتصال الرقمي' },
  s3: { en: 'School of AI, Innovation & Technology', ar: 'كلية الذكاء الاصطناعي والابتكار والتقنية' },
  s4: { en: 'School of Business, Entrepreneurship & Financial Management', ar: 'كلية الأعمال وريادة الأعمال والإدارة المالية' },
  quickHeading: { en: 'Quick Links', ar: 'روابط سريعة' },
  admissions: { en: 'Admissions', ar: 'القبول' },
  research: { en: 'Research Centres', ar: 'مراكز البحث' },
  about: { en: 'About', ar: 'عن الكلية' },
  careers: { en: 'Careers', ar: 'الوظائف' },
  contactHeading: { en: 'Contact', ar: 'تواصل' },
  copy: { en: '© 2026 Albalagh Global · Founded 6 January 2024', ar: '© ٢٠٢٦ البلاغ العالمية · تأسست في ٦ يناير ٢٠٢٤' },
  accreditation: { en: 'Accreditation Status', ar: 'حالة الاعتماد' },
  privacy: { en: 'Privacy', ar: 'الخصوصية' },
  terms: { en: 'Terms', ar: 'الشروط' },
};

export default function Footer() {
  const { t, lang } = useLanguage();

  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <Link href="/" className="brand">
            <BrandMark />
            <span>{lang === 'ar' ? 'البلاغ' : 'Albalagh'}</span>
          </Link>
          <p className="motto">{FOOTER_STRINGS.motto[lang]}</p>
        </div>
        <div>
          <h4>{FOOTER_STRINGS.schoolsHeading[lang]}</h4>
          <ul>
            <li><Link href="/academic-structure#schools">{FOOTER_STRINGS.s1[lang]}</Link></li>
            <li><Link href="/academic-structure#schools">{FOOTER_STRINGS.s2[lang]}</Link></li>
            <li><Link href="/academic-structure#schools">{FOOTER_STRINGS.s3[lang]}</Link></li>
            <li><Link href="/academic-structure#schools">{FOOTER_STRINGS.s4[lang]}</Link></li>
          </ul>
        </div>
        <div>
          <h4>{FOOTER_STRINGS.quickHeading[lang]}</h4>
          <ul>
            <li><Link href="/admissions">{FOOTER_STRINGS.admissions[lang]}</Link></li>
            <li><Link href="/research-innovation">{FOOTER_STRINGS.research[lang]}</Link></li>
            <li><Link href="/about">{FOOTER_STRINGS.about[lang]}</Link></li>
            <li><Link href="#">{FOOTER_STRINGS.careers[lang]}</Link></li>
          </ul>
        </div>
        <div>
          <h4>{FOOTER_STRINGS.contactHeading[lang]}</h4>
          <ul>
            <li>admissions@albalagh.edu</li>
          </ul>
        </div>
      </div>
      <div className="container footer-bottom">
        <span>{FOOTER_STRINGS.copy[lang]}</span>
        <span>
          <Link href="#">{FOOTER_STRINGS.accreditation[lang]}</Link> ·{' '}
          <Link href="#">{FOOTER_STRINGS.privacy[lang]}</Link> ·{' '}
          <Link href="#">{FOOTER_STRINGS.terms[lang]}</Link>
        </span>
      </div>

      <style jsx>{`
        .site-footer { background: var(--navy-dark); border-top: 1px solid var(--border-dark); padding: 64px 0 0; }
        .footer-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.2fr; gap: 40px; padding-bottom: 48px; }
        @media (max-width: 860px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 560px) { .footer-grid { grid-template-columns: 1fr; } }
        .brand { display: flex; align-items: center; gap: 10px; }
        .brand span { color: #fff; font-family: 'Fraunces', serif; font-size: 19px; font-weight: 600; }
        :global([dir='rtl']) .brand span { font-family: 'Amiri', serif; }
        .motto { color: #8891A6; font-size: 13.5px; margin-top: 14px; max-width: 240px; }
        h4 { color: #fff; font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 18px; font-weight: 600; }
        ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
        ul :global(a) { color: #AEB7CC; font-size: 14px; }
        ul :global(a:hover) { color: var(--gold-light); }
        .footer-bottom { border-top: 1px solid var(--border-dark); padding: 20px 0; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; color: #7C86A0; font-size: 12.5px; }
        .footer-bottom :global(a) { color: #AEB7CC; }
        .footer-bottom :global(a:hover) { color: var(--gold-light); }
      `}</style>
    </footer>
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
