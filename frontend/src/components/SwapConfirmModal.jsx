import React, { useState, useEffect } from 'react';
import { X, ArrowRightLeft, CheckCircle2, AlertTriangle, RefreshCw, Calendar, Clock, MapPin, User } from 'lucide-react';
import { api } from '../services/api';

export default function SwapConfirmModal({
  sourceSession,
  targetSession,
  onClose,
  onConfirm
}) {
  const [isValidating, setIsValidating] = useState(true);
  const [validationResult, setValidationResult] = useState({ isValid: false, message: '', violations: [] });
  const [isExecuting, setIsExecuting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (sourceSession && targetSession) {
      validateProposedSwap();
    }
  }, [sourceSession, targetSession]);

  const validateProposedSwap = async () => {
    setIsValidating(true);
    setErrorMessage('');
    try {
      const res = await api.validateSwap(sourceSession.id, targetSession.id);
      if (res.data) {
        setValidationResult({
          isValid: res.data.is_valid,
          message: res.message || (res.data.is_valid ? 'Swap is clash-free!' : 'Clash detected'),
          violations: res.data.violations || []
        });
      }
    } catch (err) {
      setErrorMessage(err.message || 'Validation request failed');
    } finally {
      setIsValidating(false);
    }
  };

  const handleExecute = async () => {
    setIsExecuting(true);
    setErrorMessage('');
    try {
      const res = await api.executeSwap(
        sourceSession.id,
        targetSession.id,
        sourceSession.teacher_id,
        `Drag-and-drop mutual swap between ${sourceSession.subject_code} and ${targetSession.subject_code}`
      );
      if (res.success) {
        onConfirm && onConfirm(res.data);
        onClose();
      } else {
        setErrorMessage(res.message || 'Failed to execute swap');
      }
    } catch (err) {
      setErrorMessage(err.message || 'Error executing swap');
    } finally {
      setIsExecuting(false);
    }
  };

  if (!sourceSession || !targetSession) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" style={{ maxWidth: '640px' }} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: 'rgba(245, 158, 11, 0.15)', color: 'var(--amber)', padding: '0.4rem', borderRadius: '8px' }}>
              <ArrowRightLeft size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem' }}>Confirm Timetable Slot Swap</h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                You dropped one lecture onto another. Do you want to exchange their slots?
              </span>
            </div>
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.35rem' }} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Side-by-Side Exchange Preview */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '0.75rem', alignItems: 'center' }}>
            {/* Source Card */}
            <div className="card" style={{ padding: '0.9rem', border: '1px solid var(--border-subtle)', background: 'rgba(99, 102, 241, 0.08)' }}>
              <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--primary)', fontWeight: 700, marginBottom: '0.4rem' }}>
                Dragged Session
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#fff', marginBottom: '0.2rem' }}>
                {sourceSession.subject_code}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                {sourceSession.subject_name}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <User size={12} /> {sourceSession.teacher_name}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <MapPin size={12} /> {sourceSession.room_name}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--text-primary)', fontWeight: 600 }}>
                  <Clock size={12} /> Now: {sourceSession.day} P{sourceSession.period}
                </span>
              </div>
            </div>

            {/* Exchange Icon */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '0.6rem', borderRadius: '50%', color: 'var(--amber)' }}>
                <ArrowRightLeft size={18} />
              </div>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px', fontWeight: 600 }}>EXCHANGE</span>
            </div>

            {/* Target Card */}
            <div className="card" style={{ padding: '0.9rem', border: '1px solid var(--border-subtle)', background: 'rgba(245, 158, 11, 0.08)' }}>
              <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--amber)', fontWeight: 700, marginBottom: '0.4rem' }}>
                Target Session
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#fff', marginBottom: '0.2rem' }}>
                {targetSession.subject_code}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                {targetSession.subject_name}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <User size={12} /> {targetSession.teacher_name}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <MapPin size={12} /> {targetSession.room_name}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--text-primary)', fontWeight: 600 }}>
                  <Clock size={12} /> Now: {targetSession.day} P{targetSession.period}
                </span>
              </div>
            </div>
          </div>

          {/* Validation Status Indicator */}
          <div>
            {isValidating ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem', padding: '0.6rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
                <RefreshCw size={14} className="animate-spin" />
                <span>Checking all 9 hard constraints (H1-H9) for this proposed swap...</span>
              </div>
            ) : validationResult.isValid ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--emerald)', fontSize: '0.82rem', padding: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '6px' }}>
                <CheckCircle2 size={18} />
                <div>
                  <div style={{ fontWeight: 700 }}>Clash-Free Swap Verified</div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>Both faculty members and student batches are completely free in the swapped slots.</div>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', color: 'var(--rose)', fontSize: '0.82rem', padding: '0.75rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.25)', borderRadius: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
                  <AlertTriangle size={18} />
                  <span>Cannot Swap: Hard Constraints Violated</span>
                </div>
                <div style={{ fontSize: '0.75rem', opacity: 0.95, paddingLeft: '1.6rem' }}>
                  {validationResult.violations.length > 0 ? (
                    <ul style={{ margin: '4px 0 0 0', paddingLeft: '1rem' }}>
                      {validationResult.violations.map((v, i) => (
                        <li key={i}>{v.message}</li>
                      ))}
                    </ul>
                  ) : (
                    validationResult.message
                  )}
                </div>
              </div>
            )}
          </div>

          {errorMessage && (
            <div style={{ color: 'var(--rose)', fontSize: '0.8rem', padding: '0.5rem', background: 'rgba(244, 63, 94, 0.08)', borderRadius: '6px' }}>
              {errorMessage}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
          <button className="btn btn-secondary" onClick={onClose} disabled={isExecuting}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleExecute}
            disabled={isValidating || !validationResult.isValid || isExecuting}
            style={{
              opacity: (!validationResult.isValid || isValidating) ? 0.5 : 1,
              cursor: (!validationResult.isValid || isValidating) ? 'not-allowed' : 'pointer'
            }}
          >
            {isExecuting ? (
              <>
                <RefreshCw size={14} className="animate-spin" /> Swapping...
              </>
            ) : (
              <>
                <ArrowRightLeft size={14} /> Confirm & Execute Swap
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
