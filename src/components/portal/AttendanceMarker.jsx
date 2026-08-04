'use client';

/*
  AttendanceMarker
  -----------------
  Mark-attendance grid for a single course session: one row per roster
  student, a Present/Absent toggle per row, local component state only.
  Used by the Faculty Attendance screen. Marks are held in local state
  until "Save attendance" is pressed, which calls
  facultyService.markAttendance directly (a write, so this client
  component owns the call rather than page.jsx) — the mock still doesn't
  persist anywhere, see the parent screen's on-screen notice.
*/

import { useState } from 'react';
import { Badge } from './ui';
import { markAttendance } from '@/lib/services/facultyService';

export default function AttendanceMarker({ courseId, roster, sessionLabel }) {
  const [marks, setMarks] = useState(() =>
    Object.fromEntries(roster.map((s) => [s.id, 'unmarked']))
  );
  const [saving, setSaving] = useState(false);
  const [savedNote, setSavedNote] = useState('');

  const presentCount = Object.values(marks).filter((m) => m === 'present').length;
  const absentCount = Object.values(marks).filter((m) => m === 'absent').length;

  function setMark(id, value) {
    setMarks((prev) => ({ ...prev, [id]: value }));
    setSavedNote('');
  }

  function markAll(value) {
    setMarks(Object.fromEntries(roster.map((s) => [s.id, value])));
    setSavedNote('');
  }

  async function handleSave() {
    setSaving(true);
    const records = roster.map((s) => ({ studentId: s.studentId, status: marks[s.id] }));
    await markAttendance({ courseId, records });
    setSaving(false);
    setSavedNote('Attendance recorded for this preview session only — nothing is saved to a server yet.');
  }

  return (
    <div className="marker">
      <div className="marker-head">
        <span className="session">{sessionLabel}</span>
        <div className="tally">
          <Badge tone="success">{presentCount} present</Badge>
          <Badge tone="alert">{absentCount} absent</Badge>
          <Badge tone="neutral">{roster.length - presentCount - absentCount} unmarked</Badge>
        </div>
        <div className="bulk-actions">
          <button type="button" onClick={() => markAll('present')}>
            Mark all present
          </button>
          <button type="button" onClick={() => markAll('unmarked')}>
            Reset
          </button>
        </div>
      </div>

      <ul className="roster-list">
        {roster.map((student) => (
          <li key={student.id} className="roster-row">
            <span className="student">
              <span className="name">{student.name}</span>
              <span className="id">{student.studentId}</span>
            </span>
            <div className="toggle-group" role="group" aria-label={`Attendance for ${student.name}`}>
              <button
                type="button"
                className={marks[student.id] === 'present' ? 'toggle present active' : 'toggle present'}
                aria-pressed={marks[student.id] === 'present'}
                onClick={() => setMark(student.id, 'present')}
              >
                Present
              </button>
              <button
                type="button"
                className={marks[student.id] === 'absent' ? 'toggle absent active' : 'toggle absent'}
                aria-pressed={marks[student.id] === 'absent'}
                onClick={() => setMark(student.id, 'absent')}
              >
                Absent
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div className="save-row">
        <button type="button" className="save-btn" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving…' : 'Save attendance'}
        </button>
        {savedNote && (
          <p className="saved-note" role="status">
            {savedNote}
          </p>
        )}
      </div>

      <style jsx>{`
        .marker-head { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin-bottom: 16px; }
        .session { font-size: 13.5px; font-weight: 600; color: var(--navy); }
        .tally { display: flex; gap: 8px; flex-wrap: wrap; }
        .bulk-actions { margin-inline-start: auto; display: flex; gap: 8px; }
        .bulk-actions button { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 6px 12px; font-size: 12.5px; font-weight: 600; color: var(--ink); cursor: pointer; }
        .bulk-actions button:hover { background: var(--manuscript); }

        .roster-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .roster-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; padding: 12px 4px; border-bottom: 1px solid var(--border); }
        .roster-row:last-child { border-bottom: none; }
        .student { display: flex; flex-direction: column; gap: 2px; }
        .name { font-size: 13.5px; color: var(--ink); font-weight: 500; }
        .id { font-size: 12px; color: var(--ink-muted); }

        .toggle-group { display: flex; gap: 6px; }
        .toggle { border: 1px solid var(--border); background: var(--surface); color: var(--ink-muted); border-radius: var(--radius-sm); padding: 6px 14px; font-size: 12.5px; font-weight: 600; cursor: pointer; }
        .toggle:hover { background: var(--manuscript); }
        .toggle.present.active { background: rgba(30,76,67,0.12); border-color: var(--emerald); color: var(--emerald); }
        .toggle.absent.active { background: rgba(178,58,58,0.1); border-color: #B23A3A; color: #B23A3A; }

        .save-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-top: 18px; }
        .save-btn { background: var(--navy); color: #fff; border: none; border-radius: var(--radius-sm); padding: 10px 22px; font-size: 13.5px; font-weight: 600; cursor: pointer; }
        .save-btn:hover:not(:disabled) { background: var(--navy-dark); }
        .save-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .saved-note { font-size: 12.5px; color: var(--emerald); margin: 0; }
      `}</style>
    </div>
  );
}
