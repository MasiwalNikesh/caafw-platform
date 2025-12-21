'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Cpu, Briefcase, FileText, BookOpen, Server, Sparkles } from 'lucide-react';
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
  learning: BookOpen,
};

const typeLabels: Record<string, string> = {
  product: 'Product',
  job: 'Job',
  news: 'News',
  research: 'Research',
  mcp: 'MCP Server',
  learning: 'Learning',
};

const typeColors: Record<string, string> = {
  product: 'from-blue-500 to-indigo-500',
  job: 'from-purple-500 to-indigo-500',
  news: 'from-orange-500 to-red-500',
  research: 'from-teal-500 to-cyan-500',
  mcp: 'from-violet-500 to-purple-500',
  learning: 'from-pink-500 to-rose-500',
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
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-blue-600 to-indigo-700 pt-24 sm:pt-28 pb-24">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-blue-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm mb-4">
              <Search className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Search Everything
            </h1>
            <p className="mt-4 text-lg text-indigo-100 max-w-lg">
              Find AI products, jobs, research papers, learning resources, and more across our entire platform.
            </p>
          </div>
        </div>
      </section>

      {/* Search Section */}
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 -mt-10 pb-16">
        {/* Search Input Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-4 mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-6 w-6 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search for anything..."
              className="w-full pl-14 pr-4 py-4 rounded-xl border border-gray-200 bg-gray-50 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              autoFocus
            />
          </div>
        </div>

        {/* Results Summary */}
        {data && debouncedQuery && (
          <div className="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white rounded-xl p-4 border border-gray-100">
            <p className="text-gray-600">
              Found <span className="font-semibold text-gray-900">{data.total}</span> results for "<span className="font-medium">{data.query}</span>"
            </p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.by_type).map(([type, count]) => (
                <span key={type} className="px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm font-medium">
                  {typeLabels[type] || type}: {count}
                </span>
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
              const colorClass = typeColors[result.type] || 'from-gray-500 to-gray-600';
              return (
                <div
                  key={`${result.type}-${result.id}`}
                  className="group bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all"
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClass} flex-shrink-0`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {result.url ? (
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors"
                          >
                            {result.title}
                          </a>
                        ) : (
                          <span className="text-lg font-semibold text-gray-900">
                            {result.title}
                          </span>
                        )}
                        <Badge variant="info" size="sm">
                          {typeLabels[result.type] || result.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {truncate(result.description || '', 200)}
                      </p>
                    </div>
                    {result.image_url && (
                      <img
                        src={result.image_url}
                        alt=""
                        className="h-16 w-16 rounded-xl object-cover flex-shrink-0"
                      />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : debouncedQuery.length >= 2 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
            <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <Search className="h-8 w-8 text-gray-400" />
            </div>
            <p className="text-gray-600 text-lg">No results found for "{debouncedQuery}"</p>
            <p className="text-gray-400 text-sm mt-1">Try different keywords or check your spelling</p>
          </div>
        ) : (
          <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
            <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="h-8 w-8 text-indigo-500" />
            </div>
            <p className="text-gray-600 text-lg">Start typing to search</p>
            <p className="text-gray-400 text-sm mt-1">Enter at least 2 characters to begin</p>

            {/* Quick search suggestions */}
            <div className="mt-8">
              <p className="text-sm text-gray-500 mb-3">Popular searches</p>
              <div className="flex flex-wrap justify-center gap-2">
                {['ChatGPT', 'Machine Learning', 'AI Jobs', 'LLM', 'Python'].map((term) => (
                  <button
                    key={term}
                    onClick={() => handleSearch(term)}
                    className="px-4 py-2 rounded-full bg-gray-100 text-gray-700 text-sm font-medium hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
