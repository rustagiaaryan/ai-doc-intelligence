// FILE: services/web-frontend/src/types/index.ts

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_extension: string;
  file_size: number;
  mime_type: string | null;
  s3_key: string;
  s3_bucket: string;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  processing_error: string | null;
  title: string | null;
  description: string | null;
  created_at: string;
  updated_at: string | null;
  processed_at: string | null;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  metadata: Record<string, any>;
  similarity_score?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface AskRequest {
  question: string;
  document_ids?: string[];
  top_k?: number;
  llm_model?: string;
}

export interface AskResponse {
  answer: string;
  retrieved_chunks: DocumentChunk[];
  model_used: string;
  processing_time_ms: number;
}

export interface ApiError {
  detail: string;
}
