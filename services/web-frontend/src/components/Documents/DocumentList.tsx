// FILE: services/web-frontend/src/components/Documents/DocumentList.tsx

import React from 'react';
import { Document } from '../../types';

interface DocumentListProps {
  documents: Document[];
  onDelete: (documentId: string) => void;
  onProcess: (documentId: string) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, onDelete, onProcess }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
        >
          {/* Document Icon & Name */}
          <div className="flex items-start mb-4">
            <svg
              className="w-10 h-10 text-blue-600 mr-3 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 truncate" title={doc.filename}>
                {doc.filename}
              </h3>
              <p className="text-xs text-gray-500 mt-1">{formatFileSize(doc.file_size)}</p>
            </div>
          </div>

          {/* Status Badge */}
          <div className="mb-4">
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(doc.status)}`}>
              {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
            </span>
          </div>

          {/* Metadata */}
          <div className="text-xs text-gray-600 space-y-1 mb-4">
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Uploaded: {formatDate(doc.uploaded_at)}
            </div>
            {doc.processed_at && (
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Processed: {formatDate(doc.processed_at)}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex space-x-2">
            {doc.status === 'pending' && (
              <button
                onClick={() => onProcess(doc.id)}
                className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
              >
                Process
              </button>
            )}
            {doc.status === 'completed' && (
              <button
                className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition"
                title="Document is ready for Q&A"
              >
                Ready
              </button>
            )}
            <button
              onClick={() => onDelete(doc.id)}
              className="px-3 py-2 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200 transition"
              title="Delete document"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;
