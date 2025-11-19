// FILE: services/web-frontend/src/api/documents.ts

import { apiClient } from './client';
import { Document } from '../types';

export const documentsApi = {
  async uploadDocument(file: File, onProgress?: (progress: number) => void): Promise<Document> {
    return apiClient.upload<Document>('/api/documents/upload', file, onProgress);
  },

  async listDocuments(): Promise<Document[]> {
    const response = await apiClient.get<{ documents: Document[]; total: number; page: number; page_size: number }>('/api/documents/');
    return response.documents;
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

  async processDocument(documentId: string): Promise<{ message: string; status: string }> {
    return apiClient.post<{ message: string; status: string }>(
      `/api/documents/${documentId}/process`
    );
  },
};
