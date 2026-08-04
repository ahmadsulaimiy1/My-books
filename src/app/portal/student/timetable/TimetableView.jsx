'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';
import WeeklyTimetable from '@/components/portal/WeeklyTimetable';

export default function TimetableView({ timetable }) {
  return (
    <PortalShell role="student" active="timetable" title="Timetable">
      <Card title="This week">
        <WeeklyTimetable timetable={timetable} />
      </Card>
    </PortalShell>
  );
}
