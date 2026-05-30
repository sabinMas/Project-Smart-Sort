import React from 'react';
import '../styles/ClassificationDisplay.css';

interface ClassificationDisplayProps {
  classification: any;
  confidence: number;
}

export const ClassificationDisplay: React.FC<ClassificationDisplayProps> = ({
  classification,
  confidence,
}) => {
  const confidenceColor = confidence > 0.85 ? 'high' : confidence > 0.7 ? 'medium' : 'low';
  const confidencePercent = Math.round(confidence * 100);

  return (
    <div className="classification-card">
      <h2>Classification Result</h2>

      <div className="doc-type">
        <span className="label">Document Type:</span>
        <span className="value">{classification.doc_type.toUpperCase()}</span>
      </div>

      <div className={`confidence-meter confidence-${confidenceColor}`}>
        <div className="confidence-label">Confidence Score</div>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{ width: `${confidencePercent}%` }}
          ></div>
        </div>
        <div className="confidence-text">{confidencePercent}%</div>
      </div>

      {classification.reasoning && (
        <div className="reasoning">
          <span className="label">Reasoning:</span>
          <p>{classification.reasoning}</p>
        </div>
      )}

      {classification.metadata_tags && classification.metadata_tags.length > 0 && (
        <div className="metadata-tags">
          <span className="label">Tags:</span>
          <div className="tags">
            {classification.metadata_tags.map((tag: string, idx: number) => (
              <span key={idx} className="tag">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {classification.extracted_fields &&
        Object.keys(classification.extracted_fields).length > 0 && (
          <div className="extracted-fields">
            <span className="label">Extracted Fields:</span>
            <table className="fields-table">
              <tbody>
                {Object.entries(classification.extracted_fields).map(([key, value]) => (
                  <tr key={key}>
                    <td className="field-name">{key}</td>
                    <td className="field-value">{String(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      {classification.required_reviewer && (
        <div className="required-reviewer">
          <span className="label">Requires Review From:</span>
          <div className="reviewer-badge">{classification.required_reviewer.toUpperCase()}</div>
        </div>
      )}
    </div>
  );
};
