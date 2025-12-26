// Admin types

// User roles
export type UserRole = 'user' | 'moderator' | 'admin' | 'super_admin';

// Content moderation status
export type ContentStatus = 'pending' | 'approved' | 'rejected' | 'flagged' | 'archived';

// Content types that can be moderated
export type ContentType = 'news' | 'job' | 'product' | 'event' | 'research';

// Tag
export interface Tag {
  id: number;
  name: string;
  slug: string;
  description?: string;
  is_featured: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface TagCreate {
  name: string;
  description?: string;
  is_featured?: boolean;
}

export interface TagUpdate {
  name?: string;
  description?: string;
  is_featured?: boolean;
}

export interface TagListResponse {
  items: Tag[];
  total: number;
}

// Category
export interface ContentCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  parent_id?: number;
  sort_order: number;
  is_active: boolean;
  children?: ContentCategory[];
  item_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  icon?: string;
  parent_id?: number;
  sort_order?: number;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  icon?: string;
  parent_id?: number;
  sort_order?: number;
  is_active?: boolean;
}

export interface CategoryTreeResponse {
  categories: ContentCategory[];
}

// Content moderation
export interface ModeratableContent {
  id: number;
  content_type: ContentType;
  title: string;
  description?: string;
  source: string;
  moderation_status: ContentStatus;
  reviewed_by_id?: number;
  reviewed_at?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface ModerationAction {
  action: 'approve' | 'reject' | 'flag' | 'archive';
  reason?: string;
}

export interface BulkModerationRequest {
  content_ids: number[];
  content_type: ContentType;
  action: 'approve' | 'reject' | 'flag' | 'archive';
  reason?: string;
}

export interface ContentModerationResponse {
  items: ModeratableContent[];
  total: number;
  page: number;
  page_size: number;
}

export interface ModerationHistoryItem {
  id: number;
  content_type: ContentType;
  content_id: number;
  action: string;
  reason?: string;
  moderator_id: number;
  moderator_name?: string;
  created_at: string;
}

// Admin user management
export interface AdminUser {
  id: number;
  email: string;
  name?: string;
  avatar_url?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  is_banned: boolean;
  banned_reason?: string;
  banned_at?: string;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AdminUserListResponse {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserRoleUpdate {
  role: UserRole;
}

export interface UserBanRequest {
  reason: string;
}

// API Sources
export type SourceType = 'rss' | 'api' | 'scrape';

export interface APISource {
  id: number;
  name: string;
  slug: string;
  source_type: SourceType;
  url: string;
  is_active: boolean;
  requires_api_key: boolean;
  auto_approve: boolean;
  fetch_frequency: number;
  last_fetched_at?: string;
  last_success_at?: string;
  last_error?: string;
  error_count: number;
  items_fetched: number;
  config?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface APISourceCreate {
  name: string;
  source_type: SourceType;
  url: string;
  is_active?: boolean;
  requires_api_key?: boolean;
  auto_approve?: boolean;
  fetch_frequency?: number;
  config?: Record<string, any>;
}

export interface APISourceUpdate {
  name?: string;
  source_type?: SourceType;
  url?: string;
  is_active?: boolean;
  requires_api_key?: boolean;
  auto_approve?: boolean;
  fetch_frequency?: number;
  config?: Record<string, any>;
}

export interface APISourceListResponse {
  items: APISource[];
  total: number;
}

export interface APISourceTestRequest {
  url: string;
  source_type: SourceType;
  config?: Record<string, any>;
}

export interface APISourceTestResponse {
  success: boolean;
  message: string;
  error?: string;
  sample_items?: any[];
}

// Audit Log
export interface AuditLog {
  id: number;
  admin_id: number;
  admin_name?: string;
  admin_email?: string;
  action: string;
  entity_type: string;
  entity_id: number;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  ip_address?: string;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLog[];
  total: number;
  page: number;
  page_size: number;
}

// Dashboard
export interface DashboardStats {
  pending_review: {
    news: number;
    jobs: number;
    products: number;
    events: number;
    research: number;
    total: number;
  };
  total_users: number;
  new_users_today: number;
  new_users_this_week: number;
  total_content: {
    news: number;
    jobs: number;
    products: number;
    events: number;
    research: number;
  };
  api_sources: {
    active: number;
    with_errors: number;
  };
  today_approvals: number;
  today_rejections: number;
}

export interface PendingReviewItem {
  id: number;
  content_type: ContentType;
  title: string;
  source: string;
  created_at: string;
}

export interface RecentActivity {
  id: number;
  admin_name?: string;
  action: string;
  entity_type: string;
  entity_id: number;
  created_at: string;
}

export interface SourceHealth {
  id: number;
  name: string;
  status: 'ok' | 'warning' | 'error';
  last_fetched_at?: string;
  error_count: number;
  last_error?: string;
}

export interface DashboardResponse {
  stats: DashboardStats;
  pending_review: PendingReviewItem[];
  recent_activity: RecentActivity[];
  source_health: SourceHealth[];
}

// Region types
export type RegionType = 'global' | 'continent' | 'country' | 'state' | 'city';

export interface Region {
  id: number;
  code: string;
  name: string;
  slug: string;
  region_type: RegionType;
  parent_id?: number;
  iso_code?: string;
  timezone?: string;
  description?: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface RegionWithChildren extends Region {
  children: RegionWithChildren[];
}

export interface RegionCreate {
  code: string;
  name: string;
  region_type: RegionType;
  parent_id?: number;
  iso_code?: string;
  timezone?: string;
  description?: string;
  is_active?: boolean;
  sort_order?: number;
}

export interface RegionUpdate {
  code?: string;
  name?: string;
  region_type?: RegionType;
  parent_id?: number;
  iso_code?: string;
  timezone?: string;
  description?: string;
  is_active?: boolean;
  sort_order?: number;
}

export interface RegionListResponse {
  items: Region[];
  total: number;
}

export interface RegionTreeResponse {
  regions: RegionWithChildren[];
}

export interface RegionSimple {
  id: number;
  code: string;
  name: string;
  region_type: RegionType;
  slug: string;
}

// Regional Content types
export type RegionalContentType = 'job' | 'event' | 'news' | 'product' | 'research' | 'learning' | 'announcement' | 'other';

export interface RegionalContent {
  id: number;
  region_id: number;
  region: RegionSimple;
  content_type: RegionalContentType;
  title: string;
  slug: string;
  description?: string;
  url?: string;
  image_url?: string;
  data?: Record<string, any>;
  is_active: boolean;
  is_featured: boolean;
  moderation_status: ContentStatus;
  sort_order: number;
  created_by_id?: number;
  updated_by_id?: number;
  created_at: string;
  updated_at: string;
}

export interface RegionalContentCreate {
  region_id: number;
  content_type: RegionalContentType;
  title: string;
  description?: string;
  url?: string;
  image_url?: string;
  data?: Record<string, any>;
  is_active?: boolean;
  is_featured?: boolean;
  sort_order?: number;
}

export interface RegionalContentUpdate {
  region_id?: number;
  content_type?: RegionalContentType;
  title?: string;
  description?: string;
  url?: string;
  image_url?: string;
  data?: Record<string, any>;
  is_active?: boolean;
  is_featured?: boolean;
  sort_order?: number;
}

export interface RegionalContentListResponse {
  items: RegionalContent[];
  total: number;
  page: number;
  page_size: number;
}

export interface RegionalContentBulkCreate {
  items: RegionalContentCreate[];
}

export interface RegionalContentBulkDelete {
  ids: number[];
}

export interface RegionalContentStatusUpdate {
  status: ContentStatus;
  reason?: string;
}

// API Source with Regions
export interface APISourceWithRegions extends APISource {
  regions: RegionSimple[];
}

export interface APISourceRegionAssignment {
  region_ids: number[];
}
