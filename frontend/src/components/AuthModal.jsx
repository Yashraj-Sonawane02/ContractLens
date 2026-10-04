import React, { useState } from 'react';
import { X, Lock, Mail, User, ShieldCheck, AlertCircle } from 'lucide-react';
import { authAPI } from '../services/api';

export default function AuthModal({ isOpen, onClose, onSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let data;
      if (isLogin) {
        data = await authAPI.login(email, password);
      } else {
        data = await authAPI.register(fullName, email, password);
      }
      onSuccess(data.user);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.82)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div className="glass-card animate-fade-in" style={{
        width: '100%',
        maxWidth: '420px',
        padding: '32px',
        position: 'relative',
        border: '1px solid var(--border-gold)'
      }}>
        {/* Close Button */}
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X style={{ width: '18px', height: '18px' }} />
        </button>

        {/* Modal Header */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(197, 168, 128, 0.1)',
            border: '1px solid var(--border-gold)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 12px'
          }}>
            <ShieldCheck style={{ color: 'var(--accent-gold-bright)', width: '22px', height: '22px' }} />
          </div>
          <h2 style={{ fontSize: '1.35rem', marginBottom: '4px', fontFamily: 'var(--font-heading)' }}>
            {isLogin ? 'Sign In to Terminal' : 'Register Account'}
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {isLogin ? 'Access your saved statutory contract audit history' : 'Create an account to archive contract analysis reports'}
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--risk-critical-bg)',
            border: '1px solid var(--risk-critical-border)',
            color: 'var(--risk-critical-text)',
            fontSize: '0.78rem',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle style={{ width: '15px', height: '15px', flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '5px' }}>
                Full Name
              </label>
              <div style={{ position: 'relative' }}>
                <User style={{ position: 'absolute', left: '12px', top: '11px', width: '15px', height: '15px', color: 'var(--text-subtle)' }} />
                <input 
                  type="text"
                  required
                  placeholder="Rahul Sharma"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
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
            </div>
          )}

          <div style={{ marginBottom: '14px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '5px' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail style={{ position: 'absolute', left: '12px', top: '11px', width: '15px', height: '15px', color: 'var(--text-subtle)' }} />
              <input 
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '5px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock style={{ position: 'absolute', left: '12px', top: '11px', width: '15px', height: '15px', color: 'var(--text-subtle)' }} />
              <input 
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
          </div>

          <button 
            type="submit" 
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', padding: '11px' }}
          >
            {loading ? 'Processing...' : (isLogin ? 'Sign In to Account' : 'Create Account')}
          </button>
        </form>

        {/* Toggle Login/Register */}
        <div style={{ textAlign: 'center', marginTop: '18px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          {isLogin ? "Don't have an account? " : "Already registered? "}
          <button 
            type="button"
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--accent-gold)',
              fontWeight: 700,
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            {isLogin ? 'Register Now' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}
