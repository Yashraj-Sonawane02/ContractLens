import React, { useState, useEffect } from 'react';
import { History, FileText, ArrowRight } from 'lucide-react';
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

  if (loading) {
    return (
      <div style={{ maxWidth: '900px', margin: '60px auto', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        Retrieving saved statutory audit history...
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '36px auto', padding: '0 24px 80px' }} className="animate-fade-in">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '10px', fontFamily: 'var(--font-heading)' }}>
            <History style={{ color: 'var(--accent-gold)', width: '22px', height: '22px' }} />
            Statutory Audit Log
          </h1>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Archived contract analysis reports under your account
          </span>
        </div>

        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Total Saved: <strong style={{ color: 'var(--accent-gold)' }}>{historyList.length} Reports</strong>
        </div>
      </div>

      {historyList.length === 0 ? (
        <div className="glass-card" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <FileText style={{ width: '40px', height: '40px', color: 'var(--text-subtle)', margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '4px', fontFamily: 'var(--font-heading)' }}>No Saved Audit Records</h3>
          <p style={{ fontSize: '0.84rem' }}>Executed statutory audit reports will be archived here automatically when signed in.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {historyList.map(item => (
            <div
              key={item.id}
              className="glass-card"
              onClick={() => onSelectReport(item.analysis_result)}
              style={{
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                transition: 'var(--transition)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{
                  width: '46px',
                  height: '46px',
                  borderRadius: '50%',
                  border: `3px solid ${item.health_score >= 80 ? '#6ee7b7' : item.health_score >= 60 ? '#fde047' : '#fda4af'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '1rem',
                  color: item.health_score >= 80 ? '#6ee7b7' : item.health_score >= 60 ? '#fde047' : '#fda4af',
                  fontFamily: 'var(--font-mono)'
                }}>
                  {item.health_score}
                </div>

                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.98rem', color: '#ffffff' }}>{item.document_name}</div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '2px', display: 'flex', gap: '12px' }}>
                    <span>{item.document_type}</span>
                    <span>•</span>
                    <span>{item.created_at}</span>
                    <span>•</span>
                    <span>{item.total_clauses} Clauses</span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{ display: 'flex', gap: '5px' }}>
                  {item.critical_count > 0 && <span className="badge-risk CRITICAL">{item.critical_count} CRITICAL</span>}
                  {item.high_count > 0 && <span className="badge-risk HIGH">{item.high_count} HIGH</span>}
                </div>
                <ArrowRight style={{ width: '18px', height: '18px', color: 'var(--accent-gold)' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
