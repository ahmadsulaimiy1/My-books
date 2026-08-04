'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';
import WeeklyTimetable from '@/components/portal/WeeklyTimetable';
import { demoTimetable } from '@/lib/portalDemoData';

export default function TimetableView() {
  return (
    <PortalShell role="student" active="timetable" title="Timetable">
      <Card title="This week">
        <WeeklyTimetable timetable={demoTimetable} />
      </Card>
    </PortalShell>
  );
}
