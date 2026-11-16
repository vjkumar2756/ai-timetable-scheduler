import React, { useState } from 'react';
import { User, MapPin, Clock, Edit2, AlertCircle, GripVertical, ArrowRightLeft, Move } from 'lucide-react';

export default function TimetableGrid({
  sessions = [],
  settings = { days: ["Mon", "Tue", "Wed", "Thu", "Fri"], periods_per_day: 6, default_lunch_period: 4 },
  onSessionClick,
  onSessionDrop,
  isDragDropEnabled = true,
  viewMode = "class",
  selectedEntityId = "",
  currentEntityName = ""
}) {
  const days = settings.days || ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const periodsCount = settings.periods_per_day || 6;
  const lunchPeriod = settings.default_lunch_period || 4;
  const periods = Array.from({ length: periodsCount }, (_, i) => i + 1);

  // Drag and Drop state
  const [draggedSession, setDraggedSession] = useState(null);
  const [dragOverCell, setDragOverCell] = useState(null); // { day, period }

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

  // --- HTML5 Drag & Drop Handlers ---
  const handleDragStart = (e, session) => {
    if (!isDragDropEnabled || session.isExtension) return;
    setDraggedSession(session);
    e.dataTransfer.setData('text/plain', session.id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragEnd = () => {
    setDraggedSession(null);
    setDragOverCell(null);
  };

  const handleDragOver = (e, day, period) => {
    if (!isDragDropEnabled || !draggedSession) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    if (!dragOverCell || dragOverCell.day !== day || dragOverCell.period !== period) {
      setDragOverCell({ day, period });
    }
  };

  const handleDragLeave = (e, day, period) => {
    if (dragOverCell && dragOverCell.day === day && dragOverCell.period === period) {
      setDragOverCell(null);
    }
  };

  const handleDrop = (e, day, period, targetItem) => {
    if (!isDragDropEnabled || !draggedSession) return;
    e.preventDefault();

    const sourceSession = draggedSession;
    setDraggedSession(null);
    setDragOverCell(null);

    // Guard: dropping on lunch break
    if (period === lunchPeriod) {
      return;
    }

    // Guard: dropping on same slot
    if (sourceSession.day === day && sourceSession.period === period) {
      return;
    }

    // Guard: 2-hour lab boundary checks
    if (sourceSession.duration > 1) {
      if (period + 1 > periodsCount || period === lunchPeriod || (period + 1) === lunchPeriod) {
        return;
      }
    }

    // Determine target session (ignore if target is extension of source itself)
    const effectiveTarget = (targetItem && targetItem.id !== sourceSession.id && !targetItem.isExtension)
      ? targetItem
      : null;

    if (onSessionDrop) {
      onSessionDrop(sourceSession, day, period, effectiveTarget);
    }
  };

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
                  const isHoveringLunch = dragOverCell?.day === day && dragOverCell?.period === period;
                  return (
                    <td 
                      key={period} 
                      className={`lunch-slot ${isHoveringLunch ? 'drag-target-invalid' : ''}`}
                      onDragOver={e => handleDragOver(e, day, period)}
                      onDragLeave={e => handleDragLeave(e, day, period)}
                      onDrop={e => handleDrop(e, day, period, null)}
                    >
                      <div>LUNCH BREAK</div>
                      {isHoveringLunch && (
                        <div className="drop-badge drop-badge-invalid">Blocked (H9)</div>
                      )}
                    </td>
                  );
                }

                const item = gridMap[day] ? gridMap[day][period] : null;
                const isHovered = dragOverCell?.day === day && dragOverCell?.period === period;
                const isDraggingThis = draggedSession && item && draggedSession.id === item.id;

                // Determine drag-over styling class
                let dragCellClass = '';
                let dropBadgeLabel = '';
                let dropBadgeType = '';

                if (isHovered && draggedSession) {
                  const isSameSlot = draggedSession.day === day && draggedSession.period === period;
                  const isLabOverflow = draggedSession.duration > 1 && (period + 1 > periodsCount || (period + 1) === lunchPeriod);

                  if (isSameSlot) {
                    // Current slot
                  } else if (isLabOverflow) {
                    dragCellClass = 'drag-target-invalid';
                    dropBadgeLabel = 'Lab Overflow';
                    dropBadgeType = 'invalid';
                  } else if (item && item.id !== draggedSession.id && !item.isExtension) {
                    dragCellClass = 'drag-target-swap';
                    dropBadgeLabel = 'Drop to Swap';
                    dropBadgeType = 'swap';
                  } else if (!item) {
                    dragCellClass = 'drag-target-valid';
                    dropBadgeLabel = 'Drop to Move';
                    dropBadgeType = 'valid';
                  }
                }

                // Empty / Free slot
                if (!item) {
                  return (
                    <td 
                      key={period} 
                      className={`slot-cell ${dragCellClass}`}
                      onDragOver={e => handleDragOver(e, day, period)}
                      onDragLeave={e => handleDragLeave(e, day, period)}
                      onDrop={e => handleDrop(e, day, period, null)}
                    >
                      <div className="free-slot">
                        {dropBadgeLabel ? (
                          <span className={`drop-badge drop-badge-${dropBadgeType}`}>
                            <Move size={10} style={{ marginRight: '3px' }} /> {dropBadgeLabel}
                          </span>
                        ) : (
                          'Free Period'
                        )}
                      </div>
                    </td>
                  );
                }

                // If this is the second period of a 2-hour lab
                if (item.isExtension) {
                  return (
                    <td 
                      key={period} 
                      className={`slot-cell ${dragCellClass}`} 
                      style={{ opacity: 0.85 }}
                      onDragOver={e => handleDragOver(e, day, period)}
                      onDragLeave={e => handleDragLeave(e, day, period)}
                      onDrop={e => handleDrop(e, day, period, item)}
                    >
                      <div 
                        className={`session-box ${item.subject_type === 'lab' ? 'lab' : 'theory'} ${item.status}`}
                        onClick={() => onSessionClick && onSessionClick(item)}
                        title="Click to view or edit slot (Lab continuation)"
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

                // Normal Session Slot
                return (
                  <td 
                    key={period} 
                    className={`slot-cell ${dragCellClass}`}
                    onDragOver={e => handleDragOver(e, day, period)}
                    onDragLeave={e => handleDragLeave(e, day, period)}
                    onDrop={e => handleDrop(e, day, period, item)}
                  >
                    <div 
                      className={`session-box ${item.subject_type === 'lab' ? 'lab' : 'theory'} ${item.status} ${isDraggingThis ? 'is-dragging' : ''} ${isDragDropEnabled ? 'draggable-card' : ''}`}
                      draggable={isDragDropEnabled}
                      onDragStart={e => handleDragStart(e, item)}
                      onDragEnd={handleDragEnd}
                      onClick={() => onSessionClick && onSessionClick(item)}
                      title={isDragDropEnabled ? "Drag to move or swap, or click to edit" : "Click to edit or move slot"}
                    >
                      <div className="session-header">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                          {isDragDropEnabled && (
                            <GripVertical size={12} className="drag-grip-icon" />
                          )}
                          <span className="session-code">{item.subject_code}</span>
                        </div>
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

                      {/* Drop indicator overlay on occupied cell */}
                      {dropBadgeLabel && (
                        <div className={`drop-badge drop-badge-${dropBadgeType} drop-badge-floating`}>
                          <ArrowRightLeft size={10} style={{ marginRight: '3px' }} /> {dropBadgeLabel}
                        </div>
                      )}
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
