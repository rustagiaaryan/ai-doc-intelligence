// FILE: services/web-frontend/src/components/PDF/PDFModal.tsx

import React, { useState, useEffect } from 'react';
import { PDFViewer } from './PDFViewer';
import { documentsApi } from '../../api/documents';
import { DocumentChunk } from '../../types';

interface PDFModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  highlightedChunks: DocumentChunk[];
}

export const PDFModal: React.FC<PDFModalProps> = ({
  isOpen,
  onClose,
  documentId,
  highlightedChunks,
}) => {
  const [documentUrl, setDocumentUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && documentId) {
      fetchDocumentUrl();
    }
  }, [isOpen, documentId]);

  const fetchDocumentUrl = async () => {
    console.log('[PDFModal] Fetching document URL for:', documentId);
    setIsLoading(true);
    setError(null);
    try {
      const response = await documentsApi.getDownloadUrl(documentId);
      console.log('[PDFModal] Got download URL:', response.url);
      setDocumentUrl(response.url);
    } catch (err) {
      console.error('[PDFModal] Failed to fetch document URL:', err);
      setError('Failed to load PDF. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  console.log('[PDFModal] Rendering modal - isLoading:', isLoading, 'error:', error, 'documentUrl:', documentUrl, 'chunks:', highlightedChunks.length);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-75 transition-opacity"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl w-full h-full max-w-7xl max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">
              Document Viewer
              {highlightedChunks.length > 0 && (
                <span className="ml-2 text-sm font-normal text-gray-600">
                  ({highlightedChunks.length} highlighted sections)
                </span>
              )}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition"
              aria-label="Close"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* PDF Viewer Container */}
          <div className="flex-1 overflow-hidden">
            {isLoading && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  <p className="mt-4 text-gray-600">Loading PDF...</p>
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-red-600">
                  <svg
                    className="mx-auto h-12 w-12"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="mt-4">{error}</p>
                  <button
                    onClick={fetchDocumentUrl}
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Retry
                  </button>
                </div>
              </div>
            )}

            {documentUrl && !isLoading && !error && (
              <PDFViewer
                documentUrl={documentUrl}
                highlightedChunks={highlightedChunks}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
