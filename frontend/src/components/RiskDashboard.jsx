import React, { useState } from 'react';
import { 
  ShieldAlert, AlertTriangle, FileText, Layers, Printer, BookOpen, Clock, 
  MessageSquare, Download, Mail, Award, BarChart2, CheckCircle2, ArrowRight, GitCompare
} from 'lucide-react';
import ClauseCard from './ClauseCard';
import RiskHeatmap from './RiskHeatmap';
import ContractChat from './ContractChat';
import ContractComparison from './ContractComparison';
import NegotiationGenerator from './NegotiationGenerator';
import EmpiricalBenchmarkModal from './EmpiricalBenchmarkModal';
import api from '../services/api';

export default function RiskDashboard({ data, onReset }) {
  const [activeTab, setActiveTab] = useState('top3'); // 'top3', 'all_clauses', 'negotiate', 'compare', 'chat'
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingDocx, setDownloadingDocx] = useState(false);
  const [downloadingCert, setDownloadingCert] = useState(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);

  if (!data) return null;

  const {
    document_name,
    document_type,
    health_score,
    risk_summary,
    executive_summary,
    top_concerns,
    analyzed_clauses,
    total_items_masked,
    processing_time_seconds,
    language
  } = data;

  // Priority Sort Clauses: CRITICAL first, then HIGH, MEDIUM, LOW
  const riskPriority = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
  const sortedClauses = [...analyzed_clauses].sort((a, b) => {
    return (riskPriority[b.risk_level] || 0) - (riskPriority[a.risk_level] || 0);
  });

  const top3Clauses = sortedClauses.slice(0, 3);

  const filteredClauses = analyzed_clauses.filter(c => {
    if (riskFilter === 'ALL') return true;
    return c.risk_level === riskFilter;
  });

  const getComplianceGrade = (score) => {
    if (score >= 85) return { grade: 'GRADE A • STATUTORY COMPLIANT', color: '#166534' };
    if (score >= 70) return { grade: 'GRADE B • MODERATE RISK', color: '#1e40af' };
    if (score >= 50) return { grade: 'GRADE C • HIGH RISK', color: '#92400e' };
    return { grade: 'GRADE D • SEVERE NON-COMPLIANCE', color: '#991b1b' };
  };

  const gradeInfo = getComplianceGrade(health_score);

  const handleExportPdf = async () => {
    try {
      setDownloadingPdf(true);
      const response = await api.post('/document/export-pdf', data, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const cleanName = (document_name || 'Contract').replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9]/g, "_");
      link.setAttribute('download', `ContractLens_Legal_Opinion_${cleanName}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Failed to generate PDF report.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleExportDocx = async () => {
    try {
      setDownloadingDocx(true);
      const response = await api.post('/document/export-docx', data, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const cleanName = (document_name || 'Contract').replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9]/g, "_");
      link.setAttribute('download', `Revised_Redlined_${cleanName}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('DOCX export failed:', err);
      alert('Failed to generate DOCX contract.');
    } finally {
      setDownloadingDocx(false);
    }
  };

  const handleExportCertificate = async () => {
    try {
      setDownloadingCert(true);
      const response = await api.post('/document/export-certificate', data, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const cleanName = (document_name || 'Contract').replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9]/g, "_");
      link.setAttribute('download', `Compliance_Certificate_${cleanName}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Certificate export failed:', err);
      alert('Failed to generate certificate.');
    } finally {
      setDownloadingCert(false);
    }
  };

  return (
    <div style={{ maxWidth: '1060px', margin: '0 auto', padding: '24px 24px 80px' }} className="animate-fade-in">
      
      {/* Executive Header Bar */}
      <div className="minimal-card" style={{ padding: '20px 24px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <FileText style={{ color: 'var(--accent-navy)', width: '20px', height: '20px' }} />
              <h1 style={{ fontSize: '1.25rem', margin: 0, fontWeight: 700 }}>{document_name}</h1>
              <span style={{ 
                fontSize: '0.74rem', 
                padding: '2px 8px', 
                borderRadius: 'var(--radius-sm)', 
                background: 'var(--bg-subtle)', 
                color: 'var(--text-muted)',
                fontWeight: 600
              }}>
                {document_type}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px', display: 'flex', gap: '12px' }}>
              <span>Jurisdiction: <strong>Maharashtra, India</strong></span>
              <span>•</span>
              <span>Audit Time: <strong>{processing_time_seconds}s</strong></span>
              <span>•</span>
              <span>Redacted PII: <strong>{total_items_masked} items</strong></span>
            </div>
          </div>

          {/* Action Export Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <button onClick={handleExportPdf} disabled={downloadingPdf} className="btn-minimal">
              <Printer style={{ width: '14px', height: '14px' }} />
              {downloadingPdf ? 'Exporting...' : 'PDF Report'}
            </button>

            <button onClick={handleExportDocx} disabled={downloadingDocx} className="btn-minimal">
              <FileText style={{ width: '14px', height: '14px' }} />
              {downloadingDocx ? 'Exporting...' : 'Revised DOCX'}
            </button>

            <button onClick={handleExportCertificate} disabled={downloadingCert} className="btn-minimal">
              <Award style={{ width: '14px', height: '14px' }} />
              {downloadingCert ? 'Generating...' : 'Certificate'}
            </button>

            <button onClick={onReset} className="btn-minimal btn-minimal-primary">
              Audit New File
            </button>
          </div>
        </div>
      </div>

      {/* Compliance Health Score & Triage Bar */}
      <div className="minimal-card" style={{ padding: '20px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '20px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '50%',
            background: health_score >= 75 ? 'var(--risk-low-bg)' : health_score >= 50 ? 'var(--risk-high-bg)' : 'var(--risk-critical-bg)',
            border: `2px solid ${health_score >= 75 ? 'var(--risk-low-border)' : health_score >= 50 ? 'var(--risk-high-border)' : 'var(--risk-critical-border)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '1.25rem',
            color: health_score >= 75 ? 'var(--risk-low-text)' : health_score >= 50 ? 'var(--risk-high-text)' : 'var(--risk-critical-text)',
            fontFamily: 'var(--font-mono)'
          }}>
            {health_score}
          </div>

          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600 }}>
              Statutory Compliance Index
            </div>
            <div style={{ fontWeight: 700, fontSize: '0.98rem', color: gradeInfo.color, marginTop: '2px' }}>
              {gradeInfo.grade}
            </div>
          </div>
        </div>

        {/* Triage Badges */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <div className="badge-risk CRITICAL" style={{ padding: '6px 12px' }}>
            {risk_summary.critical} CRITICAL
          </div>
          <div className="badge-risk HIGH" style={{ padding: '6px 12px' }}>
            {risk_summary.high} HIGH
          </div>
          <div className="badge-risk MEDIUM" style={{ padding: '6px 12px' }}>
            {risk_summary.medium} MEDIUM
          </div>
          <div className="badge-risk LOW" style={{ padding: '6px 12px' }}>
            {risk_summary.low} COMPLIANT
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid var(--border-main)', paddingBottom: '10px' }}>
        <button
          onClick={() => setActiveTab('top3')}
          style={{
            padding: '8px 16px',
            fontSize: '0.86rem',
            fontWeight: 700,
            borderRadius: 'var(--radius-md)',
            border: 'none',
            background: activeTab === 'top3' ? 'var(--accent-navy)' : 'transparent',
            color: activeTab === 'top3' ? 'var(--text-inverse)' : 'var(--text-muted)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <AlertTriangle style={{ width: '15px', height: '15px' }} />
          Top 3 Critical Risks
        </button>

        <button
          onClick={() => setActiveTab('all_clauses')}
          style={{
            padding: '8px 16px',
            fontSize: '0.86rem',
            fontWeight: 600,
            borderRadius: 'var(--radius-md)',
            border: 'none',
            background: activeTab === 'all_clauses' ? 'var(--accent-navy)' : 'transparent',
            color: activeTab === 'all_clauses' ? 'var(--text-inverse)' : 'var(--text-muted)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Layers style={{ width: '15px', height: '15px' }} />
          All Audited Clauses ({analyzed_clauses.length})
        </button>

        <button
          onClick={() => setActiveTab('negotiate')}
          style={{
            padding: '8px 16px',
            fontSize: '0.86rem',
            fontWeight: 600,
            borderRadius: 'var(--radius-md)',
            border: 'none',
            background: activeTab === 'negotiate' ? 'var(--accent-navy)' : 'transparent',
            color: activeTab === 'negotiate' ? 'var(--text-inverse)' : 'var(--text-muted)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Mail style={{ width: '15px', height: '15px', color: 'var(--accent-gold)' }} />
          Negotiation & Notice Generator
        </button>

        <button
          onClick={() => setActiveTab('compare')}
          style={{
            padding: '8px 16px',
            fontSize: '0.86rem',
            fontWeight: 600,
            borderRadius: 'var(--radius-md)',
            border: 'none',
            background: activeTab === 'compare' ? 'var(--accent-navy)' : 'transparent',
            color: activeTab === 'compare' ? 'var(--text-inverse)' : 'var(--text-muted)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <GitCompare style={{ width: '15px', height: '15px' }} />
          Version Redline Matrix
        </button>

        <button
          onClick={() => setActiveTab('chat')}
          style={{
            padding: '8px 16px',
            fontSize: '0.86rem',
            fontWeight: 600,
            borderRadius: 'var(--radius-md)',
            border: 'none',
            background: activeTab === 'chat' ? 'var(--accent-navy)' : 'transparent',
            color: activeTab === 'chat' ? 'var(--text-inverse)' : 'var(--text-muted)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <MessageSquare style={{ width: '15px', height: '15px' }} />
          Statutory Legal Chat
        </button>
      </div>

      {/* TAB 1: TOP 3 CRITICAL RISKS PRIMARY VIEW */}
      {activeTab === 'top3' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Action Callout Banner to Ask Landlord to Change Top 3 Clauses */}
          <div className="minimal-card" style={{ 
            padding: '20px 24px', 
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-gold)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
            flexWrap: 'wrap'
          }}>
            <div>
              <h3 style={{ fontSize: '1rem', color: 'var(--text-main)', margin: 0, fontWeight: 700 }}>
                Request Amendments for Top 3 Critical Risks
              </h3>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Generate a formal statutory amendment request asking the landlord to revise these 3 non-compliant provisions.
              </p>
            </div>

            <button
              className="btn-minimal btn-minimal-gold"
              onClick={() => setActiveTab('negotiate')}
              style={{ padding: '10px 18px', fontWeight: 700 }}
            >
              <span>Ask Landlord to Change These 3 Clauses</span>
              <ArrowRight style={{ width: '15px', height: '15px' }} />
            </button>
          </div>

          {/* Render Top 3 Risk Cards */}
          {top3Clauses.map((clause, idx) => (
            <ClauseCard key={clause.clause_id || idx} clause={clause} index={idx + 1} isTopRisk={true} />
          ))}

          {/* View All Clauses Button */}
          {analyzed_clauses.length > 3 && (
            <div style={{ textAlign: 'center', marginTop: '12px' }}>
              <button
                className="btn-minimal"
                onClick={() => setActiveTab('all_clauses')}
                style={{ padding: '10px 24px', fontSize: '0.86rem' }}
              >
                View Remaining {analyzed_clauses.length - 3} Audited Clauses
                <ArrowRight style={{ width: '14px', height: '14px' }} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ALL AUDITED CLAUSES VIEW */}
      {activeTab === 'all_clauses' && (
        <div>
          {/* Risk Filter Bar */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => (
              <button
                key={level}
                onClick={() => setRiskFilter(level)}
                className="btn-minimal"
                style={{
                  fontSize: '0.78rem',
                  padding: '6px 12px',
                  borderColor: riskFilter === level ? 'var(--accent-navy)' : 'var(--border-main)',
                  fontWeight: riskFilter === level ? 700 : 500
                }}
              >
                {level} ({level === 'ALL' ? analyzed_clauses.length : analyzed_clauses.filter(c => c.risk_level === level).length})
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {filteredClauses.map((clause, idx) => (
              <ClauseCard key={clause.clause_id || idx} clause={clause} index={idx + 1} isTopRisk={false} />
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: NEGOTIATION EMAIL & NOTICE GENERATOR */}
      {activeTab === 'negotiate' && (
        <NegotiationGenerator clauses={top3Clauses} documentName={document_name} />
      )}

      {/* TAB 4: VERSION REDLINE MATRIX */}
      {activeTab === 'compare' && (
        <ContractComparison analyzedClauses={analyzed_clauses} documentName={document_name} />
      )}

      {/* TAB 5: STATUTORY LEGAL ASSISTANT CHAT */}
      {activeTab === 'chat' && (
        <ContractChat analyzedClauses={analyzed_clauses} documentName={document_name} />
      )}

      {/* Empirical Benchmark Modal */}
      {isBenchmarkOpen && (
        <EmpiricalBenchmarkModal onClose={() => setIsBenchmarkOpen(false)} />
      )}

    </div>
  );
}
