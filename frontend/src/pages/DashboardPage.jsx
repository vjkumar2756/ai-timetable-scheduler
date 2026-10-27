import React from 'react';
import { 
  Users, School, BookOpen, DoorClosed, 
  CheckCircle, Clock, Zap, ArrowRight, ShieldCheck 
} from 'lucide-react';

export default function DashboardPage({ overview, onNavigate, onGenerateClick }) {
  const stats = [
    { label: 'Active Classes', val: overview.total_classes || 0, icon: School, color: '#6366f1' },
    { label: 'Faculty Members', val: overview.total_teachers || 0, icon: Users, color: '#06b6d4' },
    { label: 'Rooms & Labs', val: overview.total_rooms || 0, icon: DoorClosed, color: '#10b981' },
    { label: 'Course Modules', val: overview.total_subjects || 0, icon: BookOpen, color: '#f59e0b' },
  ];

  const meta = overview.schedule_metadata || {};

  return (
    <div className="page-content">
      {/* Top Welcome Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(6, 182, 212, 0.08))',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        borderRadius: 'var(--radius-lg)',
        padding: '2rem',
        marginBottom: '2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1.5rem'
      }}>
        <div style={{ maxWidth: '600px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <span className="badge badge-theory">AI-Based Scheduler</span>
            <span className="badge badge-scheduled"><ShieldCheck size={12} /> H1-H9 Enforced</span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.5rem' }}>
            SchedulAI Autonomous Timetable System
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Formulated as a Constraint Satisfaction Problem (CSP). Compares Plain Backtracking,
            Improved Backtracking with MRV & Forward Checking, Min-Conflicts Local Search, and Hybrid CSP + Simulated Annealing.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={() => onNavigate('timetable')}>
            View Timetable
          </button>
          <button className="btn btn-primary" onClick={() => onNavigate('generate')}>
            <Zap size={16} /> Generate Schedule
          </button>
        </div>
      </div>

      {/* Stats KPI Grid */}
      <div className="stats-grid">
        {stats.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div key={idx} className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: `${s.color}20`, color: s.color }}>
                <Icon size={24} />
              </div>
              <div>
                <div className="stat-val">{s.val}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Grid of Status & Quick Workflows */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Schedule Health Card */}
        <div className="card">
          <div className="card-title">
            <span>Schedule Status & Health</span>
            <span className="badge badge-scheduled">Live</span>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Active Scheduled Sessions:</span>
              <span style={{ fontWeight: 700 }}>{overview.scheduled_sessions || 0} sessions</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Total Teaching Hours:</span>
              <span style={{ fontWeight: 700 }}>{overview.total_teaching_hours || 0} hours/week</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Room Capacity Utilization:</span>
              <span style={{ fontWeight: 700, color: 'var(--cyan)' }}>{overview.room_utilization_pct || 0}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Hard Constraint Violations:</span>
              <span style={{ fontWeight: 700, color: (meta.hard_violations || 0) === 0 ? 'var(--emerald)' : 'var(--rose)' }}>
                {meta.hard_violations ?? 0} (Strict Zero)
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Current Solver:</span>
              <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{meta.algorithm || 'Improved Backtracking (MRV+FC)'}</span>
            </div>
          </div>
        </div>

        {/* Quick Operations Actions */}
        <div className="card">
          <div className="card-title">
            <span>Academic Management Modules</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div 
              style={{ padding: '0.85rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onClick={() => onNavigate('operations')}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Missed Lecture Rescheduling</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Propose clash-free replacement slots for cancelled classes</div>
              </div>
              <ArrowRight size={18} color="var(--primary)" />
            </div>

            <div 
              style={{ padding: '0.85rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onClick={() => onNavigate('operations')}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Teacher Class Swaps</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Request and validate slot exchanges across eligible faculty</div>
              </div>
              <ArrowRight size={18} color="var(--cyan)" />
            </div>

            <div 
              style={{ padding: '0.85rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onClick={() => onNavigate('workload')}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Faculty Workload Analytics</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Monitor teaching loads, limits, and utilization percentages</div>
              </div>
              <ArrowRight size={18} color="var(--emerald)" />
            </div>

            <div 
              style={{ padding: '0.85rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onClick={() => onNavigate('benchmarks')}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Assignment Benchmark Experiments</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>10-trial comparison tables, runtimes, and Min-Conflicts convergence graph</div>
              </div>
              <ArrowRight size={18} color="var(--amber)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
