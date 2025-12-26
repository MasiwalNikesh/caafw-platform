import axios from 'axios';

// Dynamically determine API URL based on current hostname
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // In browser, use same hostname but port 8000
    const hostname = window.location.hostname;
    return `http://${hostname}:8000`;
  }
  // Server-side fallback
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// Set baseURL dynamically before each request
api.interceptors.request.use((config) => {
  config.baseURL = `${getApiBaseUrl()}/api/v1`;
  return config;
});

// Generic fetch function with error handling
async function fetchAPI<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
  const response = await api.get<T>(endpoint, { params });
  return response.data;
}

// Products API
export const productsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    pricing_type?: string;
    search?: string;
    tag?: string;
  }) => fetchAPI('/products', params),

  get: (id: number) => fetchAPI(`/products/${id}`),

  getBySlug: (slug: string) => fetchAPI(`/products/slug/${slug}`),

  categories: () => fetchAPI<{ id: number; name: string; slug: string; description?: string; icon?: string }[]>('/products/categories'),

  tags: (limit?: number) => fetchAPI<{ name: string; count: number }[]>('/products/tags', { limit }),
};

// Jobs API
export const jobsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    is_remote?: boolean;
    location?: string;
    search?: string;
  }) => fetchAPI('/jobs', params),

  get: (id: number) => fetchAPI(`/jobs/${id}`),
};

// News API
export const newsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    source?: string;
    search?: string;
  }) => fetchAPI('/news', params),

  get: (id: number) => fetchAPI(`/news/${id}`),

  sources: () => fetchAPI('/news/sources'),
};

// Research API
export const researchAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    has_code?: boolean;
    search?: string;
  }) => fetchAPI('/research', params),

  get: (id: number) => fetchAPI(`/research/${id}`),

  categories: () => fetchAPI('/research/categories'),
};

// Learning API
export const learningAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    resource_type?: string;
    level?: string;
    is_free?: boolean;
    search?: string;
  }) => fetchAPI('/learning', params),

  get: (id: number) => fetchAPI(`/learning/${id}`),

  types: () => fetchAPI('/learning/types'),
};

// MCP Servers API
export const mcpAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    is_official?: boolean;
    search?: string;
    tag?: string;
  }) => fetchAPI('/mcp-servers', params),

  get: (id: number) => fetchAPI(`/mcp-servers/${id}`),

  getBySlug: (slug: string) => fetchAPI(`/mcp-servers/slug/${slug}`),

  categories: () => fetchAPI('/mcp-servers/categories'),

  tags: (limit?: number) => fetchAPI<{ name: string; count: number }[]>('/mcp-servers/tags', { limit }),
};

// Community API
export const communityAPI = {
  hackernews: (params?: {
    page?: number;
    page_size?: number;
    search?: string;
  }) => fetchAPI('/community/hackernews', params),

  reddit: (params?: {
    page?: number;
    page_size?: number;
    subreddit?: string;
    search?: string;
  }) => fetchAPI('/community/reddit', params),

  github: (params?: {
    page?: number;
    page_size?: number;
    language?: string;
    search?: string;
  }) => fetchAPI('/community/github', params),

  tweets: (params?: {
    page?: number;
    page_size?: number;
    topic?: string;
    search?: string;
  }) => fetchAPI('/community/tweets', params),

  tweetTopics: () => fetchAPI('/community/tweets/topics/list'),
};

// Events API
export const eventsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    event_type?: string;
    is_online?: boolean;
    city?: string;
    search?: string;
  }) => fetchAPI('/events', params),

  get: (id: number) => fetchAPI(`/events/${id}`),

  types: () => fetchAPI('/events/types'),
};

// Investments API
export const investmentsAPI = {
  companies: (params?: {
    page?: number;
    page_size?: number;
    funding_status?: string;
    country?: string;
    search?: string;
    sort_by?: 'total_funding' | 'last_funding_date' | 'founded_year' | 'created_at';
    sort_order?: 'asc' | 'desc';
  }) => fetchAPI('/investments/companies', params),

  getCompany: (id: number) => fetchAPI(`/investments/companies/${id}`),

  fundingRounds: (params?: {
    page?: number;
    page_size?: number;
    round_type?: string;
  }) => fetchAPI('/investments/funding-rounds', params),
};

