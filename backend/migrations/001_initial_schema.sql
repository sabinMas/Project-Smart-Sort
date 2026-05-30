-- Initial database schema for document orchestration system
-- Creates tables for documents, contacts, signatures, approvals, and audit logs

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table: stores metadata and state for each document
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Document metadata
  file_name VARCHAR(255) NOT NULL,
  file_size INTEGER,
  file_hash VARCHAR(64) UNIQUE,  -- SHA-256 of PDF for deduplication
  mime_type VARCHAR(50),

  -- Classification results (JSON from Claude)
  classification JSONB NOT NULL DEFAULT '{}',
  classification_model VARCHAR(50),  -- 'claude-sonnet-4-20250514' or 'box-ai'
  classification_confidence DECIMAL(3,2),  -- 0.0 to 1.0

  -- Box integration
  box_file_id VARCHAR(255),
  box_folder_current VARCHAR(50),  -- 'inbox', 'needs_review', 'needs_signature', 'pending_return', 'archive'

  -- Document state lifecycle
  status VARCHAR(50) NOT NULL,  -- 'classified', 'pending_approval', 'approved', 'sent_for_signature', 'awaiting_return', 'complete', 'rejected', 'expired'
  version_number INTEGER DEFAULT 1,

  -- Timing
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  classified_at TIMESTAMP,
  approved_at TIMESTAMP,
  sent_at TIMESTAMP,
  completed_at TIMESTAMP,
  expires_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Audit
  created_by VARCHAR(255),  -- Email of uploader
  approved_by VARCHAR(255),  -- Email of approver

  -- Flags
  needs_manual_review BOOLEAN DEFAULT FALSE,
  review_reason TEXT,

  CONSTRAINT valid_status CHECK (status IN (
    'classified', 'pending_approval', 'approved', 'sent_for_signature',
    'awaiting_return', 'complete', 'rejected', 'expired'
  )),
  CONSTRAINT valid_box_folder CHECK (box_folder_current IN (
    'inbox', 'needs_review', 'needs_signature', 'pending_return', 'archive'
  ))
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_box_folder ON documents(box_folder_current);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_file_hash ON documents(file_hash);

-- Contact emails table: stores verified contacts built from email traffic
CREATE TABLE IF NOT EXISTS contact_emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  company VARCHAR(255),
  domain VARCHAR(255),  -- Extracted from email domain

  -- How we know about this contact
  source VARCHAR(50) NOT NULL,  -- 'email_from', 'email_to', 'extracted_from_doc', 'manual'
  source_doc_id UUID REFERENCES documents(id) ON DELETE SET NULL,

  -- Confidence & verification
  verification_score INTEGER DEFAULT 0,  -- 0-100
  verified BOOLEAN DEFAULT FALSE,

  -- Contact history
  first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_email_date TIMESTAMP,
  last_contact_method VARCHAR(50),  -- 'inbound_email', 'signature_request', 'reply'

  -- Metadata
  tags TEXT[],
  notes TEXT,

  -- Activity tracking
  email_count INTEGER DEFAULT 0,
  signature_count INTEGER DEFAULT 0,

  CONSTRAINT valid_source CHECK (source IN (
    'email_from', 'email_to', 'extracted_from_doc', 'manual'
  ))
);

CREATE INDEX idx_contact_emails_email ON contact_emails(email);
CREATE INDEX idx_contact_emails_verification_score ON contact_emails(verification_score);
CREATE INDEX idx_contact_emails_last_email_date ON contact_emails(last_email_date);
CREATE INDEX idx_contact_emails_verified ON contact_emails(verified);

-- Signature state table: tracks signing progress for each document
CREATE TABLE IF NOT EXISTS signature_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,

  -- Recipients & their signing status
  recipients JSONB NOT NULL DEFAULT '[]',  -- [ { email, name, status, signed_at, docusign_id } ]
  signed_count INTEGER DEFAULT 0,
  total_count INTEGER DEFAULT 0,

  -- DocuSign tracking
  docusign_envelope_id VARCHAR(255) UNIQUE,
  docusign_template_id VARCHAR(255),
  return_url VARCHAR(2048),

  -- Signing deadline
  expires_at TIMESTAMP,
  reminder_sent_dates TIMESTAMP[],
  last_reminder_at TIMESTAMP,

  -- Completion
  all_signed_at TIMESTAMP,
  completion_percentage INTEGER DEFAULT 0,

  -- Audit
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT valid_counts CHECK (signed_count <= total_count)
);

CREATE INDEX idx_signature_state_document_id ON signature_state(document_id);
CREATE INDEX idx_signature_state_docusign_envelope_id ON signature_state(docusign_envelope_id);
CREATE INDEX idx_signature_state_expires_at ON signature_state(expires_at);

-- Approvals table: audit trail of human decisions
CREATE TABLE IF NOT EXISTS approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

  -- Decision
  action VARCHAR(50) NOT NULL,  -- 'approve', 'reject', 'flag_for_review', 'edit'
  decision_reason TEXT,

  -- What changed
  original_recipients JSONB,  -- Suggested by AI
  approved_recipients JSONB,  -- Approved by human
  changes_made TEXT[],

  -- Who & when
  approved_by VARCHAR(255) NOT NULL,  -- Email
  approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT valid_action CHECK (action IN (
    'approve', 'reject', 'flag_for_review', 'edit'
  ))
);

CREATE INDEX idx_approvals_document_id ON approvals(document_id);
CREATE INDEX idx_approvals_approved_by ON approvals(approved_by);
CREATE INDEX idx_approvals_approved_at ON approvals(approved_at);

-- Email audit log table: complete audit of all email traffic
CREATE TABLE IF NOT EXISTS email_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  direction VARCHAR(10),  -- 'inbound' or 'outbound'

  -- Email details
  from_address VARCHAR(255),
  to_address VARCHAR(255),
  cc_address VARCHAR(255),
  subject VARCHAR(1024),
  message_id VARCHAR(255),

  -- Context
  document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
  docusign_envelope_id VARCHAR(255),

  -- Status & metadata
  status VARCHAR(50),  -- 'sent', 'delivered', 'opened', 'bounced', 'clicked', etc.
  email_type VARCHAR(50),  -- 'document_submission', 'signature_request', 'reminder', 'completion_notification'

  -- Content tracking
  has_attachment BOOLEAN DEFAULT FALSE,
  attachment_count INTEGER,
  attachment_names TEXT[]
);

CREATE INDEX idx_email_audit_log_timestamp ON email_audit_log(timestamp);
CREATE INDEX idx_email_audit_log_direction ON email_audit_log(direction);
CREATE INDEX idx_email_audit_log_document_id ON email_audit_log(document_id);
CREATE INDEX idx_email_audit_log_from_address ON email_audit_log(from_address);
CREATE INDEX idx_email_audit_log_email_type ON email_audit_log(email_type);
