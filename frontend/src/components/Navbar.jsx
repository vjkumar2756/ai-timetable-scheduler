import React from 'react';
import { 
  Calendar, LayoutDashboard, Cpu, Database, 
  RotateCw, BarChart3, Award, Bell, ShieldCheck 
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onPresetLoad, notificationCount }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'timetable', label: 'Timetable Grid', icon: Calendar },
    { id: 'generate', label: 'Generate Schedule', icon: Cpu },
    { id: 'operations', label: 'Operations & Rescheduling', icon: RotateCw },
    { id: 'workload', label: 'Workload Analytics', icon: BarChart3 },
    { id: 'benchmarks', label: 'Algorithm Comparison', icon: Award },
    { id: 'entities', label: 'Manage Entities', icon: Database },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Calendar size={22} color="#fff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span className="brand-title">SchedulAI</span>
            <span className="brand-badge">CSP Engine</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>AI College Scheduler</span>
        </div>
      </div>

      <nav className="nav-menu">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.id === 'operations' && notificationCount > 0 && (
                <span style={{
                  marginLeft: 'auto',
                  backgroundColor: 'var(--primary)',
                  color: '#fff',
                  borderRadius: '10px',
                  padding: '1px 6px',
                  fontSize: '0.7rem',
                  fontWeight: 700
                }}>
                  {notificationCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Preset Dataset Loader Widget */}
      <div style={{
        marginTop: 'auto',
        padding: '0.85rem',
        backgroundColor: 'var(--bg-card)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)'
      }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>
          DATASET PRESETS
        </div>
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <button 
            className="btn btn-secondary" 
            style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.72rem' }}
            onClick={() => onPresetLoad('small')}
            title="3 Classes, 6 Teachers, 4 Rooms"
          >
            Small (3C)
          </button>
          <button 
            className="btn btn-secondary" 
            style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.72rem' }}
            onClick={() => onPresetLoad('large')}
            title="8 Classes, 16 Teachers, 8 Rooms"
          >
            Large (8C)
          </button>
        </div>
      </div>
    </aside>
  );
}
