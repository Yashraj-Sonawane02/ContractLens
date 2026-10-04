import React, { useState } from 'react';
import { BookOpen, UploadCloud, FileText } from 'lucide-react';
import api from '../services/api';

export default function ContractComparison({ originalAnalysis }) {
  const [secondFile, setSecondFile] = useState(null);
  const [comparing, setComparing] = useState(false);
  const [diffResult, setDiffResult] = useState(null);

  const handleCompare = async () => {
    if (!secondFile) return;
    setComparing(true);

    try {
      const formData = new FormData();
      formData.append('file', secondFile);
      formData.append('language', 'English');

      const response = await api.post('/analysis/run', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const newAnalysis = response.data;
      const oldScore = originalAnalysis.health_score;
      const newScore = newAnalysis.health_score;
      const scoreDiff = newScore - oldScore;

      setDiffResult({
        oldScore,
        newScore,
        scoreDiff,
        newDocumentName: secondFile.name,
        newAnalysis: newAnalysis
      });
    } catch (err) {
      alert("Failed to analyze second contract for comparison. Please try again.");
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '28px' }}>
      <h3 style={{ fontSize: '1.05rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
        <BookOpen style={{ color: 'var(--accent-gold)', width: '18px', height: '18px' }} />
        Contract Version & Revision Audit
      </h3>
      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
        Upload a revised draft or renewal version to track statutory risk shifts and clause modifications.
      </p>

      {!diffResult ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignItems: 'center' }}>
          
          {/* Version 1 Summary */}
          <div style={{ padding: '18px', borderRadius: 'var(--radius-sm)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-slate)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--accent-gold)', fontWeight: 700, fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>VERSION 1 (CURRENT)</div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#ffffff' }}>{originalAnalysis.document_name}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Compliance Rating: <strong style={{ color: 'var(--accent-gold)' }}>{originalAnalysis.health_score}/100</strong> • {originalAnalysis.risk_summary.critical} Critical Violations
            </div>
          </div>

          {/* Version 2 Upload */}
          <div style={{ padding: '18px', borderRadius: 'var(--radius-sm)', background: 'rgba(0, 0, 0, 0.3)', border: '1px dashed var(--border-gold)', textAlign: 'center' }}>
            <input
              type="file"
              id="second-file-input"
              accept=".pdf,.docx,.doc,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && setSecondFile(e.target.files[0])}
            />
            
            <label htmlFor="second-file-input" style={{ cursor: 'pointer', display: 'block' }}>
              <UploadCloud style={{ width: '28px', height: '28px', color: 'var(--accent-gold)', margin: '0 auto 6px' }} />
              <div style={{ fontWeight: 600, fontSize: '0.86rem', color: '#ffffff' }}>
                {secondFile ? secondFile.name : 'Select Revised Contract Draft'}
              </div>
            </label>

            {secondFile && (
              <button
                onClick={handleCompare}
                className="btn-primary"
                disabled={comparing}
                style={{ marginTop: '14px', padding: '7px 18px', fontSize: '0.8rem' }}
              >
                {comparing ? 'Auditing Revision...' : 'Execute Revision Comparison'}
              </button>
            )}
          </div>

        </div>
      ) : (
        /* Comparison Results View */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            
            <div style={{ padding: '18px', borderRadius: 'var(--radius-sm)', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-slate)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>VERSION 1 (ORIGINAL)</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, marginTop: '4px', color: '#ffffff', fontFamily: 'var(--font-mono)' }}>{diffResult.oldScore} / 100</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{originalAnalysis.document_name}</div>
            </div>

            <div style={{ padding: '18px', borderRadius: 'var(--radius-sm)', background: 'rgba(197, 168, 128, 0.08)', border: '1px solid var(--border-gold)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--accent-gold)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>VERSION 2 (REVISED DRAFT)</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, marginTop: '4px', color: diffResult.scoreDiff >= 0 ? '#6ee7b7' : '#fda4af', fontFamily: 'var(--font-mono)' }}>
                {diffResult.newScore} / 100 ({diffResult.scoreDiff >= 0 ? `+${diffResult.scoreDiff}` : diffResult.scoreDiff})
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{diffResult.newDocumentName}</div>
            </div>

          </div>

          <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-sm)', background: 'rgba(0, 0, 0, 0.35)', border: '1px solid var(--border-slate)' }}>
            <h4 style={{ fontSize: '0.88rem', marginBottom: '4px', color: '#ffffff', fontFamily: 'var(--font-heading)' }}>Revision Audit Assessment</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
              {diffResult.scoreDiff > 0 ? (
                <span style={{ color: '#6ee7b7' }}>Version 2 has an improved compliance score ({diffResult.newScore}/100), eliminating statutory risks.</span>
              ) : diffResult.scoreDiff < 0 ? (
                <span style={{ color: '#fda4af' }}>Version 2 introduced new high-risk penalties or restrictive lock-in terms, causing the score to drop to {diffResult.newScore}/100.</span>
              ) : (
                <span>Both versions have identical risk profiles.</span>
              )}
            </p>
          </div>

          <button onClick={() => { setDiffResult(null); setSecondFile(null); }} className="btn-secondary" style={{ alignSelf: 'flex-start', padding: '7px 16px', fontSize: '0.8rem' }}>
            Compare Another Draft
          </button>
        </div>
      )}

    </div>
  );
}
