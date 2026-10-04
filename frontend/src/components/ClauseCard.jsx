import React, { useState } from 'react';
import { BookOpen, AlertCircle, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

export default function ClauseCard({ clause }) {
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

  const getBorderColor = (level) => {
    if (level === 'CRITICAL') return 'var(--risk-critical-border)';
    if (level === 'HIGH') return 'var(--risk-high-border)';
    if (level === 'MEDIUM') return 'var(--risk-medium-border)';
    return 'var(--risk-low-border)';
  };

  return (
    <div className="glass-card" style={{ 
      padding: '20px 24px', 
      borderLeft: `4px solid ${getBorderColor(risk_level)}` 
    }}>
      
      {/* Clause Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-gold)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
            Sec {section_number}
          </span>
          <h3 style={{ fontSize: '1.05rem', margin: 0, fontFamily: 'var(--font-heading)' }}>{title}</h3>
          <span style={{
            fontSize: '0.7rem',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(255, 255, 255, 0.03)',
            color: 'var(--text-muted)',
            border: '1px solid var(--border-slate)',
            fontWeight: 500
          }}>
            {topic}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className={`badge-risk ${risk_level}`}>
            {risk_level} RISK
          </span>
          <button 
            onClick={() => setIsExpanded(!isExpanded)} 
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            {isExpanded ? <ChevronUp style={{ width: '18px', height: '18px' }} /> : <ChevronDown style={{ width: '18px', height: '18px' }} />}
          </button>
        </div>
      </div>

      {/* Expanded Clause Body */}
      {isExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '14px' }}>
          
          {/* Original Contract Text Box */}
          <div style={{
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(0, 0, 0, 0.35)',
            border: '1px solid var(--border-slate)',
            fontSize: '0.85rem',
            color: '#cbd5e1',
            lineHeight: 1.6,
            fontFamily: 'var(--font-body)'
          }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px', fontWeight: 700 }}>
              Original Contract Text:
            </div>
            {original_text}
          </div>

          {/* Legal Finding Box */}
          <div style={{
            padding: '14px 16px',
            borderRadius: 'var(--radius-sm)',
            background: risk_level === 'CRITICAL' ? 'var(--risk-critical-bg)' : 'rgba(255, 255, 255, 0.02)',
            border: `1px solid ${getBorderColor(risk_level)}`
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.86rem', color: '#ffffff' }}>
                <AlertCircle style={{ width: '15px', height: '15px', color: 'var(--accent-gold)' }} />
                Statutory Finding: {reason}
              </div>

              {/* Explain Simply Toggle */}
              <button
                onClick={() => setShowSimple(!showSimple)}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid var(--border-slate)',
                  color: 'var(--accent-gold)',
                  padding: '3px 9px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {showSimple ? 'View Legal Explanation' : 'Plain Legal Breakdown'}
              </button>
            </div>

            <p style={{ fontSize: '0.84rem', color: '#e2e8f0', lineHeight: 1.6, margin: 0 }}>
              {showSimple ? simple_explanation : legal_explanation}
            </p>
          </div>

          {/* Verified Statutory Citations */}
          {relevant_statutes && relevant_statutes.length > 0 && (
            <div style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(197, 168, 128, 0.05)',
              border: '1px solid var(--border-gold)'
            }}>
              <div style={{ fontSize: '0.76rem', fontWeight: 700, color: 'var(--accent-gold)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <BookOpen style={{ width: '13px', height: '13px' }} />
                Statutory Authority & Precedent
              </div>
              {relevant_statutes.map((stat, idx) => (
                <div key={idx} style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '4px' }}>
                  <strong style={{ color: '#ffffff' }}>{stat.act_name} — {stat.section}</strong>: {stat.title}
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
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-slate)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ fontSize: '0.76rem', fontWeight: 700, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Recommended Revised Drafting
                </div>
                <button
                  onClick={handleCopyWording}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--border-slate)',
                    color: copied ? '#6ee7b7' : 'var(--text-muted)',
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {copied ? <Check style={{ width: '12px', height: '12px' }} /> : <Copy style={{ width: '12px', height: '12px' }} />}
                  {copied ? 'Copied' : 'Copy Revised Clause'}
                </button>
              </div>

              <p style={{ fontSize: '0.84rem', color: '#f1f5f9', fontStyle: 'italic', margin: 0, lineHeight: 1.5, fontFamily: 'var(--font-body)' }}>
                "{suggested_wording}"
              </p>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
