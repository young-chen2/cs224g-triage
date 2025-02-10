'use client';

import { useState } from 'react';

interface ChatHistory {
  id: string;
  timestamp: string;
  patientName: string;
  symptoms: string;
  chatContext: string;
  currentTriage: 'Nurse' | 'PA' | 'Physician';
}

export const AdminPortal = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Mock data - replace with real data later
  const [chatHistories] = useState<ChatHistory[]>([
    {
      id: '1',
      timestamp: '2024-03-20 14:30',
      patientName: 'John D.',
      symptoms: 'Chest pain, shortness of breath',
      chatContext: 'Patient reported sudden onset chest pain...',
      currentTriage: 'Nurse'
    }
  ]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    }
  };

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
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Upload Guidelines Section */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-blue-600 font-bold">📄</span>
            <h2 className="text-xl font-semibold">Upload Medical Guidelines</h2>
          </div>
          
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors
              ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
              ${selectedFile ? 'bg-green-50' : 'hover:bg-gray-50'}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="flex flex-col items-center gap-3">
                <span className="text-4xl text-gray-400">⬆️</span>
                <p className="text-gray-600">
                  {selectedFile ? (
                    <>Selected: {selectedFile.name}</>
                  ) : (
                    <>
                      <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop<br />
                      PDF files only
                    </>
                  )}
                </p>
              </div>
            </label>
          </div>
          
          {selectedFile && (
            <button
              onClick={handleSubmit}
              className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-lg
                hover:bg-blue-700 transition-colors"
            >
              Upload Guidelines
            </button>
          )}
        </div>

        {/* Triage History Section */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-blue-600 font-bold">📋</span>
            <h2 className="text-xl font-semibold">Recent Triage Decisions</h2>
          </div>

          <div className="space-y-4">
            {chatHistories.length > 0 ? (
              chatHistories.map((chat) => (
                <div key={chat.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">{chat.patientName}</h3>
                      <p className="text-sm text-gray-500">{chat.timestamp}</p>
                    </div>
                    <span className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                      {chat.currentTriage}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{chat.symptoms}</p>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{chat.chatContext}</p>
                  
                  <div className="flex gap-2">
                    <button className="text-sm px-3 py-1 rounded-lg bg-green-100 text-green-700 hover:bg-green-200">
                      Triage to Nurse
                    </button>
                    <button className="text-sm px-3 py-1 rounded-lg bg-yellow-100 text-yellow-700 hover:bg-yellow-200">
                      Triage to PA
                    </button>
                    <button className="text-sm px-3 py-1 rounded-lg bg-red-100 text-red-700 hover:bg-red-200">
                      Triage to Physician
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-500 py-8">No triage decisions recorded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 