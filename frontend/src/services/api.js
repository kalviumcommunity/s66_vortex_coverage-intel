/**
 * Coverage Intel — Production API Client Service
 * Fully integrated with live FastAPI endpoints (no mock data).
 */

const API_BASE = '';

/**
 * Ask a coverage question with scenario metadata
 */
export async function askCoverage(question, scenario = {}) {
  const cleanScenario = {};
  if (scenario) {
    if (scenario.policy_type && scenario.policy_type.trim()) {
      cleanScenario.policy_type = scenario.policy_type.trim();
    }
    if (scenario.jurisdiction && scenario.jurisdiction.trim()) {
      cleanScenario.jurisdiction = scenario.jurisdiction.trim();
    }
    if (scenario.claim_type && scenario.claim_type.trim()) {
      cleanScenario.claim_type = scenario.claim_type.trim();
    }
    if (scenario.date_of_loss && scenario.date_of_loss.trim()) {
      cleanScenario.date_of_loss = scenario.date_of_loss.trim();
    }
  }

  const payload = {
    question,
    scenario: Object.keys(cleanScenario).length > 0 ? cleanScenario : null,
  };

  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch real documents listed in the active corpus
 */
export async function fetchDocuments() {
  const response = await fetch(`${API_BASE}/documents`);
  if (!response.ok) {
    throw new Error(`Failed to load documents: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch specific document text and metadata
 */
export async function fetchDocument(docId) {
  const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(docId)}`);
  if (!response.ok) {
    throw new Error(`Document not found: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch live system telemetry & corpus stats
 */
export async function fetchStats() {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.status}`);
  }
  return response.json();
}

/**
 * Reset and clear all corpus data & vector store for clean retesting
 */
export async function resetCorpusData() {
  const response = await fetch(`${API_BASE}/system/reset`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Reset failed: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch real golden benchmark test cases
 */
export async function fetchBenchmarks() {
  const response = await fetch(`${API_BASE}/evaluation/benchmarks`);
  if (!response.ok) {
    throw new Error(`Failed to load benchmarks: ${response.status}`);
  }
  return response.json();
}

/**
 * Execute golden benchmark suite against live RAG pipeline
 */
export async function runBenchmarks() {
  const response = await fetch(`${API_BASE}/evaluation/run`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Benchmark execution failed: ${response.status}`);
  }
  return response.json();
}

/**
 * Upload an approved policy document
 */
export async function uploadDocument(file, accessKey, metadata = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (metadata.documentId) formData.append('document_id', metadata.documentId);
  if (metadata.category) formData.append('category', metadata.category);
  if (metadata.version) formData.append('version', metadata.version);
  if (metadata.effectiveFrom) formData.append('effective_from', metadata.effectiveFrom);
  if (metadata.effectiveTo) formData.append('effective_to', metadata.effectiveTo);
  if (metadata.jurisdiction) formData.append('jurisdiction', metadata.jurisdiction);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    headers: {
      'X-Upload-Access-Key': accessKey,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `Upload failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Check backend service health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
