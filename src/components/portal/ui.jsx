'use client';

/*
  Shared portal UI primitives — Card, StatTile, Badge, DataTable, EmptyState.
  Every portal screen should build from these rather than hand-rolling its
  own card/table/badge markup, so the whole portal ecosystem stays visually
  and structurally consistent (see Priority 5: "no duplicate components").
*/

export function Card({ title, action, children, className = '' }) {
  return (
    <section className={`pcard ${className}`}>
      {(title || action) && (
        <div className="pcard-head">
          {title && <h2>{title}</h2>}
          {action}
        </div>
      )}
      <div className="pcard-body">{children}</div>
      <style jsx>{`
        .pcard { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); box-shadow: var(--shadow-1); }
        .pcard-head { display: flex; align-items: center; justify-content: space-between; padding: 18px 22px; border-bottom: 1px solid var(--border); }
        .pcard-head h2 { font-family: 'Fraunces', serif; font-size: 17px; color: var(--navy); margin: 0; }
        .pcard-body { padding: 22px; }
      `}</style>
    </section>
  );
}

export function StatGrid({ children }) {
  return (
    <div className="stat-grid">
      {children}
      <style jsx>{`
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
      `}</style>
    </div>
  );
}

export function StatTile({ label, value, hint }) {
  return (
    <div className="stat-tile">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
      {hint && <span className="hint">{hint}</span>}
      <style jsx>{`
        .stat-tile { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 18px 20px; display: flex; flex-direction: column; gap: 4px; }
        .label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-muted); }
        .value { font-family: 'Fraunces', serif; font-size: 26px; color: var(--navy); }
        .hint { font-size: 12.5px; color: var(--ink-muted); }
      `}</style>
    </div>
  );
}

const BADGE_TONES = {
  neutral: { bg: 'var(--manuscript)', fg: 'var(--ink-muted)', border: 'var(--border)' },
  gold: { bg: 'rgba(188,154,74,0.12)', fg: '#8A6A2E', border: 'rgba(188,154,74,0.35)' },
  success: { bg: 'rgba(30,76,67,0.08)', fg: 'var(--emerald)', border: 'rgba(30,76,67,0.25)' },
  alert: { bg: 'rgba(178,58,58,0.08)', fg: '#B23A3A', border: 'rgba(178,58,58,0.25)' },
  info: { bg: 'rgba(23,58,99,0.06)', fg: 'var(--navy)', border: 'rgba(23,58,99,0.2)' },
};

export function Badge({ tone = 'neutral', children }) {
  const t = BADGE_TONES[tone] ?? BADGE_TONES.neutral;
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        fontSize: 12,
        fontWeight: 600,
        padding: '4px 10px',
        borderRadius: 999,
        background: t.bg,
        color: t.fg,
        border: `1px solid ${t.border}`,
      }}
    >
      {children}
    </span>
  );
}

export function DataTable({ columns, rows, emptyLabel = 'No records yet.' }) {
  if (!rows?.length) return <EmptyState message={emptyLabel} />;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} scope="col">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.id ?? i}>
              {columns.map((c) => (
                <td key={c.key}>{c.render ? c.render(row) : row[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <style jsx>{`
        .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: var(--radius-md); }
        table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
        th { text-align: start; background: var(--manuscript); color: var(--ink-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600; padding: 12px 16px; border-bottom: 1px solid var(--border); }
        td { padding: 12px 16px; border-bottom: 1px solid var(--border); color: var(--ink); }
        tr:last-child td { border-bottom: none; }
      `}</style>
    </div>
  );
}

export function EmptyState({ message, action }) {
  return (
    <div className="empty">
      <svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true">
        <rect x="6" y="10" width="28" height="22" rx="2" stroke="#BC9A4A" strokeWidth="1.5" />
        <path d="M6 16h28" stroke="#BC9A4A" strokeWidth="1.5" />
      </svg>
      <p>{message}</p>
      {action}
      <style jsx>{`
        .empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 40px 20px; text-align: center; color: var(--ink-muted); font-size: 13.5px; }
      `}</style>
    </div>
  );
}
