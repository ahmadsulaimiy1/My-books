'use client';

/*
  CoursePlayer
  ------------
  Preview course-player UI: a lesson list sidebar + a "now playing" panel.
  No real video — a styled placeholder panel stands in for the content.
  "Mark complete" is local React state only (no persistence, no backend —
  see /portal/CONVENTIONS.md).
*/

import { useState } from 'react';
import { Badge } from './ui';

export default function CoursePlayer({ lessons }) {
  const [activeId, setActiveId] = useState(lessons[0]?.id);
  const [completed, setCompleted] = useState(() => new Set());

  const active = lessons.find((l) => l.id === activeId) ?? lessons[0];
  const doneCount = completed.size;

  function toggleComplete(id) {
    setCompleted((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="player">
      <aside className="lesson-list" aria-label="Lesson list">
        <div className="progress-head">
          <span>Progress</span>
          <span>{doneCount} / {lessons.length} complete</span>
        </div>
        <ol>
          {lessons.map((lesson) => (
            <li key={lesson.id}>
              <button
                type="button"
                className={lesson.id === active?.id ? 'lesson active' : 'lesson'}
                onClick={() => setActiveId(lesson.id)}
                aria-current={lesson.id === active?.id ? 'true' : undefined}
              >
                <span className={`check ${completed.has(lesson.id) ? 'done' : ''}`} aria-hidden="true">
                  {completed.has(lesson.id) ? '✓' : ''}
                </span>
                <span className="lesson-text">
                  <span className="lesson-title">{lesson.title}</span>
                  <span className="lesson-meta">{lesson.durationMins} min</span>
                </span>
              </button>
            </li>
          ))}
        </ol>
      </aside>

      <div className="main">
        <div className="viewer" role="img" aria-label={`Placeholder content panel for ${active?.title}`}>
          <span className="play-icon" aria-hidden="true">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="11" stroke="#fff" strokeWidth="1.5" />
              <path d="M10 8.5L16 12L10 15.5V8.5Z" fill="#fff" />
            </svg>
          </span>
          <span className="viewer-label">Content preview placeholder — no video is hosted yet</span>
        </div>

        <div className="lesson-panel">
          <div className="lesson-panel-head">
            <h2>{active?.title}</h2>
            {completed.has(active?.id) ? (
              <Badge tone="success">Completed</Badge>
            ) : (
              <Badge tone="neutral">Not yet completed</Badge>
            )}
          </div>
          <p className="lesson-desc">
            Sample lesson content for this preview — {active?.durationMins} minutes. In the live portal this
            panel will hold the real lesson video or reading material.
          </p>
          <button type="button" className="complete-btn" onClick={() => toggleComplete(active?.id)}>
            {completed.has(active?.id) ? 'Mark as incomplete' : 'Mark complete'}
          </button>
        </div>
      </div>

      <style jsx>{`
        .player { display: grid; grid-template-columns: 300px 1fr; gap: 20px; align-items: start; }
        @media (max-width: 860px) { .player { grid-template-columns: 1fr; } }

        .lesson-list { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); box-shadow: var(--shadow-1); overflow: hidden; }
        .progress-head { display: flex; justify-content: space-between; padding: 14px 18px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); background: var(--manuscript); border-bottom: 1px solid var(--border); }
        ol { list-style: none; margin: 0; padding: 6px; display: flex; flex-direction: column; gap: 2px; }
        .lesson { width: 100%; display: flex; align-items: center; gap: 10px; text-align: start; background: none; border: none; border-radius: var(--radius-sm); padding: 10px 12px; cursor: pointer; color: var(--ink); }
        .lesson:hover { background: var(--manuscript); }
        .lesson.active { background: var(--navy); color: #fff; }
        .lesson.active .lesson-meta { color: var(--gold-light); }
        .check { width: 18px; height: 18px; flex-shrink: 0; border-radius: 50%; border: 1.5px solid var(--gold-ink); display: flex; align-items: center; justify-content: center; font-size: 11px; color: var(--gold-ink); }
        .lesson.active .check { border-color: var(--gold); color: var(--gold); }
        .check.done { background: var(--gold); color: var(--navy-dark); }
        .lesson-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
        .lesson-title { font-size: 13.5px; font-weight: 500; }
        .lesson-meta { font-size: 11.5px; color: var(--ink-muted); }

        .main { display: flex; flex-direction: column; gap: 16px; }
        .viewer { background: var(--navy-dark); border-radius: var(--radius-md); aspect-ratio: 16 / 9; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; color: #fff; box-shadow: var(--shadow-2); }
        .play-icon { width: 56px; height: 56px; border-radius: 50%; background: rgba(255,255,255,0.12); display: flex; align-items: center; justify-content: center; }
        .viewer-label { font-size: 12.5px; color: #C7CEDC; padding: 0 24px; text-align: center; }

        .lesson-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); box-shadow: var(--shadow-1); padding: 20px 22px; }
        .lesson-panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
        .lesson-panel-head h2 { font-family: 'Fraunces', serif; font-size: 18px; color: var(--navy); margin: 0; }
        .lesson-desc { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 16px; }
        .complete-btn { background: var(--navy); color: #fff; border: none; border-radius: var(--radius-sm); padding: 10px 18px; font-size: 13.5px; font-weight: 600; cursor: pointer; }
        .complete-btn:hover { background: var(--navy-dark); }
      `}</style>
    </div>
  );
}
