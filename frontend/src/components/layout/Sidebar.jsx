import React from 'react';
import {
  LayoutDashboard,
  MessageSquare,
  FileSearch,
  Files,
  Activity,
  ShieldCheck,
  Cpu
} from 'lucide-react';

export default function Sidebar({ activeSurface, setActiveSurface }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-icon">
          <span>CI</span>
        </div>
        <div className="logo-text">
          <h1>Coverage Intel</h1>
          <span className="logo-sub">Enterprise v2.4</span>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">Main Intelligence</div>
        <button
          className={`nav-item ${activeSurface === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveSurface('dashboard')}
        >
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </button>
        <button
          className={`nav-item ${activeSurface === 'assistant' ? 'active' : ''}`}
          onClick={() => setActiveSurface('assistant')}
        >
          <MessageSquare size={18} />
          <span>Coverage Assistant</span>
          <span className="nav-badge">CORE RAG</span>
        </button>
        <button
          className={`nav-item ${activeSurface === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveSurface('evidence')}
        >
          <FileSearch size={18} />
          <span>Policy Evidence</span>
        </button>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">Operations &amp; Telemetry</div>
        <button
          className={`nav-item ${activeSurface === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveSurface('documents')}
        >
          <Files size={18} />
          <span>Document Library</span>
        </button>
        <button
          className={`nav-item ${activeSurface === 'evaluation' ? 'active' : ''}`}
          onClick={() => setActiveSurface('evaluation')}
        >
          <Activity size={18} />
          <span>Evaluation Bench</span>
        </button>
      </div>

      <div className="sidebar-footer">
        <div className="system-pill">
          <Cpu size={14} className="text-emerald" />
          <span>xAI Grok + Pinecone</span>
        </div>
        <div className="system-pill mt-1">
          <ShieldCheck size={14} className="text-blue" />
          <span>Grounding Guard: Active</span>
        </div>
      </div>
    </aside>
  );
}

