import React from 'react';
import { Radio, Sparkles, RotateCcw } from 'lucide-react';

export default function TopHeader({
  activeSurface,
  onNewQuery,
  onResetCorpus,
  docCount = 0,
  resetting = false,
}) {
  const surfaceTitles = {
    dashboard: 'Executive Dashboard',
    assistant: 'Coverage Assistant & Grounded Q&A',
    evidence: 'Policy Verification & Evidence Reader',
    documents: 'Document Library & Ingestion Telemetry',
    evaluation: 'RAG Evaluation & Benchmark Bench',
  };

  return (
    <header className="top-header">
      <div className="header-left">
        <div className="breadcrumbs">
          <span>Workspace</span>
          <span className="separator">/</span>
          <strong>{surfaceTitles[activeSurface] || activeSurface.toUpperCase()}</strong>
        </div>
        <div className="corpus-tag">
          <span className={`pulse-dot ${docCount === 0 ? 'pulse-amber' : ''}`}></span>
          <span>{docCount === 0 ? 'Corpus: Empty (Ready for Upload)' : `Active Corpus: ${docCount} Document(s)`}</span>
        </div>
      </div>

      <div className="header-right">
        <button
          className="reset-retest-btn"
          onClick={onResetCorpus}
          disabled={resetting}
          title="Clear all corpus documents and vector store to test ingestion from scratch"
        >
          <RotateCcw size={13} className={resetting ? 'animate-spin' : ''} />
          <span>{resetting ? 'Resetting...' : 'Clear Data & Retest'}</span>
        </button>

        <div className="api-status-badge">
          <Radio size={13} className="pulse-icon text-emerald" />
          <span>API Connected: 8000</span>
        </div>

        <button className="header-action-btn" onClick={onNewQuery}>
          <Sparkles size={14} />
          <span>New Query</span>
        </button>
      </div>
    </header>
  );
}
