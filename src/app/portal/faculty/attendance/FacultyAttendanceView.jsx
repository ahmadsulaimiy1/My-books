'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';
import AttendanceMarker from '@/components/portal/AttendanceMarker';
import { demoFaculty, demoRoster } from '@/lib/portalDemoData';

export default function FacultyAttendanceView() {
  const [course, setCourse] = useState(demoFaculty.coursesTaught[0]);

  return (
    <PortalShell role="faculty" active="attendance" title="Attendance">
      <Card>
        <div className="controls">
          <label htmlFor="course-select">Course session</label>
          <select id="course-select" value={course} onChange={(e) => setCourse(e.target.value)}>
            {demoFaculty.coursesTaught.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </div>
        <p className="notice">
          This is a preview — marks you make here only exist in this browser tab for this session and are not saved
          anywhere. A real attendance record will be wired up once the Firebase backend is in place.
        </p>
        <AttendanceMarker roster={demoRoster} sessionLabel={`${course} — today's session`} />
      </Card>

      <style jsx>{`
        .controls { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
        .controls label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); }
        .controls select { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 12px; font-size: 13.5px; color: var(--ink); background: var(--surface); min-width: 140px; }
        .notice { font-size: 12.5px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 18px; padding: 10px 14px; background: var(--manuscript); border: 1px solid var(--border); border-radius: var(--radius-sm); }
      `}</style>
    </PortalShell>
  );
}
