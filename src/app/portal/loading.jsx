/*
  Shared loading fallback for every route under /portal/**.
  Next.js's `loading.js` convention shows this automatically while a
  segment's Server Component (page.jsx) is awaiting its data fetch — today
  that's instant against mock data, but once the service layer is wired to
  real Firestore/Auth calls (see src/lib/services/README.md) there will be
  real network latency, and this is what covers it instead of a blank tab.
*/

export default function PortalLoading() {
  return (
    <div className="portal-loading" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>Loading…</span>
      <style>{`
        .portal-loading {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          background: var(--manuscript);
          color: var(--ink-muted);
          font-family: 'Inter', sans-serif;
          font-size: 13.5px;
          font-weight: 600;
        }
        .spinner {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2.5px solid var(--border);
          border-top-color: var(--navy);
          animation: portal-spin 0.7s linear infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .spinner { animation: none; }
        }
        @keyframes portal-spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
