import React, { useState, useEffect } from 'react';
import {
  FileUp,
  Search,
  CheckCircle2,
  ExternalLink,
  Plus,
  Loader2,
  RefreshCw,
  RotateCcw,
  Inbox
} from 'lucide-react';
import IngestionStepper from './IngestionStepper';
import UploadModal from './UploadModal';
import { fetchDocuments } from '../../services/api';

export default function DocumentsView({ onInspectEvidence, onResetCorpus }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDocs = () => {
    setLoading(true);
    fetchDocuments()
      .then((data) => setDocuments(data))
      .catch(() => setDocuments([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const filteredDocs = documents.filter(
    (d) =>
      (d.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (d.form || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (d.filename || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="documents-view">
      <div className="documents-header">
        <div>
          <h2 className="view-title">Document Library &amp; Ingestion Telemetry</h2>
          <p className="view-subtitle">
            Upload and manage policy documents; view chunking and Pinecone vectorization status
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="btn-secondary"
            onClick={onResetCorpus}
            title="Clear all uploaded policies to retest from scratch"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RotateCcw size={14} />
            <span>Clear Corpus</span>
          </button>
          <button
            className="btn-secondary"
            onClick={loadDocs}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
          <button className="upload-trigger-btn" onClick={() => setIsModalOpen(true)}>
            <Plus size={16} />
            <span>Ingest New Policy</span>
          </button>
        </div>
      </div>

      {/* 5-step Pipeline Telemetry Bar */}
      <IngestionStepper />

      {/* Master Inventory Section */}
      <section className="inventory-section">
        <div className="inventory-toolbar">
          <div className="inventory-search">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Filter active documents by title or form code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="inventory-count">
            <span>Showing {filteredDocs.length} of {documents.length} Active Corpus Documents</span>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '36px', textAlign: 'center', color: '#64748b' }}>
            <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 8px' }} />
            <p>Loading active policy corpus...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div style={{ padding: '48px 24px', textAlign: 'center', color: '#64748b' }}>
            <Inbox size={32} style={{ margin: '0 auto 12px', color: '#94a3b8' }} />
            <strong style={{ display: 'block', color: '#1e293b', fontSize: '15px', marginBottom: '6px' }}>
              No policy documents uploaded yet
            </strong>
            <p style={{ fontSize: '13px', maxWidth: '440px', margin: '0 auto 16px' }}>
              The corpus is completely clean. Click the button below to upload your first policy file (PDF, DOCX, or TXT).
            </p>
            <button className="upload-trigger-btn" onClick={() => setIsModalOpen(true)} style={{ margin: '0 auto' }}>
              <Plus size={16} />
              <span>Upload First Policy</span>
            </button>
          </div>
        ) : (
          <div className="table-responsive-wrapper">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Document Title &amp; File</th>
                  <th>Identifier</th>
                  <th>Jurisdiction</th>
                  <th>Category</th>
                  <th>File Size</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <strong>{doc.title}</strong>
                      <div className="text-muted text-xs">{doc.filename}</div>
                    </td>
                    <td>
                      <span className="code-pill">{doc.form || doc.id}</span>
                    </td>
                    <td>
                      <span className="state-badge">{doc.jurisdiction}</span>
                    </td>
                    <td>
                      <span className="doc-category-badge">{doc.category.toUpperCase()}</span>
                    </td>
                    <td>
                      <span className="text-muted text-xs">{(doc.size_bytes / 1024).toFixed(1)} KB</span>
                    </td>
                    <td>
                      <span className="status-badge status-supported">
                        <CheckCircle2 size={12} />
                        <span>{doc.status_label || 'Indexed & Active'}</span>
                      </span>
                    </td>
                    <td>
                      <button
                        className="table-action-btn"
                        onClick={() => onInspectEvidence(doc.id)}
                      >
                        <ExternalLink size={13} />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onUploadSuccess={loadDocs}
      />
    </div>
  );
}
