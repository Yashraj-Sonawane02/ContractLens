import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import LegalExplorerModal from './components/LegalExplorerModal';
import EmpiricalBenchmarkModal from './components/EmpiricalBenchmarkModal';
import LandingPage from './pages/LandingPage';
import HistoryPage from './pages/HistoryPage';
import RiskDashboard from './components/RiskDashboard';
import { authAPI } from './services/api';
import api from './services/api';
import { Cpu, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isLegalExplorerOpen, setIsLegalExplorerOpen] = useState(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('landing');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState('Initializing');

  useEffect(() => {
    // Check if user is logged in
    const currentUser = authAPI.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    }
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
    setAnalysisResult(null);
    setCurrentPage('landing');
  };

  const handleStartAnalysis = async (config) => {
    setAnalyzing(true);
    setAnalysisStage('Encrypting and uploading contract document...');

    try {
      const formData = new FormData();
      formData.append('file', config.file);
      formData.append('language', config.language);
      formData.append('domains', JSON.stringify(config.domains));

      const token = localStorage.getItem('contractlens_token');
      const customHeaders = { 'Content-Type': 'multipart/form-data' };
      if (token) {
        customHeaders['Authorization'] = `Bearer ${token}`;
      }

      setAnalysisStage('Extracting document text & structures...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStage('Contextual PII Privacy Redaction...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStage('Clause Segmentation & Stage-1 Triage...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStage('Statutory RAG Evaluation across 3 Acts (MRCA 1999 + TPA 1882 + ICA 1872)...');

      const response = await api.post('/analysis/run', formData, {
        headers: customHeaders
      });

      setAnalysisResult(response.data);
      setCurrentPage('dashboard');
    } catch (err) {
      alert("Failed to analyze legal contract: " + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
        onNavigate={(page) => {
          if (page === 'landing') setAnalysisResult(null);
          setCurrentPage(page);
        }}
        currentPage={currentPage}
        onOpenBenchmark={() => setIsBenchmarkOpen(true)}
        onOpenLegalExplorer={() => setIsLegalExplorerOpen(true)}
      />

      <main style={{ flex: 1 }}>
        {/* Loading Overlay */}
        {analyzing && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(9, 13, 22, 0.85)',
            backdropFilter: 'blur(12px)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            textAlign: 'center',
            padding: '24px'
          }}>
            <div className="minimal-card" style={{ padding: '36px 44px', maxWidth: '480px', width: '100%' }}>
              <div style={{
                width: '52px',
                height: '52px',
                borderRadius: '16px',
                background: 'var(--accent-navy)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                boxShadow: 'var(--shadow-md)'
              }}>
                <Cpu style={{ width: '26px', height: '26px' }} />
              </div>

              <h2 style={{ fontSize: '1.25rem', marginBottom: '6px', fontWeight: 700, color: 'var(--text-main)' }}>
                Auditing Legal Contract
              </h2>
              <p style={{ fontSize: '0.86rem', color: 'var(--accent-navy)', fontWeight: 600, marginBottom: '20px' }}>
                {analysisStage}
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'left' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 style={{ width: '14px', height: '14px', color: '#166534' }} /> Multi-Format Text Extraction
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 style={{ width: '14px', height: '14px', color: '#166534' }} /> Contextual PII Privacy Redaction
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 style={{ width: '14px', height: '14px', color: '#166534' }} /> Grounded RAG across MRCA 1999, TPA 1882 & ICA 1872
                </div>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'landing' && !analysisResult && (
          <LandingPage
            onStartAnalysis={handleStartAnalysis}
            onOpenLegalExplorer={() => setIsLegalExplorerOpen(true)}
            onOpenBenchmark={() => setIsBenchmarkOpen(true)}
          />
        )}

        {currentPage === 'dashboard' && analysisResult && (
          <RiskDashboard data={analysisResult} onReset={() => {
            setAnalysisResult(null);
            setCurrentPage('landing');
          }} />
        )}

        {currentPage === 'history' && (
          <HistoryPage onSelectReport={(savedReport) => {
            setAnalysisResult(savedReport);
            setCurrentPage('dashboard');
          }} />
        )}
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(loggedUser) => {
          setUser(loggedUser);
          setIsAuthOpen(false);
        }}
      />

      {/* Legal Explorer Modal */}
      <LegalExplorerModal
        isOpen={isLegalExplorerOpen}
        onClose={() => setIsLegalExplorerOpen(false)}
      />

      {/* Empirical Benchmark Modal */}
      {isBenchmarkOpen && (
        <EmpiricalBenchmarkModal
          onClose={() => setIsBenchmarkOpen(false)}
        />
      )}

      {/* Minimal Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '20px',
        borderTop: '1px solid var(--border-main)',
        color: 'var(--text-muted)',
        fontSize: '0.78rem'
      }}>
        ContractLens V2 — Statutory Legal AI SaaS grounded in Maharashtra Rent Control Act 1999, Transfer of Property Act 1882, and Indian Contract Act 1872.
      </footer>
    </div>
  );
}
