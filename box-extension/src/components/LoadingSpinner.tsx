import React from 'react';
import '../styles/LoadingSpinner.css';

export const LoadingSpinner: React.FC = () => (
  <div className="loading-container">
    <div className="spinner"></div>
    <p>Loading classification data...</p>
  </div>
);
