// FILE: services/web-frontend/src/api/documents.ts

import { apiClient } from './client';
import { Document } from '../types';

export const documentsApi = {
  async uploadDocument(file: File, onProgress?: (progress: number) => void): Promise<Document> {
    return apiClient.upload<Document>('/api/documents/upload', file, onProgress);
  },

  async listDocuments(): Promise<Document[]> {
    return apiClient.get<Document[]>('/api/documents/');
  },

  async getDocument(documentId: string): Promise<Document> {
    return apiClient.get<Document>(`/api/documents/${documentId}`);
  },

  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/api/documents/${documentId}`);
  },

  async getDownloadUrl(documentId: string): Promise<{ download_url: string }> {
    return apiClient.get<{ download_url: string }>(`/api/documents/${documentId}/download`);
  },

  async processDocument(documentId: string): Promise<{ message: string; chunks_created: number }> {
    return apiClient.post<{ message: string; chunks_created: number }>(
      '/api/process/document',
      { document_id: documentId }
    );
  },
};
