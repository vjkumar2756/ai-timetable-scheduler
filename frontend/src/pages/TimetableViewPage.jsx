import React, { useState } from 'react';
import { 
  Download, Filter, Layers, User, MapPin, CheckCircle, AlertTriangle, 
  Hand, Move, ArrowRightLeft, Info, X, CheckCircle2, AlertOctagon, RefreshCw
} from 'lucide-react';
import TimetableGrid from '../components/TimetableGrid';
import EditSessionModal from '../components/EditSessionModal';
import SwapConfirmModal from '../components/SwapConfirmModal';
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

  // Drag-and-Drop State
  const [isDragDropEnabled, setIsDragDropEnabled] = useState(true);
  const [swapModalData, setSwapModalData] = useState({ isOpen: false, sourceSession: null, targetSession: null });
  const [toast, setToast] = useState(null); // { type: 'success'|'error'|'info', title, message, violations: [] }
  const [isProcessingDrop, setIsProcessingDrop] = useState(false);

  const sessions = scheduleData.sessions || [];
  const meta = scheduleData.metadata || {};

  // Toast Helper
  const showToast = (type, title, message, violations = []) => {
    setToast({ type, title, message, violations });
    setTimeout(() => {
      setToast(prev => (prev?.title === title ? null : prev));
    }, 5000);
  };

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

  // --- Core Drag & Drop Dispatcher ---
  const handleSessionDrop = async (sourceSession, targetDay, targetPeriod, targetSession) => {
    // 1. If dropped on another session -> Trigger Swap Flow
    if (targetSession) {
      setSwapModalData({
        isOpen: true,
        sourceSession,
        targetSession
      });
      return;
    }

    // 2. If dropped on an empty/free slot -> Move Session
    setIsProcessingDrop(true);
    try {
      // Validate move against all 9 hard constraints
      const valRes = await api.validateManualEdit(
        sourceSession.id,
        targetDay,
        targetPeriod,
        sourceSession.room_id,
        sourceSession.teacher_id
      );

      if (valRes.data && valRes.data.is_valid) {
        // Execute move
        const applyRes = await api.applyManualEdit(
          sourceSession.id,
          targetDay,
          targetPeriod,
          sourceSession.room_id,
          sourceSession.teacher_id
        );

        if (applyRes.success) {
          onScheduleUpdated && onScheduleUpdated();
          showToast(
            'success',
            'Session Moved Successfully',
            `Moved ${sourceSession.subject_code} to ${targetDay} Period ${targetPeriod} (Clash-Free!)`
          );
        } else {
          showToast('error', 'Failed to Move Session', applyRes.message || 'Server rejected move');
        }
      } else {
        const violations = valRes.data?.violations || [];
        const errorSummary = violations.length > 0 
          ? violations.map(v => v.message).join('; ')
          : (valRes.message || 'Hard constraint conflict detected');

        showToast(
          'error',
          'Cannot Move (Clash Detected)',
          errorSummary,
          violations
        );
      }
    } catch (err) {
      showToast('error', 'Move Error', err.message || 'Network error while validating move');
    } finally {
      setIsProcessingDrop(false);
    }
  };

  return (
    <div className="page-content" style={{ position: 'relative' }}>
      {/* Top Filter & Action Bar */}
      <div className="card" style={{ marginBottom: '1.25rem', padding: '1rem 1.25rem' }}>
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

          {/* Entity Dropdown Selector + Drag Toggle + Export */}
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
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

            {/* Drag & Drop Feature Toggle Pill */}
            <button
              className={`btn ${isDragDropEnabled ? 'btn-primary' : 'btn-secondary'}`}
              style={{ 
                padding: '0.45rem 0.85rem',
                border: isDragDropEnabled ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                background: isDragDropEnabled ? 'rgba(99, 102, 241, 0.2)' : undefined,
                color: isDragDropEnabled ? '#a5b4fc' : undefined
              }}
              onClick={() => setIsDragDropEnabled(!isDragDropEnabled)}
              title="Toggle Drag-and-Drop timetable slot editing"
            >
              <Hand size={14} />
              <span>Drag & Drop: <strong>{isDragDropEnabled ? 'ON' : 'OFF'}</strong></span>
            </button>

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

      {/* Helpful Drag & Drop Instruction Strip */}
      {isDragDropEnabled && (
        <div 
          className="drag-instructions-strip"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'linear-gradient(90deg, rgba(99, 102, 241, 0.12), rgba(16, 185, 129, 0.08))',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: 'var(--radius-md)',
            padding: '0.6rem 1rem',
            marginBottom: '1rem',
            fontSize: '0.8rem',
            color: 'var(--text-secondary)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ color: 'var(--primary)', display: 'flex' }}>
              <Move size={15} />
            </span>
            <span>
              <strong style={{ color: '#fff' }}>Interactive Drag & Drop:</strong> Grab any class card and drag it to a <span style={{ color: 'var(--emerald)', fontWeight: 600 }}>Free Slot</span> to move it, or drop onto another class to <span style={{ color: 'var(--amber)', fontWeight: 600 }}>Swap Slots</span>.
            </span>
          </div>
          {isProcessingDrop && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)', fontWeight: 600 }}>
              <RefreshCw size={14} className="animate-spin" /> Verifying constraints...
            </div>
          )}
        </div>
      )}

      {/* Title & Metadata Strip */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{currentTitle}</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Showing {filteredSessions.length} sessions • {isDragDropEnabled ? 'Drag cards to rearrange or click to open slot editor' : 'Click any session to inspect or move slot'}
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
        isDragDropEnabled={isDragDropEnabled}
        onSessionClick={sess => setEditingSession(sess)}
        onSessionDrop={handleSessionDrop}
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

      {/* Swap Confirmation Modal */}
      {swapModalData.isOpen && (
        <SwapConfirmModal
          sourceSession={swapModalData.sourceSession}
          targetSession={swapModalData.targetSession}
          onClose={() => setSwapModalData({ isOpen: false, sourceSession: null, targetSession: null })}
          onConfirm={() => {
            onScheduleUpdated && onScheduleUpdated();
            showToast(
              'success',
              'Timetable Swap Executed',
              `Swapped ${swapModalData.sourceSession?.subject_code} with ${swapModalData.targetSession?.subject_code}!`
            );
          }}
        />
      )}

      {/* Floating Toast Notification */}
      {toast && (
        <div 
          className={`toast-notification toast-${toast.type}`}
          style={{
            position: 'fixed',
            bottom: '1.5rem',
            right: '1.5rem',
            zIndex: 100,
            minWidth: '320px',
            maxWidth: '460px',
            backgroundColor: 'var(--bg-card)',
            border: `1px solid ${toast.type === 'success' ? 'var(--emerald)' : toast.type === 'error' ? 'var(--rose)' : 'var(--primary)'}`,
            borderRadius: 'var(--radius-lg)',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.6), 0 8px 10px -6px rgba(0, 0, 0, 0.4)',
            padding: '1rem',
            animation: 'slideUp 0.25s ease-out',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {toast.type === 'success' && <CheckCircle2 size={18} style={{ color: 'var(--emerald)', flexShrink: 0 }} />}
              {toast.type === 'error' && <AlertOctagon size={18} style={{ color: 'var(--rose)', flexShrink: 0 }} />}
              {toast.type === 'info' && <Info size={18} style={{ color: 'var(--primary)', flexShrink: 0 }} />}
              <strong style={{ fontSize: '0.9rem', color: '#fff' }}>{toast.title}</strong>
            </div>
            <button 
              onClick={() => setToast(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '2px' }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '1.6rem' }}>
            {toast.message}
          </div>

          {toast.violations && toast.violations.length > 0 && (
            <div style={{ paddingLeft: '1.6rem', marginTop: '0.3rem' }}>
              <ul style={{ margin: 0, paddingLeft: '1rem', fontSize: '0.74rem', color: 'var(--rose)' }}>
                {toast.violations.map((v, i) => (
                  <li key={i}>{v.message}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
