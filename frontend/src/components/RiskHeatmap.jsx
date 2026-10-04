import React from 'react';
import { Layers } from 'lucide-react';

export default function RiskHeatmap({ heatmapData, onSelectClause }) {
  if (!heatmapData || heatmapData.length === 0) return null;

  const getHeatmapBorder = (level) => {
    switch (level) {
      case 'CRITICAL': return 'var(--risk-critical-border)';
      case 'HIGH': return 'var(--risk-high-border)';
      case 'MEDIUM': return 'var(--risk-medium-border)';
      default: return 'var(--risk-low-border)';
    }
  };

  const getHeatmapBg = (level) => {
    switch (level) {
      case 'CRITICAL': return 'var(--risk-critical-bg)';
      case 'HIGH': return 'var(--risk-high-bg)';
      case 'MEDIUM': return 'var(--risk-medium-bg)';
      default: return 'var(--risk-low-bg)';
    }
  };

  return (
    <div className="glass-card" style={{ padding: '24px 28px' }}>
      <h3 style={{ fontSize: '1rem', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
        <Layers style={{ color: 'var(--accent-gold)', width: '16px', height: '16px' }} />
        Contract Clause Risk Distribution Heatmap
      </h3>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
        Visual mapping of risk intensity across evaluated clauses. Click any clause block to inspect statutory findings.
      </p>

      {/* Heatmap Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '10px' }}>
        {heatmapData.map((item) => {
          const border = getHeatmapBorder(item.risk_level);
          const bg = getHeatmapBg(item.risk_level);
          return (
            <div
              key={item.clause_id}
              onClick={() => onSelectClause(item.clause_id)}
              style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                background: bg,
                border: `1px solid ${border}`,
                cursor: 'pointer',
                transition: 'var(--transition)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-gold)', fontFamily: 'var(--font-mono)' }}>
                  Sec {item.section}
                </span>
                <span className={`badge-risk ${item.risk_level}`} style={{ fontSize: '0.62rem', padding: '1px 5px' }}>
                  {item.risk_level}
                </span>
              </div>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#ffffff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {item.title}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
