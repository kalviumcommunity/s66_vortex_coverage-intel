import React, { useState } from 'react';
import { Search, Sparkles, Loader2, RefreshCw, SlidersHorizontal } from 'lucide-react';
import ScenarioDrawer from './ScenarioDrawer';
import AnswerCard from './AnswerCard';

export default function AssistantView({
  question,
  setQuestion,
  scenario,
  setScenario,
  answer,
  loading,
  error,
  onAsk,
  onInspectEvidence,
}) {
  const [showScenarioDrawer, setShowScenarioDrawer] = useState(true);

  const handleScenarioChange = (field, value) => {
    setScenario((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() && !loading) {
      onAsk(question);
    }
  };

  return (
    <div className="assistant-view">
      <div className="assistant-header-bar">
        <div>
          <h2 className="view-title">Policy Coverage Assistant</h2>
          <p className="view-subtitle">
            Grounded anaphora-aware Q&amp;A pipeline powered by xAI Grok and Pinecone embeddings
          </p>
        </div>
        <button
          className="drawer-toggle-btn"
          onClick={() => setShowScenarioDrawer(!showScenarioDrawer)}
        >
          <SlidersHorizontal size={14} />
          <span>{showScenarioDrawer ? 'Hide Scenario Config' : 'Configure Scenario'}</span>
        </button>
      </div>

      {/* Scenario Parameters Drawer */}
      {showScenarioDrawer && (
        <ScenarioDrawer scenario={scenario} onChange={handleScenarioChange} />
      )}

      {/* Main Query Bar */}
      <form className="assistant-query-form" onSubmit={handleSubmit}>
        <div className="assistant-input-wrap">
          <Search className="assistant-search-icon" size={20} />
          <textarea
            className="assistant-textarea"
            rows="2"
            placeholder="Describe the claim or loss scenario in detail (e.g. 'A pipe froze and ruptured in the attic while the homeowner was on a 10-day winter vacation. Is the resulting ceiling and floor damage covered?')..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
        </div>
        <button
          type="submit"
          className="assistant-submit-btn"
          disabled={loading || !question.trim()}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              <span>Analyzing Corpus...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Run Assessment</span>
            </>
          )}
        </button>
      </form>

      {/* Error display */}
      {error && (
        <div className="error-alert">
          <strong>Request Failed:</strong> {error}
        </div>
      )}

      {/* Loading telemetry card */}
      {loading && (
        <div className="telemetry-loading-card">
          <div className="telemetry-step active">
            <span className="step-spinner"></span>
            <span>1. Vectorizing loss description via Pinecone inference (`multilingual-e5-large`)...</span>
          </div>
          <div className="telemetry-step active">
            <span className="step-spinner"></span>
            <span>2. Performing hybrid dense &amp; BM25 search across HO-3 policy clauses...</span>
          </div>
          <div className="telemetry-step active">
            <span className="step-spinner"></span>
            <span>3. Cross-encoder reranking &amp; citation grounding with xAI Grok...</span>
          </div>
        </div>
      )}

      {/* Answer display */}
      {!loading && answer && (
        <AnswerCard answer={answer} onInspectEvidence={onInspectEvidence} />
      )}
    </div>
  );
}

