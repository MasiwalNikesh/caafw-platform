'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Cpu, Briefcase, FileText, BookOpen, Server } from 'lucide-react';
import { searchAPI } from '@/lib/api';
import { SearchResponse } from '@/types';
import { truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';

const typeIcons: Record<string, React.ElementType> = {
  product: Cpu,
  job: Briefcase,
  news: FileText,
  research: FileText,
  mcp: Server,
};

const typeLabels: Record<string, string> = {
  product: 'Product',
  job: 'Job',
  news: 'News',
  research: 'Research',
  mcp: 'MCP Server',
};

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const handleSearch = (value: string) => {
    setQuery(value);
    // Simple debounce
    setTimeout(() => setDebouncedQuery(value), 300);
  };

  const { data, isLoading } = useQuery<SearchResponse>({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchAPI.global({ q: debouncedQuery, limit: 50 }),
    enabled: debouncedQuery.length >= 2,
  });

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">Search</h1>
        <p className="mt-2 text-gray-600">
          Search across products, jobs, research, and more
        </p>
      </div>

      {/* Search Input */}
      <div className="relative mb-8">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search for anything..."
          className="w-full pl-12 pr-4 py-4 rounded-xl border border-gray-300 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          autoFocus
        />
      </div>

      {/* Results Summary */}
      {data && debouncedQuery && (
        <div className="mb-6 flex items-center justify-between">
          <p className="text-gray-600">
            Found <span className="font-semibold">{data.total}</span> results for "{data.query}"
          </p>
          <div className="flex gap-2">
            {Object.entries(data.by_type).map(([type, count]) => (
              <Badge key={type} variant="default">
                {typeLabels[type] || type}: {count}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {isLoading ? (
        <ListSkeleton count={5} />
      ) : data?.results.length ? (
        <div className="space-y-4">
          {data.results.map((result) => {
            const Icon = typeIcons[result.type] || FileText;
            return (
              <Card key={`${result.type}-${result.id}`}>
                <CardHeader>
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center">
                      <Icon className="h-5 w-5 text-gray-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-base">
                          {result.url ? (
                            <a
                              href={result.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-indigo-600"
                            >
                              {result.title}
                            </a>
                          ) : (
                            result.title
                          )}
                        </CardTitle>
                        <Badge variant="info" size="sm">
                          {typeLabels[result.type] || result.type}
                        </Badge>
                      </div>
                      <CardDescription className="mt-1">
                        {truncate(result.description || '', 200)}
                      </CardDescription>
                    </div>
                    {result.image_url && (
                      <img
                        src={result.image_url}
                        alt=""
                        className="h-16 w-16 rounded-lg object-cover"
                      />
                    )}
                  </div>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      ) : debouncedQuery.length >= 2 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No results found for "{debouncedQuery}"</p>
        </div>
      ) : (
        <div className="text-center py-12">
          <Search className="mx-auto h-12 w-12 text-gray-300" />
          <p className="mt-4 text-gray-500">Enter at least 2 characters to search</p>
        </div>
      )}
    </div>
  );
}
