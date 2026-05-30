import React, { useState, useEffect } from 'react';
import './App.css';
import { ClassificationDisplay } from './components/ClassificationDisplay';
import { WorkflowStatus } from './components/WorkflowStatus';
import { TaskAssignment } from './components/TaskAssignment';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import { getBoxContext } from './utils/boxSDK';

interface ClassificationData {
  document_id: string;
  doc_type: string;
  confidence: number;
  reasoning: string;
  extracted_fields: Record<string, any>;
  required_reviewer: string | null;
  metadata_tags: string[];
  classified_at: string;
}

interface ProcessingResult {
  document_id: string;
  box_file_id: string;
  destination_folder: string;
  status: 'success' | 'failure' | 'escalated';
  task_id: string | null;
  assigned_to: string | null;
  metadata_applied: Record<string, any>;
  notification_sent_to: string[];
  error_message: string | null;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const App: React.FC = () => {
  const [classification, setClassification] = useState<ClassificationData | null>(null);
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  // Initialize: Get file ID from Box context
  useEffect(() => {
    const initializeExtension = async () => {
      try {
        const boxContext = await getBoxContext();
        setFileId(boxContext.fileId);
        setFileName(boxContext.fileName);
        await fetchClassification(boxContext.fileId);
      } catch (err) {
        setError('Failed to initialize extension. Make sure you have a file selected in Box.');
        console.error('Initialization error:', err);
      }
    };

    initializeExtension();
  }, []);

  const fetchClassification = async (fileId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/documents/${fileId}`);
      if (response.ok) {
        const data = await response.json();
        setClassification(data.classification);
        setProcessingResult(data.processing_result);
      } else if (response.status === 404) {
        setError('No classification data found for this file. It may not have been processed yet.');
      } else {
        setError(`Error fetching classification: ${response.statusText}`);
      }
    } catch (err) {
      setError(`Failed to connect to backend: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (fileId) {
      fetchClassification(fileId);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📋 Document Classification</h1>
        {fileName && <p className="file-name">{fileName}</p>}
        <button className="refresh-btn" onClick={handleRefresh} disabled={loading}>
          {loading ? 'Loading...' : '🔄 Refresh'}
        </button>
      </header>

      <main className="app-content">
        {error && <ErrorMessage message={error} />}

        {loading && <LoadingSpinner />}

        {!loading && classification && (
          <>
            <ClassificationDisplay
              classification={classification}
              confidence={classification.confidence}
            />

            {processingResult && <WorkflowStatus processingResult={processingResult} />}

            {classification.required_reviewer && (
              <TaskAssignment
                reviewer={classification.required_reviewer}
                docType={classification.doc_type}
                confidence={classification.confidence}
                fileId={fileId || ''}
              />
            )}
          </>
        )}

        {!loading && !classification && !error && (
          <div className="no-data">
            <p>No classification data available.</p>
            <p className="hint">Select a file in Box to see its classification results.</p>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <small>Box Smart Inbox • Powered by AI Classification</small>
      </footer>
    </div>
  );
};

export default App;
