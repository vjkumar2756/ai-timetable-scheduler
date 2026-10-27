import React from 'react';
import { User, MapPin, Clock, Edit2, AlertCircle } from 'lucide-react';

export default function TimetableGrid({
  sessions = [],
  settings = { days: ["Mon", "Tue", "Wed", "Thu", "Fri"], periods_per_day: 6, default_lunch_period: 4 },
  onSessionClick,
  viewMode = "class",
  selectedEntityId = "",
  currentEntityName = ""
}) {
  const days = settings.days || ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const periodsCount = settings.periods_per_day || 6;
  const lunchPeriod = settings.default_lunch_period || 4;
  const periods = Array.from({ length: periodsCount }, (_, i) => i + 1);

  // Group sessions by day and period
  // Structure: gridMap[day][period] = session
  const gridMap = {};
  days.forEach(d => {
    gridMap[d] = {};
  });

  sessions.forEach(sess => {
    if (gridMap[sess.day]) {
      gridMap[sess.day][sess.period] = sess;
      // If duration is 2, mark subsequent period as multi-period extension
      if (sess.duration > 1) {
        for (let offset = 1; offset < sess.duration; offset++) {
          gridMap[sess.day][sess.period + offset] = { ...sess, isExtension: true };
        }
      }
    }
  });

  return (
    <div className="timetable-container">
      <table className="timetable-grid">
        <thead>
          <tr>
            <th className="day-header">DAY</th>
            {periods.map(p => (
              <th key={p} style={{ width: p === lunchPeriod ? '90px' : undefined }}>
                {p === lunchPeriod ? 'LUNCH' : `PERIOD ${p}`}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {days.map(day => (
            <tr key={day}>
              <td className="day-header" style={{ textAlign: 'center' }}>
                {day}
              </td>
              {periods.map(period => {
                // Lunch Break Column
                if (period === lunchPeriod) {
                  return (
                    <td key={period} className="lunch-slot">
                      LUNCH BREAK
                    </td>
                  );
                }

                const item = gridMap[day] ? gridMap[day][period] : null;

                if (!item) {
                  return (
                    <td key={period} className="slot-cell">
                      <div className="free-slot">Free Period</div>
                    </td>
                  );
                }

                // If this is the second period of a 2-hour lab, it was rendered spanning or marked
                if (item.isExtension) {
                  return (
                    <td key={period} className="slot-cell" style={{ opacity: 0.85 }}>
                      <div 
                        className={`session-box ${item.subject_type === 'lab' ? 'lab' : 'theory'} ${item.status}`}
                        onClick={() => onSessionClick && onSessionClick(item)}
                        title="Click to view or edit slot"
                      >
                        <div className="session-header">
                          <span className="session-code">{item.subject_code} (Cont.)</span>
                          <span className="badge badge-lab">Lab 2/2</span>
                        </div>
                        <div className="session-footer">
                          <span>{item.room_name}</span>
                          <Edit2 size={12} />
                        </div>
                      </div>
                    </td>
                  );
                }

                return (
                  <td key={period} className="slot-cell">
                    <div 
                      className={`session-box ${item.subject_type === 'lab' ? 'lab' : 'theory'} ${item.status}`}
                      onClick={() => onSessionClick && onSessionClick(item)}
                      title="Click to edit or move slot"
                    >
                      <div className="session-header">
                        <span className="session-code">{item.subject_code}</span>
                        <span className={`badge ${item.subject_type === 'lab' ? 'badge-lab' : 'badge-theory'}`}>
                          {item.subject_type === 'lab' ? 'LAB (2h)' : 'THEORY'}
                        </span>
                      </div>
                      
                      <div className="session-name" title={item.subject_name}>
                        {item.subject_name}
                      </div>

                      {item.status === 'cancelled' && (
                        <div style={{ color: 'var(--rose)', fontSize: '0.68rem', fontWeight: 700, margin: '2px 0' }}>
                          CANCELLED
                        </div>
                      )}
                      {item.status === 'rescheduled' && (
                        <div style={{ color: 'var(--amber)', fontSize: '0.68rem', fontWeight: 700, margin: '2px 0' }}>
                          RESCHEDULED
                        </div>
                      )}

                      <div className="session-footer">
                        <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <User size={10} />
                          {viewMode === 'teacher' ? item.class_name : item.teacher_name?.split(' ')[1] || item.teacher_name}
                        </span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <MapPin size={10} />
                          {item.room_name?.split(' ')[0] || item.room_name}
                        </span>
                      </div>
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
