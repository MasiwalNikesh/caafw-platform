'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Server, Star, Download, GitFork, ExternalLink, CheckCircle, Boxes, X } from 'lucide-react';
import { mcpAPI } from '@/lib/api';
import { MCPServer, PaginatedResponse } from '@/types';
import { formatNumber, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function MCPPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string>('');
  const [tagFilter, setTagFilter] = useState<string>('');

  const { data, isLoading } = useQuery<PaginatedResponse<MCPServer>>({
    queryKey: ['mcp-servers', page, search, category, tagFilter],
    queryFn: () =>
      mcpAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        category: category || undefined,
        tag: tagFilter || undefined,
      }),
  });

  const { data: categories } = useQuery<{ value: string; label: string }[]>({
    queryKey: ['mcp-categories'],
    queryFn: () => mcpAPI.categories(),
  });

  const { data: popularTags } = useQuery({
    queryKey: ['mcp-tags'],
    queryFn: () => mcpAPI.tags(15),
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Boxes className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              MCP Servers
            </h1>
          </div>
          <p className="text-lg text-violet-100 max-w-2xl">
            Discover Model Context Protocol servers for AI assistants
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Servers
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Official & Community
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Open Source
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Filters Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex flex-col gap-4">
            {/* Primary filters row */}
            <div className="flex flex-col sm:flex-row gap-4">
              <SearchInput
                value={search}
                onChange={setSearch}
                placeholder="Search MCP servers..."
                className="flex-1 max-w-md"
              />
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Categories</option>
                {categories?.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Tag filter chips */}
            {popularTags && popularTags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-gray-500 py-1">Tags:</span>
                {popularTags.map((tag) => (
                  <button
                    key={tag.name}
                    onClick={() => setTagFilter(tagFilter === tag.name ? '' : tag.name)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                      tagFilter === tag.name
                        ? 'bg-violet-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {tag.name}
                    {tagFilter === tag.name && <X className="inline h-3 w-3 ml-1" />}
                  </button>
                ))}
              </div>
            )}

            {/* Active filters indicator */}
            {(category || tagFilter) && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Active filters:</span>
                {category && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-medium">
                    Category: {categories?.find(c => c.value === category)?.label}
                    <button onClick={() => setCategory('')} className="hover:text-violet-900">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {tagFilter && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-medium">
                    Tag: {tagFilter}
                    <button onClick={() => setTagFilter('')} className="hover:text-violet-900">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                <button
                  onClick={() => {
                    setCategory('');
                    setTagFilter('');
                  }}
                  className="text-xs text-gray-500 hover:text-gray-700 underline"
                >
                  Clear all
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <ListSkeleton count={6} />
        ) : (
          <>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {data?.items.map((server) => (
                <MCPCard key={server.id} server={server} />
              ))}
            </div>

            {data && data.total_pages > 1 && (
              <div className="mt-8">
                <Pagination
                  currentPage={page}
                  totalPages={data.total_pages}
                  onPageChange={setPage}
                />
              </div>
            )}

            {data?.items.length === 0 && (
              <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
                <Boxes className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No MCP servers found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function MCPCard({ server }: { server: MCPServer }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
      <div className="flex items-start gap-3">
        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-violet-100 to-violet-50 flex items-center justify-center">
          <Server className="h-5 w-5 text-violet-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900">{server.name}</h3>
            {server.is_official && (
              <span title="Official"><CheckCircle className="h-4 w-4 text-blue-500" /></span>
            )}
          </div>
          <Badge variant="default" className="mt-1">
            {server.category.replace('_', ' ')}
          </Badge>
        </div>
      </div>

      <p className="mt-4 text-sm text-gray-600 line-clamp-2">
        {truncate(server.short_description || server.description || '', 120)}
      </p>

      {server.tags && server.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {server.tags.slice(0, 4).map((tag) => (
            <span key={tag} className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center gap-3 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            {formatNumber(server.stars)}
          </span>
          {server.downloads > 0 && (
            <span className="flex items-center gap-1">
              <Download className="h-4 w-4" />
              {formatNumber(server.downloads)}
            </span>
          )}
          <span className="flex items-center gap-1">
            <GitFork className="h-4 w-4" />
            {formatNumber(server.forks)}
          </span>
        </div>
        {server.repository_url && (
          <a
            href={server.repository_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-violet-600 to-purple-600 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-violet-500/25"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            GitHub
          </a>
        )}
      </div>
    </div>
  );
}
