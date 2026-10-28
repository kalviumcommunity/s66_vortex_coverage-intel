import React, { useState, useEffect } from 'react';
import { Inbox, Plus, ArrowLeft } from 'lucide-react';
import PolicyTreeNav from './PolicyTreeNav';
import PolicyReader from './PolicyReader';
import AuditSidebar from './AuditSidebar';
import { fetchDocuments, fetchDocument } from '../../services/api';

export default function EvidenceView({ selectedChunkId, activeSnippet, onGoToUpload, onBackToAssistant }) {
  const [documents, setDocuments] = useState([]);
  const [activeDocId, setActiveDocId] = useState(selectedChunkId || '');
  const [currentDoc, setCurrentDoc] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchDocuments()
      .then((docs) => {
        setDocuments(docs);
        if (docs.length > 0) {
          const match = docs.find(
            (d) =>
              d.id === selectedChunkId ||
              d.filename === selectedChunkId ||
              (selectedChunkId && d.id && (selectedChunkId.startsWith(d.id) || d.id.startsWith(selectedChunkId)))
          );
          setActiveDocId(match ? match.id : docs[0].id);
        } else {
          setActiveDocId('');
          setCurrentDoc(null);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [selectedChunkId]);

  useEffect(() => {
    if (activeDocId) {
      fetchDocument(activeDocId)
        .then(setCurrentDoc)
        .catch(() => setCurrentDoc(null));
    }
  }, [activeDocId]);

  if (!loading && documents.length === 0) {
    return (
      <div className="evidence-view">
        <div className="evidence-topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="view-title">Policy Verification &amp; Evidence Reader</h2>
            <p className="view-subtitle">
              Inspect clause hierarchies, paper document layout, and grounding provenance
            </p>
          </div>
          {onBackToAssistant && (
            <button
              className="back-btn"
              onClick={onBackToAssistant}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                background: '#0284c7',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '13.5px',
                fontWeight: '600',
                cursor: 'pointer',
              }}
            >
              <ArrowLeft size={16} />
              <span>Back to Assessment</span>
            </button>
          )}
        </div>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '60px 20px', textAlign: 'center', color: '#64748b' }}>
          <Inbox size={36} style={{ margin: '0 auto 12px', color: '#94a3b8' }} />
          <h3 style={{ color: '#1e293b', fontSize: '16px', marginBottom: '6px' }}>No Policy Documents In Corpus</h3>
          <p style={{ fontSize: '13.5px', maxWidth: '420px', margin: '0 auto 20px' }}>
            Upload a policy document (.pdf, .docx, or .txt) in the Document Library to view its clause structure and verified grounding citations here.
          </p>
          {onGoToUpload && (
            <button className="upload-trigger-btn" onClick={onGoToUpload} style={{ margin: '0 auto' }}>
              <Plus size={16} />
              <span>Go to Document Library</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="evidence-view">
      <div className="evidence-topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="view-title">Policy Verification &amp; Evidence Reader</h2>
          <p className="view-subtitle">
            Direct clause inspection and sentence-level evidence attribution across active policies
          </p>
        </div>
        {onBackToAssistant && (
          <button
            className="back-btn"
            onClick={onBackToAssistant}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              background: '#0284c7',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '13.5px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              transition: 'background 0.15s ease'
            }}
          >
            <ArrowLeft size={16} />
            <span>Back to Assessment</span>
          </button>
        )}
      </div>

      <div className="evidence-split-surface">
        {/* Left: Outline & Tree (25%) */}
        <PolicyTreeNav
          documents={documents}
          activeDocId={activeDocId}
          onSelectDoc={setActiveDocId}
        />

        {/* Center: Paper Reader (50%) */}
        <PolicyReader document={currentDoc} activeSnippet={activeSnippet} />

        {/* Right: Provenance & Audit Sidebar (25%) */}
        <AuditSidebar document={currentDoc} activeSnippet={activeSnippet} />
      </div>
    </div>
  );
}
