'use client';

/*
  WeeklyTimetable
  ----------------
  Renders demoTimetable (array of { day, slots: [{ time, course, mode }] })
  as a weekly grid, one column per day. Days with no slots show a rest
  message rather than an empty column.
*/

import { Badge } from './ui';

export default function WeeklyTimetable({ timetable }) {
  return (
    <div className="timetable">
      {timetable.map((day) => (
        <div className="day-col" key={day.day}>
          <div className="day-head">{day.day}</div>
          <div className="day-body">
            {day.slots.length === 0 ? (
              <p className="no-class">No scheduled classes</p>
            ) : (
              day.slots.map((slot, i) => (
                <div className="slot" key={i}>
                  <span className="time">{slot.time}</span>
                  <span className="course">{slot.course}</span>
                  <Badge tone={slot.mode === 'Live' ? 'info' : 'neutral'}>{slot.mode}</Badge>
                </div>
              ))
            )}
          </div>
        </div>
      ))}

      <style jsx>{`
        .timetable { display: grid; grid-template-columns: repeat(5, minmax(160px, 1fr)); gap: 12px; overflow-x: auto; }
        @media (max-width: 760px) { .timetable { grid-template-columns: repeat(5, minmax(200px, 1fr)); } }
        .day-col { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; display: flex; flex-direction: column; }
        .day-head { background: var(--navy); color: #fff; font-family: 'Fraunces', serif; font-size: 14px; padding: 10px 14px; text-align: center; }
        .day-body { padding: 10px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
        .slot { display: flex; flex-direction: column; gap: 6px; background: var(--manuscript); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 10px 12px; }
        .time { font-size: 12px; font-weight: 600; color: var(--navy); }
        .course { font-size: 12.5px; color: var(--ink); line-height: 1.4; }
        .no-class { font-size: 12.5px; color: var(--ink-muted); padding: 10px 4px; margin: 0; }
      `}</style>
    </div>
  );
}
