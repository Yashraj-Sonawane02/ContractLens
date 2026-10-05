import React, { useState } from 'react';
import { BookOpen, UploadCloud, FileText, CheckCircle2, AlertTriangle, XCircle, ArrowRight, ShieldCheck, GitCompare } from 'lucide-react';
import api from '../services/api';

export default function ContractComparison({ originalAnalysis, data, analyzedClauses, documentName }) {
  const sourceAnalysis = originalAnalysis || data || {
    document_name: documentName || "Original Contract",
    health_score: 70,
    analyzed_clauses: analyzedClauses || [],
    language: "English"
  };

  const [secondFile, setSecondFile] = useState(null);
  const [comparing, setComparing] = useState(false);
  const [diffResult, setDiffResult] = useState(null);

  const handleCompare = async () => {
    if (!secondFile) return;
    setComparing(true);

    try {
      const formData = new FormData();
      formData.append('file', secondFile);
      formData.append('language', sourceAnalysis.language || 'English');

      const response = await api.post('/analysis/run', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const newAnalysis = response.data;
      const oldScore = sourceAnalysis.health_score || 70;
      const newScore = newAnalysis.health_score || 70;
      const scoreDiff = newScore - oldScore;

      const matrix = buildClauseDiffMatrix(
        sourceAnalysis.analyzed_clauses || [],
        newAnalysis.analyzed_clauses || []
      );

      const resolvedCount = matrix.filter(m => m.status === 'RESOLVED').length;
      const newRiskCount = matrix.filter(m => m.status === 'NEW_RISK').length;

      setDiffResult({
        oldScore,
        newScore,
        scoreDiff,
        newDocumentName: secondFile.name,
        newAnalysis: newAnalysis,
        matrix: matrix,
        resolvedCount: resolvedCount,
        newRiskCount: newRiskCount
      });
    } catch (err) {
      console.error('Comparison error:', err);
      alert("Failed to analyze revised contract for comparison. Please check backend connection.");
    } finally {
      setComparing(false);
    }
  };

  const buildClauseDiffMatrix = (oldClauses, newClauses) => {
    const matrix = [];
    const maxLen = Math.max(oldClauses.length, newClauses.length);

    for (let i = 0; i < maxLen; i++) {
      const oldC = oldClauses[i] || null;
      const newC = newClauses[i] || null;

      let status = 'UNALTERED';
      if (oldC && newC) {
        if (['CRITICAL', 'HIGH', 'MEDIUM'].includes(oldC.risk_level) && newC.risk_level === 'LOW') {
          status = 'RESOLVED';
        } else if (oldC.risk_level === 'LOW' && ['CRITICAL', 'HIGH', 'MEDIUM'].includes(newC.risk_level)) {
          status = 'NEW_RISK';
        } else if (oldC.original_text !== newC.original_text) {
          status = 'MODIFIED';
        } else {
          status = 'UNALTERED';
        }
      } else if (!oldC && newC) {
        status = 'ADDED_IN_V2';
      } else if (oldC && !newC) {
        status = 'DELETED_IN_V2';
      }

      matrix.push({
        secNum: oldC?.section_number || newC?.section_number || i + 1,
        title: oldC?.title || newC?.title || `Clause ${i + 1}`,
        oldClause: oldC,
        newClause: newC,
        status: status
      });
    }
    return matrix;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RESOLVED':
        return { label: 'Statutorily Resolved', bg: 'var(--risk-low-bg)', text: 'var(--risk-low-text)', border: 'var(--risk-low-border)' };
      case 'NEW_RISK':
        return { label: 'New Risk Introduced', bg: 'var(--risk-critical-bg)', text: 'var(--risk-critical-text)', border: 'var(--risk-critical-border)' };
      case 'MODIFIED':
        return { label: 'Wording Amended', bg: 'var(--risk-medium-bg)', text: 'var(--risk-medium-text)', border: 'var(--risk-medium-border)' };
      case 'DELETED_IN_V2':
        return { label: 'Clause Removed in v2', bg: 'var(--bg-subtle)', text: 'var(--text-muted)', border: 'var(--border-main)' };
      case 'ADDED_IN_V2':
        return { label: 'New Clause Added in v2', bg: 'var(--risk-high-bg)', text: 'var(--risk-high-text)', border: 'var(--risk-high-border)' };
      default:
        return { label: 'Unaltered', bg: 'var(--bg-subtle)', text: 'var(--text-muted)', border: 'var(--border-main)' };
    }
  };

  return (
    <div className="minimal-card" style={{ padding: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--border-main)', paddingBottom: '14px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', margin: 0, fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)' }}>
            <GitCompare style={{ color: 'var(--accent-navy)', width: '20px', height: '20px' }} />
            Contract Version & Redline Alignment Matrix
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0' }}>
            Compare counter-drafts side-by-side to track statutory risk shifts and unauthorized clause modifications.
          </p>
        </div>

        {diffResult && (
          <button 
            onClick={() => { setDiffResult(null); setSecondFile(null); }} 
            className="btn-minimal"
          >
            Compare Another Draft
          </button>
        )}
      </div>

      {!diffResult ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignItems: 'center' }}>
          
          {/* Version 1 Details */}
          <div style={{ padding: '20px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, fontFamily: 'var(--font-mono)', marginBottom: '6px' }}>
              VERSION 1 (ORIGINAL AUDITED DRAFT)
            </div>
            <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)', marginBottom: '8px' }}>
              {sourceAnalysis.document_name}
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', gap: '12px' }}>
              <span>Compliance Index: <strong style={{ color: 'var(--accent-navy)' }}>{sourceAnalysis.health_score}/100</strong></span>
              <span>•</span>
              <span>Clauses: <strong>{(sourceAnalysis.analyzed_clauses || []).length}</strong></span>
            </div>
          </div>

          {/* Version 2 Upload */}
          <div style={{ padding: '24px', borderRadius: 'var(--radius-md)', background: 'var(--bg-surface)', border: '2px dashed var(--border-main)', textAlign: 'center' }}>
            <input
              type="file"
              id="second-file-input"
              accept=".pdf,.docx,.doc,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && setSecondFile(e.target.files[0])}
            />
            
            <label htmlFor="second-file-input" style={{ cursor: 'pointer', display: 'block' }}>
              <UploadCloud style={{ width: '32px', height: '32px', color: 'var(--accent-navy)', margin: '0 auto 8px' }} />
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>
                {secondFile ? secondFile.name : 'Click to Upload Revised Counter-Draft (v2)'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Supports PDF, DOCX, or TXT
              </div>
            </label>

            {secondFile && (
              <button
                onClick={handleCompare}
                className="btn-minimal btn-minimal-primary"
                disabled={comparing}
                style={{ marginTop: '16px', padding: '8px 20px', fontSize: '0.84rem' }}
              >
                {comparing ? 'Auditing Side-by-Side Revisions...' : 'Execute Revision Comparison'}
              </button>
            )}
          </div>

        </div>
      ) : (
        /* Executive Side-by-Side Comparison Matrix */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Executive Rating Shift Bar */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '14px' }}>
            
            {/* Version 1 Rating */}
            <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>VERSION 1 SCORE</span>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                {diffResult.oldScore} / 100
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>{sourceAnalysis.document_name}</div>
            </div>

            {/* Version 2 Rating */}
            <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', border: `1px solid ${diffResult.scoreDiff >= 0 ? 'var(--risk-low-border)' : 'var(--risk-critical-border)'}` }}>
              <span style={{ fontSize: '0.72rem', color: diffResult.scoreDiff >= 0 ? 'var(--risk-low-text)' : 'var(--risk-critical-text)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>VERSION 2 SCORE</span>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: diffResult.scoreDiff >= 0 ? 'var(--risk-low-text)' : 'var(--risk-critical-text)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                {diffResult.newScore} / 100 ({diffResult.scoreDiff >= 0 ? `+${diffResult.scoreDiff}` : diffResult.scoreDiff})
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>{diffResult.newDocumentName}</div>
            </div>

            {/* Revision Delta Summary */}
            <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>REVISION DELTA</div>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--risk-low-text)', marginTop: '4px' }}>
                ✅ {diffResult.resolvedCount} Violations Resolved
              </div>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: diffResult.newRiskCount > 0 ? 'var(--risk-critical-text)' : 'var(--text-muted)', marginTop: '2px' }}>
                ⚠️ {diffResult.newRiskCount} New Risks Introduced
              </div>
            </div>

          </div>

          {/* Side-by-Side Clause Alignment Matrix */}
          <div>
            <h3 style={{ fontSize: '1rem', marginBottom: '12px', fontWeight: 700, color: 'var(--text-main)' }}>
              Side-by-Side Clause Alignment Matrix
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {diffResult.matrix.map((row, i) => {
                const badge = getStatusBadge(row.status);
                return (
                  <div key={i} style={{ borderRadius: 'var(--radius-md)', background: 'var(--bg-surface)', border: `1px solid ${badge.border}`, overflow: 'hidden' }}>
                    
                    {/* Clause Header Bar */}
                    <div style={{ padding: '10px 14px', background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border-main)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        Clause {row.secNum}: {row.title}
                      </span>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '2px 8px', borderRadius: 'var(--radius-sm)', background: badge.bg, color: badge.text, border: `1px solid ${badge.border}` }}>
                        {badge.label}
                      </span>
                    </div>

                    {/* Side-by-Side Dual Columns */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px', background: 'var(--border-main)' }}>
                      
                      {/* Version 1 Column */}
                      <div style={{ padding: '12px 14px', background: 'var(--bg-surface)' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '4px' }}>
                          VERSION 1 (ORIGINAL DRAFT)
                        </div>
                        {row.oldClause ? (
                          <>
                            <p style={{ fontSize: '0.82rem', color: 'var(--text-main)', margin: '0 0 6px', fontStyle: 'italic' }}>
                              "{row.oldClause.original_text}"
                            </p>
                            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                              Risk Rating: <strong>{row.oldClause.risk_level}</strong> — {row.oldClause.reason}
                            </div>
                          </>
                        ) : (
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Not present in Version 1</span>
                        )}
                      </div>

                      {/* Version 2 Column */}
                      <div style={{ padding: '12px 14px', background: 'var(--bg-surface)' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--accent-navy)', fontWeight: 700, marginBottom: '4px' }}>
                          VERSION 2 (REVISED COUNTER-DRAFT)
                        </div>
                        {row.newClause ? (
                          <>
                            <p style={{ fontSize: '0.82rem', color: 'var(--text-main)', margin: '0 0 6px', fontStyle: 'italic' }}>
                              "{row.newClause.original_text}"
                            </p>
                            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                              Risk Rating: <strong>{row.newClause.risk_level}</strong> — {row.newClause.reason}
                            </div>
                          </>
                        ) : (
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Removed in Version 2</span>
                        )}
                      </div>

                    </div>

                  </div>
                );
              })}
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
