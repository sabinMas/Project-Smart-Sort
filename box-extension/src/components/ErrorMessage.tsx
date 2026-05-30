import React from 'react';
import '../styles/ErrorMessage.css';

interface ErrorMessageProps {
  message: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => (
  <div className="error-banner">
    <span className="error-icon">⚠️</span>
    <p>{message}</p>
  </div>
);
