// FILE: services/web-frontend/src/api/conversations.ts

import { apiClient } from './client';
import { Conversation, ConversationWithMessages } from '../types';

export const conversationsApi = {
  async listConversations(documentId?: string, limit: number = 50, offset: number = 0): Promise<{ conversations: Conversation[]; total: number }> {
    const params = new URLSearchParams();
    if (documentId) params.append('document_id', documentId);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    return apiClient.get<{ conversations: Conversation[]; total: number }>(
      `/api/conversations?${params.toString()}`
    );
  },

  async createConversation(documentId?: string, title?: string): Promise<Conversation> {
    return apiClient.post<Conversation>('/api/conversations', {
      document_id: documentId,
      title,
    });
  },

  async getConversation(conversationId: string): Promise<ConversationWithMessages> {
    return apiClient.get<ConversationWithMessages>(`/api/conversations/${conversationId}`);
  },

  async updateConversation(conversationId: string, title: string): Promise<Conversation> {
    return apiClient.patch<Conversation>(`/api/conversations/${conversationId}`, {
      title,
    });
  },

  async deleteConversation(conversationId: string): Promise<void> {
    return apiClient.delete(`/api/conversations/${conversationId}`);
  },
};
