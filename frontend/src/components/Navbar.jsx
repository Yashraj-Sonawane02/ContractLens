import React, { useState, useEffect } from 'react';
import { Scale, FileText, User, LogOut, History, Sun, Moon, BookOpen } from 'lucide-react';

export default function Navbar({ 
  user, 
  onOpenAuth, 
  onLogout, 
  onNavigate, 
  currentPage,
  onOpenLegalExplorer
}) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('contractlens_theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('contractlens_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 32px',
      borderBottom: '1px solid var(--border-main)',
      background: 'var(--bg-surface)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      transition: 'var(--transition)'
    }}>
      {/* Brand Logo & Title */}
      <div 
        onClick={() => onNavigate('landing')} 
        style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
      >
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'var(--accent-navy)',
          color: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <Scale style={{ width: '18px', height: '18px' }} />
        </div>
        <div>
          <h1 style={{ 
            fontFamily: 'var(--font-heading)', 
            fontSize: '1.05rem', 
            margin: 0, 
            lineHeight: 1.1, 
            letterSpacing: '-0.02em',
            color: 'var(--text-main)',
            fontWeight: 800
          }}>
            ContractLens
          </h1>
        </div>
      </div>

      {/* Navigation & Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        
        <button 
          className="btn-minimal"
          onClick={() => onNavigate('landing')}
          style={{
            borderColor: currentPage === 'landing' ? 'var(--accent-navy)' : 'var(--border-main)',
            fontWeight: currentPage === 'landing' ? 700 : 500
          }}
        >
          <FileText style={{ width: '14px', height: '14px' }} />
          New Audit
        </button>

        {onOpenLegalExplorer && (
          <button 
            className="btn-minimal"
            onClick={onOpenLegalExplorer}
            title="Search Maharashtra Statutory Database"
          >
            <BookOpen style={{ width: '14px', height: '14px' }} />
            Statutes
          </button>
        )}

        {user && (
          <button 
            className="btn-minimal"
            onClick={() => onNavigate('history')}
            style={{ 
              borderColor: currentPage === 'history' ? 'var(--accent-navy)' : 'var(--border-main)',
              fontWeight: currentPage === 'history' ? 700 : 500
            }}
          >
            <History style={{ width: '14px', height: '14px' }} />
            History
          </button>
        )}

        {/* Theme Toggle Button */}
        <button 
          className="btn-minimal"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          style={{ padding: '8px' }}
        >
          {theme === 'light' ? (
            <Moon style={{ width: '15px', height: '15px', color: '#475569' }} />
          ) : (
            <Sun style={{ width: '15px', height: '15px', color: '#fbbf24' }} />
          )}
        </button>

        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '6px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-subtle)',
              fontSize: '0.82rem',
              color: 'var(--text-main)',
              fontWeight: 600
            }}>
              <User style={{ width: '13px', height: '13px', color: 'var(--accent-navy)' }} />
              <span>{user.full_name.split(' ')[0]}</span>
            </div>
            <button 
              onClick={onLogout}
              title="Logout"
              className="btn-minimal"
              style={{ padding: '8px' }}
            >
              <LogOut style={{ width: '14px', height: '14px', color: 'var(--text-muted)' }} />
            </button>
          </div>
        ) : (
          <button 
            className="btn-minimal btn-minimal-primary"
            onClick={onOpenAuth}
            style={{ marginLeft: '4px' }}
          >
            <User style={{ width: '13px', height: '13px' }} />
            Sign In
          </button>
        )}
      </div>
    </header>
  );
}
