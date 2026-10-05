import React, { useState } from 'react';
import { 
  UploadCloud, Scale, FileText, ArrowRight, ShieldCheck, AlertCircle, BookOpen
} from 'lucide-react';

export default function LandingPage({ onStartAnalysis, onOpenLegalExplorer }) {
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileError, setFileError] = useState('');
  const [pastedText, setPastedText] = useState('');
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'paste'

  const handleFileChange = (file) => {
    setFileError('');
    if (!file) return;

    const validExtensions = ['pdf', 'docx', 'doc', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(ext)) {
      setFileError('Unsupported document format. Please upload a valid PDF, DOCX, or TXT legal document.');
      setSelectedFile(null);
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setFileError('File size exceeds the maximum limit of 15MB.');
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
    if (activeTab === 'upload') {
      if (!selectedFile) {
        setFileError('Please select or drag a contract document to begin audit.');
        return;
      }
      onStartAnalysis({
        file: selectedFile,
        domains: ['rental_property'],
        language: selectedLanguage
      });
    } else {
      if (!pastedText || pastedText.trim().length < 30) {
        setFileError('Please paste a valid legal contract clause or text (min 30 characters).');
        return;
      }
      const blob = new Blob([pastedText], { type: 'text/plain' });
      const file = new File([blob], "pasted_contract.txt", { type: "text/plain" });
      onStartAnalysis({
        file: file,
        domains: ['rental_property'],
        language: selectedLanguage
      });
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '60px auto 100px', padding: '0 24px' }} className="animate-fade-in">
      
      {/* Minimal Header */}
      <div style={{ textAlign: 'center', marginBottom: '36px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 12px',
          borderRadius: '20px',
          background: 'var(--bg-subtle)',
          border: '1px solid var(--border-main)',
          color: 'var(--text-muted)',
          fontSize: '0.78rem',
          fontWeight: 600,
          marginBottom: '16px'
        }}>
          <ShieldCheck style={{ width: '14px', height: '14px', color: 'var(--accent-navy)' }} />
          Maharashtra Statutory Legal Engine
        </div>

        <h1 style={{ 
          fontSize: '2.2rem', 
          lineHeight: 1.25, 
          letterSpacing: '-0.03em',
          color: 'var(--text-main)',
          marginBottom: '12px',
          fontWeight: 800
        }}>
          Audit your Leave & License Agreement
        </h1>

        <p style={{ 
          fontSize: '1rem', 
          color: 'var(--text-muted)', 
          maxWidth: '580px', 
          margin: '0 auto',
          lineHeight: 1.5 
        }}>
          Instantly identify unlawful penalty forfeitures, illegal utility cut-off threats, and notice period imbalances grounded in Indian statutory laws.
        </p>
      </div>

      {/* Main Upload / Input Card */}
      <div className="minimal-card" style={{ padding: '32px' }}>
        
        {/* Input Toggle (File Upload vs Text Paste) */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid var(--border-main)', paddingBottom: '12px' }}>
          <button
            onClick={() => { setActiveTab('upload'); setFileError(''); }}
            style={{
              padding: '6px 14px',
              fontSize: '0.84rem',
              fontWeight: 600,
              borderRadius: 'var(--radius-md)',
              border: 'none',
              background: activeTab === 'upload' ? 'var(--bg-subtle)' : 'transparent',
              color: activeTab === 'upload' ? 'var(--text-main)' : 'var(--text-muted)',
              cursor: 'pointer'
            }}
          >
            Upload Document (PDF / DOCX)
          </button>
          <button
            onClick={() => { setActiveTab('paste'); setFileError(''); }}
            style={{
              padding: '6px 14px',
              fontSize: '0.84rem',
              fontWeight: 600,
              borderRadius: 'var(--radius-md)',
              border: 'none',
              background: activeTab === 'paste' ? 'var(--bg-subtle)' : 'transparent',
              color: activeTab === 'paste' ? 'var(--text-main)' : 'var(--text-muted)',
              cursor: 'pointer'
            }}
          >
            Paste Contract Text
          </button>
        </div>

        {activeTab === 'upload' ? (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragOver ? 'var(--accent-navy)' : 'var(--border-main)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: '40px 24px',
              textAlign: 'center',
              background: dragOver ? 'var(--bg-subtle)' : 'var(--bg-surface)',
              transition: 'var(--transition)',
              cursor: 'pointer'
            }}
            onClick={() => document.getElementById('file-upload-input').click()}
          >
            <input
              id="file-upload-input"
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
            />

            <UploadCloud style={{ width: '38px', height: '38px', color: 'var(--accent-navy)', margin: '0 auto 12px' }} />

            {selectedFile ? (
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.98rem', color: 'var(--text-main)' }}>
                  {selectedFile.name}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {(selectedFile.size / 1024).toFixed(1)} KB • Ready for statutory analysis
                </div>
              </div>
            ) : (
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.94rem', color: 'var(--text-main)' }}>
                  Click to select or drag contract file here
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                  Supports PDF, DOCX, or TXT (Max 15MB)
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <textarea
              rows={6}
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste Maharashtra Leave & License contract clauses or full agreement text here..."
              style={{
                width: '100%',
                padding: '12px 14px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-main)',
                background: 'var(--bg-input)',
                color: 'var(--text-main)',
                fontSize: '0.88rem',
                fontFamily: 'var(--font-body)',
                outline: 'none',
                resize: 'vertical'
              }}
            />
          </div>
        )}

        {/* Error Banner */}
        {fileError && (
          <div style={{
            marginTop: '16px',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--risk-critical-bg)',
            border: '1px solid var(--risk-critical-border)',
            color: 'var(--risk-critical-text)',
            fontSize: '0.82rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle style={{ width: '16px', height: '16px', flexShrink: 0 }} />
            <span>{fileError}</span>
          </div>
        )}

        {/* Action Controls Footer */}
        <div style={{ 
          marginTop: '24px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          {/* Language Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              Analysis Output:
            </span>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              style={{
                padding: '6px 12px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-main)',
                background: 'var(--bg-surface)',
                color: 'var(--text-main)',
                fontSize: '0.82rem',
                fontWeight: 600,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="English">English</option>
              <option value="Marathi">Marathi (मराठी)</option>
              <option value="Hindi">Hindi (हिंदी)</option>
            </select>
          </div>

          {/* Start Audit Button */}
          <button
            className="btn-minimal btn-minimal-primary"
            onClick={handleStart}
            style={{ padding: '10px 24px', fontSize: '0.9rem', width: '100%', maxWidth: '220px' }}
          >
            <span>Run Statutory Audit</span>
            <ArrowRight style={{ width: '16px', height: '16px' }} />
          </button>
        </div>
      </div>

      {/* Minimal Quick Links Footer */}
      {onOpenLegalExplorer && (
        <div style={{ 
          marginTop: '32px', 
          display: 'flex', 
          justifyContent: 'center'
        }}>
          <button 
            className="btn-minimal"
            onClick={onOpenLegalExplorer}
            style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}
          >
            <BookOpen style={{ width: '13px', height: '13px' }} />
            Maharashtra Legal Database (MRCA + TPA + ICA)
          </button>
        </div>
      )}

    </div>
  );
}
