import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ReportViewer from './components/ReportViewer';
import ChatInterface from './components/ChatInterface';
import Navbar from './components/Navbar';
import Loader from './components/Loader';
import { ThemeProvider } from './components/ThemeProvider';
import './styles.css';

function App() {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleReportUploaded = (data) => {
    setReportData(data);
    setLoading(false);
    requestAnimationFrame(() => {
      const analysis = document.getElementById('analysis');
      if (analysis) analysis.scrollIntoView({ behavior: 'smooth' });
    });
  };

  return (
    <ThemeProvider>
      <Navbar />
      <Loader show={loading} label="Analyzing your report…" />

      <div className="container">
        <header className="header">
          <div className="brand">
            <div className="brand-badge">MR</div>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: 800, letterSpacing: '0.04em' }}>
                MED REPORT
              </div>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                Clinical Insights, Simplified
              </div>
            </div>
          </div>

          <h1 className="title">Medical Report Explainer</h1>
          <p className="subtitle">
            Upload a PDF report to get a clean summary, flagged values, and chat with AI about what each metric means.
          </p>

          {!reportData && (
            <div className="feature-strip">
              <div className="feature">
                <div className="feature-icon">🔎</div>
                <div className="feature-text">
                  <strong>Smart parsing</strong> of lab terms & values
                </div>
              </div>
              <div className="feature">
                <div className="feature-icon">⚠️</div>
                <div className="feature-text">
                  <strong>Abnormal flags</strong> with safe explanations
                </div>
              </div>
              <div className="feature">
                <div className="feature-icon">💬</div>
                <div className="feature-text">
                  <strong>Ask anything</strong> about your report
                </div>
              </div>
            </div>
          )}
        </header>

        {!reportData ? (
          <section id="upload">
            <FileUpload
              onUploadSuccess={handleReportUploaded}
              loading={loading}
              setLoading={setLoading}
            />
          </section>
        ) : (
          <section id="analysis" className="reveal">
            <div className="grid">
              <div className="card card-pop">
                <div className="card-title">
                  <span className="icon">📋</span>
                  <span>Report Analysis</span>
                </div>
                <ReportViewer reportData={reportData} />
              </div>

              <div className="card card-pop delay-1">
                <div className="card-title">
                  <span className="icon">💬</span>
                  <span>Ask Questions</span>
                </div>
                <ChatInterface reportContext={reportData.extracted_text} />
              </div>
            </div>
          </section>
        )}

        <footer>
          ⚠️ Educational use only. Not a substitute for professional medical advice.
        </footer>
      </div>
    </ThemeProvider>
  );
}

export default App;
