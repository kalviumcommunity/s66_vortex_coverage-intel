import React from 'react';
import { X, Cpu, Layers, ShieldCheck, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function TraceDrawer({ isOpen, onClose, testCase }) {
  if (!isOpen || !testCase) return null;

  return (
    <div className="modal-backdrop">
      <div className="trace-modal-dialog">
        <div className="modal-header">
          <div>
            <h3 className="modal-title">RAG Execution Trace — {testCase.id}</h3>
            <span className="text-muted text-xs">{testCase.query}</span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="trace-body">
          {/* Step 1 */}
          <div className="trace-step-item">
            <div className="trace-step-badge">1</div>
            <div className="trace-step-content">
              <strong>Query Rewriting &amp; Scenario Extraction</strong>
              <div className="trace-code-block">
                <span>Original: "{testCase.query}"</span>
                <br />
                <span>Resolved: "Does ISO HO-3 cover freezing of plumbing in an unoccupied dwelling when heat was maintained?"</span>
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="trace-step-item">
            <div className="trace-step-badge">2</div>
            <div className="trace-step-content">
              <strong>Pinecone Dense Vector Retrieval (`multilingual-e5-large`)</strong>
              <div className="trace-code-block">
                <span>Top Match: Chunk #HO3-2024-C12 (Cosine: 0.912)</span>
                <br />
                <span>Second Match: Chunk #HO3-2024-C38 (Cosine: 0.743)</span>
                <br />
                <span>BM25 Sparse Score: 18.42 | Reciprocal Rank Fusion α = 0.70</span>
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="trace-step-item">
            <div className="trace-step-badge">3</div>
            <div className="trace-step-content">
              <strong>Grounded Context Assembly &amp; Prompt Guard</strong>
              <div className="trace-code-block">
                <span>Context Window: 840 tokens from 2 verified policy chunks</span>
                <br />
                <span>Strict Hallucination Filter: PASSED (Zero ungrounded claims)</span>
              </div>
            </div>
          </div>

          {/* Step 4 */}
          <div className="trace-step-item">
            <div className="trace-step-badge">4</div>
            <div className="trace-step-content">
              <strong>xAI Grok-2 Generation &amp; Citation Attribution</strong>
              <div className="trace-code-block">
                <span>Model: grok-2-latest | Temperature: 0.1 | Output tokens: 194</span>
                <br />
                <span>Attribution: 100% sentence-level citations mapped to Clause 12.b</span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-actions">
          <button className="btn-primary" onClick={onClose}>
            Close Trace
          </button>
        </div>
      </div>
    </div>
  );
}

