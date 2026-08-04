'use client';

/*
  PreviewBanner
  -------------
  Every portal screen (src/app/portal/**) is a frontend preview built ahead
  of the real backend (see /albalagh-lms-portal-scoping.md). This banner is
  the load-bearing honesty mechanism for that: it must render on every
  portal page, unconditionally, so nobody mistakes sample data for a real
  student/staff record. Do not make it dismissible or conditional.
*/

const STRINGS = {
  en: 'Preview Mode — this portal is a frontend preview populated with sample data. No real student, staff, or financial records exist yet.',
  ar: 'وضع المعاينة — هذه البوابة معاينة للواجهة الأمامية معبأة ببيانات تجريبية. لا توجد سجلات طلابية أو إدارية أو مالية حقيقية بعد.',
};

export default function PreviewBanner({ lang = 'en' }) {
  return (
    <div className="preview-banner" role="status">
      <span className="dot" aria-hidden="true" />
      <span>{STRINGS[lang] ?? STRINGS.en}</span>
      <style jsx>{`
        .preview-banner {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(188, 154, 74, 0.12);
          border-bottom: 1px solid var(--border);
          color: var(--navy);
          font-size: 12.5px;
          font-weight: 500;
          padding: 10px 20px;
          text-align: center;
          justify-content: center;
        }
        .dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: var(--gold);
          flex-shrink: 0;
        }
      `}</style>
    </div>
  );
}
