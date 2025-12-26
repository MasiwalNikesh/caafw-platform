# Admin Dashboard - Implementation Plan

## Overview

A comprehensive admin dashboard for managing the AI Community Platform, including content moderation, user management, and system configuration.

---

## 1. Database Schema Changes

### 1.1 User Roles & Permissions

```sql
-- User roles enum
CREATE TYPE user_role AS ENUM ('user', 'moderator', 'admin', 'super_admin');

-- Add role to users table
ALTER TABLE users ADD COLUMN role user_role DEFAULT 'user';
ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN banned_reason TEXT;
ALTER TABLE users ADD COLUMN banned_at TIMESTAMP;
ALTER TABLE users ADD COLUMN banned_by INTEGER REFERENCES users(id);
```

### 1.2 Content Moderation

```sql
-- Content status for all content types
CREATE TYPE content_status AS ENUM (
    'pending',      -- Awaiting review
    'approved',     -- Verified and published
    'rejected',     -- Rejected by admin
    'flagged',      -- Flagged for review
    'archived'      -- Removed from public view
);

-- Add moderation fields to existing tables
ALTER TABLE news_articles ADD COLUMN status content_status DEFAULT 'pending';
ALTER TABLE news_articles ADD COLUMN reviewed_by INTEGER REFERENCES users(id);
ALTER TABLE news_articles ADD COLUMN reviewed_at TIMESTAMP;
ALTER TABLE news_articles ADD COLUMN rejection_reason TEXT;

ALTER TABLE research_papers ADD COLUMN status content_status DEFAULT 'approved'; -- Auto-approve arXiv
ALTER TABLE jobs ADD COLUMN status content_status DEFAULT 'pending';
ALTER TABLE products ADD COLUMN status content_status DEFAULT 'pending';
ALTER TABLE events ADD COLUMN status content_status DEFAULT 'pending';
```

### 1.3 Tags & Categories

```sql
-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    icon VARCHAR(50),
    color VARCHAR(7),  -- Hex color
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7),
    usage_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content-Tag relationships (polymorphic)
CREATE TABLE content_tags (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,  -- 'news', 'research', 'job', 'product', 'event'
    content_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tag_id, content_type, content_id)
);

-- Content-Category relationships
CREATE TABLE content_categories (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,
    content_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(category_id, content_type, content_id)
);
```

### 1.4 Audit Log

```sql
-- Admin action audit log
CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_log_admin ON admin_audit_log(admin_id);
CREATE INDEX idx_audit_log_entity ON admin_audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created ON admin_audit_log(created_at);
```

### 1.5 API Source Configuration

```sql
-- API sources configuration (admin-managed)
CREATE TABLE api_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL,  -- 'rss', 'api', 'scrape'
    url VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    requires_api_key BOOLEAN DEFAULT FALSE,
    auto_approve BOOLEAN DEFAULT FALSE,  -- Trust level
    fetch_frequency INTEGER DEFAULT 360,  -- Minutes
    last_fetched_at TIMESTAMP,
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    config JSONB,  -- Additional configuration
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. Backend API Endpoints

### 2.1 Authentication & Authorization

```
POST   /api/admin/login              # Admin login
POST   /api/admin/logout             # Admin logout
GET    /api/admin/me                 # Current admin info
POST   /api/admin/refresh-token      # Refresh JWT
```

### 2.2 Dashboard Overview

```
GET    /api/admin/dashboard/stats           # Overview statistics
GET    /api/admin/dashboard/recent-activity # Recent admin actions
GET    /api/admin/dashboard/pending-review  # Items needing review
GET    /api/admin/dashboard/system-health   # API source status
```

### 2.3 Content Moderation

```
# News
GET    /api/admin/news                      # List with filters
GET    /api/admin/news/:id                  # Single article
PATCH  /api/admin/news/:id/approve          # Approve
PATCH  /api/admin/news/:id/reject           # Reject with reason
PATCH  /api/admin/news/:id/flag             # Flag for review
DELETE /api/admin/news/:id                  # Soft delete

# Research Papers
GET    /api/admin/research                  # List papers
PATCH  /api/admin/research/:id/status       # Update status

# Jobs
GET    /api/admin/jobs                      # List jobs
PATCH  /api/admin/jobs/:id/approve          # Approve job
PATCH  /api/admin/jobs/:id/reject           # Reject job

# Products
GET    /api/admin/products                  # List products
PATCH  /api/admin/products/:id/approve      # Approve product

# Events
GET    /api/admin/events                    # List events
PATCH  /api/admin/events/:id/approve        # Approve event