// Search API
export const searchAPI = {
  global: (params: {
    q: string;
    types?: string;
    limit?: number;
  }) => fetchAPI('/search', params),
};

// Auth API (used by AuthContext, but exported for direct use if needed)
export const authAPI = {
  register: (data: { email: string; password: string; name?: string }) =>
    api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  me: () => api.get('/auth/me'),

  updateProfile: (data: Record<string, any>) =>
    api.patch('/auth/profile', data),
};

// Quiz API
export const quizAPI = {
  getQuestions: () => fetchAPI<any[]>('/quiz/questions'),

  submit: (answers: { question_id: number; answer: string }[]) =>
    api.post('/quiz/submit', { answers }),

  getResults: () => fetchAPI<any[]>('/quiz/results'),

  getResult: (id: number) => fetchAPI<any>(`/quiz/results/${id}`),
};

// Learning Paths API
export const learningPathsAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    level?: string;
    is_featured?: boolean;
    search?: string;
  }) => fetchAPI('/learning-paths', params),

  get: (id: number) => fetchAPI(`/learning-paths/${id}`),

  recommendations: () => fetchAPI('/learning-paths/recommendations'),

  myProgress: () => fetchAPI('/learning-paths/my-progress'),

  start: (id: number) => api.post(`/learning-paths/${id}/start`),

  updateProgress: (id: number, data: { completed_resource_ids?: number[]; current_resource_id?: number }) =>
    api.patch(`/learning-paths/${id}/progress`, data),

  completeResource: (pathId: number, resourceId: number) =>
    api.post(`/learning-paths/${pathId}/complete-resource/${resourceId}`),

  resetProgress: (id: number) => api.delete(`/learning-paths/${id}/progress`),
};

// Content types for bookmarks
export type BookmarkContentType =
  | 'product'
  | 'job'
  | 'research'
  | 'learning'
  | 'learning_path'
  | 'event'
  | 'mcp_server'
  | 'news'
  | 'hackernews'
  | 'github';

// Bookmarks API
export const bookmarksAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    content_type?: BookmarkContentType;
  }) => fetchAPI('/bookmarks', params),

  create: (data: { content_type: BookmarkContentType; content_id: number; notes?: string }) =>
    api.post('/bookmarks', data),

  check: (contentType: BookmarkContentType, contentId: number) =>
    fetchAPI<{ is_bookmarked: boolean; bookmark_id: number | null }>('/bookmarks/check', {
      content_type: contentType,
      content_id: contentId,
    }),

  update: (id: number, data: { notes?: string }) =>
    api.patch(`/bookmarks/${id}`, data),

  delete: (id: number) => api.delete(`/bookmarks/${id}`),

  deleteByContent: (contentType: BookmarkContentType, contentId: number) =>
    api.delete('/bookmarks/by-content', { params: { content_type: contentType, content_id: contentId } }),
};

// Collections API
export const collectionsAPI = {
  list: (params?: { page?: number; page_size?: number }) =>
    fetchAPI('/collections', params),

  get: (id: number) => fetchAPI(`/collections/${id}`),

  create: (data: { name: string; description?: string; is_public?: boolean; color?: string; icon?: string }) =>
    api.post('/collections', data),

  update: (id: number, data: { name?: string; description?: string; is_public?: boolean; color?: string; icon?: string }) =>
    api.patch(`/collections/${id}`, data),

  delete: (id: number) => api.delete(`/collections/${id}`),

  addItem: (collectionId: number, bookmarkId: number) =>
    api.post(`/collections/${collectionId}/items`, { bookmark_id: bookmarkId }),

  removeItem: (collectionId: number, itemId: number) =>
    api.delete(`/collections/${collectionId}/items/${itemId}`),

  reorderItems: (collectionId: number, itemIds: number[]) =>
    api.post(`/collections/${collectionId}/reorder`, { item_ids: itemIds }),
};
