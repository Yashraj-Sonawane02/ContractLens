import React, { useState, useEffect } from 'react';
import { Mail, Copy, Check, Send, RefreshCw, FileText } from 'lucide-react';
import api from '../services/api';

export default function NegotiationGenerator({ clauses, documentName, data }) {
  const [tone, setTone] = useState('formal'); // 'polite', 'formal', 'legal_notice'
  const [recipientName, setRecipientName] = useState('Licensor / Landlord');
  const [senderName, setSenderName] = useState('Licensee / Tenant');
  const [loading, setLoading] = useState(false);
  const [emailData, setEmailData] = useState(null);
  const [copiedSubject, setCopiedSubject] = useState(false);
  const [copiedBody, setCopiedBody] = useState(false);

  const handleGenerate = async () => {
    const analysisPayload = data || {
      document_name: documentName || "Leave & License Agreement",
      analyzed_clauses: clauses || [],
      risk_summary: { critical: 3, high: 0, medium: 0, low: 0 }
    };

    try {
      setLoading(true);
      const res = await api.post('/negotiation/generate', {
        analysis_data: analysisPayload,
        tone: tone,
        recipient_name: recipientName,
        sender_name: senderName,
        language: 'English'
      });
      if (res.data && res.data.data) {
        setEmailData(res.data.data);
      }
    } catch (err) {
      console.error('Failed to generate negotiation email:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGenerate();
  }, [tone]);

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    if (type === 'subject') {
      setCopiedSubject(true);
      setTimeout(() => setCopiedSubject(false), 2000);
    } else {
      setCopiedBody(true);
      setTimeout(() => setCopiedBody(false), 2000);
    }
  };

  const handleOpenMailApp = () => {
    if (!emailData) return;
    const mailtoUrl = `mailto:?subject=${encodeURIComponent(emailData.subject)}&body=${encodeURIComponent(emailData.body)}`;
    window.location.href = mailtoUrl;
  };

  return (
    <div className="minimal-card" style={{ padding: '24px' }}>
      
      {/* Header Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid var(--border-main)', paddingBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Mail style={{ color: 'var(--accent-navy)', width: '20px', height: '20px' }} />
          <div>
            <h2 style={{ fontSize: '1.1rem', margin: 0, fontWeight: 700 }}>
              Landlord Counter-Proposal & Notice Generator
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0' }}>
              Generates a formal legal amendment request asking the landlord to revise the top 3 risky clauses.
            </p>
          </div>
        </div>

        <button 
          onClick={handleGenerate} 
          disabled={loading} 
          className="btn-minimal"
        >
          <RefreshCw style={{ width: '13px', height: '13px', animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          {loading ? 'Generating...' : 'Regenerate'}
        </button>
      </div>

      {/* Controls Bar: Tone Selector & Names */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px 200px', gap: '14px', marginBottom: '20px', background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-main)' }}>
        
        {/* Tone Selection */}
        <div>
          <label style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
            Negotiation Tone:
          </label>
          <div style={{ display: 'flex', gap: '6px' }}>
            {[
              { id: 'formal', label: 'Formal Legal' },
              { id: 'polite', label: 'Polite / Professional' },
              { id: 'legal_notice', label: 'Advocate Notice' }
            ].map(t => (
              <button
                key={t.id}
                onClick={() => setTone(t.id)}
                className="btn-minimal"
                style={{
                  fontSize: '0.76rem',
                  padding: '4px 10px',
                  background: tone === t.id ? 'var(--accent-navy)' : 'var(--bg-surface)',
                  color: tone === t.id ? 'var(--text-inverse)' : 'var(--text-main)',
                  fontWeight: tone === t.id ? 700 : 500
                }}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Recipient Name */}
        <div>
          <label style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
            Addressed To:
          </label>
          <input
            type="text"
            value={recipientName}
            onChange={(e) => setRecipientName(e.target.value)}
            style={{
              width: '100%',
              padding: '6px 10px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-main)',
              color: 'var(--text-main)',
              fontSize: '0.82rem',
              outline: 'none'
            }}
          />
        </div>

        {/* Sender Name */}
        <div>
          <label style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
            Signed By:
          </label>
          <input
            type="text"
            value={senderName}
            onChange={(e) => setSenderName(e.target.value)}
            style={{
              width: '100%',
              padding: '6px 10px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-main)',
              color: 'var(--text-main)',
              fontSize: '0.82rem',
              outline: 'none'
            }}
          />
        </div>

      </div>

      {/* Generated Output Preview */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '36px 20px', color: 'var(--text-muted)' }}>
          <RefreshCw style={{ width: '20px', height: '20px', animation: 'spin 1s linear infinite', marginBottom: '8px' }} />
          <p style={{ fontSize: '0.86rem', margin: 0 }}>Drafting statutorily grounded negotiation communication...</p>
        </div>
      ) : emailData ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          
          {/* Subject Line Field */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Subject Line:
              </span>
              <button 
                onClick={() => copyToClipboard(emailData.subject, 'subject')} 
                className="btn-minimal"
                style={{ fontSize: '0.72rem', padding: '2px 8px' }}
              >
                {copiedSubject ? <Check style={{ width: '12px', height: '12px', color: '#166534' }} /> : <Copy style={{ width: '12px', height: '12px' }} />}
                {copiedSubject ? 'Copied' : 'Copy Subject'}
              </button>
            </div>
            <div style={{ padding: '10px 14px', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)', borderRadius: 'var(--radius-md)', fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)' }}>
              {emailData.subject}
            </div>
          </div>

          {/* Email Body Field */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Notice Body:
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  onClick={() => copyToClipboard(emailData.body, 'body')} 
                  className="btn-minimal"
                  style={{ fontSize: '0.72rem', padding: '4px 10px' }}
                >
                  {copiedBody ? <Check style={{ width: '12px', height: '12px', color: '#166534' }} /> : <Copy style={{ width: '12px', height: '12px' }} />}
                  {copiedBody ? 'Copied Text' : 'Copy Notice Text'}
                </button>

                <button 
                  onClick={handleOpenMailApp} 
                  className="btn-minimal btn-minimal-primary"
                  style={{ fontSize: '0.72rem', padding: '4px 10px' }}
                >
                  <Send style={{ width: '12px', height: '12px' }} />
                  Open in Email Client
                </button>
              </div>
            </div>

            <textarea
              readOnly
              value={emailData.body}
              rows={12}
              style={{
                width: '100%',
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-main)',
                color: 'var(--text-main)',
                fontSize: '0.86rem',
                lineHeight: '1.6',
                fontFamily: 'var(--font-mono)',
                outline: 'none',
                resize: 'vertical'
              }}
            />
          </div>

        </div>
      ) : null}

    </div>
  );
}
