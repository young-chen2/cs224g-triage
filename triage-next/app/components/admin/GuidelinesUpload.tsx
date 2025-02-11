'use client';

import { useState } from 'react';

export const GuidelinesUpload = ({ isDarkMode }: { isDarkMode: boolean }) => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);

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
        <div className={`${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} rounded-xl shadow-md p-6`}>
            <div className="flex items-center gap-2 mb-4">
                <span className="text-blue-600 font-bold text-2xl">📄</span>
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
                    className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    Upload Guidelines
                </button>
            )}
        </div>
    );
}; 