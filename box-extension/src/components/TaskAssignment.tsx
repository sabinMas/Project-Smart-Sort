import React, { useState } from 'react';
import '../styles/TaskAssignment.css';

interface TaskAssignmentProps {
  reviewer: string;
  docType: string;
  confidence: number;
  fileId: string;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const TaskAssignment: React.FC<TaskAssignmentProps> = ({
  reviewer,
  docType,
  confidence,
  fileId,
}) => {
  const [assignedTo, setAssignedTo] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleAssignTask = async () => {
    if (!assignedTo) {
      setMessage('Please enter an assignee email');
      return;
    }

    setIsSubmitting(true);
    setMessage('');

    try {
      const response = await fetch(`${BACKEND_URL}/tasks/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          assigned_to: assignedTo,
          due_date: dueDate || undefined,
          message: `Please review this ${docType} document (${Math.round(confidence * 100)}% confidence)`,
        }),
      });

      if (response.ok) {
        setMessage('✅ Task assigned successfully!');
        setAssignedTo('');
        setDueDate('');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setMessage(`❌ Failed to assign task: ${errorData.detail || response.statusText}`);
      }
    } catch (err) {
      setMessage(`❌ Error connecting to backend: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="task-assignment-card">
      <h3>Assign Review Task</h3>

      <div className="reviewer-info">
        <p>
          This {docType} document needs review from: <strong>{reviewer.toUpperCase()}</strong>
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="assignee">Assign to (email):</label>
        <input
          id="assignee"
          type="email"
          placeholder="reviewer@company.com"
          value={assignedTo}
          onChange={(e) => setAssignedTo(e.target.value)}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-group">
        <label htmlFor="dueDate">Due Date (optional):</label>
        <input
          id="dueDate"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          disabled={isSubmitting}
        />
      </div>

      <button
        className="assign-btn"
        onClick={handleAssignTask}
        disabled={isSubmitting || !assignedTo}
      >
        {isSubmitting ? 'Assigning...' : 'Assign Task'}
      </button>

      {message && <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>{message}</div>}
    </div>
  );
};
