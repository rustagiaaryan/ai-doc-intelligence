// FILE: services/web-frontend/src/pages/Chat.tsx

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { documentsApi } from '../api/documents';
import { ragApi } from '../api/rag';
import { Document, ChatMessage, DocumentChunk } from '../types';

const Chat: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [retrievedChunks, setRetrievedChunks] = useState<DocumentChunk[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadDocuments = async () => {
    try {
      const docs = await documentsApi.listDocuments();
      const completedDocs = docs.filter(doc => doc.status === 'completed');
      setDocuments(completedDocs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleDocumentToggle = (docId: string) => {
    setSelectedDocuments(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await ragApi.askQuestion({
        question: inputValue,
        document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
        top_k: 5,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setRetrievedChunks(response.retrieved_chunks);
    } catch (err: any) {
      console.error('Failed to get answer:', err);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${err.response?.data?.detail || 'Failed to get answer. Please try again.'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Ask Questions</h1>
              {user && (
                <p className="text-sm text-gray-600 mt-1">
                  Chat with your documents using AI
                </p>
              )}
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                Dashboard
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar - Document Selection */}
        <aside className="w-64 bg-white shadow-sm p-4 overflow-y-auto">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Filter by Documents</h2>

          {documents.length === 0 ? (
            <p className="text-sm text-gray-500">No processed documents available</p>
          ) : (
            <div className="space-y-2">
              {documents.map(doc => (
                <label
                  key={doc.id}
                  className="flex items-start space-x-2 p-2 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedDocuments.includes(doc.id)}
                    onChange={() => handleDocumentToggle(doc.id)}
                    className="mt-1 rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 break-words">{doc.filename}</span>
                </label>
              ))}
            </div>
          )}

          {selectedDocuments.length === 0 && documents.length > 0 && (
            <p className="text-xs text-gray-500 mt-4 p-2 bg-blue-50 rounded">
              No documents selected. Questions will search all documents.
            </p>
          )}
        </aside>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">Start a conversation</h3>
                <p className="mt-2 text-gray-600">Ask questions about your documents</p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl px-4 py-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white shadow text-gray-900'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p
                      className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-3xl px-4 py-3 rounded-lg bg-white shadow">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Retrieved Chunks Panel */}
          {retrievedChunks.length > 0 && (
            <div className="border-t bg-gray-50 p-4">
              <details className="group">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700 hover:text-gray-900">
                  View Source Chunks ({retrievedChunks.length})
                </summary>
                <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
                  {retrievedChunks.map((chunk, index) => (
                    <div key={chunk.id} className="bg-white p-3 rounded border text-sm">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-medium text-gray-500">Chunk {chunk.chunk_index + 1}</span>
                        {chunk.similarity_score && (
                          <span className="text-xs text-blue-600">
                            {(chunk.similarity_score * 100).toFixed(1)}% match
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700 text-xs line-clamp-3">{chunk.content}</p>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t bg-white p-4">
            <div className="max-w-4xl mx-auto flex space-x-4">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                rows={3}
                disabled={isLoading || documents.length === 0}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim() || documents.length === 0}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            {documents.length === 0 && (
              <p className="text-center text-sm text-gray-500 mt-2">
                No processed documents available. Please upload and process documents first.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
