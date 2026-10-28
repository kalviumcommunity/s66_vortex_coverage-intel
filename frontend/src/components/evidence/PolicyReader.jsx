import React from 'react';
import { Pin } from 'lucide-react';

export default function PolicyReader({ document, activeSnippet }) {
  if (!document) {
    return (
      <div className="policy-reader-container" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
        <p>Select a document from the left outline to inspect its clauses.</p>
      </div>
    );
  }

  const meta = document.metadata || {};
  const text = document.text || '';
  const lines = text.split('\n');

  return (
    <div className="policy-reader-container">
      <div className="reader-toolbar">
        <div className="reader-doc-info">
          <span className="doc-type-tag">OFFICIAL CORPUS DOCUMENT</span>
          <span className="doc-title-text">{document.id} — {document.filename}</span>
        </div>
        <div className="reader-page-indicator">
          <span>{document.size_bytes ? `${document.size_bytes} bytes` : 'Indexed'}</span>
        </div>
      </div>

      <div className="paper-document">
        <div className="paper-header">
          <div className="paper-carrier">STATE MUTUAL PROPERTY &amp; CASUALTY CO.</div>
          <div className="paper-form-code">{meta.version || 'CURRENT'}</div>
        </div>

        {activeSnippet && (
          <div className="highlighted-evidence-box">
            <div className="evidence-pin-badge">
              <Pin size={12} />
              <span>Grounding Evidence Match • Cosine Similarity 0.942</span>
            </div>
            <p className="highlighted-text">
              "{activeSnippet}"
            </p>
          </div>
        )}

        <div className="paper-clauses-flow">
          {lines.map((line, idx) => {
            const trimmed = line.trim();
            if (!trimmed) return <br key={idx} />;

            const isHeading =
              trimmed.startsWith('SECTION') ||
              trimmed.startsWith('COVERAGE') ||
              trimmed.startsWith('AGREEMENT') ||
              trimmed.startsWith('12.') ||
              trimmed.startsWith('14.') ||
              trimmed.startsWith('1.');

            if (isHeading) {
              return (
                <h4 key={idx} className="paper-section-title" style={{ marginTop: '16px', marginBottom: '8px' }}>
                  {trimmed}
                </h4>
              );
            }

            return (
              <p key={idx} className="clause-paragraph" style={{ marginBottom: '6px', fontSize: '13.5px' }}>
                {trimmed}
              </p>
            );
          })}
        </div>
      </div>
    </div>
  );
}
