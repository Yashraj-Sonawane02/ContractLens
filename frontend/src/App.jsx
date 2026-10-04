import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import LegalExplorerModal from './components/LegalExplorerModal';
import LandingPage from './pages/LandingPage';
import HistoryPage from './pages/HistoryPage';
import RiskDashboard from './components/RiskDashboard';
import { authAPI } from './services/api';
import api from './services/api';
import { Sparkles, Shield, Cpu, Lock, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isLegalExplorerOpen, setIsLegalExplorerOpen] = useState(false);
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
    setAnalysisStage('Uploading contract document...');

    try {
      const formData = new FormData();
      formData.append('file', config.file);
      formData.append('language', config.language);
      formData.append('domains', JSON.stringify(config.domains));

      const token = localStorage.getItem('contractlens_token');
      if (token) {
        formData.append('authorization', `Bearer ${token}`);
      }

      setAnalysisStage('Extracting document text & structures...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStage('Contextual PII Privacy Redaction...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStage('Clause Segmentation & Stage-1 Triage...');
      await new Promise(r => setTimeout(r, 150));

      setAnalysisStage('Statutory RAG Evaluation across 3 Acts (MRCA 1999 + TPA 1882 + ICA 1872)...');

      const response = await api.post('/analysis/run', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
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
            background: 'rgba(9, 13, 22, 0.9)',
            backdropFilter: 'blur(16px)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            textAlign: 'center',
            padding: '24px'
          }}>
            <div className="glass-card" style={{ padding: '40px 48px', maxWidth: '520px' }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '20px',
                background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                boxShadow: '0 0 30px rgba(99, 102, 241, 0.6)'
              }}>
                <Cpu style={{ color: '#ffffff', width: '32px', height: '32px' }} />
              </div>

              <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Analyzing Legal Contract</h2>
              <p style={{ fontSize: '0.88rem', color: '#818cf8', fontWeight: 600, marginBottom: '24px' }}>
                {analysisStage}
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'left' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 style={{ width: '14px', height: '14px', color: '#10b981' }} /> Fast Multi-Format Extraction
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 style={{ width: '14px', height: '14px', color: '#10b981' }} /> Contextual PII Privacy Redaction
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 style={{ width: '14px', height: '14px', color: '#10b981' }} /> Grounded RAG across MRCA 1999, TPA 1882 & ICA 1872
                </div>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'landing' && !analysisResult && (
          <LandingPage
            onStartAnalysis={handleStartAnalysis}
            onOpenLegalExplorer={() => setIsLegalExplorerOpen(true)}
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

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '24px',
        borderTop: '1px solid var(--border-glass)',
        color: 'var(--text-subtle)',
        fontSize: '0.8rem'
      }}>
        LeagLease V2 (ContractLens) — AI-assisted legal document intelligence grounded in Maharashtra Rent Control Act 1999, Transfer of Property Act 1882, and Indian Contract Act 1872.
      </footer>
    </div>
  );
}
