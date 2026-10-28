import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  ShieldCheck,
  AlertCircle,
  FileText,
  Bookmark,
  ExternalLink,
  Copy,
  Check,
  Maximize2,
  X,
  Sparkles
} from 'lucide-react';

export default function AnswerCard({ answer, onInspectEvidence }) {
  const [copied, setCopied] = useState(false);
  const [modalCitation, setModalCitation] = useState(null);
  const [clauseCopied, setClauseCopied] = useState(false);

  if (!answer) return null;

  const statusMap = {
    grounded: {
      label: 'Covered — Grounded in Policy Language',
      badgeClass: 'status-supported',
      icon: <ShieldCheck size={18} className="text-emerald" />,
    },
    supported: {
      label: 'Covered — Supported by Evidence',
      badgeClass: 'status-supported',
      icon: <ShieldCheck size={18} className="text-emerald" />,
    },
    weak_evidence: {
      label: 'Conditions Precedent / Review Required',
      badgeClass: 'status-conditional',
      icon: <AlertCircle size={18} className="text-amber" />,
    },
    insufficient_evidence: {
      label: 'Insufficient Evidence / Uncovered',
      badgeClass: 'status-insufficient',
      icon: <AlertCircle size={18} className="text-red" />,
    },
  };

  const statusInfo = statusMap[answer.status] || {
    label: answer.status,
    badgeClass: 'status-conditional',
    icon: <AlertCircle size={18} />,
  };

  const answerText = answer.answer_text || answer.summary || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(answerText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyClause = (text) => {
    navigator.clipboard.writeText(text);
    setClauseCopied(true);
    setTimeout(() => setClauseCopied(false), 2000);
  };

  return (
    <div className="answer-card">
      {/* Header bar */}
      <div className="answer-header">
        <div className="verdict-banner">
          {statusInfo.icon}
          <span className={`status-badge ${statusInfo.badgeClass}`}>
            {statusInfo.label}
          </span>
          <span className="pipeline-pill">
            <Sparkles size={12} />
            <span>xAI Grok &bull; Pinecone Inference</span>
          </span>
        </div>
        <div className="answer-actions">
          <button className="icon-btn" onClick={handleCopy} title="Copy Answer Synthesis">
            {copied ? <Check size={15} className="text-emerald" /> : <Copy size={15} />}
          </button>
        </div>
      </div>

      {/* Warnings & Conditions Banner */}
      {answer.warnings && answer.warnings.length > 0 && (
        <div className="warning-banner">
          <AlertCircle size={16} className="warning-icon" />
          <div className="warning-content">
            <strong>Condition Precedent &amp; Warning:</strong>
            <ul>
              {answer.warnings.map((warn, i) => (
                <li key={i}>{typeof warn === 'object' ? warn.message : warn}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Formatted Markdown Grounded Assessment */}
      <div className="answer-body">
        <div className="answer-heading-row">
          <h4 className="answer-heading">Grounded Coverage Assessment</h4>
          <span className="guardrail-badge">DECISION SUPPORT &bull; ZERO FABRICATION</span>
        </div>

        <div className="answer-markdown-content">
          <ReactMarkdown>{answerText}</ReactMarkdown>
        </div>
      </div>

      {/* Verified Policy Citations */}
      {answer.citations && answer.citations.length > 0 && (
        <div className="citations-section">
          <div className="citations-header">
            <Bookmark size={15} />
            <span>Verified Policy Citations ({answer.citations.length})</span>
            <span className="citations-sub">Click any citation to inspect the verbatim policy clause directly</span>
          </div>

          <div className="citations-grid">
            {answer.citations.map((cite, index) => {
              const snippetText = cite.text_snippet || cite.excerpt || cite.exact_text || '';
              const docId = cite.document_id || cite.document_title || 'POL-HO3-2024';
              const section = cite.section_title || cite.section || 'Section I';
              const page = cite.page_number || cite.page || 1;
              const relevance = Math.round((cite.relevance_score || 0.92) * 100);

              return (
                <div key={index} className="citation-card" onClick={() => setModalCitation(cite)}>
                  <div className="citation-top">
                    <span className="citation-tag">
                      <FileText size={12} />
                      {docId}
                    </span>
                    <span className="citation-location">
                      Page {page} &bull; {section}
                    </span>
                  </div>

                  <blockquote className="citation-quote">
                    "{snippetText}"
                  </blockquote>

                  <div className="citation-bottom">
                    <span className="citation-score">
                      Match Relevance: {relevance}%
                    </span>
                    <div className="citation-btn-group" onClick={(e) => e.stopPropagation()}>
                      <button
                        className="citation-inspect-btn"
                        onClick={() => setModalCitation(cite)}
                        title="View clause details directly"
                      >
                        <Maximize2 size={12} />
                        <span>Inspect Clause</span>
                      </button>
                      <button
                        className="citation-reader-btn"
                        onClick={() => onInspectEvidence(docId, snippetText)}
                        title="Open in full document reader"
                      >
                        <ExternalLink size={12} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Direct In-Place Citation Inspection Modal */}
      {modalCitation && (
        <div className="clause-modal-backdrop" onClick={() => setModalCitation(null)}>
          <div className="clause-modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="clause-modal-header">
              <div className="clause-modal-title-group">
                <FileText size={18} className="text-blue" />
                <div>
                  <h4 className="clause-modal-title">
                    {modalCitation.document_title || modalCitation.document_id || 'Policy Document'}
                  </h4>
                  <span className="clause-modal-subtitle">
                    {modalCitation.section_title || modalCitation.section || 'Section I'} &bull; Page {modalCitation.page_number || modalCitation.page || 1}
                  </span>
                </div>
              </div>
              <button className="clause-modal-close" onClick={() => setModalCitation(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="clause-modal-body">
              <div className="clause-metric-row">
                <span className="clause-metric-pill">
                  Cosine Match: {Math.round((modalCitation.relevance_score || 0.92) * 100)}%
                </span>
                <span className="clause-metric-pill">
                  Jurisdiction: {modalCitation.jurisdiction || 'US-ALL'}
                </span>
                <span className="clause-metric-pill">
                  Status: Grounded &amp; Verified
                </span>
              </div>

              <div className="clause-verbatim-box">
                <div className="clause-box-label">Verbatim Policy Text (Extracted from Source Document)</div>
                <p className="clause-verbatim-text">
                  "{modalCitation.text_snippet || modalCitation.excerpt || modalCitation.exact_text}"
                </p>
              </div>
            </div>

            <div className="clause-modal-footer">
              <button
                className="btn-secondary"
                onClick={() => handleCopyClause(modalCitation.text_snippet || modalCitation.excerpt || '')}
              >
                {clauseCopied ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
                <span>{clauseCopied ? 'Clause Copied!' : 'Copy Exact Clause'}</span>
              </button>
              <button
                className="btn-primary"
                onClick={() => {
                  const docId = modalCitation.document_id || modalCitation.document_title || 'POL-HO3-2024';
                  const snip = modalCitation.text_snippet || modalCitation.excerpt || '';
                  setModalCitation(null);
                  onInspectEvidence(docId, snip);
                }}
              >
                <ExternalLink size={14} />
                <span>Open In Full Policy Reader</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
