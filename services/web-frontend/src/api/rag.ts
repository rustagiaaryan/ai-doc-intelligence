// FILE: services/web-frontend/src/api/rag.ts

import { apiClient } from './client';
import { AskRequest, AskResponse } from '../types';

export const ragApi = {
  async askQuestion(request: AskRequest): Promise<AskResponse> {
    return apiClient.post<AskResponse>('/api/rag/ask', request);
  },
};
