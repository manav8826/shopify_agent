import axios from 'axios';

// Create axios instance with base URL
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Standardize error message extraction
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    console.error('API Error:', message);
    return Promise.reject(new Error(message));
  }
);

export interface SessionResponse {
  session_id: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  tables?: any[];
  thought_process?: string;
}

export interface HistoryMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const api = {
  healthCheck: () => client.get('/health'),

  createSession: (storeUrl: string) =>
    client.post<SessionResponse>('/sessions', { store_url: storeUrl }),

  chat: (sessionId: string, message: string) =>
    client.post<ChatResponse>('/chat', { session_id: sessionId, message }),

  getHistory: (sessionId: string) =>
    client.get<HistoryMessage[]>(`/sessions/${sessionId}/history`),

  listSessions: () =>
    client.get<any[]>('/sessions'),

  deleteSession: (sessionId: string) =>
    client.delete(`/sessions/${sessionId}`),
};

export default api;
