import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, FileText, Layers, Printer, BookOpen, Clock, Lock, MessageSquare } from 'lucide-react';
import ClauseCard from './ClauseCard';
import RiskHeatmap from './RiskHeatmap';
import ContractChat from './ContractChat';
import ContractComparison from './ContractComparison';

export default function RiskDashboard({ data, onReset }) {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'clauses', 'chat', 'compare'
  const [riskFilter, setRiskFilter] = useState('ALL');

  if (!data) return null;

  const {
    document_name,
    document_type,
    health_score,
    risk_summary,
    executive_summary,
    top_concerns,
    analyzed_clauses,
    risk_heatmap,
    total_items_masked,
    processing_time_seconds,
    language
  } = data;

  const filteredClauses = analyzed_clauses.filter(c => {
    if (riskFilter === 'ALL') return true;
    return c.risk_level === riskFilter;
  });

  const getComplianceGrade = (score) => {
    if (score >= 85) return { grade: 'GRADE A • COMPLIANT', color: '#6ee7b7' };
    if (score >= 70) return { grade: 'GRADE B • MODERATE RISK', color: '#93c5fd' };
    if (score >= 50) return { grade: 'GRADE C • HIGH RISK', color: '#fde047' };
    return { grade: 'GRADE D • SEVERE NON-COMPLIANCE', color: '#fda4af' };
  };

  const gradeInfo = getComplianceGrade(health_score);

  const handlePrintReport = () => {
    window.print();
  };

  return (
    <div style={{ maxWidth: '1140px', margin: '0 auto', padding: '24px 24px 80px' }} className="animate-fade-in">
      
      {/* Executive Document Metadata Header */}
      <div className="glass-card card-gold-accent" style={{ padding: '24px 28px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <FileText style={{ color: 'var(--accent-gold)', width: '20px', height: '20px' }} />
            <h1 style={{ fontSize: '1.4rem', margin: 0, fontFamily: 'var(--font-heading)' }}>{document_name}</h1>
            <span style={{ 
              fontSize: '0.72rem', 
              padding: '3px 10px', 
              borderRadius: 'var(--radius-sm)', 
              background: 'rgba(255, 255, 255, 0.04)', 
              color: 'var(--accent-gold)', 
              border: '1px solid var(--border-gold)',
              fontFamily: 'var(--font-mono)'
            }}>
              {document_type}
            </span>
          </div>

          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span>Jurisdiction: <strong>Maharashtra, India</strong></span>
            <span>•</span>
            <span>PII Redacted: <strong style={{ color: 'var(--accent-gold)' }}>{total_items_masked} items</strong></span>
            <span>•</span>
            <span style={{ color: 'var(--text-gold)', display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-mono)' }}>
              <Clock style={{ width: '13px', height: '13px' }} /> Latency: {processing_time_seconds}s
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handlePrintReport} className="btn-secondary" style={{ fontSize: '0.82rem' }}>
            <Printer style={{ width: '14px', height: '14px', color: 'var(--accent-gold)' }} /> Export Statutory Audit PDF
          </button>

          <button onClick={onReset} className="btn-secondary" style={{ fontSize: '0.82rem' }}>
            Audit New Document
          </button>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
        {[
          { id: 'dashboard', label: 'Statutory Audit Summary', icon: ShieldAlert },
          { id: 'clauses', label: `Audited Clauses (${analyzed_clauses.length})`, icon: Layers },
          { id: 'chat', label: 'Statutory Legal Assistant', icon: MessageSquare },
          { id: 'compare', label: 'Version Comparison', icon: BookOpen }
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '10px 18px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.84rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: isActive ? 'rgba(197, 168, 128, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                color: isActive ? '#ffffff' : 'var(--text-muted)',
                border: `1px solid ${isActive ? 'var(--accent-gold)' : 'var(--border-slate)'}`,
                transition: 'var(--transition)'
              }}
            >
              <Icon style={{ width: '15px', height: '15px', color: isActive ? 'var(--accent-gold-bright)' : 'var(--text-muted)' }} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW & HEATMAP */}
      {activeTab === 'dashboard' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Top Score Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '20px' }}>
            
            {/* Health Score Gauge Card */}
            <div className="glass-card" style={{ padding: '28px 20px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700, marginBottom: '14px' }}>
                Compliance Rating
              </div>

              <div style={{
                width: '110px',
                height: '110px',
                borderRadius: '50%',
                border: `6px solid ${gradeInfo.color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2.2rem',
                fontWeight: 800,
                fontFamily: 'var(--font-heading)',
                color: gradeInfo.color,
                marginBottom: '12px'
              }}>
                {health_score}
                <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontFamily: 'var(--font-body)' }}>/100</span>
              </div>

              <div style={{ fontSize: '0.78rem', fontWeight: 700, color: gradeInfo.color, letterSpacing: '0.04em' }}>
                {gradeInfo.grade}
              </div>
            </div>

            {/* Executive Summary & Statutory Risk Counters */}
            <div className="glass-card" style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1rem', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldAlert style={{ color: 'var(--accent-gold)', width: '16px', height: '16px' }} />
                  Executive Statutory Audit Summary
                </h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
                  {executive_summary}
                </p>
              </div>

              {/* Risk Level Stat Badges */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginTop: '18px' }}>
                <div style={{ padding: '10px', borderRadius: 'var(--radius-sm)', background: 'var(--risk-critical-bg)', border: '1px solid var(--risk-critical-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--risk-critical-text)', fontFamily: 'var(--font-mono)' }}>{risk_summary.critical}</div>
                  <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--risk-critical-text)' }}>CRITICAL</div>
                </div>

                <div style={{ padding: '10px', borderRadius: 'var(--radius-sm)', background: 'var(--risk-high-bg)', border: '1px solid var(--risk-high-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--risk-high-text)', fontFamily: 'var(--font-mono)' }}>{risk_summary.high}</div>
                  <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--risk-high-text)' }}>HIGH</div>
                </div>

                <div style={{ padding: '10px', borderRadius: 'var(--radius-sm)', background: 'var(--risk-medium-bg)', border: '1px solid var(--risk-medium-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--risk-medium-text)', fontFamily: 'var(--font-mono)' }}>{risk_summary.medium}</div>
                  <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--risk-medium-text)' }}>MEDIUM</div>
                </div>

                <div style={{ padding: '10px', borderRadius: 'var(--radius-sm)', background: 'var(--risk-low-bg)', border: '1px solid var(--risk-low-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--risk-low-text)', fontFamily: 'var(--font-mono)' }}>{risk_summary.low}</div>
                  <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--risk-low-text)' }}>LOW</div>
                </div>
              </div>
            </div>

          </div>

          {/* Top Concerns List */}
          {top_concerns && top_concerns.length > 0 && (
            <div style={{
              padding: '18px 22px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--risk-critical-bg)',
              border: '1px solid var(--risk-critical-border)'
            }}>
              <h4 style={{ color: 'var(--risk-critical-text)', fontSize: '0.92rem', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle style={{ width: '16px', height: '16px' }} />
                High Priority Statutory Compliance Violations
              </h4>
              <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#fecdd3', lineHeight: 1.6 }}>
                {top_concerns.map((concern, idx) => (
                  <li key={idx} style={{ marginBottom: '3px' }}>{concern}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Document Risk Heatmap */}
          <RiskHeatmap heatmapData={risk_heatmap} onSelectClause={(id) => {
            setActiveTab('clauses');
          }} />

        </div>
      )}

      {/* TAB 2: FLAGGED CLAUSES */}
      {activeTab === 'clauses' && (
        <div>
          {/* Risk Level Filter Bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Showing {filteredClauses.length} of {analyzed_clauses.length} evaluated clauses:
            </div>
            
            <div style={{ display: 'flex', gap: '6px' }}>
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => (
                <button
                  key={level}
                  onClick={() => setRiskFilter(level)}
                  style={{
                    padding: '5px 12px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    cursor: 'pointer',
                    background: riskFilter === level ? 'rgba(197, 168, 128, 0.2)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${riskFilter === level ? 'var(--accent-gold)' : 'var(--border-slate)'}`,
                    color: riskFilter === level ? '#ffffff' : 'var(--text-muted)'
                  }}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Clause Cards List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {filteredClauses.map(clause => (
              <ClauseCard key={clause.clause_id} clause={clause} />
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: CONTRACT CHAT */}
      {activeTab === 'chat' && (
        <ContractChat contractText={data.document_name} analyzedClauses={analyzed_clauses} />
      )}

      {/* TAB 4: CONTRACT COMPARISON */}
      {activeTab === 'compare' && (
        <ContractComparison originalAnalysis={data} />
      )}

    </div>
  );
}
