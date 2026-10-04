import React, { useState, useEffect } from 'react';
import { X, Search, BookOpen, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

export default function LegalExplorerModal({ isOpen, onClose }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [laws, setLaws] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedLaw, setSelectedLaw] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchLaws('');
    }
  }, [isOpen]);

  const fetchLaws = async (q) => {
    setLoading(true);
    try {
      const response = await api.get(`/legal/explorer?query=${encodeURIComponent(q)}`);
      setLaws(response.data.laws || []);
      if (response.data.laws && response.data.laws.length > 0) {
        setSelectedLaw(response.data.laws[0]);
      }
    } catch (err) {
      console.error("Failed to fetch legal statutes:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchLaws(searchQuery);
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1100,
      padding: '24px'
    }}>
      <div className="glass-card animate-fade-in" style={{
        width: '100%',
        maxWidth: '960px',
        height: '80vh',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        border: '1px solid var(--border-gold)',
        padding: 0,
        overflow: 'hidden'
      }}>
        
        {/* Modal Header */}
        <div style={{ padding: '18px 24px', borderBottom: '1px solid var(--border-slate)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(9, 14, 26, 0.95)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookOpen style={{ color: 'var(--accent-gold)', width: '20px', height: '20px' }} />
            <div>
              <h2 style={{ fontSize: '1.15rem', margin: 0, fontFamily: 'var(--font-heading)' }}>Statutory Knowledge Explorer</h2>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Pre-indexed Statutory Database: MRCA 1999, TPA 1882 & ICA 1872</span>
            </div>
          </div>

          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X style={{ width: '20px', height: '20px' }} />
          </button>
        </div>

        {/* Search Bar */}
        <div style={{ padding: '14px 24px', borderBottom: '1px solid var(--border-slate)', background: 'rgba(0, 0, 0, 0.25)' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search style={{ position: 'absolute', left: '12px', top: '11px', width: '15px', height: '15px', color: 'var(--text-subtle)' }} />
              <input
                type="text"
                placeholder="Search by section or keyword (e.g., Section 24, rent escalation, penalty, deposit)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px 9px 36px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--border-slate)',
                  color: '#ffffff',
                  fontSize: '0.86rem'
                }}
              />
            </div>
            <button type="submit" className="btn-primary" style={{ padding: '8px 18px', fontSize: '0.82rem' }}>
              Search Database
            </button>
          </form>
        </div>

        {/* Modal Body Grid */}
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '300px 1fr', overflow: 'hidden' }}>
          
          {/* Left Column: Statutes List */}
          <div style={{ borderRight: '1px solid var(--border-slate)', overflowY: 'auto', padding: '12px' }}>
            {laws.map((law) => {
              const isSelected = selectedLaw && selectedLaw.id === law.id;
              return (
                <div
                  key={law.id}
                  onClick={() => setSelectedLaw(law)}
                  style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: '6px',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(197, 168, 128, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${isSelected ? 'var(--accent-gold)' : 'transparent'}`,
                    transition: 'var(--transition)'
                  }}
                >
                  <div style={{ fontSize: '0.7rem', color: 'var(--accent-gold)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{law.act_name}</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', marginTop: '2px' }}>{law.section}</div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {law.title}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Section Detail View */}
          <div style={{ padding: '24px', overflowY: 'auto' }}>
            {selectedLaw ? (
              <div>
                <div style={{ display: 'inline-block', padding: '3px 8px', borderRadius: 'var(--radius-sm)', background: 'rgba(197, 168, 128, 0.1)', color: 'var(--accent-gold)', fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', marginBottom: '10px' }}>
                  {selectedLaw.act_name} ({selectedLaw.jurisdiction})
                </div>

                <h3 style={{ fontSize: '1.25rem', marginBottom: '8px', fontFamily: 'var(--font-heading)' }}>{selectedLaw.section}: {selectedLaw.title}</h3>

                <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-sm)', background: 'rgba(0, 0, 0, 0.35)', border: '1px solid var(--border-slate)', fontSize: '0.86rem', color: '#cbd5e1', lineHeight: 1.7, marginBottom: '18px' }}>
                  {selectedLaw.content}
                </div>

                <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-sm)', background: 'rgba(197, 168, 128, 0.05)', border: '1px solid var(--border-gold)' }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-gold)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    <CheckCircle2 style={{ width: '13px', height: '13px' }} /> Key Legal Takeaway
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#ffffff', margin: 0, lineHeight: 1.5 }}>
                    {selectedLaw.key_legal_takeaway}
                  </p>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '80px', fontSize: '0.85rem' }}>
                Select a statutory section on the left to view full legal text.
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
