import { api } from './api';
import type {
  Tag,
  TagCreate,
  TagUpdate,
  TagListResponse,
  ContentCategory,
  CategoryCreate,
  CategoryUpdate,
  CategoryTreeResponse,
  ContentModerationResponse,
  ModerationAction,
  BulkModerationRequest,
  ModerationHistoryItem,
  AdminUser,
  AdminUserListResponse,
  UserRoleUpdate,
  UserBanRequest,
  APISource,
  APISourceCreate,
  APISourceUpdate,
  APISourceListResponse,
  APISourceTestRequest,
  APISourceTestResponse,
  AuditLogListResponse,
  DashboardResponse,
  ContentType,
  ContentStatus,
  UserRole,
  Region,
  RegionWithChildren,
  RegionCreate,
  RegionUpdate,
  RegionListResponse,
  RegionTreeResponse,
  RegionType,
  RegionalContent,
  RegionalContentCreate,
  RegionalContentUpdate,
  RegionalContentListResponse,
  RegionalContentBulkCreate,
  RegionalContentBulkDelete,
  RegionalContentStatusUpdate,
  RegionalContentType,
} from '@/types/admin';

const ADMIN_BASE = '/admin';

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get<DashboardResponse>(`${ADMIN_BASE}/dashboard/stats`).then(r => r.data),

  getPendingReview: (limit?: number) =>
    api.get(`${ADMIN_BASE}/dashboard/pending-review`, { params: { limit } }).then(r => r.data),

  getRecentActivity: (limit?: number) =>
    api.get(`${ADMIN_BASE}/dashboard/recent-activity`, { params: { limit } }).then(r => r.data),

  getSourceHealth: () =>
    api.get(`${ADMIN_BASE}/dashboard/source-health`).then(r => r.data),
};

