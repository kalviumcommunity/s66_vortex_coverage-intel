import React, { useState, useEffect } from 'react';
import {
  FileCheck2,
  Database,
  ShieldCheck,
  Search,
  ArrowRight,
  TrendingUp,
  Clock,
  ExternalLink,
  RotateCcw,
  Inbox
} from 'lucide-react';
import CompletionGauge from './CompletionGauge';
import { fetchStats, fetchDocuments } from '../../services/api';

export default function DashboardView({
  onSelectQuery,
  onInspectEvidence,
  recentVerifications = [],
  onResetCorpus,
}) {
  const [heroInput, setHeroInput] = useState('');
  const [stats, setStats] = useState({
    total_documents: 0,
    total_chunks: 0,
    completeness_percentage: 0.0,
    vector_store: 'Pinecone',
    embedding_model: 'multilingual-e5-large',
    llm_model: 'grok-2-latest',
  });
  const [activeDocs, setActiveDocs] = useState([]);

  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
    fetchDocuments().then(setActiveDocs).catch(() => {});
  }, []);

  const sampleQueries = activeDocs.length > 0 ? [
    'Is water damage from a burst pipe covered?',
    'Does water backup coverage apply to sump pump failure?',
    'Is freezing of plumbing covered in an unoccupied home?',
    'What conditions apply to sudden and accidental discharge?',
  ] : [
    'Upload a policy in Document Library to begin testing coverage scenarios',
  ];

  const handleHeroSubmit = (e) => {
    e.preventDefault();
    if (heroInput.trim()) {
      onSelectQuery(heroInput.trim());
    }
  };

  return (
    <div className="dashboard-view">
      {/* 4 Metric Cards Grid - Live Dynamic Data */}
      <section className="metrics-grid">
        <div className="metric-card">
          <div className="metric-card-header">
            <span className="metric-label">Active Corpus Documents</span>
            <div className="metric-icon-wrap bg-blue-subtle">
              <FileCheck2 size={18} className="text-blue" />
            </div>
          </div>
          <div className="metric-value-row">
            <span className="metric-number">{stats.total_documents}</span>
            <span className="metric-trend text-emerald">
              <TrendingUp size={13} /> {stats.total_documents > 0 ? 'Live Corpus' : 'Awaiting Upload'}
            </span>
          </div>
          <p className="metric-description">
            {stats.total_documents > 0
              ? `${stats.total_documents} master policy file(s) loaded`
              : 'Zero sample documents loaded. Ready for clean ingestion.'}
          </p>
        </div>

        <div className="metric-card metric-gauge-card">
          <div className="metric-gauge-left">
            <span className="metric-label">Ingestion Completeness</span>
            <div className="metric-value-row">
              <span className="metric-number">{stats.completeness_percentage}%</span>
            </div>
            <p className="metric-description">
              {stats.total_chunks > 0 ? 'All extracted clauses vectorized' : 'Awaiting first document'}
            </p>
          </div>
          <CompletionGauge percentage={stats.completeness_percentage} />
        </div>

        <div className="metric-card">
          <div className="metric-card-header">
            <span className="metric-label">Indexed Vector Chunks</span>
            <div className="metric-icon-wrap bg-emerald-subtle">
              <Database size={18} className="text-emerald" />
            </div>
          </div>
          <div className="metric-value-row">
            <span className="metric-number">{stats.total_chunks}</span>
            <span className="metric-tag">{stats.vector_store.toUpperCase()}</span>
          </div>
          <p className="metric-description">Embedded via {stats.embedding_model}</p>
        </div>

        <div className="metric-card">
          <div className="metric-card-header">
            <span className="metric-label">Grounding Guard</span>
            <div className="metric-icon-wrap bg-purple-subtle">
              <ShieldCheck size={18} className="text-purple" />
            </div>
          </div>
          <div className="metric-value-row">
            <span className="metric-number" style={{ fontSize: '20px' }}>ACTIVE</span>
            <span className="metric-tag bg-emerald-badge">{stats.llm_model}</span>
          </div>
          <p className="metric-description">Sentence-level attribution &amp; anti-hallucination filter</p>
        </div>
      </section>

      {/* Hero Query Section */}
      <section className="hero-search-section">
        <div className="hero-search-card">
          <div className="hero-badge">
            <span>Coverage Inquiry</span>
          </div>
          <h2 className="hero-title">Verify coverage claims against verified policy evidence</h2>
          <form className="hero-form" onSubmit={handleHeroSubmit}>
            <div className="hero-input-wrap">
              <Search className="hero-search-icon" size={20} />
              <input
                type="text"
                className="hero-input"
                placeholder={
                  activeDocs.length > 0
                    ? "Ask any coverage question (e.g. 'Is water damage from frozen pipes covered?')..."
                    : "Upload a policy document in the Document Library first, then ask here..."
                }
                value={heroInput}
                onChange={(e) => setHeroInput(e.target.value)}
              />
            </div>
            <button type="submit" className="hero-submit-btn">
              <span>Ask Assistant</span>
              <ArrowRight size={16} />
            </button>
          </form>

          {/* Quick Query Pills */}
          {activeDocs.length > 0 && (
            <div className="pills-container">
              <span className="pills-label">Suggested Scenarios:</span>
              <div className="pills-list">
                {sampleQueries.map((query, index) => (
                  <button
                    key={index}
                    type="button"
                    className="query-pill"
                    onClick={() => onSelectQuery(query)}
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Recent Verifications / Inquiries Table */}
      <section className="recent-table-section">
        <div className="section-header-row">
          <div>
            <h3 className="section-title">Session Coverage Verifications</h3>
            <p className="section-subtitle">Real-time audit log of queries evaluated in this session</p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button className="table-action-btn" onClick={onResetCorpus}>
              <RotateCcw size={12} />
              <span>Reset Data</span>
            </button>
            <div className="filter-pill">
              <Clock size={13} />
              <span>{recentVerifications.length} Query Run(s)</span>
            </div>
          </div>
        </div>

        {recentVerifications.length === 0 ? (
          <div style={{ padding: '36px 20px', textAlign: 'center', color: '#64748b' }}>
            <Inbox size={28} style={{ margin: '0 auto 10px', color: '#94a3b8' }} />
            <strong style={{ display: 'block', color: '#334155', marginBottom: '4px' }}>
              No coverage verifications performed yet
            </strong>
            <p style={{ fontSize: '13px' }}>
              {activeDocs.length === 0
                ? "Start by uploading your policy documents in the Document Library tab."
                : "Type an inquiry above or run the evaluation bench to see grounded audit logs here."}
            </p>
          </div>
        ) : (
          <div className="table-responsive-wrapper">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Inquiry Scenario</th>
                  <th>Status</th>
                  <th>Citations</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentVerifications.map((row, idx) => (
                  <tr key={idx}>
                    <td className="query-col">
                      <span className="query-text">{row.query}</span>
                      <span className="query-meta">{row.time || 'Just now'}</span>
                    </td>
                    <td>
                      <span className={`status-badge status-${row.status}`}>
                        {row.statusLabel || row.status}
                      </span>
                    </td>
                    <td>
                      <span className="citation-pill">
                        {row.citationsCount ? `${row.citationsCount} citation(s)` : 'None'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="table-action-btn"
                        onClick={() => onInspectEvidence(row.documentId)}
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
    </div>
  );
}
