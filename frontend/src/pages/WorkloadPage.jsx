import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { BarChart3, AlertCircle, CheckCircle, Users } from 'lucide-react';
import { api } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function WorkloadPage() {
  const [workload, setWorkload] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchWorkload();
  }, []);

  const fetchWorkload = async () => {
    setIsLoading(true);
    try {
      const res = await api.getWorkload();
      if (res.data) setWorkload(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const filtered = workload.filter(t => 
    t.teacher_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Chart data
  const chartData = {
    labels: filtered.map(t => t.teacher_name.split(' ').slice(1).join(' ') || t.teacher_name),
    datasets: [
      {
        label: 'Assigned Teaching Hours',
        data: filtered.map(t => t.assigned_hours),
        backgroundColor: '#6366f1',
        borderRadius: 4
      },
      {
        label: 'Maximum Weekly Capacity',
        data: filtered.map(t => t.max_weekly_load),
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94a3b8' }
      }
    },
    scales: {
      x: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255,255,255,0.05)' }
      },
      y: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255,255,255,0.05)' },
        beginAtZero: true
      }
    }
  };

  return (
    <div className="page-content">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Faculty Workload Analytics</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Authoritative tracking of weekly assigned teaching loads against maximum contracted capacity.
          </p>
        </div>

        <input
          type="text"
          className="form-control"
          placeholder="Search faculty..."
          style={{ width: '220px' }}
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Chart Card */}
      <div className="card" style={{ marginBottom: '1.75rem', height: '320px' }}>
        <div className="card-title">
          <span>Weekly Load Distribution (Hours)</span>
          <span className="badge badge-theory">Contract Limit vs Actual</span>
        </div>
        <div style={{ height: '240px' }}>
          <Bar data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Faculty Workload Table */}
      <div className="card" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '0.75rem 1rem' }}>FACULTY MEMBER</th>
              <th style={{ padding: '0.75rem 1rem' }}>ASSIGNED / MAX</th>
              <th style={{ padding: '0.75rem 1rem', width: '25%' }}>CAPACITY UTILIZATION</th>
              <th style={{ padding: '0.75rem 1rem' }}>REMAINING</th>
              <th style={{ padding: '0.75rem 1rem' }}>SESSIONS</th>
              <th style={{ padding: '0.75rem 1rem' }}>SUBJECTS TAUGHT</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(t => {
              const isOver = t.assigned_hours > t.max_weekly_load;
              const barColor = isOver ? 'var(--rose)' : t.utilization_percentage > 85 ? 'var(--amber)' : 'var(--emerald)';
              return (
                <tr key={t.teacher_id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '0.85rem 1rem', fontWeight: 600 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Users size={16} color="var(--primary)" />
                      <span>{t.teacher_name}</span>
                    </div>
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }}>
                    <span style={{ fontWeight: 700, color: isOver ? 'var(--rose)' : '#fff' }}>
                      {t.assigned_hours}h
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}> / {t.max_weekly_load}h</span>
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ flex: 1, height: '8px', backgroundColor: 'var(--bg-input)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div
                          style={{
                            width: `${Math.min(100, t.utilization_percentage)}%`,
                            height: '100%',
                            backgroundColor: barColor,
                            borderRadius: '4px',
                            transition: 'width 0.3s ease'
                          }}
                        />
                      </div>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, minWidth: '40px' }}>
                        {t.utilization_percentage}%
                      </span>
                    </div>
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: t.remaining_capacity === 0 ? 'var(--amber)' : 'var(--emerald)', fontWeight: 600 }}>
                    {t.remaining_capacity}h
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: 'var(--text-secondary)' }}>
                    {t.session_count} classes
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }}>
                    <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                      {Object.entries(t.subject_distribution || {}).map(([sub, hrs]) => (
                        <span key={sub} className="badge badge-theory" style={{ fontSize: '0.68rem' }}>
                          {sub} ({hrs}h)
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
