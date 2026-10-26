import React, { useState, Component } from 'react'
import Home from './pages/layoutPage'
import Header from './globalComponents/Header'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    console.error("Caught error in App:", error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 30, background: '#fef2f2', border: '1px solid #ef4444', margin: 20, borderRadius: 8, color: '#991b1b' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: 10 }}>Something went wrong while rendering the app</h2>
          <pre style={{ background: '#fee2e2', padding: 15, borderRadius: 6, overflowX: 'auto', fontSize: '0.875rem' }}>
            {this.state.error?.toString()}
          </pre>
          <pre style={{ marginTop: 10, fontSize: '0.75rem', opacity: 0.8 }}>
            {this.state.error?.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <div className='min-h-screen'>
        <Header />
        <Home />
      </div>
    </ErrorBoundary>
  )
}

export default App
