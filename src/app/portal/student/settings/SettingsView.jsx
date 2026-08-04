'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';
import { updateSettings } from '@/lib/services/studentService';

const NOTIFICATION_TOGGLES = [
  { key: 'assignmentReminders', label: 'Assignment due-date reminders' },
  { key: 'quizAlerts', label: 'New quiz alerts' },
  { key: 'resultUpdates', label: 'Result & transcript updates' },
  { key: 'messageAlerts', label: 'New message alerts' },
];

export default function SettingsView() {
  const [language, setLanguage] = useState('en');
  const [toggles, setToggles] = useState({
    assignmentReminders: true,
    quizAlerts: true,
    resultUpdates: true,
    messageAlerts: false,
  });
  const [savedNote, setSavedNote] = useState('');
  const [saving, setSaving] = useState(false);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setSavedNote('');
    await updateSettings({ language, notifications: toggles });
    setSaving(false);
    setSavedNote('Preferences updated for this session. This is a preview — nothing is saved to a server yet.');
  }

  return (
    <PortalShell role="student" active="settings" title="Settings">
      <form onSubmit={handleSave}>
        <Card title="Language preference" className="settings-card">
          <div className="field-row">
            <label htmlFor="language-select">Portal language</label>
            <select
              id="language-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="ar">Arabic (coming soon)</option>
            </select>
          </div>
          <p className="hint">
            The portal preview is English-first for now. Arabic support will follow the public site&apos;s bilingual
            experience once the portal is connected to a real backend.
          </p>
        </Card>

        <Card title="Notification preferences" className="settings-card">
          <ul className="toggle-list">
            {NOTIFICATION_TOGGLES.map((t) => (
              <li key={t.key}>
                <label htmlFor={t.key}>
                  <input
                    type="checkbox"
                    id={t.key}
                    checked={toggles[t.key]}
                    onChange={(e) =>
                      setToggles((prev) => ({ ...prev, [t.key]: e.target.checked }))
                    }
                  />
                  <span>{t.label}</span>
                </label>
              </li>
            ))}
          </ul>
        </Card>

        <div className="save-row">
          <button type="submit" className="save-btn" disabled={saving}>
            {saving ? 'Saving…' : 'Save preferences'}
          </button>
          {savedNote && (
            <p className="saved-note" role="status">
              {savedNote}
            </p>
          )}
        </div>
      </form>

      <style jsx>{`
        .settings-card { margin-bottom: 20px; }
        .field-row { display: flex; align-items: center; gap: 14px; margin-bottom: 12px; flex-wrap: wrap; }
        .field-row label { font-size: 13.5px; font-weight: 600; color: var(--ink); }
        .field-row select { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 12px; font-size: 13.5px; color: var(--ink); background: var(--surface); min-width: 200px; }
        .hint { font-size: 12.5px; color: var(--ink-muted); line-height: 1.6; margin: 0; }

        .toggle-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
        .toggle-list label { display: flex; align-items: center; gap: 10px; font-size: 13.5px; color: var(--ink); cursor: pointer; }
        .toggle-list input { accent-color: var(--navy); width: 17px; height: 17px; flex-shrink: 0; }

        .save-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
        .save-btn { background: var(--navy); color: #fff; border: none; border-radius: var(--radius-sm); padding: 10px 22px; font-size: 13.5px; font-weight: 600; cursor: pointer; }
        .save-btn:hover:not(:disabled) { background: var(--navy-dark); }
        .save-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .saved-note { font-size: 12.5px; color: var(--emerald); margin: 0; }
      `}</style>
    </PortalShell>
  );
}
