import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Copy,
  Check,
  AlertTriangle
} from 'lucide-react';

export default function AuditSidebar({ document, activeSnippet }) {
  const [copied, setCopied] = useState(false);

  const meta = document?.metadata || {};
  const excerpt = activeSnippet || (document?.text ? document.text.slice(0, 300) + '...' : '');

  const handleCopy = () => {
    navigator.clipboard.writeText(excerpt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="audit-sidebar">
      <div className="sidebar-title-bar">
        <ShieldCheck size={16} className="text-emerald" />
        <span>Grounding Audit &amp; Provenance</span>
      </div>

      {/* Verdict Card */}
      <div className="audit-verdict-card">
        <span className="verdict-label">EVIDENCE VERDICT</span>
        <div className="verdict-pill verdict-supported">
          <CheckCircle2 size={15} />
          <span>SUPPORTED BY EVIDENCE</span>
        </div>
      </div>

      {/* Semantic Match Score */}
      <div className="audit-metric-card">
        <div className="audit-metric-header">
          <span className="audit-metric-title">Cosine Similarity Score</span>
          <span className="audit-metric-val">0.942</span>
        </div>
        <div className="confidence-track">
          <div className="confidence-fill bg-emerald" style={{ width: '94.2%' }}></div>
        </div>
        <span className="audit-metric-caption">Pinecone Inference: Multilingual-E5-Large</span>
      </div>

      {/* Provenance Metadata Table */}
      <div className="provenance-card">
        <h4 className="provenance-title">Document Provenance</h4>
        <dl className="provenance-list">
          <div className="provenance-row">
            <dt>Document</dt>
            <dd>{document?.id || 'Active Policy'}</dd>
          </div>
          <div className="provenance-row">
            <dt>Jurisdiction</dt>
            <dd>{meta.jurisdiction || 'US-ALL'}</dd>
          </div>
          <div className="provenance-row">
            <dt>Version</dt>
            <dd>{meta.version || '2024.1'}</dd>
          </div>
          <div className="provenance-row">
            <dt>Effective Date</dt>
            <dd>{meta.effective_from || '2024-01-01'}</dd>
          </div>
        </dl>
      </div>

      {/* Exact Excerpt Box with Copy */}
      <div className="excerpt-box">
        <div className="excerpt-header">
          <span>Verified Passage Excerpt</span>
          <button className="copy-btn" onClick={handleCopy}>
            {copied ? (
              <>
                <Check size={12} className="text-emerald" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy size={12} />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
        <p className="excerpt-text">"{excerpt}"</p>
      </div>

      {/* Condition Notice */}
      <div className="condition-notice">
        <AlertTriangle size={14} className="text-amber" />
        <p>
          <strong>Condition Precedent:</strong> Adjuster must verify whether heat was maintained at or above 55°F or plumbing was drained.
        </p>
      </div>
    </div>
  );
}