# Bulk operations
POST   /api/admin/content/bulk-approve      # Bulk approve
POST   /api/admin/content/bulk-reject       # Bulk reject
```

### 2.4 Tags & Categories

```
# Categories
GET    /api/admin/categories                # List all
POST   /api/admin/categories                # Create
PUT    /api/admin/categories/:id            # Update
DELETE /api/admin/categories/:id            # Delete
PATCH  /api/admin/categories/:id/reorder    # Change order

# Tags
GET    /api/admin/tags                      # List all
POST   /api/admin/tags                      # Create
PUT    /api/admin/tags/:id                  # Update
DELETE /api/admin/tags/:id                  # Delete
POST   /api/admin/tags/merge                # Merge tags
GET    /api/admin/tags/suggestions          # AI-suggested tags

# Assign tags/categories to content
POST   /api/admin/content/:type/:id/tags         # Add tags
DELETE /api/admin/content/:type/:id/tags/:tagId  # Remove tag
POST   /api/admin/content/:type/:id/categories   # Set categories
```

### 2.5 User Management

```
GET    /api/admin/users                     # List users
GET    /api/admin/users/:id                 # User details
PATCH  /api/admin/users/:id                 # Update user
PATCH  /api/admin/users/:id/role            # Change role
PATCH  /api/admin/users/:id/ban             # Ban user
PATCH  /api/admin/users/:id/unban           # Unban user
DELETE /api/admin/users/:id                 # Delete user
GET    /api/admin/users/:id/activity        # User activity log
```

### 2.6 API Sources Management

```
GET    /api/admin/sources                   # List all sources
POST   /api/admin/sources                   # Add new source
PUT    /api/admin/sources/:id               # Update source
DELETE /api/admin/sources/:id               # Remove source
PATCH  /api/admin/sources/:id/toggle        # Enable/disable
POST   /api/admin/sources/:id/fetch         # Manual fetch
GET    /api/admin/sources/:id/logs          # Fetch logs
POST   /api/admin/sources/test              # Test new source
```

### 2.7 System & Settings

```
GET    /api/admin/settings                  # All settings
PUT    /api/admin/settings                  # Update settings
GET    /api/admin/audit-log                 # Audit log
GET    /api/admin/analytics                 # Platform analytics
POST   /api/admin/cache/clear               # Clear cache
GET    /api/admin/system/health             # System health check
```

---

## 3. Frontend Structure

### 3.1 File Structure

```
frontend/
├── app/
│   └── admin/
│       ├── layout.tsx              # Admin layout with sidebar
│       ├── page.tsx                # Dashboard overview
│       ├── login/
│       │   └── page.tsx            # Admin login
│       ├── content/
│       │   ├── page.tsx            # Content moderation queue
│       │   ├── news/
│       │   │   └── page.tsx        # News management
│       │   ├── research/
│       │   │   └── page.tsx        # Research papers
│       │   ├── jobs/
│       │   │   └── page.tsx        # Jobs management
│       │   ├── products/
│       │   │   └── page.tsx        # Products management
│       │   └── events/
│       │       └── page.tsx        # Events management
│       ├── taxonomy/
│       │   ├── categories/
│       │   │   └── page.tsx        # Categories management
│       │   └── tags/
│       │       └── page.tsx        # Tags management
│       ├── users/
│       │   ├── page.tsx            # User list
│       │   └── [id]/
│       │       └── page.tsx        # User details
│       ├── sources/
│       │   └── page.tsx            # API sources management
│       ├── settings/
│       │   └── page.tsx            # System settings
│       └── audit-log/
│           └── page.tsx            # Audit log viewer
├── components/
│   └── admin/
│       ├── Sidebar.tsx             # Admin navigation
│       ├── Header.tsx              # Admin header
│       ├── StatsCard.tsx           # Dashboard stat card
│       ├── ContentTable.tsx        # Reusable content table
│       ├── ModerationActions.tsx   # Approve/reject buttons
│       ├── TagSelector.tsx         # Tag picker component
│       ├── CategoryTree.tsx        # Category tree view
│       ├── UserCard.tsx            # User info card
│       ├── SourceStatus.tsx        # API source status
│       ├── AuditLogEntry.tsx       # Audit log entry
│       └── FilterBar.tsx           # Content filters
└── lib/
    └── admin/
        ├── api.ts                  # Admin API client
        ├── hooks.ts                # Admin-specific hooks
        └── types.ts                # Admin types
