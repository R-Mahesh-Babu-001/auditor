import React, { Component, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { Provider } from "react-redux";
import store from "./redux/store/store.js";
import App from './App.jsx'

class RootErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("AuditReady UI Runtime Error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 32, fontFamily: "system-ui, sans-serif", maxWidth: 800, margin: "40px auto", background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, boxShadow: "0 4px 12px rgba(0,0,0,0.05)" }}>
          <h2 style={{ color: "#ef4444", fontSize: 20, marginBottom: 8, fontWeight: 700 }}>Workspace Rendering Error</h2>
          <p style={{ color: "#64748b", fontSize: 14, marginBottom: 16 }}>An unhandled client error occurred while rendering the workspace.</p>
          <pre style={{ background: "#f8fafc", padding: 16, borderRadius: 6, fontSize: 13, color: "#0f172a", overflow: "auto", border: "1px solid #cbd5e1", whiteSpace: "pre-wrap" }}>
            {this.state.error?.toString()}
            {"\n\n"}
            {this.state.errorInfo?.componentStack}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{ marginTop: 16, padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontWeight: 600 }}
          >
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <RootErrorBoundary>
    <Provider store={store}>
      <App />
    </Provider>
  </RootErrorBoundary>
)
