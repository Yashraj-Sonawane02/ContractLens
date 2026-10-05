import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Send, Scale, User, Bot } from 'lucide-react';
import api from '../services/api';

export default function ContractChat({ contractText, analyzedClauses, language }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Statutory Legal Assistant ready. Ask specific questions regarding notice obligations, deposit refunds, rent escalation caps, or statutory compliance under Indian Law.'
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
    <div className="minimal-card" style={{ padding: '24px', height: '600px', display: 'flex', flexDirection: 'column' }}>
      
      {/* Chat Header */}
      <div style={{ paddingBottom: '14px', borderBottom: '1px solid var(--border-main)', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '34px', height: '34px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Scale style={{ color: 'var(--accent-navy)', width: '18px', height: '18px' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', margin: 0, fontWeight: 700, color: 'var(--text-main)' }}>Statutory Legal Assistant</h3>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>Grounded in Indian Statutory Law & Contract Terms</span>
          </div>
        </div>

        {/* Voice Support Indicator */}
        <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Mic style={{ width: '13px', height: '13px', color: 'var(--accent-navy)' }} /> Voice Input Supported
        </div>
      </div>

      {/* Messages Stream */}
      <div style={{ flex: 1, overflowY: 'auto', paddingRight: '6px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '10px',
            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%'
          }}>
            {msg.sender === 'bot' && (
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Bot style={{ color: 'var(--accent-navy)', width: '15px', height: '15px' }} />
              </div>
            )}

            <div style={{
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              background: msg.sender === 'user' ? 'var(--accent-navy)' : 'var(--bg-subtle)',
              border: `1px solid ${msg.sender === 'user' ? 'var(--accent-navy)' : 'var(--border-main)'}`,
              color: msg.sender === 'user' ? 'var(--text-inverse)' : 'var(--text-main)',
              fontWeight: msg.sender === 'user' ? 600 : 400,
              fontSize: '0.85rem',
              lineHeight: 1.5,
              whiteSpace: 'pre-line'
            }}>
              {msg.text}
            </div>

            {msg.sender === 'user' && (
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-navy)', color: 'var(--text-inverse)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User style={{ width: '14px', height: '14px' }} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: '10px', alignSelf: 'flex-start' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--bg-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot style={{ color: 'var(--accent-navy)', width: '15px', height: '15px' }} />
            </div>
            <div style={{ padding: '8px 12px', borderRadius: 'var(--radius-md)', background: 'var(--bg-subtle)', border: '1px solid var(--border-main)', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              Evaluating question against pre-indexed statutory database...
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSendMessage} style={{ marginTop: '14px', display: 'flex', gap: '8px' }}>
        <button
          type="button"
          onClick={toggleVoiceInput}
          className="btn-minimal"
          style={{
            padding: '8px 12px',
            background: isListening ? 'var(--risk-critical-bg)' : 'var(--bg-surface)',
            color: isListening ? 'var(--risk-critical-text)' : 'var(--text-main)',
            borderColor: isListening ? 'var(--risk-critical-border)' : 'var(--border-main)'
          }}
          title={isListening ? "Listening... click to stop" : "Speak question"}
        >
          {isListening ? <MicOff style={{ width: '15px', height: '15px' }} /> : <Mic style={{ width: '15px', height: '15px' }} />}
        </button>

        <input
          type="text"
          placeholder={isListening ? "Listening..." : "Ask a statutory question (e.g., Is the late payment penalty enforceable?)..."}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          style={{
            flex: 1,
            padding: '8px 12px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-main)',
            color: 'var(--text-main)',
            fontSize: '0.86rem',
            outline: 'none'
          }}
        />

        <button type="submit" className="btn-minimal btn-minimal-primary" disabled={loading} style={{ padding: '8px 16px' }}>
          <Send style={{ width: '14px', height: '14px' }} />
        </button>
      </form>

    </div>
  );
}