```

### 3.2 Dashboard Overview Page

```
┌─────────────────────────────────────────────────────────────────┐
│  Admin Dashboard                                    [Admin Name] │
├────────┬────────────────────────────────────────────────────────┤
│        │                                                        │
│  MENU  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│        │   │ Pending  │ │ Users    │ │ Content  │ │ Sources  │ │
│ Dashboard  │   47     │ │  1,234   │ │  5,678   │ │  12/15   │ │
│ Content │   └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│ Users   │                                                        │
│ Sources │   PENDING REVIEW                          [View All]   │
│ Tags    │   ┌────────────────────────────────────────────────┐  │
│ Settings│   │ [News] New GPT-5 Announcement - TechCrunch     │  │
│ Audit   │   │ [Job] ML Engineer at Startup X                 │  │
│         │   │ [Event] AI Conference 2025                     │  │
│         │   └────────────────────────────────────────────────┘  │
│         │                                                        │
│         │   API SOURCE STATUS                                    │
│         │   ┌────────────────────────────────────────────────┐  │
│         │   │ ● arXiv          Last fetch: 2h ago     [OK]   │  │
│         │   │ ● HackerNews     Last fetch: 1h ago     [OK]   │  │
│         │   │ ○ Twitter        Error: Rate limited   [WARN]  │  │
│         │   └────────────────────────────────────────────────┘  │
└────────┴────────────────────────────────────────────────────────┘
```

### 3.3 Content Moderation Page

```
┌─────────────────────────────────────────────────────────────────┐
│  Content Moderation                                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [All] [Pending: 47] [Approved] [Rejected] [Flagged]            │
│                                                                  │
│  Type: [All ▼]  Source: [All ▼]  Date: [Last 7 days ▼]  🔍     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ☐ │ NEWS │ OpenAI Releases GPT-5         │ TechCrunch    │   │
│  │   │      │ 2 hours ago                    │ [PENDING]     │   │
│  │   │      │ Tags: [LLM] [OpenAI]          │               │   │
│  │   │      │                    [✓ Approve] [✗ Reject] [👁] │   │
│  ├───┼──────┼────────────────────────────────┼───────────────┤   │
│  │ ☐ │ JOB  │ Senior ML Engineer             │ Greenhouse    │   │
│  │   │      │ Anthropic - San Francisco      │ [PENDING]     │   │
│  │   │      │ Tags: [Jobs] [ML]             │               │   │
│  │   │      │                    [✓ Approve] [✗ Reject] [👁] │   │
│  └───┴──────┴────────────────────────────────┴───────────────┘   │
│                                                                  │
│  [Bulk: Approve Selected] [Reject Selected]      Page 1 of 5    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.4 Tags & Categories Page

