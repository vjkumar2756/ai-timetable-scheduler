import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertTriangle, Save, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function EditSessionModal({
  session,
  rooms = [],
  teachers = [],
  settings = { days: ["Mon", "Tue", "Wed", "Thu", "Fri"], periods_per_day: 6 },
  onClose,
  onSaved
}) {
  const [day, setDay] = useState(session.day);
  const [period, setPeriod] = useState(session.period);
  const [roomId, setRoomId] = useState(session.room_id);
  const [teacherId, setTeacherId] = useState(session.teacher_id);
  
  const [validationState, setValidationState] = useState({ checked: false, isValid: false, violations: [] });
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const days = settings.days || ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const periods = Array.from({ length: settings.periods_per_day || 6 }, (_, i) => i + 1);

  // Auto-validate whenever inputs change
  useEffect(() => {
    checkValidity();
  }, [day, period, roomId, teacherId]);

  const checkValidity = async () => {
    try {
      const res = await api.validateManualEdit(session.id, day, period, roomId, teacherId);
      if (res.data) {
        setValidationState({
          checked: true,
          isValid: res.data.is_valid,
          violations: res.data.violations || []
        });
      }
    } catch (err) {
      console.error("Validation error:", err);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setErrorMessage('');
    try {
      const res = await api.applyManualEdit(session.id, day, period, roomId, teacherId);
      if (res.success) {
        onSaved && onSaved(res.data);
        onClose();
      } else {
        setErrorMessage(res.message || 'Failed to save changes');
      }
    } catch (err) {
      setErrorMessage(err.message || 'Network or validation error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Edit Session Slot</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {session.class_name} • {session.subject_name} ({session.subject_code})
            </span>
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.3rem' }} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Target Day */}
          <div className="form-group">
            <label className="form-label">Day of Week</label>
            <select className="form-control" value={day} onChange={e => setDay(e.target.value)}>
              {days.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* Target Starting Period */}
          <div className="form-group">
            <label className="form-label">Starting Period ({session.duration} hour duration)</label>
            <select className="form-control" value={period} onChange={e => setPeriod(Number(e.target.value))}>
              {periods.map(p => (
                <option key={p} value={p}>Period {p}</option>
              ))}
            </select>
          </div>

          {/* Target Room */}
          <div className="form-group">
            <label className="form-label">Room</label>
            <select className="form-control" value={roomId} onChange={e => setRoomId(e.target.value)}>
              {rooms.map(r => (
                <option key={r.id} value={r.id}>
                  {r.name} (Cap: {r.capacity}, Type: {r.type})
                </option>
              ))}
            </select>
          </div>

          {/* Target Teacher */}
          <div className="form-group">
            <label className="form-label">Assigned Teacher</label>
            <select className="form-control" value={teacherId} onChange={e => setTeacherId(e.target.value)}>
              {teachers.map(t => (
                <option key={t.id} value={t.id}>
                  {t.name} (Max Load: {t.max_weekly_load}h)
                </option>
              ))}
            </select>
          </div>

          {/* Authoritative Real-Time Validation Feedback */}
          {validationState.checked && (
            <div>
              {validationState.isValid ? (
                <div className="alert alert-success">
                  <CheckCircle2 size={18} />
                  <div>
                    <strong>Valid Move:</strong> Zero conflicts detected. All 9 hard constraints satisfied!
                  </div>
                </div>
              ) : (
                <div className="alert alert-danger">
                  <AlertTriangle size={18} />
                  <div>
                    <strong>Hard Constraint Conflicts Detected:</strong>
                    <ul style={{ marginLeft: '1.2rem', marginTop: '0.3rem', fontSize: '0.78rem' }}>
                      {validationState.violations.map((v, idx) => (
                        <li key={idx}>[{v.code}] {v.message}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}

          {errorMessage && (
            <div className="alert alert-danger">
              <AlertTriangle size={18} />
              <div>{errorMessage}</div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSave} 
            disabled={!validationState.isValid || isSaving}
            title={!validationState.isValid ? "Cannot save move with hard violations" : "Save valid move"}
          >
            {isSaving ? <RefreshCw className="spin" size={16} /> : <Save size={16} />}
            {isSaving ? 'Saving...' : 'Apply Move'}
          </button>
        </div>
      </div>
    </div>
  );
}
