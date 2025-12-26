// Common types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Product types
export interface Product {
  id: number;
  name: string;
  slug: string;
  tagline?: string;
  description?: string;
  source: string;
  website_url?: string;
  logo_url?: string;
  thumbnail_url?: string;
  upvotes: number;
  comments_count: number;
  rating?: number;
  reviews_count: number;
  pricing_type?: string;
  pricing_details?: Record<string, any>;
  is_featured: boolean;
  tags?: string[];
  categories: ProductCategory[];
  launched_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
}

// Job types
export interface Job {
  id: number;
  title: string;
  slug: string;
  description?: string;
  source: string;
  company_name: string;
  company_logo?: string;
  company_url?: string;
  location?: string;
  city?: string;
  state?: string;
  country?: string;
  is_remote: boolean;
  is_hybrid: boolean;
  job_type?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  skills?: string[];
  requirements?: string[];
  benefits?: string[];
  apply_url?: string;
  is_featured: boolean;
  is_active: boolean;
  isRecommended?: boolean;
  posted_at?: string;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

// News types
export interface NewsArticle {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  content?: string;
  source: string;
  author?: string;
  author_url?: string;
  image_url?: string;
  thumbnail_url?: string;
  url: string;
  category?: string;
  tags?: string[];
  views: number;
  shares: number;
  is_featured: boolean;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

// Research types
export interface ResearchPaper {
  id: number;
  title: string;
  slug: string;
  abstract?: string;
  source: string;
  arxiv_id?: string;
  doi?: string;
  pdf_url?: string;
  paper_url: string;
  code_url?: string;
  primary_category?: string;
  categories?: string[];
  citations: number;
  stars: number;
  tasks?: string[];
  methods?: string[];
  datasets?: string[];
  has_code: boolean;
  is_featured: boolean;
  authors: Author[];
  published_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Author {
  id: number;
  name: string;
  affiliation?: string;
}

// Learning types
export interface LearningResource {
  id: number;
  title: string;
  slug: string;
  description?: string;
  source: string;
  resource_type: string;
  provider?: string;
  instructor?: string;
  institution?: string;
  url: string;
  image_url?: string;
  thumbnail_url?: string;
  duration_minutes?: number;
  level?: string;
  language: string;
  is_free: boolean;
  price?: number;
  currency: string;
  rating?: number;
  reviews_count: number;
  enrollments: number;
  topics?: string[];
  skills?: string[];
  is_featured: boolean;
  published_at?: string;
  last_updated?: string;
  created_at: string;
  updated_at: string;
}

// MCP Server types
export interface MCPServer {
  id: number;
  name: string;
  slug: string;
  description?: string;
  short_description?: string;
  source: string;
  category: string;
  tags?: string[];
  repository_url?: string;
  documentation_url?: string;
  npm_url?: string;
  package_name?: string;
  version?: string;
  author?: string;
  install_command?: string;
  config_example?: string;
  capabilities?: string[];
  tools?: string[];
  resources?: string[];
  stars: number;
  downloads: number;
  forks: number;
  is_official: boolean;
  is_verified: boolean;
  is_featured: boolean;
  published_at?: string;
  last_updated?: string;
  created_at: string;
  updated_at: string;
}

// Community types
export interface HackerNewsItem {
  id: number;
  hn_id: number;
  item_type: string;
  title?: string;
  url?: string;
  text?: string;
  author?: string;
  score: number;
  comments_count: number;
  posted_at?: string;
  created_at: string;
}

export interface RedditPost {
  id: number;
  reddit_id: string;
  subreddit: string;
  title: string;
  selftext?: string;
  url?: string;
  author?: string;
  thumbnail?: string;
  is_video: boolean;
  score: number;
  upvote_ratio?: number;
  num_comments: number;
  num_awards: number;
  flair_text?: string;
  posted_at?: string;
  created_at: string;
}

export interface GitHubRepo {
  id: number;
  github_id: number;
  name: string;
  full_name: string;
  description?: string;
  owner: string;
  owner_type: string;
  owner_avatar?: string;
  url: string;
  homepage?: string;
  language?: string;
  topics?: string[];
  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;
  default_branch: string;
  is_fork: boolean;
  is_archived: boolean;
  license_name?: string;
  trending_rank?: number;
  stars_today: number;
  repo_created_at?: string;
  repo_updated_at?: string;
  created_at: string;
}

export interface Tweet {
  id: number;
  tweet_id: string;
  text: string;
  author_id: string;
  author_username: string;
  author_name?: string;
  author_profile_image?: string;
  author_verified: boolean;
  likes: number;
  retweets: number;
  replies: number;
  quotes: number;
  impressions: number;
  has_media: boolean;
  media_urls?: string[];
  topic?: string;
  is_retweet: boolean;
  is_reply: boolean;
  tweeted_at?: string;
  created_at: string;
}

// Event types
export interface Event {
  id: number;
  title: string;
  slug: string;
  description?: string;
  short_description?: string;
  source: string;
  event_type: string;
  organizer_name?: string;
  organizer_url?: string;
  venue_name?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  is_online: boolean;
  online_url?: string;
  url: string;
  registration_url?: string;
  image_url?: string;
  is_free: boolean;
  price_min?: number;
  price_max?: number;
  currency: string;
  capacity?: number;
  attendees_count: number;
  topics?: string[];
  tags?: string[];
  speakers?: any[];
  is_featured: boolean;
  status?: string;
  starts_at?: string;
  ends_at?: string;
  timezone?: string;
  created_at: string;
  updated_at: string;
}

// Investment types
export interface Company {
  id: number;
  name: string;
  slug: string;
  description?: string;
  short_description?: string;
  source: string;
  website_url?: string;
  linkedin_url?: string;
  twitter_url?: string;
  crunchbase_url?: string;
  logo_url?: string;
  headquarters?: string;
  city?: string;
  state?: string;
  country?: string;
  founded_year?: number;
  employee_count?: string;
  company_type?: string;
  industries?: string[];
  categories?: string[];
  total_funding?: number;
  funding_currency: string;
  last_funding_type?: string;
  last_funding_date?: string;
  funding_status?: string;
  ipo_status?: string;
  valuation?: number;
  valuation_date?: string;
  num_investors: number;
  lead_investors?: string[];
  is_ai_company: boolean;
  is_featured: boolean;
  funding_rounds: FundingRound[];
  created_at: string;
  updated_at: string;
}

export interface FundingRound {
  id: number;
  round_type: string;
  round_number?: number;
  amount?: number;
  currency: string;
  pre_money_valuation?: number;
  post_money_valuation?: number;
  lead_investors?: string[];
  investors?: string[];
  num_investors: number;
  announced_at?: string;
  closed_at?: string;
}

// Search types
export interface SearchResult {
  id: number;
  type: string;
  title: string;
  description?: string;
  url?: string;
  image_url?: string;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  by_type: Record<string, number>;
}

// User types
export interface User {
  id: number;
  email: string;
  name?: string;
  avatar_url?: string;
  is_verified: boolean;
  created_at: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  ai_level?: 'novice' | 'beginner' | 'intermediate' | 'expert';
  ai_level_score?: number;
  has_completed_quiz: boolean;
  auto_filter_content: boolean;
  interests?: string[];
  learning_goals?: string[];
}

export interface UserWithProfile extends User {
  profile?: UserProfile;
}

// Quiz types
export interface QuizQuestion {
  id: number;
  question_text: string;
  question_type: 'multiple_choice' | 'self_assessment' | 'multi_select';
  category: string;
  options?: { id: string; text: string }[];
  scale_labels?: Record<string, string>;
  order: number;
}

export interface QuizAnswer {
  question_id: number;
  answer: string;
}

export interface QuizResult {
  id: number;
  total_score: number;
  max_possible_score: number;
  percentage: number;
  computed_level: 'novice' | 'beginner' | 'intermediate' | 'expert';
  category_scores?: Record<string, number>;
  created_at: string;
}

// Learning Path types
export interface LearningPath {
  id: number;
  title: string;
  slug: string;
  description?: string;
  level: 'novice' | 'beginner' | 'intermediate' | 'expert';
  duration_hours?: number;
  topics?: string[];
  resource_ids: number[];
  is_featured: boolean;
  is_active: boolean;
  resource_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface LearningPathDetail extends LearningPath {
  resources: LearningResource[];
  user_progress?: UserLearningProgress;
}

export interface UserLearningProgress {
  id: number;
  user_id: number;
  path_id: number;
  completed_resource_ids: number[];
  current_resource_id?: number;
  progress_percentage: number;
  started_at?: string;
  last_activity_at?: string;
  completed_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PathRecommendation {
  path: LearningPath;
  reason: string;
  match_score: number;
}

export interface RecommendationsResponse {
  recommendations: PathRecommendation[];
  user_level?: string;
}
