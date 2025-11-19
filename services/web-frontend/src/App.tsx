import React from 'react';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Document Intelligence Platform
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Welcome!</h2>
          <p className="text-gray-600 mb-4">
            Your AI-powered document intelligence platform is ready.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            {/* Feature 1 */}
            <div className="border rounded-lg p-4">
              <div className="text-4xl mb-2">📄</div>
              <h3 className="font-semibold mb-2">Upload Documents</h3>
              <p className="text-sm text-gray-600">
                Upload PDF, DOCX, TXT, and MD files for processing
              </p>
            </div>

            {/* Feature 2 */}
            <div className="border rounded-lg p-4">
              <div className="text-4xl mb-2">🧠</div>
              <h3 className="font-semibold mb-2">AI Processing</h3>
              <p className="text-sm text-gray-600">
                Automatic text extraction, chunking, and embedding generation
              </p>
            </div>

            {/* Feature 3 */}
            <div className="border rounded-lg p-4">
              <div className="text-4xl mb-2">💬</div>
              <h3 className="font-semibold mb-2">Ask Questions</h3>
              <p className="text-sm text-gray-600">
                Get AI-powered answers with source citations
              </p>
            </div>
          </div>
        </div>

        {/* Status Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 text-blue-900">Backend Services Status</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span>Auth Service - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span>Document Service - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span>LLM Proxy - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span>Ingestion Worker - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span>RAG Service - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span>API Gateway - Ready</span>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> To use the full platform, configure Google OAuth credentials in the Auth Service.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
