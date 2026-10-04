import React, { useState } from 'react';
import { 
  UploadCloud, ShieldCheck, Scale, FileText, ArrowRight, Lock, BookOpen, Search, AlertCircle
} from 'lucide-react';

const LEGAL_DOMAINS = [
  {
    id: 'rental_property',
    name: 'Maharashtra Property & Tenancy Agreements',
    acts: [
      'Maharashtra Rent Control Act, 1999 (MRCA)',
      'Transfer of Property Act, 1882 (TPA)',
      'Indian Contract Act, 1872 (ICA)'
    ],
    desc: 'Audits Leave & License terms, deposit forfeiture rules, rent escalation caps, notice period imbalances, and unlawful utility threats.',
    badge: 'Primary Jurisdiction'
  },
  {
    id: 'commercial_nda',
    name: 'Commercial & Corporate Contracts',
    acts: ['Indian Contract Act, 1872 (Sec. 23 & 28)'],
    desc: 'Audits non-disclosure terms, unilateral liability waivers, non-competes, and dispute resolution clauses.',
    badge: 'Standard Legal'
  }
];

export default function LandingPage({ onStartAnalysis, onOpenLegalExplorer }) {
  const [selectedDomains, setSelectedDomains] = useState(['rental_property']);
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileError, setFileError] = useState('');

  const toggleDomain = (id) => {
    if (selectedDomains.includes(id)) {
      if (selectedDomains.length > 1) {
        setSelectedDomains(selectedDomains.filter(d => d !== id));
      }
    } else {
      setSelectedDomains([...selectedDomains, id]);
    }
  };

  const handleFileChange = (file) => {
    setFileError('');
    if (!file) return;

    const validExtensions = ['pdf', 'docx', 'doc', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(ext)) {
      setFileError('Unsupported document format. Please provide a valid legal PDF, DOCX, or TXT file.');
      setSelectedFile(null);
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setFileError('File size exceeds the maximum permitted limit of 15MB.');
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleStart = () => {
    if (!selectedFile) {
      setFileError('Please select or upload a legal contract document for analysis.');
      return;
    }
    onStartAnalysis({
      file: selectedFile,
      domains: selectedDomains,
      language: selectedLanguage
    });
  };

  return (
    <div style={{ maxWidth: '1140px', margin: '0 auto', padding: '40px 24px 80px' }}>
      
      {/* Executive Header Banner */}
      <div style={{ textAlign: 'center', marginBottom: '44px' }} className="animate-fade-in">
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 18px',
          borderRadius: '4px',
          background: 'rgba(197, 168, 128, 0.08)',
          border: '1px solid var(--border-gold)',
          color: 'var(--accent-gold)',
          fontSize: '0.78rem',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          marginBottom: '18px'
        }}>
          <Scale style={{ width: '14px', height: '14px', color: 'var(--accent-gold-bright)' }} />
          Statutory RAG Verification • Grounded in Indian Legislation
        </div>

        <h1 style={{ 
          fontSize: '2.8rem', 
          lineHeight: 1.15, 
          marginBottom: '16px',
          letterSpacing: '0.02em',
          color: '#ffffff'
        }}>
          STATUTORY LEGAL AUDIT TERMINAL
        </h1>
        
        <p style={{ fontSize: '1.05rem', color: 'var(--text-muted)', maxWidth: '720px', margin: '0 auto', lineHeight: 1.6 }}>
          Automated statutory risk analysis and privacy protection under the 
          <strong style={{ color: '#f1f5f9' }}> Maharashtra Rent Control Act 1999</strong>, 
          <strong style={{ color: '#f1f5f9' }}> Transfer of Property Act 1882</strong>, and 
          <strong style={{ color: '#f1f5f9' }}> Indian Contract Act 1872</strong>.
        </p>

        {/* Pre-Indexed Acts Tag Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '12px',
          marginTop: '22px',
          flexWrap: 'wrap'
        }}>
          {['MRCA 1999 (Sec. 7, 10, 24, 29, 55)', 'TPA 1882 (Sec. 105, 106, 108)', 'ICA 1872 (Sec. 23, 28, 74)'].map((act, idx) => (
            <div key={idx} style={{ 
              padding: '6px 14px', 
              borderRadius: '4px', 
              background: 'rgba(255, 255, 255, 0.03)', 
              border: '1px solid var(--border-slate)', 
              fontSize: '0.78rem', 
              color: 'var(--text-gold)', 
              fontFamily: 'var(--font-mono)',
              fontWeight: 500
            }}>
              • {act}
            </div>
          ))}
        </div>
      </div>

      {/* Main Workspace Terminal Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: '28px', marginBottom: '40px' }}>
        
        {/* Left Column: Domain & Jurisdiction Parameters */}
        <div className="glass-card card-gold-accent" style={{ padding: '28px' }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen style={{ color: 'var(--accent-gold)', width: '18px', height: '18px' }} />
            1. Select Statutory Jurisdiction
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Choose applicable legal framework for automated statutory verification.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
            {LEGAL_DOMAINS.map((domain) => {
              const isSelected = selectedDomains.includes(domain.id);
              return (
                <div
                  key={domain.id}
                  onClick={() => toggleDomain(domain.id)}
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    background: isSelected ? 'rgba(197, 168, 128, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${isSelected ? 'var(--accent-gold)' : 'var(--border-slate)'}`,
                    cursor: 'pointer',
                    transition: 'var(--transition)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.92rem', color: isSelected ? '#ffffff' : 'var(--text-main)' }}>
                      {domain.name}
                    </span>
                    <span style={{ 
                      fontSize: '0.68rem', 
                      padding: '2px 8px', 
                      borderRadius: '3px', 
                      background: 'rgba(255, 255, 255, 0.05)', 
                      color: 'var(--accent-gold)', 
                      border: '1px solid var(--border-gold)',
                      fontFamily: 'var(--font-mono)'
                    }}>
                      {domain.badge}
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    {domain.desc}
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    {domain.acts.map((actName, aIdx) => (
                      <span key={aIdx} style={{ fontSize: '0.72rem', color: 'var(--accent-gold)', fontFamily: 'var(--font-mono)' }}>
                        ✓ {actName}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Language Selection */}
          <div style={{ paddingTop: '18px', borderTop: '1px solid var(--border-slate)' }}>
            <h3 style={{ fontSize: '0.85rem', marginBottom: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Output Language Format
            </h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              {['English', 'Hindi (हिंदी)', 'Marathi (मराठी)'].map((lang) => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => setSelectedLanguage(lang.split(' ')[0])}
                  style={{
                    flex: 1,
                    padding: '8px 10px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    background: selectedLanguage === lang.split(' ')[0] ? 'rgba(197, 168, 128, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${selectedLanguage === lang.split(' ')[0] ? 'var(--accent-gold)' : 'var(--border-slate)'}`,
                    color: selectedLanguage === lang.split(' ')[0] ? '#ffffff' : 'var(--text-muted)',
                    transition: 'var(--transition)'
                  }}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Contract Document Upload */}
        <div className="glass-card card-gold-accent" style={{ padding: '28px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <UploadCloud style={{ color: 'var(--accent-gold)', width: '18px', height: '18px' }} />
              2. Upload Contract Document
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              Accepts PDF, DOCX, or TXT (up to 15MB). Contextual PII masking automatically redacts names, Aadhaar/PAN IDs, and financial credentials locally under DPDP Act guidelines before statutory evaluation.
            </p>

            {/* Upload Drag & Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              style={{
                border: `2px dashed ${dragOver ? 'var(--accent-gold-bright)' : selectedFile ? 'var(--accent-gold)' : 'rgba(255, 255, 255, 0.12)'}`,
                borderRadius: 'var(--radius-md)',
                padding: '36px 20px',
                textAlign: 'center',
                background: dragOver ? 'rgba(197, 168, 128, 0.08)' : selectedFile ? 'rgba(197, 168, 128, 0.05)' : 'rgba(0, 0, 0, 0.25)',
                cursor: 'pointer',
                transition: 'var(--transition)',
                marginBottom: '18px'
              }}
            >
              <input
                type="file"
                id="contract-file-input"
                accept=".pdf,.docx,.doc,.txt"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
              />
              
              <label htmlFor="contract-file-input" style={{ cursor: 'pointer', display: 'block' }}>
                {selectedFile ? (
                  <div>
                    <FileText style={{ width: '40px', height: '40px', color: 'var(--accent-gold-bright)', margin: '0 auto 10px' }} />
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#ffffff' }}>{selectedFile.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for Audit
                    </div>
                  </div>
                ) : (
                  <div>
                    <UploadCloud style={{ width: '40px', height: '40px', color: 'var(--accent-gold)', margin: '0 auto 10px' }} />
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#ffffff' }}>
                      Drag and drop contract file here
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      or <span style={{ color: 'var(--accent-gold)', textDecoration: 'underline' }}>select file from computer</span>
                    </div>
                  </div>
                )}
              </label>
            </div>

            {/* Error Message */}
            {fileError && (
              <div style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--risk-critical-bg)',
                border: '1px solid var(--risk-critical-border)',
                color: 'var(--risk-critical-text)',
                fontSize: '0.8rem',
                marginBottom: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <AlertCircle style={{ width: '15px', height: '15px', flexShrink: 0 }} />
                <span>{fileError}</span>
              </div>
            )}

            {/* Legal Safeguard Notes */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.78rem', color: 'var(--text-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Lock style={{ width: '13px', height: '13px', color: 'var(--accent-gold)' }} />
                <span>Contextual PII Redaction: Preserves numerical legal figures while masking personal identifiers.</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <ShieldCheck style={{ width: '13px', height: '13px', color: 'var(--accent-gold)' }} />
                <span>Deterministic Statutory Matching: Evaluated strictly against verified sections of Indian law.</span>
              </div>
            </div>
          </div>

          {/* Start Audit CTA */}
          <div style={{ marginTop: '24px' }}>
            <button
              onClick={handleStart}
              className="btn-primary"
              style={{
                width: '100%',
                justifyContent: 'center',
                padding: '14px',
                fontSize: '0.92rem'
              }}
            >
              Execute Statutory Audit
              <ArrowRight style={{ width: '16px', height: '16px' }} />
            </button>
          </div>
        </div>

      </div>

      {/* Statutory Explorer Card */}
      <div className="glass-card" style={{ padding: '24px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen style={{ color: 'var(--accent-gold)', width: '18px', height: '18px' }} />
            Pre-Indexed Statutory Database
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
            Inspect full legal provisions from MRCA 1999, TPA 1882, and ICA 1872 directly in the Statutory Knowledge Explorer.
          </p>
        </div>
        <button onClick={onOpenLegalExplorer} className="btn-secondary" style={{ padding: '8px 16px', fontSize: '0.82rem' }}>
          <Search style={{ width: '14px', height: '14px', color: 'var(--accent-gold)' }} /> Open Statutory Database
        </button>
      </div>

    </div>
  );
}