```
┌─────────────────────────────────────────────────────────────────┐
│  Tags & Categories                                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CATEGORIES                                    [+ Add Category]  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ▼ Machine Learning (234 items)              [Edit] [Delete]│ │
│  │   ├─ Deep Learning (89)                                    │ │
│  │   ├─ NLP (67)                                              │ │
│  │   └─ Computer Vision (45)                                  │ │
│  │ ▼ AI Tools (156 items)                                     │ │
│  │   ├─ LLM Apps (78)                                         │ │
│  │   └─ Developer Tools (45)                                  │ │
│  │ ▶ Research (890 items)                                     │ │
│  │ ▶ Career (234 items)                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  TAGS                                               [+ Add Tag]  │
│  🔍 Search tags...                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ [LLM] 456 uses  [GPT] 234 uses  [Transformer] 189 uses    │ │
│  │ [PyTorch] 167 uses  [OpenAI] 145 uses  [RAG] 123 uses     │ │
│  │ [Fine-tuning] 98 uses  [Anthropic] 87 uses  [CUDA] 76     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Merge Tags]  [Delete Unused]  [Auto-suggest from AI]          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Tasks

### Phase 1: Foundation (Backend)

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 1.1 | Create database migrations for new tables | High | - |
| 1.2 | Add `role` field to User model | High | - |
| 1.3 | Create Category, Tag, ContentTag models | High | - |
| 1.4 | Create AuditLog model | Medium | - |
| 1.5 | Create APISource model | Medium | - |
| 1.6 | Add `status` fields to content models | High | - |
| 1.7 | Create admin authentication middleware | High | - |
| 1.8 | Create role-based permission decorators | High | - |

### Phase 2: Admin APIs (Backend)

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 2.1 | Create `/api/admin/dashboard` endpoints | High | - |
| 2.2 | Create content moderation endpoints | High | - |
| 2.3 | Create tag CRUD endpoints | High | - |
| 2.4 | Create category CRUD endpoints | High | - |
| 2.5 | Create user management endpoints | High | - |
| 2.6 | Create API source management endpoints | Medium | - |
| 2.7 | Create audit log endpoints | Medium | - |
| 2.8 | Add bulk operations support | Medium | - |

### Phase 3: Admin Frontend

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 3.1 | Create admin layout with sidebar | High | - |
| 3.2 | Create admin login page | High | - |
| 3.3 | Create dashboard overview page | High | - |
| 3.4 | Create content moderation table | High | - |
| 3.5 | Create moderation action components | High | - |
| 3.6 | Create tag management page | High | - |
| 3.7 | Create category tree component | High | - |
| 3.8 | Create user management page | Medium | - |
| 3.9 | Create API source status page | Medium | - |
| 3.10 | Create audit log viewer | Low | - |
| 3.11 | Create settings page | Low | - |

### Phase 4: Enhancements

| # | Task | Priority | Estimate |
|---|------|----------|----------|
| 4.1 | Add keyboard shortcuts for moderation | Low | - |
| 4.2 | Add real-time updates (WebSocket) | Low | - |
| 4.3 | Add AI-powered tag suggestions | Low | - |
| 4.4 | Add export functionality | Low | - |
| 4.5 | Add email notifications for admins | Low | - |

---

## 5. User Roles & Permissions

### Role Hierarchy

| Role | Level | Description |
|------|-------|-------------|
| `user` | 0 | Regular platform user |
| `moderator` | 1 | Can review and approve content |
| `admin` | 2 | Full content + user management |
| `super_admin` | 3 | System settings + role assignment |

### Permission Matrix

| Action | User | Moderator | Admin | Super Admin |
|--------|------|-----------|-------|-------------|
| View public content | ✓ | ✓ | ✓ | ✓ |
| Submit content | ✓ | ✓ | ✓ | ✓ |
| View pending content | ✗ | ✓ | ✓ | ✓ |
| Approve/Reject content | ✗ | ✓ | ✓ | ✓ |
| Manage tags | ✗ | ✓ | ✓ | ✓ |
| Manage categories | ✗ | ✗ | ✓ | ✓ |
| View user list | ✗ | ✗ | ✓ | ✓ |
| Ban/Unban users | ✗ | ✗ | ✓ | ✓ |
| Change user roles | ✗ | ✗ | ✗ | ✓ |
| Manage API sources | ✗ | ✗ | ✓ | ✓ |
| View audit log | ✗ | ✗ | ✓ | ✓ |
| System settings | ✗ | ✗ | ✗ | ✓ |

---

## 6. Content Moderation Workflow

```
┌─────────────┐
│ API Fetch   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐     auto_approve=true     ┌───────────┐
│ New Content     │ ─────────────────────────▶│ APPROVED  │
└────────┬────────┘                           └───────────┘
         │ auto_approve=false
         ▼
┌─────────────────┐
│ PENDING REVIEW  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌────────┐
│APPROVE│  │ REJECT │
└───┬───┘  └───┬────┘
    │          │
    ▼          ▼
┌───────────┐  ┌────────────┐
│ APPROVED  │  │ REJECTED   │
│ (visible) │  │ (hidden)   │
└───────────┘  └────────────┘
```

### Auto-Approve Rules

| Source | Auto-Approve | Reason |
|--------|--------------|--------|
| arXiv | Yes | Peer-reviewed research |
| Company blogs (OpenAI, etc.) | Yes | Official sources |
| HackerNews | Yes | Community vetted |
| Greenhouse/Lever Jobs | Yes | Real job postings |
| User submissions | No | Requires review |
| Unknown RSS feeds | No | Requires review |

---

## 7. Technical Notes

### Authentication

- Use JWT tokens with short expiry (15 min)
- Separate admin JWT from user JWT
- Store refresh tokens securely
- Log all admin authentication events

### Caching Strategy

- Cache dashboard stats (5 min TTL)
- Cache category tree (1 hour TTL)
- Cache tag cloud (30 min TTL)
- Invalidate on write operations

### Security Considerations

- Rate limit admin endpoints
- IP allowlist for admin access (optional)
- Two-factor authentication (Phase 2)
- Session invalidation on role change
- Audit log for all destructive actions

---

## 8. API Response Examples

### Dashboard Stats

```json
{
  "pending_review": 47,
  "total_users": 1234,
  "total_content": 5678,
  "active_sources": 12,
  "failed_sources": 3,
  "today_approvals": 23,
  "today_rejections": 5
}
```

### Content Item

```json
{
  "id": 123,
  "type": "news",
  "title": "OpenAI Releases GPT-5",
  "source": "techcrunch",
  "status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "tags": [
    {"id": 1, "name": "LLM", "slug": "llm"},
    {"id": 2, "name": "OpenAI", "slug": "openai"}
  ],
  "categories": [
    {"id": 1, "name": "AI News", "slug": "ai-news"}
  ],
  "reviewed_by": null,
  "reviewed_at": null
}
```
