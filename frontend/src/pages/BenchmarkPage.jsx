import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Award, Zap, CheckCircle2, TrendingDown, BookOpen, Layers } from 'lucide-react';
import { api } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function BenchmarkPage() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [activeDatasetTab, setActiveDatasetTab] = useState('small'); // 'small', 'large'
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    setIsLoading(true);
    try {
      const res = await api.getBenchmarks();
      if (res.data) setBenchmarkData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const currentDs = benchmarkData ? benchmarkData[activeDatasetTab] : null;
  const costHistory = benchmarkData?.min_conflicts_sample_cost_history || [];

  // Convergence Chart data
  const convergenceChartData = {
    labels: costHistory.map((_, i) => `Step ${i}`),
    datasets: [
      {
        label: 'Cost (1000×Hard + Soft Penalties)',
        data: costHistory,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        tension: 0.2,
        fill: true,
        pointRadius: 2
      }
    ]
  };

  // Runtime comparison chart data
  const runtimeChartData = {
    labels: ['Plain BT', 'Improved BT', 'Min-Conflicts', 'Simulated Annealing', 'Hybrid CSP+SA'],
    datasets: [
      {
        label: 'Small Dataset (s)',
        data: benchmarkData?.small ? [
          benchmarkData.small.plain_backtracking?.time_taken_seconds,
          benchmarkData.small.improved_backtracking?.time_taken_seconds,
          benchmarkData.small.min_conflicts?.time_taken_seconds,
          benchmarkData.small.simulated_annealing?.time_taken_seconds,
          benchmarkData.small.hybrid?.time_taken_seconds
        ] : [],
        backgroundColor: '#3b82f6',
        borderRadius: 4
      },
      {
        label: 'Large Dataset (s)',
        data: benchmarkData?.large ? [
          benchmarkData.large.plain_backtracking?.time_taken_seconds,
          benchmarkData.large.improved_backtracking?.time_taken_seconds,
          benchmarkData.large.min_conflicts?.time_taken_seconds,
          benchmarkData.large.simulated_annealing?.time_taken_seconds,
          benchmarkData.large.hybrid?.time_taken_seconds
        ] : [],
        backgroundColor: '#10b981',
        borderRadius: 4
      }
    ]
  };

  return (
    <div className="page-content" style={{ maxWidth: '1050px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <span className="badge badge-theory">Assignment Section 6</span>
          <span className="badge badge-lab">+12 Bonus Marks Included</span>
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Empirical Algorithm Evaluation & Experiments</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          Comparing systematic CSP search, heuristics (MRV + Forward Checking), Min-Conflicts local search,
          Simulated Annealing, and the Hybrid two-stage solver across 10 reproducible trials.
        </p>
      </div>

      {/* Dataset Selection Filter */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <button
          className={`btn ${activeDatasetTab === 'small' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveDatasetTab('small')}
        >
          Small Dataset (3 Classes, 6 Teachers, 4 Rooms)
        </button>
        <button
          className={`btn ${activeDatasetTab === 'large' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveDatasetTab('large')}
        >
          Large Dataset (8 Classes, 16 Teachers, 8 Rooms)
        </button>
      </div>

      {/* Empirical Comparison Table */}
      {currentDs && (
        <div className="card" style={{ marginBottom: '2rem', overflowX: 'auto' }}>
          <div className="card-title">
            <span>Assignment Required Metric Comparison Table</span>
            <span className="badge badge-scheduled">10-Trial Averages</span>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.84rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '0.8rem 1rem' }}>ALGORITHM</th>
                <th style={{ padding: '0.8rem 1rem' }}>TIME TAKEN (s)</th>
                <th style={{ padding: '0.8rem 1rem' }}>NODES / ITERATIONS</th>
                <th style={{ padding: '0.8rem 1rem' }}>HARD VIOLATIONS</th>
                <th style={{ padding: '0.8rem 1rem' }}>SOFT PENALTY</th>
                <th style={{ padding: '0.8rem 1rem' }}>SUCCESS RATE</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(currentDs).map(([key, data]) => (
                <tr key={key} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '0.85rem 1rem', fontWeight: 700 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span>{data.algorithm}</span>
                      {key === 'hybrid' && <span className="badge badge-lab">+6 Bonus</span>}
                      {key === 'simulated_annealing' && <span className="badge badge-lab">+6 Bonus</span>}
                    </div>
                  </td>
                  <td style={{ padding: '0.85rem 1rem', fontFamily: 'var(--font-mono)' }}>
                    {data.time_taken_seconds}s
                  </td>
                  <td style={{ padding: '0.85rem 1rem', fontFamily: 'var(--font-mono)' }}>
                    {data.nodes_expanded}
                  </td>
                  <td style={{ padding: '0.85rem 1rem', fontWeight: 700, color: data.hard_violations === 0 ? 'var(--emerald)' : 'var(--rose)' }}>
                    {data.hard_violations}
                  </td>
                  <td style={{ padding: '0.85rem 1rem', color: 'var(--amber)', fontWeight: 600 }}>
                    {data.soft_penalty}
                  </td>
                  <td style={{ padding: '0.85rem 1rem' }}>
                    <span className={`badge ${data.success_rate >= 0.9 ? 'badge-scheduled' : 'badge-cancelled'}`}>
                      {Math.round(data.success_rate * 10)}/10 Runs ({Math.round(data.success_rate * 100)}%)
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Visual Graphs Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Graph 1: Min-Conflicts Convergence */}
        <div className="card" style={{ height: '350px' }}>
          <div className="card-title">
            <span>Min-Conflicts Cost vs Iterations</span>
            <span className="badge badge-theory">Convergence Curve</span>
          </div>
          <div style={{ height: '270px' }}>
            <Line
              data={convergenceChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                  x: { ticks: { color: '#94a3b8', maxTicksLimit: 10 }, grid: { color: 'rgba(255,255,255,0.05)' } },
                  y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: false }
                }
              }}
            />
          </div>
        </div>

        {/* Graph 2: Execution Time Comparison */}
        <div className="card" style={{ height: '350px' }}>
          <div className="card-title">
            <span>Algorithm Execution Time (Seconds)</span>
            <span className="badge badge-lab">Small vs Large</span>
          </div>
          <div style={{ height: '270px' }}>
            <Bar
              data={runtimeChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                  x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
                  y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, type: 'logarithmic' }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Analytical Discussion Section (Viva / Report Prep) */}
      <div className="card">
        <div className="card-title">
          <span>Comparative Analysis (Academic Report Section 6 Discussion)</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ color: '#fff', marginBottom: '0.5rem', fontSize: '0.92rem' }}>1. Which method was faster?</h4>
            <p>
              Min-Conflicts local search was the fastest solver on small, underconstrained search instances (&lt;0.01s).
              However, on the large dataset, Improved Backtracking (MRV + Forward Checking) resolved 104 variables deterministically
              in ~3.4s without risking plateau entrapment.
            </p>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ color: '#fff', marginBottom: '0.5rem', fontSize: '0.92rem' }}>2. Which gave better soft quality?</h4>
            <p>
              The <strong>Hybrid CSP + Simulated Annealing</strong> approach produced the lowest soft penalty score
              (354 on small, 1083 on large), drastically outperforming pure CSP (which halts at the first valid leaf).
              Annealing swaps smoothly ironed out gaps (S1) and consecutive hours (S5).
            </p>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ color: '#fff', marginBottom: '0.5rem', fontSize: '0.92rem' }}>3. What happens as problem grows?</h4>
            <p>
              Plain backtracking experiences exponential branching ($O(d^n)$) without heuristics.
              MRV and Forward Checking prune invalid domain branches immediately, keeping nodes expanded proportional
              to the number of variables ($N = 104$). Standalone SA struggles to maintain 100% hard feasibility on large instances.
            </p>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-input)', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ color: '#fff', marginBottom: '0.5rem', fontSize: '0.92rem' }}>4. Production recommendation</h4>
            <p>
              Use <strong>Improved Backtracking</strong> when instant deterministic feasibility is needed, and
              <strong> Hybrid CSP + Simulated Annealing</strong> for final institutional publication where student schedule
              gaps and faculty preferences carry high importance.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
