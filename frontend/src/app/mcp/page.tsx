'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Server, Star, Download, GitFork, ExternalLink, CheckCircle } from 'lucide-react';
import { mcpAPI } from '@/lib/api';
import { MCPServer, PaginatedResponse } from '@/types';
import { formatNumber, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function MCPPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string>('');

  const { data, isLoading } = useQuery<PaginatedResponse<MCPServer>>({
    queryKey: ['mcp-servers', page, search, category],
    queryFn: () =>
      mcpAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        category: category || undefined,
      }),
  });

  const { data: categories } = useQuery<{ value: string; label: string }[]>({
    queryKey: ['mcp-categories'],
    queryFn: () => mcpAPI.categories(),
  });

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">MCP Servers</h1>
        <p className="mt-2 text-gray-600">
          Discover Model Context Protocol servers for AI assistants
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search MCP servers..."
          className="flex-1 max-w-md"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">All Categories</option>
          {categories?.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
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
            <div className="text-center py-12">
              <p className="text-gray-500">No MCP servers found</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function MCPCard({ server }: { server: MCPServer }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="h-10 w-10 rounded-lg bg-pink-100 flex items-center justify-center">
            <Server className="h-5 w-5 text-pink-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base">{server.name}</CardTitle>
              {server.is_official && (
                <CheckCircle className="h-4 w-4 text-blue-500" title="Official" />
              )}
            </div>
            <Badge variant="default" className="mt-1">
              {server.category.replace('_', ' ')}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardDescription>
        {truncate(server.short_description || server.description || '', 120)}
      </CardDescription>

      {server.tags && server.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {server.tags.slice(0, 4).map((tag) => (
            <Badge key={tag} size="sm">
              {tag}
            </Badge>
          ))}
        </div>
      )}

      <CardFooter className="text-sm text-gray-500">
        <div className="flex items-center gap-3">
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
            className="flex items-center gap-1 text-indigo-600 hover:text-indigo-500"
          >
            <ExternalLink className="h-4 w-4" />
            GitHub
          </a>
        )}
      </CardFooter>
    </Card>
  );
}
