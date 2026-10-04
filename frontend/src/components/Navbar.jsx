import React from 'react';
import { Scale, FileCheck, User, LogOut, History } from 'lucide-react';

export default function Navbar({ user, onOpenAuth, onLogout, onNavigate, currentPage }) {
  return (
    <header className="navbar-container" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 40px',
      borderBottom: '1px solid var(--border-gold)',
      background: 'rgba(9, 14, 26, 0.95)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      {/* Brand Header */}
      <div 
        onClick={() => onNavigate('landing')} 
        style={{ display: 'flex', alignItems: 'center', gap: '14px', cursor: 'pointer' }}
      >
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '6px',
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          border: '1px solid var(--accent-gold)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--shadow-gold)'
        }}>
          <Scale style={{ color: 'var(--accent-gold-bright)', width: '20px', height: '20px' }} />
        </div>
        <div>
          <h1 style={{ 
            fontFamily: 'var(--font-heading)', 
            fontSize: '1.2rem', 
            margin: 0, 
            lineHeight: 1.1, 
            letterSpacing: '0.04em',
            color: '#ffffff'
          }}>
            CONTRACTLENS
          </h1>
          <span style={{ fontSize: '0.7rem', color: 'var(--accent-gold)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            Statutory Legal Compliance Engine
          </span>
        </div>
      </div>

      {/* Navigation Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button 
          className="btn-secondary"
          onClick={() => onNavigate('landing')}
          style={{ 
            padding: '8px 18px', 
            fontSize: '0.82rem',
            borderColor: currentPage === 'landing' ? 'var(--accent-gold)' : 'var(--border-slate)'
          }}
        >
          <FileCheck style={{ width: '15px', height: '15px', color: 'var(--accent-gold)' }} />
          New Audit
        </button>

        {user && (
          <button 
            className="btn-secondary"
            onClick={() => onNavigate('history')}
            style={{ 
              padding: '8px 18px', 
              fontSize: '0.82rem',
              borderColor: currentPage === 'history' ? 'var(--accent-gold)' : 'var(--border-slate)'
            }}
          >
            <History style={{ width: '15px', height: '15px', color: '#93c5fd' }} />
            Audit History
          </button>
        )}

        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: '4px',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-slate)',
              fontSize: '0.82rem'
            }}>
              <User style={{ width: '14px', height: '14px', color: 'var(--accent-gold)' }} />
              <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{user.full_name}</span>
            </div>
            <button 
              onClick={onLogout}
              title="Logout"
              style={{
                background: 'transparent',
                border: '1px solid var(--border-slate)',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '7px 10px',
                borderRadius: '4px',
                transition: 'var(--transition)'
              }}
            >
              <LogOut style={{ width: '15px', height: '15px' }} />
            </button>
          </div>
        ) : (
          <button 
            className="btn-primary"
            onClick={onOpenAuth}
          >
            <User style={{ width: '14px', height: '14px' }} />
            Sign In / Access
          </button>
        )}
      </div>
    </header>
  );
}
