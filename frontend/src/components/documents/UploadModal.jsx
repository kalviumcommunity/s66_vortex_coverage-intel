import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../../services/api';

export default function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [accessKey, setAccessKey] = useState('coverage-intel-admin-key');
  const [policyForm, setPolicyForm] = useState('HO-3');
  const [jurisdiction, setJurisdiction] = useState('CA');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      await uploadDocument(file, accessKey, {
        documentId: file.name.replace(/\.[^/.]+$/, ''),
        category: 'policy',
        jurisdiction: jurisdiction,
        version: '2024-v1',
      });
      setSuccess(true);
      setTimeout(() => {
        onUploadSuccess?.();
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-dialog">
        <div className="modal-header">
          <h3 className="modal-title">Ingest New Policy Document</h3>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {/* File Dropzone */}
          <div
            className={`dropzone ${file ? 'has-file' : ''}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => document.getElementById('modal-file-input').click()}
          >
            <input
              id="modal-file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && setFile(e.target.files[0])}
            />
            <UploadCloud size={32} className="dropzone-icon" />
            {file ? (
              <div className="file-info">
                <FileText size={18} className="text-blue" />
                <strong>{file.name}</strong>
                <span>({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            ) : (
              <div>
                <strong>Click to browse or drag &amp; drop policy file</strong>
                <p>Supports ISO standard PDF, Word (.docx), or UTF-8 Text (.txt)</p>
              </div>
            )}
          </div>

          {/* Form options */}
          <div className="modal-grid">
            <div className="modal-field">
              <label>Policy Form Code</label>
              <select value={policyForm} onChange={(e) => setPolicyForm(e.target.value)}>
                <option value="HO-3">HO-3 (Homeowners Special Form)</option>
                <option value="HO-5">HO-5 (Comprehensive)</option>
                <option value="DP-3">DP-3 (Dwelling Property)</option>
                <option value="HO-04-95">HO 04 95 (Water Backup Endorsement)</option>
              </select>
            </div>

            <div className="modal-field">
              <label>Target Jurisdiction</label>
              <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}>
                <option value="CA">California (CA)</option>
                <option value="FL">Florida (FL)</option>
                <option value="TX">Texas (TX)</option>
                <option value="NY">New York (NY)</option>
                <option value="ALL">National Standard</option>
              </select>
            </div>
          </div>

          <div className="modal-field mt-2">
            <label>Upload Secret Access Key</label>
            <input
              type="password"
              value={accessKey}
              onChange={(e) => setAccessKey(e.target.value)}
              placeholder="Enter authorization key..."
            />
          </div>

          {error && (
            <div className="error-alert mt-2">
              <AlertCircle size={15} />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="success-alert mt-2">
              <CheckCircle2 size={15} />
              <span>Document successfully uploaded and queued for vectorization!</span>
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={!file || loading || success}>
              {loading ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  <span>Processing Document...</span>
                </>
              ) : (
                <span>Begin Ingestion Pipeline</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