// Content Moderation API
export const contentAPI = {
  list: (params?: {
    content_type?: ContentType;
    status?: ContentStatus;
    source?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get<ContentModerationResponse>(`${ADMIN_BASE}/content`, { params }).then(r => r.data),

  approve: (contentType: ContentType, contentId: number) =>
    api.post(`${ADMIN_BASE}/content/${contentType}/${contentId}/approve`).then(r => r.data),

  reject: (contentType: ContentType, contentId: number, reason?: string) =>
    api.post(`${ADMIN_BASE}/content/${contentType}/${contentId}/reject`, { reason }).then(r => r.data),

  flag: (contentType: ContentType, contentId: number, reason?: string) =>
    api.post(`${ADMIN_BASE}/content/${contentType}/${contentId}/flag`, { reason }).then(r => r.data),

  archive: (contentType: ContentType, contentId: number) =>
    api.post(`${ADMIN_BASE}/content/${contentType}/${contentId}/archive`).then(r => r.data),

  bulkAction: (request: BulkModerationRequest) =>
    api.post(`${ADMIN_BASE}/content/bulk`, request).then(r => r.data),

  getHistory: (contentType: ContentType, contentId: number) =>
    api.get<ModerationHistoryItem[]>(`${ADMIN_BASE}/content/${contentType}/${contentId}/history`).then(r => r.data),

  addTag: (contentType: ContentType, contentId: number, tagId: number) =>
    api.post(`${ADMIN_BASE}/content/${contentType}/${contentId}/tags/${tagId}`).then(r => r.data),

  removeTag: (contentType: ContentType, contentId: number, tagId: number) =>
    api.delete(`${ADMIN_BASE}/content/${contentType}/${contentId}/tags/${tagId}`).then(r => r.data),
};

// Tags API
export const tagsAPI = {
  list: (params?: {
    search?: string;
    is_featured?: boolean;
    page?: number;
    page_size?: number;
  }) => api.get<TagListResponse>(`${ADMIN_BASE}/tags`, { params }).then(r => r.data),

  get: (id: number) => api.get<Tag>(`${ADMIN_BASE}/tags/${id}`).then(r => r.data),

  create: (data: TagCreate) => api.post<Tag>(`${ADMIN_BASE}/tags`, data).then(r => r.data),

  update: (id: number, data: TagUpdate) => api.put<Tag>(`${ADMIN_BASE}/tags/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`${ADMIN_BASE}/tags/${id}`).then(r => r.data),

  merge: (sourceIds: number[], targetId: number) =>
    api.post(`${ADMIN_BASE}/tags/merge`, { source_tag_ids: sourceIds, target_tag_id: targetId }).then(r => r.data),

  cleanup: () => api.post(`${ADMIN_BASE}/tags/cleanup`).then(r => r.data),

  suggestions: (contentType: ContentType) =>
    api.get(`${ADMIN_BASE}/tags/suggestions/${contentType}`).then(r => r.data),
};

// Categories API
export const categoriesAPI = {
  list: (params?: {
    parent_id?: number;
    is_active?: boolean;
    flat?: boolean;
  }) => api.get<CategoryTreeResponse>(`${ADMIN_BASE}/categories`, { params }).then(r => r.data),

  get: (id: number) => api.get<ContentCategory>(`${ADMIN_BASE}/categories/${id}`).then(r => r.data),

  create: (data: CategoryCreate) => api.post<ContentCategory>(`${ADMIN_BASE}/categories`, data).then(r => r.data),

  update: (id: number, data: CategoryUpdate) =>
    api.put<ContentCategory>(`${ADMIN_BASE}/categories/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`${ADMIN_BASE}/categories/${id}`).then(r => r.data),

  reorder: (categoryOrders: { id: number; sort_order: number }[]) =>
    api.post(`${ADMIN_BASE}/categories/reorder`, { category_orders: categoryOrders }).then(r => r.data),

  assignContent: (contentType: ContentType, contentId: number, categoryId: number) =>
    api.post(`${ADMIN_BASE}/categories/${categoryId}/content`, {
      content_type: contentType,
      content_id: contentId,
    }).then(r => r.data),

  removeContent: (contentType: ContentType, contentId: number, categoryId: number) =>
    api.delete(`${ADMIN_BASE}/categories/${categoryId}/content/${contentType}/${contentId}`).then(r => r.data),
};

// Users API
export const usersAPI = {
  list: (params?: {
    search?: string;
    role?: UserRole;
    is_active?: boolean;
    is_banned?: boolean;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    page?: number;
    page_size?: number;
  }) => api.get<AdminUserListResponse>(`${ADMIN_BASE}/users`, { params }).then(r => r.data),

  get: (id: number) => api.get<AdminUser>(`${ADMIN_BASE}/users/${id}`).then(r => r.data),

  updateRole: (id: number, data: UserRoleUpdate) =>
    api.patch(`${ADMIN_BASE}/users/${id}/role`, data).then(r => r.data),

  ban: (id: number, data: UserBanRequest) =>
    api.patch(`${ADMIN_BASE}/users/${id}/ban`, data).then(r => r.data),

  unban: (id: number) => api.patch(`${ADMIN_BASE}/users/${id}/unban`).then(r => r.data),

  activate: (id: number) => api.patch(`${ADMIN_BASE}/users/${id}/activate`).then(r => r.data),

  deactivate: (id: number) => api.patch(`${ADMIN_BASE}/users/${id}/deactivate`).then(r => r.data),

  delete: (id: number) => api.delete(`${ADMIN_BASE}/users/${id}`).then(r => r.data),

  getActivity: (id: number, limit?: number) =>
    api.get(`${ADMIN_BASE}/users/${id}/activity`, { params: { limit } }).then(r => r.data),

  getStatsByRole: () => api.get(`${ADMIN_BASE}/users/stats/by-role`).then(r => r.data),
};

// API Sources API
export const sourcesAPI = {
  list: (params?: {
    is_active?: boolean;
    source_type?: 'rss' | 'api' | 'scrape';
  }) => api.get<APISourceListResponse>(`${ADMIN_BASE}/sources`, { params }).then(r => r.data),

  get: (id: number) => api.get<APISource>(`${ADMIN_BASE}/sources/${id}`).then(r => r.data),

  create: (data: APISourceCreate) => api.post<APISource>(`${ADMIN_BASE}/sources`, data).then(r => r.data),

  update: (id: number, data: APISourceUpdate) =>
    api.put<APISource>(`${ADMIN_BASE}/sources/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`${ADMIN_BASE}/sources/${id}`).then(r => r.data),

  toggle: (id: number) => api.patch(`${ADMIN_BASE}/sources/${id}/toggle`).then(r => r.data),

  fetch: (id: number) => api.post(`${ADMIN_BASE}/sources/${id}/fetch`).then(r => r.data),

  resetErrors: (id: number) => api.patch(`${ADMIN_BASE}/sources/${id}/reset-errors`).then(r => r.data),

  test: (data: APISourceTestRequest) =>
    api.post<APISourceTestResponse>(`${ADMIN_BASE}/sources/test`, data).then(r => r.data),

  getSummary: () => api.get(`${ADMIN_BASE}/sources/stats/summary`).then(r => r.data),
};

// Audit Log API
export const auditAPI = {
  list: (params?: {
    admin_id?: number;
    action?: string;
    entity_type?: string;
    entity_id?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }) => api.get<AuditLogListResponse>(`${ADMIN_BASE}/audit-log`, { params }).then(r => r.data),

  get: (id: number) => api.get(`${ADMIN_BASE}/audit-log/${id}`).then(r => r.data),

  getActions: () => api.get(`${ADMIN_BASE}/audit-log/actions`).then(r => r.data),

  getEntityTypes: () => api.get(`${ADMIN_BASE}/audit-log/entity-types`).then(r => r.data),

  getAdminsWithActivity: () => api.get(`${ADMIN_BASE}/audit-log/admins`).then(r => r.data),

  getStats: (days?: number) =>
    api.get(`${ADMIN_BASE}/audit-log/stats`, { params: { days } }).then(r => r.data),
};

// MCP Category type
export type MCPCategory = 'database' | 'cloud' | 'developer_tools' | 'communication' | 'search' | 'productivity' | 'ai_ml' | 'storage' | 'monitoring' | 'other';

// MCP Server Admin types
export interface MCPServerAdmin {
  id: number;
  name: string;
  slug: string;
  description?: string;
  short_description?: string;
  category: MCPCategory;
  tags?: string[];
  repository_url?: string;
  stars: number;
  downloads: number;
  is_official: boolean;
  is_verified: boolean;
  is_featured: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface MCPServerUpdate {
  category?: MCPCategory;
  tags?: string[];
  is_official?: boolean;
  is_verified?: boolean;
  is_featured?: boolean;
  is_active?: boolean;
  short_description?: string;
}

export interface MCPStats {
  total: number;
  by_category: Record<string, number>;
  official_count: number;
  verified_count: number;
  featured_count: number;
  active_count: number;
}

// MCP Servers Admin API
export const mcpAdminAPI = {
  list: (params?: {
    page?: number;
    page_size?: number;
    category?: MCPCategory;
    is_official?: boolean;
    is_verified?: boolean;
    is_featured?: boolean;
    is_active?: boolean;
    search?: string;
    sort_by?: 'created_at' | 'name' | 'stars' | 'downloads';
    sort_order?: 'asc' | 'desc';
  }) => api.get<{ items: MCPServerAdmin[]; total: number; page: number; page_size: number; total_pages: number }>(`${ADMIN_BASE}/mcp`, { params }).then(r => r.data),

  get: (id: number) => api.get<MCPServerAdmin>(`${ADMIN_BASE}/mcp/${id}`).then(r => r.data),

  update: (id: number, data: MCPServerUpdate) =>
    api.patch<MCPServerAdmin>(`${ADMIN_BASE}/mcp/${id}`, data).then(r => r.data),

  verify: (id: number) => api.post(`${ADMIN_BASE}/mcp/${id}/verify`).then(r => r.data),

  unverify: (id: number) => api.post(`${ADMIN_BASE}/mcp/${id}/unverify`).then(r => r.data),

  feature: (id: number) => api.post(`${ADMIN_BASE}/mcp/${id}/feature`).then(r => r.data),

  unfeature: (id: number) => api.post(`${ADMIN_BASE}/mcp/${id}/unfeature`).then(r => r.data),

  activate: (id: number) => api.post(`${ADMIN_BASE}/mcp/${id}/activate`).then(r => r.data),

  deactivate: (id: number) => api.post(`${ADMIN_BASE}/mcp/${id}/deactivate`).then(r => r.data),

  getStats: () => api.get<MCPStats>(`${ADMIN_BASE}/mcp/stats`).then(r => r.data),

  bulkAction: (serverIds: number[], action: 'verify' | 'unverify' | 'feature' | 'unfeature' | 'activate' | 'deactivate') =>
    api.post(`${ADMIN_BASE}/mcp/bulk-action`, { server_ids: serverIds, action }).then(r => r.data),
};

// Regions API
export const regionsAPI = {
  list: (params?: {
    region_type?: RegionType;
    parent_id?: number;
    is_active?: boolean;
  }) => api.get<RegionListResponse>(`${ADMIN_BASE}/regions`, { params }).then(r => r.data),

  getTree: (params?: { is_active?: boolean }) =>
    api.get<RegionTreeResponse>(`${ADMIN_BASE}/regions/tree`, { params }).then(r => r.data),

  get: (id: number) => api.get<RegionWithChildren>(`${ADMIN_BASE}/regions/${id}`).then(r => r.data),

  create: (data: RegionCreate) => api.post<Region>(`${ADMIN_BASE}/regions`, data).then(r => r.data),

  update: (id: number, data: RegionUpdate) =>
    api.put<Region>(`${ADMIN_BASE}/regions/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`${ADMIN_BASE}/regions/${id}`).then(r => r.data),

  toggle: (id: number) => api.patch(`${ADMIN_BASE}/regions/${id}/toggle`).then(r => r.data),
};

// Regional Content API
export const regionalContentAPI = {
  list: (params?: {
    region_id?: number;
    content_type?: RegionalContentType;
    moderation_status?: ContentStatus;
    is_active?: boolean;
    is_featured?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get<RegionalContentListResponse>(`${ADMIN_BASE}/regional-content`, { params }).then(r => r.data),

  get: (id: number) => api.get<RegionalContent>(`${ADMIN_BASE}/regional-content/${id}`).then(r => r.data),

  create: (data: RegionalContentCreate) =>
    api.post<RegionalContent>(`${ADMIN_BASE}/regional-content`, data).then(r => r.data),

  update: (id: number, data: RegionalContentUpdate) =>
    api.put<RegionalContent>(`${ADMIN_BASE}/regional-content/${id}`, data).then(r => r.data),

  delete: (id: number) => api.delete(`${ADMIN_BASE}/regional-content/${id}`).then(r => r.data),

  bulkCreate: (data: RegionalContentBulkCreate) =>
    api.post(`${ADMIN_BASE}/regional-content/bulk`, data).then(r => r.data),

  bulkDelete: (data: RegionalContentBulkDelete) =>
    api.delete(`${ADMIN_BASE}/regional-content/bulk`, { data }).then(r => r.data),

  updateStatus: (id: number, data: RegionalContentStatusUpdate) =>
    api.patch(`${ADMIN_BASE}/regional-content/${id}/status`, data).then(r => r.data),

  duplicate: (id: number, targetRegionId: number) =>
    api.post(`${ADMIN_BASE}/regional-content/${id}/duplicate`, null, { params: { target_region_id: targetRegionId } }).then(r => r.data),

  exportCsv: (params?: { region_id?: number; content_type?: RegionalContentType }) =>
    api.get(`${ADMIN_BASE}/regional-content/export/csv`, { params, responseType: 'blob' }).then(r => r.data),
};
