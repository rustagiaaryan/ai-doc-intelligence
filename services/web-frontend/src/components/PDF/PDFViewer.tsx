// FILE: services/web-frontend/src/components/PDF/PDFViewer.tsx

import React, { useState } from 'react';
import { Document as PDFDocument, Page, pdfjs } from 'react-pdf';
import { DocumentChunk, ChunkPosition } from '../../types';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PDFViewerProps {
  documentUrl: string;
  highlightedChunks?: DocumentChunk[];
  onLoadSuccess?: (numPages: number) => void;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  documentUrl,
  highlightedChunks = [],
  onLoadSuccess,
}) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    if (onLoadSuccess) {
      onLoadSuccess(numPages);
    }
  };

  // Get highlights for current page
  const getHighlightsForPage = (page: number): ChunkPosition[] => {
    return highlightedChunks
      .filter(chunk => chunk.position && chunk.position.page_number === page - 1)
      .map(chunk => chunk.position!)
      .filter(Boolean);
  };

  const renderHighlights = (pageNum: number) => {
    const highlights = getHighlightsForPage(pageNum);

    return highlights.map((highlight, index) => {
      const { bbox, page_width, page_height } = highlight;

      // Calculate percentage-based positioning for responsive scaling
      const left = (bbox.x0 / page_width) * 100;
      const top = (bbox.y0 / page_height) * 100;
      const width = ((bbox.x1 - bbox.x0) / page_width) * 100;
      const height = ((bbox.y1 - bbox.y0) / page_height) * 100;

      return (
        <div
          key={index}
          className="absolute bg-yellow-300 bg-opacity-30 border-2 border-yellow-500 pointer-events-none"
          style={{
            left: `${left}%`,
            top: `${top}%`,
            width: `${width}%`,
            height: `${height}%`,
          }}
        />
      );
    });
  };

  const handlePreviousPage = () => {
    setPageNumber(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setPageNumber(prev => Math.min(prev + 1, numPages));
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.2, 2.0));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.2, 0.5));
  };

  // Jump to page with highlighted chunk
  const jumpToHighlight = () => {
    const firstHighlightedChunk = highlightedChunks.find(chunk => chunk.position);
    if (firstHighlightedChunk?.position) {
      setPageNumber(firstHighlightedChunk.position.page_number + 1);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-100">
      {/* Toolbar */}
      <div className="bg-white border-b p-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={handlePreviousPage}
            disabled={pageNumber <= 1}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-gray-700">
            Page {pageNumber} of {numPages}
          </span>
          <button
            onClick={handleNextPage}
            disabled={pageNumber >= numPages}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleZoomOut}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            -
          </button>
          <span className="text-sm text-gray-700">{Math.round(scale * 100)}%</span>
          <button
            onClick={handleZoomIn}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            +
          </button>
        </div>

        {highlightedChunks.length > 0 && (
          <button
            onClick={jumpToHighlight}
            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            Jump to Highlight
          </button>
        )}
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-auto flex justify-center p-4">
        <div className="relative">
          <PDFDocument
            file={documentUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading PDF...</p>
              </div>
            }
            error={
              <div className="text-center py-8 text-red-600">
                <p>Failed to load PDF.</p>
                <p className="text-sm mt-2">Please check the document URL.</p>
              </div>
            }
          >
            <div className="relative shadow-lg">
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
              {/* Overlay highlights */}
              <div className="absolute inset-0 pointer-events-none">
                {renderHighlights(pageNumber)}
              </div>
            </div>
          </PDFDocument>
        </div>
      </div>

      {/* Highlight Info */}
      {highlightedChunks.length > 0 && (
        <div className="bg-white border-t p-3">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">{highlightedChunks.length}</span> relevant chunk(s) highlighted in yellow
          </p>
        </div>
      )}
    </div>
  );
};
