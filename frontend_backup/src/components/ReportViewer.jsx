import React from 'react';

const ReportViewer = ({ reportData }) => {
  const getSummaryPoints = (summary) => {
    const points = summary
      .split(/\.\s*\*|\*/)
      .filter((point) => point.trim().length > 20)
      .map((point) => point.trim().replace(/^[\*\s]+/, ''));

    return points.length > 0 ? points : [summary];
  };

  return (
    <div>
      <div className="summary-box">
        <div className="summary-title">KEY FINDINGS</div>

        <ul>
          {getSummaryPoints(reportData.summary).map((point, index) => (
            <li key={index}>{point}</li>
          ))}
        </ul>
      </div>

      <div>
        <div className="summary-title">MEDICAL TERMS DETECTED</div>

        <div className="term-list">
          {reportData.medical_terms.map((term, index) => (
            <div
              key={index}
              className={`term-item ${term.is_abnormal ? 'abnormal' : 'normal'}`}
            >
              <div className="term-header">
                <div className="term-name">
                  <span>{term.is_abnormal ? '⚠️' : '✓'}</span>
                  {term.term}
                </div>

                {term.value && (
                  <span className={`term-value value-${term.status}`}>
                    {term.value} {term.unit}
                  </span>
                )}
              </div>

              <p>{term.explanation}</p>

              {term.status && (
                <p>
                  <strong>Status:</strong> {term.status.toUpperCase()}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReportViewer;
