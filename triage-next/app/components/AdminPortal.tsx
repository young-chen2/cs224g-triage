'use client';

import { useState } from 'react';

export const AdminPortal = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    
    // TODO: Implement PDF upload logic
    console.log('Uploading:', selectedFile.name);
  };

  return (
    <div className="admin-portal">
      <div className="upload-section">
        <h2>Upload Medical Documents</h2>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          className="file-input"
        />
        {selectedFile && (
          <div className="selected-file">
            <p>Selected: {selectedFile.name}</p>
            <button onClick={handleSubmit}>Upload</button>
          </div>
        )}
      </div>

      <div className="triage-history">
        <h2>Triage Decisions History</h2>
        <div className="history-list">
          {/* TODO: Implement triage history view */}
          <p>No triage decisions recorded yet.</p>
        </div>
      </div>
    </div>
  );
}; 