import React, { useState, useEffect } from 'react';
import { History, FileText, ArrowRight, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function HistoryPage({ onSelectReport }) {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await api.get('/analysis/history');
      setHistoryList(response.data || []);
    } catch (err) {
      console.error("Failed to load user analysis history:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecord = async (e, recordId) => {
    e.stopPropagation();
    try {
      await api.delete(`/analysis/history/${recordId}`);
      setHistoryList(prev => prev.filter(item => item.id !== recordId));
    } catch (err) {
      alert("Failed to delete history record.");
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '800px', margin: '60px auto', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        Retrieving saved statutory audit history...
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '880px', margin: '36px auto', padding: '0 24px 80px' }} className="animate-fade-in">
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', margin: 0, display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700, color: 'var(--text-main)' }}>
            <History style={{ color: 'var(--accent-navy)', width: '22px', height: '22px' }} />
            Statutory Audit Log
          </h1>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px', display: 'block' }}>
            Archived contract analysis reports under your account
          </span>
        </div>

        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Total Saved: <strong style={{ color: 'var(--accent-navy)' }}>{historyList.length} Reports</strong>
        </div>
      </div>

      {historyList.length === 0 ? (
        <div className="minimal-card" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <FileText style={{ width: '36px', height: '36px', color: 'var(--text-subtle)', margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1.05rem', color: 'var(--text-main)', marginBottom: '4px', fontWeight: 700 }}>No Saved Audit Records</h3>
          <p style={{ fontSize: '0.84rem' }}>Executed statutory audit reports will be archived here automatically when signed in.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {historyList.map(item => (
            <div
              key={item.id}
              className="minimal-card"
              onClick={() => onSelectReport(item.analysis_result)}
              style={{
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                {/* Health Score Circle */}
                <div style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  border: `2px solid ${item.health_score >= 75 ? 'var(--risk-low-border)' : item.health_score >= 50 ? 'var(--risk-high-border)' : 'var(--risk-critical-border)'}`,
                  background: item.health_score >= 75 ? 'var(--risk-low-bg)' : item.health_score >= 50 ? 'var(--risk-high-bg)' : 'var(--risk-critical-bg)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '0.96rem',
                  color: item.health_score >= 75 ? 'var(--risk-low-text)' : item.health_score >= 50 ? 'var(--risk-high-text)' : 'var(--risk-critical-text)',
                  fontFamily: 'var(--font-mono)'
                }}>
                  {item.health_score}
                </div>

                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.96rem', color: 'var(--text-main)' }}>
                    {item.document_name}
                  </div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '2px', display: 'flex', gap: '10px' }}>
                    <span>{item.document_type}</span>
                    <span>•</span>
                    <span>{item.created_at}</span>
                    <span>•</span>
                    <span>{item.total_clauses} Clauses</span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ display: 'flex', gap: '6px' }}>
                  {item.critical_count > 0 && <span className="badge-risk CRITICAL">{item.critical_count} CRITICAL</span>}
                  {item.high_count > 0 && <span className="badge-risk HIGH">{item.high_count} HIGH</span>}
                </div>

                <button
                  onClick={(e) => handleDeleteRecord(e, item.id)}
                  className="btn-minimal"
                  title="Delete Log"
                  style={{ padding: '6px', border: 'none' }}
                >
                  <Trash2 style={{ width: '15px', height: '15px', color: 'var(--text-subtle)' }} />
                </button>

                <ArrowRight style={{ width: '16px', height: '16px', color: 'var(--accent-navy)' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
