import React, { useState } from 'react';
import { BookOpen, AlertCircle, ChevronDown, ChevronUp, Copy, Check, ShieldAlert } from 'lucide-react';

export default function ClauseCard({ clause, index, isTopRisk }) {
  const [showSimple, setShowSimple] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  if (!clause) return null;

  const {
    section_number,
    title,
    original_text,
    topic,
    risk_level,
    reason,
    legal_explanation,
    simple_explanation,
    relevant_statutes,
    suggested_wording
  } = clause;

  const handleCopyWording = () => {
    if (suggested_wording) {
      navigator.clipboard.writeText(suggested_wording);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getLeftBorderColor = (level) => {
    if (level === 'CRITICAL') return 'var(--risk-critical-border)';
    if (level === 'HIGH') return 'var(--risk-high-border)';
    if (level === 'MEDIUM') return 'var(--risk-medium-border)';
    return 'var(--risk-low-border)';
  };

  return (
    <div className="minimal-card" style={{ 
      padding: '20px 24px', 
      borderLeft: `4px solid ${getLeftBorderColor(risk_level)}`,
      marginBottom: '4px'
    }}>
      
      {/* Clause Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {isTopRisk && (
            <span style={{ 
              fontSize: '0.72rem', 
              fontWeight: 800, 
              color: 'var(--accent-gold)', 
              background: 'var(--accent-gold-bg)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-gold)'
            }}>
              RISK #{index}
            </span>
          )}
          
          <h3 style={{ fontSize: '1rem', margin: 0, fontWeight: 700, color: 'var(--text-main)' }}>
            {title || `Clause ${section_number}`}
          </h3>

          {topic && (
            <span style={{
              fontSize: '0.72rem',
              padding: '2px 8px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--bg-subtle)',
              color: 'var(--text-muted)',
              fontWeight: 500
            }}>
              {topic}
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className={`badge-risk ${risk_level}`}>
            {risk_level}
          </span>
          <button 
            onClick={() => setIsExpanded(!isExpanded)} 
            className="btn-minimal"
            style={{ padding: '4px 8px', border: 'none', background: 'transparent' }}
          >
            {isExpanded ? <ChevronUp style={{ width: '16px', height: '16px' }} /> : <ChevronDown style={{ width: '16px', height: '16px' }} />}
          </button>
        </div>
      </div>

      {/* Expanded Clause Body */}
      {isExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '14px' }}>
          
          {/* Original Contract Text */}
          <div style={{
            padding: '12px 14px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-main)',
            fontSize: '0.84rem',
            color: 'var(--text-muted)',
            lineHeight: 1.5
          }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px', fontWeight: 700 }}>
              Original Clause Text:
            </div>
            "{original_text}"
          </div>

          {/* Statutory Finding Box */}
          <div style={{
            padding: '12px 14px',
            borderRadius: 'var(--radius-md)',
            background: risk_level === 'CRITICAL' ? 'var(--risk-critical-bg)' : risk_level === 'HIGH' ? 'var(--risk-high-bg)' : 'var(--bg-surface)',
            border: `1px solid ${getLeftBorderColor(risk_level)}`
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <div style={{ fontWeight: 700, fontSize: '0.86rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertCircle style={{ width: '15px', height: '15px', color: 'var(--accent-gold)' }} />
                Statutory Finding: {reason}
              </div>

              {/* Explain Simply Toggle */}
              <button
                onClick={() => setShowSimple(!showSimple)}
                className="btn-minimal"
                style={{ padding: '2px 8px', fontSize: '0.72rem' }}
              >
                {showSimple ? 'Legal Mode' : 'Plain Mode'}
              </button>
            </div>

            <p style={{ fontSize: '0.84rem', color: 'var(--text-main)', lineHeight: 1.5, margin: 0 }}>
              {showSimple ? simple_explanation : legal_explanation}
            </p>
          </div>

          {/* Verified Statutory Citations */}
          {relevant_statutes && relevant_statutes.length > 0 && (
            <div style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-main)'
            }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--accent-gold)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <BookOpen style={{ width: '13px', height: '13px' }} />
                Statutory Law Citation
              </div>
              {relevant_statutes.map((stat, idx) => (
                <div key={idx} style={{ fontSize: '0.8rem', color: 'var(--text-main)', marginTop: '4px' }}>
                  <strong>{stat.act_name} — {stat.section}</strong>: {stat.title}
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {stat.key_legal_takeaway}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recommended Revised Drafting */}
          {suggested_wording && (
            <div style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-subtle)',
              border: '1px solid var(--border-main)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Recommended Statutory Revision:
                </div>
                <button
                  onClick={handleCopyWording}
                  className="btn-minimal"
                  style={{ padding: '2px 8px', fontSize: '0.72rem' }}
                >
                  {copied ? <Check style={{ width: '12px', height: '12px', color: '#166534' }} /> : <Copy style={{ width: '12px', height: '12px' }} />}
                  {copied ? 'Copied' : 'Copy Revised Term'}
                </button>
              </div>

              <p style={{ fontSize: '0.84rem', color: 'var(--text-main)', fontStyle: 'italic', margin: 0, lineHeight: 1.5 }}>
                "{suggested_wording}"
              </p>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
