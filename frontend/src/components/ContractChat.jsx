import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Send, Scale, User, Bot, BookOpen } from 'lucide-react';
import api from '../services/api';

export default function ContractChat({ contractText, analyzedClauses, language }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Statutory Legal Assistant ready. You may ask specific questions regarding notice obligations, deposit refunds, rent escalation caps, or statutory compliance under Indian Law.'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-IN';

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
      };

      rec.onerror = () => {
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      setRecognition(rec);
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognition) {
      alert("Voice input is not supported in this browser. Please use text input.");
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || loading) return;

    const userMsg = inputText.trim();
    const updatedMessages = [...messages, { sender: 'user', text: userMsg }];
    setMessages(updatedMessages);
    setInputText('');
    setLoading(true);

    try {
      const response = await api.post('/chat/ask', {
        question: userMsg,
        analyzed_clauses: analyzedClauses || [],
        conversation_history: messages,
        language: language || 'English'
      });

      const botAnswer = response.data.answer;
      setMessages(prev => [...prev, { sender: 'bot', text: botAnswer }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: "An error occurred while evaluating your query against the statutory database. Please rephrase or try again."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '24px', height: '600px', display: 'flex', flexDirection: 'column' }}>
      
      {/* Chat Header */}
      <div style={{ paddingBottom: '16px', borderBottom: '1px solid var(--border-slate)', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-sm)', background: 'rgba(197, 168, 128, 0.1)', border: '1px solid var(--border-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Scale style={{ color: 'var(--accent-gold-bright)', width: '18px', height: '18px' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', margin: 0, fontFamily: 'var(--font-heading)' }}>Statutory Legal Assistant</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Grounded in Indian Legislation & Document Terms</span>
          </div>
        </div>

        {/* Voice Support Indicator */}
        <div style={{ fontSize: '0.75rem', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'var(--font-mono)' }}>
          <Mic style={{ width: '13px', height: '13px' }} /> Voice Enabled
        </div>
      </div>

      {/* Messages Stream */}
      <div style={{ flex: 1, overflowY: 'auto', paddingRight: '8px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '10px',
            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%'
          }}>
            {msg.sender === 'bot' && (
              <div style={{ width: '30px', height: '30px', borderRadius: '50%', background: 'rgba(197, 168, 128, 0.15)', border: '1px solid var(--border-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Bot style={{ color: 'var(--accent-gold)', width: '16px', height: '16px' }} />
              </div>
            )}

            <div style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: msg.sender === 'user' ? 'linear-gradient(135deg, #c5a880 0%, #9e825a 100%)' : 'rgba(255, 255, 255, 0.03)',
              border: `1px solid ${msg.sender === 'user' ? 'var(--accent-gold)' : 'var(--border-slate)'}`,
              color: msg.sender === 'user' ? '#0b132b' : '#f1f5f9',
              fontWeight: msg.sender === 'user' ? 600 : 400,
              fontSize: '0.86rem',
              lineHeight: 1.6,
              whiteSpace: 'pre-line'
            }}>
              {msg.text}
            </div>

            {msg.sender === 'user' && (
              <div style={{ width: '30px', height: '30px', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User style={{ color: '#ffffff', width: '16px', height: '16px' }} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: '10px', alignSelf: 'flex-start' }}>
            <div style={{ width: '30px', height: '30px', borderRadius: '50%', background: 'rgba(197, 168, 128, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot style={{ color: 'var(--accent-gold)', width: '16px', height: '16px' }} />
            </div>
            <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-md)', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-slate)', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              Evaluating query against pre-indexed statutory database...
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSendMessage} style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
        <button
          type="button"
          onClick={toggleVoiceInput}
          style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            background: isListening ? 'var(--risk-critical-bg)' : 'rgba(255, 255, 255, 0.03)',
            border: `1px solid ${isListening ? 'var(--risk-critical-border)' : 'var(--border-slate)'}`,
            color: isListening ? 'var(--risk-critical-text)' : 'var(--text-muted)',
            cursor: 'pointer',
            transition: 'var(--transition)'
          }}
          title={isListening ? "Listening... click to stop" : "Speak question"}
        >
          {isListening ? <MicOff style={{ width: '16px', height: '16px' }} /> : <Mic style={{ width: '16px', height: '16px' }} />}
        </button>

        <input
          type="text"
          placeholder={isListening ? "Listening..." : "Ask a legal question (e.g., Is the late payment fee legally valid?)..."}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid var(--border-slate)',
            color: '#ffffff',
            fontSize: '0.86rem'
          }}
        />

        <button type="submit" className="btn-primary" disabled={loading} style={{ padding: '10px 18px' }}>
          <Send style={{ width: '14px', height: '14px' }} />
        </button>
      </form>

    </div>
  );
}
