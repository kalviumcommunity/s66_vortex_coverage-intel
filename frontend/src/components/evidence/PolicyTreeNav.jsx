import React from 'react';
import { Folder, FileText, CheckCircle2 } from 'lucide-react';

export default function PolicyTreeNav({ documents = [], activeDocId, onSelectDoc }) {
  return (
    <div className="policy-tree-nav">
      <div className="tree-header">
        <Folder size={15} />
        <span>Active Policy Documents</span>
      </div>

      <div className="tree-content">
        <div className="tree-items" style={{ marginLeft: 0, borderLeft: 'none' }}>
          {documents.map((doc) => (
            <button
              key={doc.id}
              className={`tree-leaf ${activeDocId === doc.id ? 'active' : ''}`}
              onClick={() => onSelectDoc(doc.id)}
            >
              {activeDocId === doc.id ? (
                <CheckCircle2 size={13} className="text-emerald" />
              ) : (
                <FileText size={13} />
              )}
              <span style={{ fontSize: '12px' }}>{doc.form || doc.id}</span>
              {doc.category === 'endorsement' && (
                <span className="tree-tag" style={{ background: '#0284c7' }}>RIDER</span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
