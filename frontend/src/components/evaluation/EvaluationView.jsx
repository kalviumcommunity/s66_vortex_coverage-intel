import React, { useState, useEffect } from 'react';
import {
  Play,
  RotateCcw,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Inbox
} from 'lucide-react';
import TraceDrawer from './TraceDrawer';
import { fetchBenchmarks, runBenchmarks } from '../../services/api';

export default function EvaluationView() {
  const [activeTab, setActiveTab] = useState('all');
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [testCases, setTestCases] = useState([]);
  const [hasRun, setHasRun] = useState(false);
  const [metrics, setMetrics] = useState({
    total_tests: 0,
    passed_tests: 0,
    precision_rate: '0.0%',
    avg_latency: '0ms',
    faithfulness: 0.0,
  });

  useEffect(() => {
    fetchBenchmarks().then((cases) => {
      setMetrics((prev) => ({ ...prev, total_tests: cases.length }));
    }).catch(() => {});
  }, []);

  const handleRunSuite = async () => {
    setIsRunning(true);
    try {
      const data = await runBenchmarks();
      if (data.metrics) setMetrics(data.metrics);
      if (data.test_cases) setTestCases(data.test_cases);
      setHasRun(true);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  };

  const filteredTests = testCases.filter((tc) => {
    if (activeTab === 'all') return true;
    return (tc.category || '').includes(activeTab);
  });

  return (
    <div className="evaluation-view">
      <div className="evaluation-header">
        <div>
          <h2 className="view-title">RAG Evaluation &amp; Benchmark Bench</h2>
          <p className="view-subtitle">
            Execute the golden benchmark suite to verify retrieval precision, recall, and zero-hallucination compliance
          </p>
        </div>
        <button
          className="run-suite-btn"
          onClick={handleRunSuite}
          disabled={isRunning}
        >
          {isRunning ? (
            <>
              <RotateCcw size={15} className="animate-spin" />
              <span>Executing Live Benchmark...</span>
            </>
          ) : (
            <>
              <Play size={15} />
              <span>Execute Live Benchmark</span>
            </>
          )}
        </button>
      </div>

      {/* Real Live Metrics Grid */}
      <div className="eval-metrics-grid">
        <div className="eval-metric-card">
          <span className="eval-metric-label">Precision Rate</span>
          <div className="eval-metric-val-row">
            <span className="eval-metric-number">{metrics.precision_rate}</span>
          </div>
          <span className="eval-benchmark-tag">Live Retrieval</span>
        </div>

        <div className="eval-metric-card">
          <span className="eval-metric-label">Average Latency</span>
          <div className="eval-metric-val-row">
            <span className="eval-metric-number">{metrics.avg_latency}</span>
          </div>
          <span className="eval-benchmark-tag">End-to-End</span>
        </div>

        <div className="eval-metric-card">
          <span className="eval-metric-label">Faithfulness Score</span>
          <div className="eval-metric-val-row">
            <span className="eval-metric-number">{metrics.faithfulness}</span>
          </div>
          <span className="eval-benchmark-tag">Hallucination Guard</span>
        </div>

        <div className="eval-metric-card">
          <span className="eval-metric-label">Passed Tests</span>
          <div className="eval-metric-val-row">
            <span className="eval-metric-number">{metrics.passed_tests} / {metrics.total_tests}</span>
          </div>
          <span className="eval-benchmark-tag">Golden Dataset</span>
        </div>
      </div>

      {/* Test Cases Table Section */}
      <section className="benchmark-table-section">
        <div className="benchmark-toolbar">
          <div className="benchmark-tabs">
            <button
              className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              All Tests ({testCases.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'normal' ? 'active' : ''}`}
              onClick={() => setActiveTab('normal')}
            >
              Normal Coverage
            </button>
            <button
              className={`tab-btn ${activeTab === 'excl' ? 'active' : ''}`}
              onClick={() => setActiveTab('excl')}
            >
              Exclusions &amp; Endorsements
            </button>
            <button
              className={`tab-btn ${activeTab === 'vconf' ? 'active' : ''}`}
              onClick={() => setActiveTab('vconf')}
            >
              Version Conflicts
            </button>
          </div>
        </div>

        {!hasRun ? (
          <div style={{ padding: '48px 20px', textAlign: 'center', color: '#64748b' }}>
            <Inbox size={32} style={{ margin: '0 auto 12px', color: '#94a3b8' }} />
            <strong style={{ display: 'block', color: '#1e293b', fontSize: '15px', marginBottom: '6px' }}>
              Golden Benchmark Ready
            </strong>
            <p style={{ fontSize: '13px', maxWidth: '420px', margin: '0 auto 16px' }}>
              Click "Execute Live Benchmark" above to run the 4 golden set test scenarios through the RAG pipeline.
            </p>
          </div>
        ) : (
          <div className="table-responsive-wrapper">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Test ID</th>
                  <th>Query Scenario</th>
                  <th>Expected Determination</th>
                  <th>Actual Result</th>
                  <th>Status</th>
                  <th>Citations</th>
                  <th>Latency</th>
                  <th>Trace</th>
                </tr>
              </thead>
              <tbody>
                {filteredTests.map((tc) => (
                  <tr key={tc.id}>
                    <td>
                      <strong>{tc.id}</strong>
                    </td>
                    <td className="query-col">
                      <span>{tc.query}</span>
                    </td>
                    <td>
                      <span className="text-sm font-medium">{tc.expected}</span>
                    </td>
                    <td>
                      <span className="text-sm">{tc.actual}</span>
                    </td>
                    <td>
                      <span className={`status-badge ${tc.status === 'passed' ? 'status-supported' : 'status-insufficient'}`}>
                        {tc.status === 'passed' ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                        <span>{tc.status.toUpperCase()}</span>
                      </span>
                    </td>
                    <td>
                      <span className="citation-pill">{tc.citations}</span>
                    </td>
                    <td>
                      <span className="code-pill">{tc.latency}</span>
                    </td>
                    <td>
                      <button
                        className="table-action-btn"
                        onClick={() => setSelectedTrace(tc)}
                      >
                        <Zap size={13} />
                        <span>Trace</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Trace Drawer Modal */}
      <TraceDrawer
        isOpen={Boolean(selectedTrace)}
        onClose={() => setSelectedTrace(null)}
        testCase={selectedTrace}
      />
    </div>
  );
}
