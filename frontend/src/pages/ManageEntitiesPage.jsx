import React, { useState } from 'react';
import { Plus, Users, School, BookOpen, DoorClosed, CheckCircle2, AlertTriangle, Upload } from 'lucide-react';
import { api } from '../services/api';

export default function ManageEntitiesPage({
  teachers = [],
  classes = [],
  subjects = [],
  rooms = [],
  onDataUpdated
}) {
  const [activeTab, setActiveTab] = useState('teachers');
  const [feedback, setFeedback] = useState({ success: null, message: '' });

  // New Teacher Form State
  const [newTeacher, setNewTeacher] = useState({
    id: '',
    name: '',
    subject_ids: '',
    max_weekly_load: 18,
    unavailable_day: 'Mon',
    unavailable_period: 1
  });

  // New Class Form State
  const [newClass, setNewClass] = useState({
    id: '',
    name: '',
    strength: 45,
    lunch_break_period: 4
  });

  // New Subject Form State
  const [newSubject, setNewSubject] = useState({
    id: '',
    code: '',
    name: '',
    weekly_hours: 3,
    type: 'theory',
    lab_duration: 1
  });

  // New Room Form State
  const [newRoom, setNewRoom] = useState({
    id: '',
    name: '',
    capacity: 60,
    type: 'classroom'
  });

  // --- Handlers ---
  const handleAddTeacher = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        id: newTeacher.id || `T_${Date.now().toString().slice(-4)}`,
        name: newTeacher.name,
        subject_ids: newTeacher.subject_ids.split(',').map(s => s.trim()).filter(Boolean),
        unavailable_slots: newTeacher.unavailable_period ? [{ day: newTeacher.unavailable_day, period: Number(newTeacher.unavailable_period) }] : [],
        max_weekly_load: Number(newTeacher.max_weekly_load),
        active: true
      };
      const res = await api.createTeacher(payload);
      if (res.success) {
        setFeedback({ success: true, message: `Teacher '${payload.name}' added successfully!` });
        setNewTeacher({ id: '', name: '', subject_ids: '', max_weekly_load: 18, unavailable_day: 'Mon', unavailable_period: 1 });
        onDataUpdated && onDataUpdated();
      }
    } catch (err) {
      setFeedback({ success: false, message: err.message });
    }
  };

  const handleAddClass = async (e) => {
    e.preventDefault();
    try {
      // Automatically map 3-4 active subjects to new class with reasonable hours
      const reqs = {};
      subjects.slice(0, 4).forEach(s => {
        reqs[s.id] = s.type === 'lab' ? 2 : 3;
      });

      const payload = {
        id: newClass.id || `CLS_${Date.now().toString().slice(-4)}`,
        name: newClass.name,
        strength: Number(newClass.strength),
        subject_requirements: reqs,
        lunch_break_period: Number(newClass.lunch_break_period),
        active: true
      };
      const res = await api.createClass(payload);
      if (res.success) {
        setFeedback({ success: true, message: `Class '${payload.name}' created successfully!` });
        setNewClass({ id: '', name: '', strength: 45, lunch_break_period: 4 });
        onDataUpdated && onDataUpdated();
      }
    } catch (err) {
      setFeedback({ success: false, message: err.message });
    }
  };

  const handleAddSubject = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        id: newSubject.id || newSubject.code,
        code: newSubject.code,
        name: newSubject.name,
        weekly_hours: Number(newSubject.weekly_hours),
        type: newSubject.type,
        lab_duration: newSubject.type === 'lab' ? 2 : 1
      };
      const res = await api.createSubject(payload);
      if (res.success) {
        setFeedback({ success: true, message: `Subject '${payload.name}' added successfully!` });
        setNewSubject({ id: '', code: '', name: '', weekly_hours: 3, type: 'theory', lab_duration: 1 });
        onDataUpdated && onDataUpdated();
      }
    } catch (err) {
      setFeedback({ success: false, message: err.message });
    }
  };

  const handleAddRoom = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        id: newRoom.id || `R_${Date.now().toString().slice(-4)}`,
        name: newRoom.name,
        capacity: Number(newRoom.capacity),
        type: newRoom.type,
        active: true
      };
      const res = await api.createRoom(payload);
      if (res.success) {
        setFeedback({ success: true, message: `Room '${payload.name}' added successfully!` });
        setNewRoom({ id: '', name: '', capacity: 60, type: 'classroom' });
        onDataUpdated && onDataUpdated();
      }
    } catch (err) {
      setFeedback({ success: false, message: err.message });
    }
  };

  return (
    <div className="page-content" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Manage Educational Resources</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          Dynamically add and update teachers, classes, subjects, and rooms without modifying code.
        </p>
      </div>

      {feedback.message && (
        <div className={`alert ${feedback.success ? 'alert-success' : 'alert-danger'}`} style={{ marginBottom: '1.5rem' }}>
          {feedback.success ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
          <div>{feedback.message}</div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
        <button className={`btn ${activeTab === 'teachers' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('teachers')}>
          <Users size={16} /> Faculty ({teachers.length})
        </button>
        <button className={`btn ${activeTab === 'classes' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('classes')}>
          <School size={16} /> Classes ({classes.length})
        </button>
        <button className={`btn ${activeTab === 'subjects' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('subjects')}>
          <BookOpen size={16} /> Subjects ({subjects.length})
        </button>
        <button className={`btn ${activeTab === 'rooms' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('rooms')}>
          <DoorClosed size={16} /> Rooms & Labs ({rooms.length})
        </button>
      </div>

      {/* TEACHERS TAB */}
      {activeTab === 'teachers' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <form className="card" onSubmit={handleAddTeacher}>
            <div className="card-title">Add New Teacher / Faculty</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Teacher ID (e.g. T20)</label>
                <input className="form-control" required value={newTeacher.id} onChange={e => setNewTeacher({ ...newTeacher, id: e.target.value })} placeholder="Auto if blank" />
              </div>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-control" required value={newTeacher.name} onChange={e => setNewTeacher({ ...newTeacher, name: e.target.value })} placeholder="Dr. Jane Doe" />
              </div>
              <div className="form-group">
                <label className="form-label">Qualified Subjects (comma separated codes)</label>
                <input className="form-control" required value={newTeacher.subject_ids} onChange={e => setNewTeacher({ ...newTeacher, subject_ids: e.target.value })} placeholder="CS101, CS104L" />
              </div>
              <div className="form-group">
                <label className="form-label">Max Weekly Hours</label>
                <input type="number" className="form-control" value={newTeacher.max_weekly_load} onChange={e => setNewTeacher({ ...newTeacher, max_weekly_load: e.target.value })} />
              </div>
            </div>
            <button type="submit" className="btn btn-primary"><Plus size={16} /> Add Teacher</button>
          </form>

          <div className="card">
            <div className="card-title">Active Faculty Members</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {teachers.map(t => (
                <div key={t.id} style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: 700 }}>{t.name}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginLeft: '0.5rem' }}>ID: {t.id} • Max Load: {t.max_weekly_load}h</span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.3rem' }}>
                    {t.subject_ids.map(s => <span key={s} className="badge badge-theory">{s}</span>)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* CLASSES TAB */}
      {activeTab === 'classes' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <form className="card" onSubmit={handleAddClass}>
            <div className="card-title">Add New Class / Batch</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Class ID (e.g. CSE_5A)</label>
                <input className="form-control" required value={newClass.id} onChange={e => setNewClass({ ...newClass, id: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Class Name</label>
                <input className="form-control" required value={newClass.name} onChange={e => setNewClass({ ...newClass, name: e.target.value })} placeholder="B.Tech 5th Sem" />
              </div>
              <div className="form-group">
                <label className="form-label">Student Strength</label>
                <input type="number" className="form-control" value={newClass.strength} onChange={e => setNewClass({ ...newClass, strength: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Lunch Break Period</label>
                <input type="number" className="form-control" value={newClass.lunch_break_period} onChange={e => setNewClass({ ...newClass, lunch_break_period: e.target.value })} />
              </div>
            </div>
            <button type="submit" className="btn btn-primary"><Plus size={16} /> Add Class</button>
          </form>

          <div className="card">
            <div className="card-title">Configured Classes</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {classes.map(c => (
                <div key={c.id} style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: 700 }}>{c.name}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginLeft: '0.5rem' }}>
                      Strength: {c.strength} • Lunch: Period {c.lunch_break_period}
                    </span>
                  </div>
                  <span className="badge badge-scheduled">Active</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SUBJECTS TAB */}
      {activeTab === 'subjects' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <form className="card" onSubmit={handleAddSubject}>
            <div className="card-title">Add New Subject</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Course Code (e.g. CS301)</label>
                <input className="form-control" required value={newSubject.code} onChange={e => setNewSubject({ ...newSubject, code: e.target.value, id: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Subject Name</label>
                <input className="form-control" required value={newSubject.name} onChange={e => setNewSubject({ ...newSubject, name: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Weekly Hours</label>
                <input type="number" className="form-control" value={newSubject.weekly_hours} onChange={e => setNewSubject({ ...newSubject, weekly_hours: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Type</label>
                <select className="form-control" value={newSubject.type} onChange={e => setNewSubject({ ...newSubject, type: e.target.value })}>
                  <option value="theory">Theory (Classroom)</option>
                  <option value="lab">Lab (Lab Room)</option>
                </select>
              </div>
            </div>
            <button type="submit" className="btn btn-primary"><Plus size={16} /> Add Subject</button>
          </form>

          <div className="card">
            <div className="card-title">Registered Subjects</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {subjects.map(s => (
                <div key={s.id} style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: 700 }}>{s.code}</span> — {s.name}
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginLeft: '0.5rem' }}>({s.weekly_hours} hrs/week)</span>
                  </div>
                  <span className={`badge ${s.type === 'lab' ? 'badge-lab' : 'badge-theory'}`}>{s.type.toUpperCase()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ROOMS TAB */}
      {activeTab === 'rooms' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <form className="card" onSubmit={handleAddRoom}>
            <div className="card-title">Add New Room or Lab</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Room ID (e.g. LT7, LAB3)</label>
                <input className="form-control" required value={newRoom.id} onChange={e => setNewRoom({ ...newRoom, id: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Room Display Name</label>
                <input className="form-control" required value={newRoom.name} onChange={e => setNewRoom({ ...newRoom, name: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Student Capacity</label>
                <input type="number" className="form-control" value={newRoom.capacity} onChange={e => setNewRoom({ ...newRoom, capacity: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Room Type</label>
                <select className="form-control" value={newRoom.type} onChange={e => setNewRoom({ ...newRoom, type: e.target.value })}>
                  <option value="classroom">Classroom (Theory)</option>
                  <option value="lab">Computer / Hardware Lab</option>
                </select>
              </div>
            </div>
            <button type="submit" className="btn btn-primary"><Plus size={16} /> Add Room</button>
          </form>

          <div className="card">
            <div className="card-title">Available Infrastructure</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {rooms.map(r => (
                <div key={r.id} style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: 700 }}>{r.name}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginLeft: '0.5rem' }}>Capacity: {r.capacity} seats</span>
                  </div>
                  <span className={`badge ${r.type === 'lab' ? 'badge-lab' : 'badge-theory'}`}>{r.type.toUpperCase()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
