'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Bookmark,
  Package,
  Briefcase,
  FileText,
  GraduationCap,
  Route,
  Calendar,
  Server,
  Newspaper,
  MessageSquare,
  Github,
  ExternalLink,
  Trash2,
} from 'lucide-react';
import { bookmarksAPI, BookmarkContentType } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { Pagination } from '@/components/ui/Pagination';
import { FadeIn, StaggeredList, StaggeredItem } from '@/components/ui/animations';

const contentTypeConfig: Record<BookmarkContentType, { label: string; icon: any; color: string; href: (id: number) => string }> = {
  product: { label: 'Products', icon: Package, color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400', href: (id) => `/products` },
  job: { label: 'Jobs', icon: Briefcase, color: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400', href: (id) => `/jobs` },
  research: { label: 'Research', icon: FileText, color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400', href: (id) => `/research` },
  learning: { label: 'Learning', icon: GraduationCap, color: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400', href: (id) => `/learning` },
  learning_path: { label: 'Learning Paths', icon: Route, color: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400', href: (id) => `/learning-paths/${id}` },
  event: { label: 'Events', icon: Calendar, color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400', href: (id) => `/events` },
  mcp_server: { label: 'MCP Servers', icon: Server, color: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400', href: (id) => `/mcp` },
  news: { label: 'News', icon: Newspaper, color: 'bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400', href: (id) => `/news` },
  hackernews: { label: 'Hacker News', icon: MessageSquare, color: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400', href: (id) => `/community` },
  github: { label: 'GitHub', icon: Github, color: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400', href: (id) => `/community` },
};

const contentTypes: (BookmarkContentType | 'all')[] = [
  'all',
  'product',
  'job',
  'research',
  'learning',
  'learning_path',
  'event',
  'mcp_server',
];

export default function BookmarksPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState<BookmarkContentType | 'all'>('all');

  const { data, isLoading, error } = useQuery({
    queryKey: ['bookmarks', page, filter],
    queryFn: () =>
      bookmarksAPI.list({
        page,
        page_size: 20,
        content_type: filter === 'all' ? undefined : filter,
      }),
    enabled: isAuthenticated,
  });

  if (authLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-900">
        <section className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-violet-600 to-purple-700 pt-24 sm:pt-28 pb-16">
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
                <Bookmark className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
                My Bookmarks
              </h1>
            </div>
          </div>
        </section>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
          <ListSkeleton count={6} />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-900">
        <section className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-violet-600 to-purple-700 pt-24 sm:pt-28 pb-16">
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
                <Bookmark className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
                My Bookmarks
              </h1>
            </div>
          </div>
        </section>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 p-8 text-center">
            <Bookmark className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Sign in to view your bookmarks</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Save your favorite content and access it anytime.</p>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-600 to-violet-600 px-6 py-3 text-white font-medium hover:opacity-90 transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-violet-600 to-purple-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-violet-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <FadeIn>
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
                <Bookmark className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
                My Bookmarks
              </h1>
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <p className="text-lg text-purple-100 max-w-2xl">
              Your saved content from across the platform. Quickly access products, jobs, research, and more.
            </p>
          </FadeIn>
          <FadeIn delay={0.2}>
            <div className="mt-6 flex flex-wrap gap-3">
              <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
                {data?.total || 0} Saved Items
              </span>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 p-6 mb-8">
          <div className="flex flex-wrap gap-2">
            {contentTypes.map((type) => {
              const isActive = filter === type;
              if (type === 'all') {
                return (
                  <button
                    key={type}
                    onClick={() => setFilter(type)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    All
                  </button>
                );
              }
              const config = contentTypeConfig[type];
              const Icon = config.icon;
              return (
                <button
                  key={type}
                  onClick={() => setFilter(type)}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {config.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <ListSkeleton count={6} />
        ) : data?.items?.length === 0 ? (
          <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700">
            <Bookmark className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 text-lg">No bookmarks yet</p>
            <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">
              Start saving content you want to revisit later
            </p>
          </div>
        ) : (
          <>
            <StaggeredList className="space-y-4">
              {data?.items?.map((bookmark: any) => (
                <BookmarkCard key={bookmark.id} bookmark={bookmark} />
              ))}
            </StaggeredList>

            {data && data.total_pages > 1 && (
              <div className="mt-8">
                <Pagination
                  currentPage={page}
                  totalPages={data.total_pages}
                  onPageChange={setPage}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function BookmarkCard({ bookmark }: { bookmark: any }) {
  const config = contentTypeConfig[bookmark.content_type as BookmarkContentType];
  const Icon = config?.icon || Bookmark;
  const content = bookmark.content_data || {};

  const title = content.title || content.name || 'Untitled';
  const description = content.description || '';
  const url = content.url;

  return (
    <StaggeredItem>
      <motion.div
        whileHover={{ y: -2 }}
        className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 p-6 hover:shadow-lg transition-all"
      >
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-xl ${config?.color || 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'}`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge size="sm" className={config?.color}>
                    {config?.label || bookmark.content_type}
                  </Badge>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                  {title}
                </h3>
                {content.company_name && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                    {content.company_name}
                  </p>
                )}
              </div>
              {url && (
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-purple-600 dark:text-purple-400 hover:underline text-sm flex-shrink-0"
                >
                  Open <ExternalLink className="h-3.5 w-3.5" />
                </a>
              )}
            </div>
            {description && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {description}
              </p>
            )}
            {bookmark.notes && (
              <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  <span className="font-medium">Note:</span> {bookmark.notes}
                </p>
              </div>
            )}
            <div className="mt-3 flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
              <span>Saved {new Date(bookmark.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </motion.div>
    </StaggeredItem>
  );
}

