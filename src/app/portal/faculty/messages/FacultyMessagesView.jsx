'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';

export default function FacultyMessagesView({ messages }) {
  const [selectedId, setSelectedId] = useState(messages[0]?.id);
  const selected = messages.find((m) => m.id === selectedId);

  return (
    <PortalShell role="faculty" active="messages" title="Messages">
      <div className="inbox">
        <Card title="Inbox" className="list-card">
          <ul className="msg-list">
            {messages.map((m) => (
              <li key={m.id}>
                <button
                  type="button"
                  className={m.id === selectedId ? 'msg-row active' : 'msg-row'}
                  onClick={() => setSelectedId(m.id)}
                  aria-current={m.id === selectedId ? 'true' : undefined}
                >
                  {m.unread && <span className="dot" aria-label="Unread" />}
                  <span className="msg-text">
                    <span className="from">{m.from}</span>
                    <span className="subject">{m.subject}</span>
                  </span>
                  <span className="date">{m.date}</span>
                </button>
              </li>
            ))}
          </ul>
        </Card>

        <Card title={selected ? selected.subject : 'Select a message'} className="detail-card">
          {selected ? (
            <div className="detail">
              <div className="detail-meta">
                <span>
                  <strong>From:</strong> {selected.from}
                </span>
                <span>{selected.date}</span>
              </div>
              <p className="body">{selected.body}</p>
            </div>
          ) : (
            <p className="empty-hint">Choose a message from the inbox to read it.</p>
          )}
        </Card>
      </div>

      <style jsx>{`
        .inbox { display: grid; grid-template-columns: 320px 1fr; gap: 20px; align-items: start; }
        @media (max-width: 860px) { .inbox { grid-template-columns: 1fr; } }

        .list-card :global(.pcard-body) { padding: 0; }
        .msg-list { list-style: none; margin: 0; padding: 0; }
        .msg-list li { border-bottom: 1px solid var(--border); }
        .msg-list li:last-child { border-bottom: none; }
        .msg-row { width: 100%; display: flex; align-items: center; gap: 10px; text-align: start; background: none; border: none; padding: 14px 18px; cursor: pointer; color: var(--ink); }
        .msg-row:hover { background: var(--manuscript); }
        .msg-row.active { background: var(--manuscript); box-shadow: inset 3px 0 0 var(--navy); }
        .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--gold-ink); flex-shrink: 0; }
        .msg-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
        .from { font-size: 13px; font-weight: 600; color: var(--navy); }
        .subject { font-size: 12.5px; color: var(--ink-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .date { font-size: 11.5px; color: var(--ink-muted); flex-shrink: 0; }

        .detail-meta { display: flex; justify-content: space-between; font-size: 13px; color: var(--ink-muted); margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid var(--border); }
        .body { font-size: 14px; color: var(--ink); line-height: 1.7; margin: 0; }
        .empty-hint { font-size: 13.5px; color: var(--ink-muted); margin: 0; }
      `}</style>
    </PortalShell>
  );
}
