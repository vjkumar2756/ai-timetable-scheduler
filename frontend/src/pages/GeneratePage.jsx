import React, { useState } from 'react';
import { 
  Cpu, Zap, CheckCircle2, AlertTriangle, 
  Clock, ShieldAlert, Award, ArrowRight, RefreshCw 
} from 'lucide-react';
import { api } from '../services/api';

export default function GeneratePage({ onGenerated, onNavigate }) {
  const [algorithm, setAlgorithm] = useState('improved_backtracking');
  const [timeLimit, setTimeLimit] = useState(25);
  const [randomSeed, setRandomSeed] = useState(42);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const algorithms = [
    {
      id: 'improved_backtracking',
      name: 'Improved Backtracking (MRV + FC + Degree + LCV)',
      badge: 'Recommended',
      badgeClass: 'badge-theory',
      desc: 'Systematic CSP solver utilizing Minimum Remaining Values, Forward Checking domain pruning, and Degree tie-breaking. Guarantees 100% hard constraint satisfaction.'
    },
    {
      id: 'hybrid_csp_sa',
      name: 'Hybrid CSP + Simulated Annealing',
      badge: '+6 Bonus Marks',
      badgeClass: 'badge-lab',
      desc: 'Two-stage optimizer: Improved Backtracking first computes a strictly feasible schedule (0 hard violations), then Simulated Annealing refines soft constraints.'
    },
    {
      id: 'min_conflicts',
      name: 'Min-Conflicts Local Search',
      badge: 'Local Search',
      badgeClass: 'badge-rescheduled',
      desc: 'Iterative local search starting from complete greedy assignment. Picks conflicted sessions and minimizes conflicts with random walk plateau escape.'
    },
    {
      id: 'plain_backtracking',
      name: 'Plain Backtracking (Baseline)',
      badge: 'Academic Baseline',
      badgeClass: 'badge-theory',
      desc: 'Unaugmented chronological backtracking without heuristics. Used as baseline comparison to illustrate speedups achieved by MRV and Forward Checking.'
    },
    {
      id: 'simulated_annealing',
      name: 'Simulated Annealing (Standalone)',
      badge: '+6 Bonus Marks',
      badgeClass: 'badge-lab',
      desc: 'Metropolis probabilistic local search with geometric temperature cooling schedule and neighborhood session swap operators.'
    }
  ];

  const handleGenerate = async () => {
    setIsLoading(true);
    setErrorMsg('');
    setResult(null);

    try {
      const res = await api.generateSchedule(algorithm, timeLimit, randomSeed);
      if (res.data) {
        setResult(res.data);
        if (res.success) {
          onGenerated && onGenerated(res.data);
        } else {
          setErrorMsg(res.message || 'Generation failed');
        }
      } else {
        setErrorMsg(res.message || 'Error occurred');
      }
    } catch (err) {
      setErrorMsg(err.message || 'Network error while connecting to backend');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-content" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Generate College Timetable</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          Select an AI search algorithm, configure search parameters, and initiate automated generation.
        </p>
      </div>

      {/* Algorithm Selection Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {algorithms.map(algo => {
          const isSelected = algorithm === algo.id;
          return (
            <div
              key={algo.id}
              onClick={() => setAlgorithm(algo.id)}
              style={{
                backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-card)',
                borderColor: isSelected ? 'var(--primary)' : 'var(--border-subtle)',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderRadius: 'var(--radius-lg)',
                padding: '1.1rem 1.25rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '1rem'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <input
                  type="radio"
                  name="algorithm"
                  checked={isSelected}
                  onChange={() => setAlgorithm(algo.id)}
                  style={{ marginTop: '0.25rem', accentColor: 'var(--primary)' }}
                />
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.95rem', color: isSelected ? '#fff' : 'var(--text-main)' }}>
                      {algo.name}
                    </span>
                    <span className={`badge ${algo.badgeClass}`}>{algo.badge}</span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {algo.desc}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Settings Row */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.25rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
          <div className="form-group">
            <label className="form-label">Search Time Limit (seconds)</label>
            <input
              type="number"
              className="form-control"
              min="5"
              max="60"
              value={timeLimit}
              onChange={e => setTimeLimit(Number(e.target.value))}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Reproducible Random Seed</label>
            <input
              type="number"
              className="form-control"
              value={randomSeed}
              onChange={e => setRandomSeed(Number(e.target.value))}
            />
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem' }}>
        <button
          className="btn btn-primary"
          style={{ padding: '0.8rem 1.8rem', fontSize: '0.95rem' }}
          onClick={handleGenerate}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <RefreshCw className="spin" size={18} />
              <span>Solving CSP & Evaluating Constraints...</span>
            </>
          ) : (
            <>
              <Zap size={18} />
              <span>Generate Timetable Now</span>
            </>
          )}
        </button>
      </div>

      {/* Error Alert */}
      {errorMsg && (
        <div className="alert alert-danger" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={20} />
          <div>
            <strong>Generation Issue:</strong> {errorMsg}
          </div>
        </div>
      )}

      {/* Success Metrics Display */}
      {result && (
        <div className="card" style={{ borderLeft: result.success ? '4px solid var(--emerald)' : '4px solid var(--rose)' }}>
          <div className="card-title">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {result.success ? <CheckCircle2 color="var(--emerald)" size={20} /> : <AlertTriangle color="var(--rose)" size={20} />}
              <span>{result.success ? 'Timetable Generation Succeeded' : 'Infeasible or Incomplete'}</span>
            </span>
            <span className="badge badge-scheduled">
              {result.execution_time_seconds}s
            </span>
          </div>

          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            {result.diagnostic_message}
          </p>

          <div className="stats-grid" style={{ marginBottom: '1.25rem' }}>
            <div className="stat-card" style={{ padding: '0.85rem' }}>
              <div>
                <div className="stat-val" style={{ fontSize: '1.3rem' }}>{result.execution_time_seconds}s</div>
                <div className="stat-label">Execution Time</div>
              </div>
            </div>

            <div className="stat-card" style={{ padding: '0.85rem' }}>
              <div>
                <div className="stat-val" style={{ fontSize: '1.3rem' }}>
                  {result.nodes_expanded || result.iterations || 0}
                </div>
                <div className="stat-label">{result.nodes_expanded ? 'Nodes Expanded' : 'Iterations'}</div>
              </div>
            </div>

            <div className="stat-card" style={{ padding: '0.85rem' }}>
              <div>
                <div className="stat-val" style={{ fontSize: '1.3rem', color: result.hard_violations === 0 ? 'var(--emerald)' : 'var(--rose)' }}>
                  {result.hard_violations}
                </div>
                <div className="stat-label">Hard Violations (H1-H9)</div>
              </div>
            </div>

            <div className="stat-card" style={{ padding: '0.85rem' }}>
              <div>
                <div className="stat-val" style={{ fontSize: '1.3rem', color: 'var(--amber)' }}>
                  {result.soft_penalty}
                </div>
                <div className="stat-label">Soft Penalty Score</div>
              </div>
            </div>
          </div>

          {result.success && (
            <button className="btn btn-primary" onClick={() => onNavigate('timetable')}>
              <span>View Generated Timetable Grid</span>
              <ArrowRight size={16} />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
