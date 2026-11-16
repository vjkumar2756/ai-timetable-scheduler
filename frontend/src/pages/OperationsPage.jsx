import React, { useState, useEffect } from 'react';
import { 
  RotateCw, ArrowLeftRight, Ban, Bell, CheckCircle2, 
  AlertTriangle, Save, RefreshCw, Clock 
} from 'lucide-react';
import { api } from '../services/api';

export default function OperationsPage({ sessions = [], classes = [], teachers = [], onDataUpdated }) {
  const [activeSubTab, setActiveSubTab] = useState('reschedule'); // 'reschedule', 'swap', 'cancel', 'notifications'
  
  // Rescheduling states
  const [selectedSessionId, setSelectedSessionId] = useState('');
  const [altTeacherId, setAltTeacherId] = useState('');
  const [rescheduleOptions, setRescheduleOptions] = useState([]);
  const [isSearchingSlots, setIsSearchingSlots] = useState(false);
  const [rescheduleMsg, setRescheduleMsg] = useState('');

  // Swap states
  const [swapSession1, setSwapSession1] = useState('');
  const [swapSession2, setSwapSession2] = useState('');
  const [swapValidation, setSwapValidation] = useState(null);
  const [swapReason, setSwapReason] = useState('Mutually agreed timetable swap');
  const [isExecutingSwap, setIsExecutingSwap] = useState(false);
  const [swapMsg, setSwapMsg] = useState('');

  // Cancel states
  const [cancelSessionId, setCancelSessionId] = useState('');
  const [cancelReason, setCancelReason] = useState('Emergency faculty leave');
  const [closeClassId, setCloseClassId] = useState(classes[0]?.id || '');
  const [closeDay, setCloseDay] = useState('Mon');
  const [closeReason, setCloseReason] = useState('Departmental symposium / holiday');
  const [cancelStatusMsg, setCancelStatusMsg] = useState('');

  // Notifications
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.getNotifications();
      if (res.data) setNotifications(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  // --- Handlers: Rescheduling ---
  const handleFindSlots = async () => {
    if (!selectedSessionId) return;
    setIsSearchingSlots(true);
    setRescheduleMsg('');
    setRescheduleOptions([]);
    try {
      const res = await api.findRescheduleSlots(selectedSessionId, altTeacherId || null);
      setRescheduleMsg(res.message);
      if (res.data?.options) {
        setRescheduleOptions(res.data.options);
      }
    } catch (err) {
      setRescheduleMsg(err.message || 'Error searching alternative slots');
    } finally {
      setIsSearchingSlots(false);
    }
  };

  const handleApplyReschedule = async (opt) => {
    try {
      const payload = {
        session_id: selectedSessionId,
        target_day: opt.day,
        target_period: opt.period,
        target_room_id: opt.room_id,
        target_teacher_id: opt.teacher_id,
        reason: 'Rescheduled into clash-free slot'
      };
      const res = await api.applyReschedule(payload);
      if (res.success) {
        setRescheduleMsg("Lecture successfully rescheduled! Timetable updated.");
        setRescheduleOptions([]);
        fetchNotifications();
        onDataUpdated && onDataUpdated();
      }
    } catch (err) {
      setRescheduleMsg(err.message || 'Failed to apply rescheduling');
    }
  };

  // --- Handlers: Swaps ---
  const handleValidateSwap = async () => {
    if (!swapSession1 || !swapSession2) return;
    setSwapValidation(null);
    setSwapMsg('');
    try {
      const res = await api.validateSwap(swapSession1, swapSession2);
      setSwapValidation(res);
    } catch (err) {
      setSwapMsg(err.message);
    }
  };

  const handleExecuteSwap = async () => {
    setIsExecutingSwap(true);
    setSwapMsg('');
    try {
      const s1 = sessions.find(s => s.id === swapSession1);
      const requesterId = s1?.teacher_id || 'T1';
      const res = await api.executeSwap(swapSession1, swapSession2, requesterId, swapReason);
      if (res.success) {
        setSwapMsg("Swap executed successfully! Timetable updated.");
        setSwapValidation(null);
        fetchNotifications();
        onDataUpdated && onDataUpdated();
      } else {
        setSwapMsg(res.message || 'Swap execution failed');
      }
    } catch (err) {
      setSwapMsg(err.message);
    } finally {
      setIsExecutingSwap(false);
    }
  };

  // --- Handlers: Cancellations ---
  const handleCancelSession = async () => {
    if (!cancelSessionId) return;
    try {
      const res = await api.cancelSession(cancelSessionId, cancelReason);
      setCancelStatusMsg(res.message);
      fetchNotifications();
      onDataUpdated && onDataUpdated();
    } catch (err) {
      setCancelStatusMsg(err.message);
    }
  };

  const handleCloseClassDay = async () => {
    if (!closeClassId || !closeDay) return;
    try {
      const res = await api.closeClassDay(closeClassId, closeDay, closeReason);
      setCancelStatusMsg(res.message);
      fetchNotifications();
      onDataUpdated && onDataUpdated();
    } catch (err) {
      setCancelStatusMsg(err.message);
    }
  };

  return (
    <div className="page-content" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Academic Operations & Workflows</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          Reschedule missed lectures, validate teacher slot exchanges, handle cancellations, and monitor audit notifications.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
        <button
          className={`btn ${activeSubTab === 'reschedule' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('reschedule')}
        >
          <RotateCw size={16} /> Missed Lecture Rescheduling
        </button>
        <button
          className={`btn ${activeSubTab === 'swap' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('swap')}
        >
          <ArrowLeftRight size={16} /> Teacher Class Swap
        </button>
        <button
          className={`btn ${activeSubTab === 'cancel' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('cancel')}
        >
          <Ban size={16} /> Cancellations & Closure
        </button>
        <button
          className={`btn ${activeSubTab === 'notifications' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('notifications')}
        >
          <Bell size={16} /> In-App Notifications ({notifications.length})
        </button>
      </div>

      {/* 1. RESCHEDULING SUBTAB */}
      {activeSubTab === 'reschedule' && (
        <div className="card">
          <div className="card-title">
            <span>Find Clash-Free Rescheduling Slots</span>
            <span className="badge badge-theory">Authoritative Check</span>
          </div>

          <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', marginBottom: '1rem' }}>
            The rescheduling engine automatically checks all 9 hard constraints (room capacity, room type,
            lunch breaks, teacher availability, teacher max workload) and ranks options by best timetable quality.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Select Missed / Cancelled Session</label>
              <select className="form-control" value={selectedSessionId} onChange={e => setSelectedSessionId(e.target.value)}>
                <option value="">-- Choose a session --</option>
                {sessions.map(s => (
                  <option key={s.id} value={s.id}>
                    [{s.day} P{s.period}] {s.class_name} • {s.subject_code} ({s.teacher_name}) {s.status === 'cancelled' ? '[CANCELLED]' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Optional Substitute Faculty</label>
              <select className="form-control" value={altTeacherId} onChange={e => setAltTeacherId(e.target.value)}>
                <option value="">-- Keep Assigned Faculty --</option>
                {teachers.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          </div>

          <button className="btn btn-primary" onClick={handleFindSlots} disabled={!selectedSessionId || isSearchingSlots}>
            {isSearchingSlots ? <RefreshCw className="spin" size={16} /> : <RotateCw size={16} />}
            <span>{isSearchingSlots ? 'Searching Constraint Space...' : 'Find Feasible Replacement Slots'}</span>
          </button>

          {rescheduleMsg && (
            <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: rescheduleOptions.length > 0 ? 'var(--emerald)' : 'var(--text-secondary)' }}>
              {rescheduleMsg}
            </div>
          )}

          {/* Options List */}
          {rescheduleOptions.length > 0 && (
            <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Feasible Replacement Proposals:</div>
              {rescheduleOptions.map((opt, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '0.85rem 1rem',
                    backgroundColor: 'var(--bg-input)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <span style={{ fontWeight: 700, color: 'var(--cyan)' }}>{opt.day} — Period {opt.period}</span>
                    <span style={{ margin: '0 0.5rem', color: 'var(--text-muted)' }}>•</span>
                    <span>{opt.room_name}</span>
                    <span style={{ margin: '0 0.5rem', color: 'var(--text-muted)' }}>•</span>
                    <span>{opt.teacher_name}</span>
                    <span className="badge badge-scheduled" style={{ marginLeft: '0.75rem' }}>
                      Penalty: {opt.soft_penalty}
                    </span>
                  </div>

                  <button className="btn btn-success" style={{ padding: '0.4rem 0.85rem', fontSize: '0.78rem' }} onClick={() => handleApplyReschedule(opt)}>
                    Approve & Reschedule
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 2. SWAP SUBTAB */}
      {activeSubTab === 'swap' && (
        <div className="card">
          <div className="card-title">
            <span>Teacher Timetable Class Swap</span>
            <span className="badge badge-lab">Multi-Constraint Audit</span>
          </div>

          <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', marginBottom: '1.25rem' }}>
            Exchanges assigned time slots between two lectures. Validates teacher qualifications, lunch breaks, room types, and room conflicts before approval.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Session 1 (Requester)</label>
              <select className="form-control" value={swapSession1} onChange={e => setSwapSession1(e.target.value)}>
                <option value="">-- Select Session 1 --</option>
                {sessions.map(s => (
                  <option key={s.id} value={s.id}>
                    [{s.day} P{s.period}] {s.teacher_name} • {s.subject_code} ({s.class_name})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Session 2 (Target Exchange)</label>
              <select className="form-control" value={swapSession2} onChange={e => setSwapSession2(e.target.value)}>
                <option value="">-- Select Session 2 --</option>
                {sessions.map(s => (
                  <option key={s.id} value={s.id}>
                    [{s.day} P{s.period}] {s.teacher_name} • {s.subject_code} ({s.class_name})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Swap Reason</label>
            <input className="form-control" value={swapReason} onChange={e => setSwapReason(e.target.value)} />
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-secondary" onClick={handleValidateSwap} disabled={!swapSession1 || !swapSession2}>
              Validate Swap Conflicts
            </button>

            {swapValidation?.success && (
              <button className="btn btn-primary" onClick={handleExecuteSwap} disabled={isExecutingSwap}>
                {isExecutingSwap ? 'Executing...' : 'Execute & Approve Swap'}
              </button>
            )}
          </div>

          {swapValidation && (
            <div style={{ marginTop: '1rem' }}>
              {swapValidation.success ? (
                <div className="alert alert-success">
                  <CheckCircle2 size={18} />
                  <div>
                    <strong>Swap Valid:</strong> Satisfies all 9 hard constraints with zero clashes. Ready to execute.
                  </div>
                </div>
              ) : (
                <div className="alert alert-danger">
                  <AlertTriangle size={18} />
                  <div>
                    <strong>Cannot Swap:</strong> {swapValidation.message}
                  </div>
                </div>
              )}
            </div>
          )}

          {swapMsg && (
            <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--emerald)' }}>
              {swapMsg}
            </div>
          )}
        </div>
      )}

      {/* 3. CANCELLATION SUBTAB */}
      {activeSubTab === 'cancel' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Cancel Individual Session */}
          <div className="card">
            <div className="card-title">Cancel Individual Session</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Select Session to Cancel</label>
                <select className="form-control" value={cancelSessionId} onChange={e => setCancelSessionId(e.target.value)}>
                  <option value="">-- Choose session --</option>
                  {sessions.filter(s => s.status !== 'cancelled').map(s => (
                    <option key={s.id} value={s.id}>
                      [{s.day} P{s.period}] {s.class_name} • {s.subject_code} ({s.teacher_name})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Cancellation Reason</label>
                <input className="form-control" value={cancelReason} onChange={e => setCancelReason(e.target.value)} />
              </div>
            </div>

            <button className="btn btn-danger" onClick={handleCancelSession} disabled={!cancelSessionId}>
              Cancel Selected Session
            </button>
          </div>

          {/* Full Class Closure */}
          <div className="card">
            <div className="card-title">Full Class Closure for a Day</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Class</label>
                <select className="form-control" value={closeClassId} onChange={e => setCloseClassId(e.target.value)}>
                  {classes.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Day to Close</label>
                <select className="form-control" value={closeDay} onChange={e => setCloseDay(e.target.value)}>
                  {["Mon", "Tue", "Wed", "Thu", "Fri"].map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Reason</label>
                <input className="form-control" value={closeReason} onChange={e => setCloseReason(e.target.value)} />
              </div>
            </div>

            <button className="btn btn-danger" onClick={handleCloseClassDay}>
              Close Class for Day
            </button>
          </div>

          {cancelStatusMsg && (
            <div className="alert alert-info">{cancelStatusMsg}</div>
          )}
        </div>
      )}

      {/* 4. NOTIFICATIONS SUBTAB */}
      {activeSubTab === 'notifications' && (
        <div className="card">
          <div className="card-title">
            <span>In-App Notifications & Audit Feed</span>
            <span className="badge badge-theory">{notifications.length} Total</span>
          </div>

          {notifications.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No notifications recorded yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {notifications.map((n, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '0.85rem 1rem',
                    backgroundColor: 'var(--bg-input)',
                    borderRadius: 'var(--radius-md)',
                    borderLeft: n.category === 'cancellation' ? '3px solid var(--rose)' : '3px solid var(--primary)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.2rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>{n.title}</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{new Date(n.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{n.message}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Recipient: {n.recipient} • Category: {n.category}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
