/**
 * Audit Copilot API Client.
 * Connects frontend directly to FastAPI backend and Neon PostgreSQL.
 */

import { safeStorage } from "../lib/safeStorage";

const API_BASE = import.meta.env?.VITE_API_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Accept": "application/json",
    ...options.headers,
  };

  const token = safeStorage.getItem("audit_token");
  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Don't set Content-Type if sending FormData (browser sets boundary)
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || errorText;
    } catch {
      // Keep raw text
    }
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Health & System
  getHealth: () => request("/health"),
  getReady: () => request("/ready"),

  // Auth & Context
  login: (email, password) =>
    request("/api/auth/token", { method: "POST", body: JSON.stringify({ email, password }) }),
  getCurrentUser: () => request("/api/auth/me"),

  // Dashboard
  getDashboardKpis: (engagementId) =>
    request(`/api/dashboard/kpis${engagementId ? `?engagement_id=${engagementId}` : ""}`),

  // Engagements
  getEngagements: () => request("/api/engagements"),
  createEngagement: (data) =>
    request("/api/engagements", { method: "POST", body: JSON.stringify(data) }),

  // Evidence
  getEvidenceFiles: (engagementId) =>
    request(`/api/evidence${engagementId ? `?engagement_id=${engagementId}` : ""}`),
  uploadEvidenceFile: (formData) =>
    request("/api/evidence/upload", { method: "POST", body: formData }),

  // Datasets
  getDatasets: (engagementId) =>
    request(`/api/datasets${engagementId ? `?engagement_id=${engagementId}` : ""}`),
  uploadDataset: (formData) =>
    request("/api/datasets/upload", { method: "POST", body: formData }),
  previewDataset: (datasetId) =>
    request(`/api/datasets/${datasetId}/preview`),

  // RCM
  getCriteria: () => request("/api/rcm/criteria"),
  getRisks: () => request("/api/rcm/risks"),
  getControls: () => request("/api/rcm/controls"),
  getRcmCoverage: () => request("/api/rcm/coverage"),

  // Tests & Execution
  getTestTemplates: () => request("/api/tests/templates"),
  getTestRuns: (engagementId) =>
    request(`/api/tests/runs${engagementId ? `?engagement_id=${engagementId}` : ""}`),
  runAuditTest: (data) =>
    request("/api/tests/run", { method: "POST", body: JSON.stringify(data) }),

  // Exceptions & Triage
  getExceptions: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/exceptions${query ? `?${query}` : ""}`);
  },
  getExceptionDetail: (id) => request(`/api/exceptions/${id}`),
  setExceptionDisposition: (id, data) =>
    request(`/api/exceptions/${id}/disposition`, { method: "POST", body: JSON.stringify(data) }),

  // Findings
  getFindings: (engagementId) =>
    request(`/api/findings${engagementId ? `?engagement_id=${engagementId}` : ""}`),
  createFinding: (data) =>
    request("/api/findings", { method: "POST", body: JSON.stringify(data) }),

  // Workpapers
  getWorkpapers: (engagementId) =>
    request(`/api/workpapers${engagementId ? `?engagement_id=${engagementId}` : ""}`),
  generateWorkpaper: (data) =>
    request("/api/workpapers/generate", { method: "POST", body: JSON.stringify(data) }),
  getWorkpaperVersions: (id) => request(`/api/workpapers/${id}/versions`),
  approveWorkpaper: (id, notes = "") =>
    request(`/api/workpapers/${id}/approve`, { method: "POST", body: JSON.stringify({ notes }) }),

  // Remediation
  getRemediations: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/remediation${query ? `?${query}` : ""}`);
  },
  createRemediation: (data) =>
    request("/api/remediation", { method: "POST", body: JSON.stringify(data) }),
  updateRemediation: (id, data) =>
    request(`/api/remediation/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  verifyRemediation: (id, data) =>
    request(`/api/remediation/${id}/verify`, { method: "POST", body: JSON.stringify(data) }),

  // Continuous Auditing
  getContinuousRules: (engagementId) =>
    request(`/api/continuous/rules${engagementId ? `?engagement_id=${engagementId}` : ""}`),
  createContinuousRule: (data) =>
    request("/api/continuous/rules", { method: "POST", body: JSON.stringify(data) }),
  triggerContinuousRule: (ruleId, data = {}) =>
    request(`/api/continuous/rules/${ruleId}/trigger`, { method: "POST", body: JSON.stringify(data) }),

  // ITGC & Governance
  getSodMatrix: () => request("/api/governance/sod-matrix"),
  runItgcSod: (data) =>
    request("/api/governance/itgc/sod", { method: "POST", body: JSON.stringify(data) }),
  runVendorAssurance: (data) =>
    request("/api/governance/vendor-assurance", { method: "POST", body: JSON.stringify(data) }),
  runAiGovernance: (data) =>
    request("/api/governance/ai-governance", { method: "POST", body: JSON.stringify(data) }),
  getSopMaps: () => request("/api/governance/sop-maps"),
  getAuditLogs: () => request("/api/governance/audit-logs"),
};

