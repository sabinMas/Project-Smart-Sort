import React from 'react';
import '../styles/WorkflowStatus.css';

// Mirrors the local ProcessingResult interface in App.tsx (kept local to avoid
// touching shared type files; the shape must match App.tsx).
export interface ProcessingResult {
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

// Exactly six labels in fixed order (Req 3.2).
const STAGE_LABELS = [
  'Received',
  'Classified',
  'Routed',
  'Task Created',
  'Notified',
  'Complete',
] as const;

export type StageState = 'completed' | 'pending' | 'error';

export interface Stage {
  label: string;
  state: StageState;
}

// Choose the first stage whose precondition is unmet.
function failurePointIndex(pr: ProcessingResult): number {
  if (!pr.destination_folder) return 2; // Routed
  if (pr.task_id == null) return 3; // Task Created
  if (pr.notification_sent_to.length === 0) return 4; // Notified
  return 5; // Complete
}

// Walk left-to-right; after the first non-'completed' stage, force all later
// stages to 'pending' (Req 3.4).
function enforceMonotonic(
  labels: readonly string[],
  states: StageState[]
): Stage[] {
  let broken = false;
  return labels.map((label, i) => {
    if (broken) {
      return { label, state: 'pending' as StageState };
    }
    if (states[i] !== 'completed') {
      broken = true;
    }
    return { label, state: states[i] };
  });
}

export function deriveStages(pr: ProcessingResult): Stage[] {
  // success => every stage completed (Req 3.3)
  if (pr.status === 'success') {
    return STAGE_LABELS.map((label) => ({ label, state: 'completed' as StageState }));
  }

  // failure => mark the failure point as error, earlier stages completed,
  // later stages pending (Req 3.6)
  if (pr.status === 'failure') {
    const failIndex = failurePointIndex(pr);
    return STAGE_LABELS.map((label, i) => ({
      label,
      state: i < failIndex ? 'completed' : i === failIndex ? 'error' : 'pending',
    }));
  }

  // in-progress / escalated => derive per-stage from available fields,
  // enforcing monotonicity (once pending, all later stages pending).
  const taskDone = pr.task_id != null; // Req 3.4
  const notifiedDone = pr.notification_sent_to.length > 0; // Req 3.5
  const states: StageState[] = [
    'completed', // Received
    'completed', // Classified
    pr.destination_folder ? 'completed' : 'pending', // Routed
    taskDone ? 'completed' : 'pending', // Task Created
    taskDone && notifiedDone ? 'completed' : 'pending', // Notified
    'pending', // Complete (only success completes it)
  ];
  return enforceMonotonic(STAGE_LABELS, states);
}

export const WorkflowStatus: React.FC<{ processingResult: ProcessingResult }> = ({
  processingResult,
}) => {
  const stages = deriveStages(processingResult);
  return (
    <div className="workflow-status">
      <h3>Processing Status</h3>
      <ol className="workflow-stages">
        {stages.map((s) => (
          <li key={s.label} className={`stage stage-${s.state}`}>
            <span className="stage-icon" aria-hidden="true">
              {s.state === 'completed' ? '✓' : s.state === 'error' ? '✕' : '○'}
            </span>
            <span className="stage-label">{s.label}</span>
          </li>
        ))}
      </ol>
      {processingResult.status === 'failure' && processingResult.error_message && (
        <p className="workflow-error">{processingResult.error_message}</p>
      )}
    </div>
  );
};
