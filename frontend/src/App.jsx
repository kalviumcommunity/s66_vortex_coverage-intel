import React, { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import TopHeader from './components/layout/TopHeader';
import DashboardView from './components/dashboard/DashboardView';
import AssistantView from './components/assistant/AssistantView';
import EvidenceView from './components/evidence/EvidenceView';
import DocumentsView from './components/documents/DocumentsView';
import EvaluationView from './components/evaluation/EvaluationView';
import { askCoverage, resetCorpusData, fetchDocuments } from './services/api';
import './styles.css';

export default function App() {
  const [activeSurface, setActiveSurface] = useState('dashboard');
  const [question, setQuestion] = useState('');
  const [scenario, setScenario] = useState({
    policy_type: '',
    date_of_loss: '',
    jurisdiction: '',
    claim_type: '',
  });
  const [loading, setLoading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [error, setError] = useState(null);
  const [selectedEvidenceChunk, setSelectedEvidenceChunk] = useState('');
  const [activeSnippet, setActiveSnippet] = useState('');
  const [recentVerifications, setRecentVerifications] = useState([]);
  const [docCount, setDocCount] = useState(0);

  const refreshDocCount = () => {
    fetchDocuments()
      .then((docs) => setDocCount(docs.length))
      .catch(() => setDocCount(0));
  };

  useEffect(() => {
    refreshDocCount();
  }, [activeSurface]);

  const handleAsk = async (qText) => {
    const query = qText || question;
    if (!query.trim()) return;

    setQuestion(query);
    setLoading(true);
    setError(null);
    setActiveSurface('assistant');

    try {
      const data = await askCoverage(query, scenario);
      setAnswer(data);

      // Track real verification in session history
      const topCitation = data.citations && data.citations[0];
      setRecentVerifications((prev) => [
        {
          id: `Q-${prev.length + 1}`,
          query: query,
          status: data.status,
          statusLabel:
            data.status === 'grounded'
              ? 'Supported by Evidence'
              : data.status === 'weak_evidence'
              ? 'Conditions Required'
              : 'Insufficient Evidence',
          citationsCount: (data.citations || []).length,
          documentId: topCitation?.document_id || '',
          time: 'Just now',
        },
        ...prev,
      ]);
    } catch (err) {
      setError(err.message || 'Error communicating with Coverage Intel backend');
    } finally {
      setLoading(false);
    }
  };

  const handleInspectEvidence = (chunkOrDocId, snippet = '') => {
    if (chunkOrDocId) setSelectedEvidenceChunk(chunkOrDocId);
    if (snippet) setActiveSnippet(snippet);
    setActiveSurface('evidence');
  };

  const handleNewQuery = () => {
    setQuestion('');
    setAnswer(null);
    setError(null);
    setActiveSurface('assistant');
  };

  const handleResetCorpus = async () => {
    setResetting(true);
    try {
      await resetCorpusData();
      setRecentVerifications([]);
      setAnswer(null);
      setQuestion('');
      setSelectedEvidenceChunk('');
      setActiveSnippet('');
      setDocCount(0);
      setActiveSurface('documents');
    } catch (err) {
      console.error('Error resetting data:', err);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar activeSurface={activeSurface} setActiveSurface={setActiveSurface} />

      {/* Main Surface Canvas */}
      <main className="main-content">
        <TopHeader
          activeSurface={activeSurface}
          onNewQuery={handleNewQuery}
          onResetCorpus={handleResetCorpus}
          docCount={docCount}
          resetting={resetting}
        />

        <div className="surface-canvas">
          {activeSurface === 'dashboard' && (
            <DashboardView
              onSelectQuery={handleAsk}
              onInspectEvidence={handleInspectEvidence}
              recentVerifications={recentVerifications}
              onResetCorpus={handleResetCorpus}
            />
          )}

          {activeSurface === 'assistant' && (
            <AssistantView
              question={question}
              setQuestion={setQuestion}
              scenario={scenario}
              setScenario={setScenario}
              answer={answer}
              loading={loading}
              error={error}
              onAsk={handleAsk}
              onInspectEvidence={handleInspectEvidence}
            />
          )}

          {activeSurface === 'evidence' && (
            <EvidenceView
              selectedChunkId={selectedEvidenceChunk}
              activeSnippet={activeSnippet}
              onGoToUpload={() => setActiveSurface('documents')}
              onBackToAssistant={() => setActiveSurface('assistant')}
            />
          )}

          {activeSurface === 'documents' && (
            <DocumentsView
              onInspectEvidence={handleInspectEvidence}
              onResetCorpus={handleResetCorpus}
            />
          )}

          {activeSurface === 'evaluation' && <EvaluationView />}
        </div>
      </main>
    </div>
  );
}
