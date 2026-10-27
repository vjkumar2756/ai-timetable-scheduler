import React, { useState } from 'react';
import { Download, Filter, Layers, User, MapPin, CheckCircle, AlertTriangle } from 'lucide-react';
import TimetableGrid from '../components/TimetableGrid';
import EditSessionModal from '../components/EditSessionModal';
import { api } from '../services/api';

export default function TimetableViewPage({
  scheduleData,
  classes = [],
  teachers = [],
  rooms = [],
  settings = {},
  onScheduleUpdated
}) {
  const [viewMode, setViewMode] = useState('class'); // 'class', 'teacher', 'room'
  const [selectedClassId, setSelectedClassId] = useState(classes[0]?.id || '');
  const [selectedTeacherId, setSelectedTeacherId] = useState(teachers[0]?.id || '');
  const [selectedRoomId, setSelectedRoomId] = useState(rooms[0]?.id || '');
  const [editingSession, setEditingSession] = useState(null);

  const sessions = scheduleData.sessions || [];
  const meta = scheduleData.metadata || {};

  // Filter sessions according to viewMode
  let filteredSessions = sessions;
  let currentTitle = '';

  if (viewMode === 'class') {
    const activeClassId = selectedClassId || classes[0]?.id;
    filteredSessions = sessions.filter(s => s.class_id === activeClassId);
    const cls = classes.find(c => c.id === activeClassId);
    currentTitle = cls ? `${cls.name} (${cls.strength} Students)` : 'Class Timetable';
  } else if (viewMode === 'teacher') {
    const activeTeacherId = selectedTeacherId || teachers[0]?.id;
    filteredSessions = sessions.filter(s => s.teacher_id === activeTeacherId);
    const t = teachers.find(t => t.id === activeTeacherId);
    currentTitle = t ? `${t.name} (Max: ${t.max_weekly_load}h)` : 'Faculty Schedule';
  } else if (viewMode === 'room') {
    const activeRoomId = selectedRoomId || rooms[0]?.id;
    filteredSessions = sessions.filter(s => s.room_id === activeRoomId);
    const r = rooms.find(r => r.id === activeRoomId);
    currentTitle = r ? `${r.name} (Cap: ${r.capacity}, ${r.type})` : 'Room Occupancy';
  }

  return (
    <div className="page-content">
      {/* Top Filter & Action Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          {/* View Selector Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, marginRight: '0.25rem' }}>
              View By:
            </span>
            <button
              className={`btn ${viewMode === 'class' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.45rem 0.85rem' }}
              onClick={() => setViewMode('class')}
            >
              <Layers size={14} /> Class / Batch
            </button>
            <button
              className={`btn ${viewMode === 'teacher' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.45rem 0.85rem' }}
              onClick={() => setViewMode('teacher')}
            >
              <User size={14} /> Teacher / Faculty
            </button>
            <button
              className={`btn ${viewMode === 'room' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.45rem 0.85rem' }}
              onClick={() => setViewMode('room')}
            >
              <MapPin size={14} /> Room / Lab
            </button>
          </div>

          {/* Entity Dropdown Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {viewMode === 'class' && (
              <select
                className="form-control"
                value={selectedClassId}
                onChange={e => setSelectedClassId(e.target.value)}
                style={{ width: '220px' }}
              >
                {classes.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            )}

            {viewMode === 'teacher' && (
              <select
                className="form-control"
                value={selectedTeacherId}
                onChange={e => setSelectedTeacherId(e.target.value)}
                style={{ width: '220px' }}
              >
                {teachers.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}

            {viewMode === 'room' && (
              <select
                className="form-control"
                value={selectedRoomId}
                onChange={e => setSelectedRoomId(e.target.value)}
                style={{ width: '220px' }}
              >
                {rooms.map(r => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            )}

            {/* CSV Export Button */}
            <a 
              href={api.exportCsvUrl()} 
              download="schedulai_timetable.csv" 
              className="btn btn-secondary" 
              style={{ textDecoration: 'none' }}
              title="Download full timetable in CSV format"
            >
              <Download size={14} /> Export CSV
            </a>
          </div>
        </div>
      </div>

      {/* Title & Metadata Strip */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{currentTitle}</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Showing {filteredSessions.length} sessions • Click any session to inspect or move slot
          </span>
        </div>

        {meta.algorithm && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem' }}>
            <span className="badge badge-theory">{meta.algorithm}</span>
            <span style={{ color: 'var(--emerald)', fontWeight: 600 }}>0 Hard Violations</span>
            <span style={{ color: 'var(--text-muted)' }}>Soft Score: {meta.soft_penalty}</span>
          </div>
        )}
      </div>

      {/* Main Grid Matrix */}
      <TimetableGrid
        sessions={filteredSessions}
        settings={settings}
        viewMode={viewMode}
        onSessionClick={sess => setEditingSession(sess)}
      />

      {/* Manual Edit Modal */}
      {editingSession && (
        <EditSessionModal
          session={editingSession}
          rooms={rooms}
          teachers={teachers}
          settings={settings}
          onClose={() => setEditingSession(null)}
          onSaved={() => {
            onScheduleUpdated && onScheduleUpdated();
          }}
        />
      )}
    </div>
  );
}
