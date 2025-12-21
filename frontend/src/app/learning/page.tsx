'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Clock, Star, Users, ExternalLink, Play, Sparkles, GraduationCap } from 'lucide-react';
import { learningAPI } from '@/lib/api';
import { LearningResource, PaginatedResponse } from '@/types';
import { formatNumber, formatCurrency, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { LevelFilterToggle } from '@/components/ui/LevelFilterToggle';
import { useLevelFilter } from '@/hooks/useLevelFilter';
import { ProtectedLink } from '@/components/ui/ProtectedLink';

export default function LearningPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isFree, setIsFree] = useState<boolean | undefined>();
  const [level, setLevel] = useState<string>('');
  const [personalizedFilter, setPersonalizedFilter] = useState(true);

  const { isRecommendedLearning, hasCompletedQuiz } = useLevelFilter();

  const { data, isLoading } = useQuery<PaginatedResponse<LearningResource>>({
    queryKey: ['learning', page, search, isFree, level],
    queryFn: () =>
      learningAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        is_free: isFree,
        level: level || undefined,
      }),
  });

  const processedResources = useMemo(() => {
    if (!data?.items) return [];
    if (!personalizedFilter || !hasCompletedQuiz) return data.items;

    return data.items.map((resource) => ({
      ...resource,
      isRecommended: isRecommendedLearning(resource.level),
    }));
  }, [data?.items, personalizedFilter, hasCompletedQuiz, isRecommendedLearning]);

  const sortedResources = useMemo(() => {
    if (!personalizedFilter || !hasCompletedQuiz) return processedResources;
    return [...processedResources].sort((a, b) => {
      if (a.isRecommended && !b.isRecommended) return -1;
      if (!a.isRecommended && b.isRecommended) return 1;
      return 0;
    });
  }, [processedResources, personalizedFilter, hasCompletedQuiz]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-pink-600 to-purple-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-pink-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Learning Resources
            </h1>
          </div>
          <p className="text-lg text-purple-100 max-w-2xl">
            Courses, tutorials, and videos to level up your AI skills. Learn from industry experts and top institutions.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Resources
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Free & Paid Options
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              All Skill Levels
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Filters Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1 w-full lg:w-auto">
              <SearchInput
                value={search}
                onChange={setSearch}
                placeholder="Search courses, tutorials..."
                className="flex-1 max-w-md"
              />
              <select
                value={isFree === undefined ? '' : isFree ? 'free' : 'paid'}
                onChange={(e) => {
                  const val = e.target.value;
                  setIsFree(val === '' ? undefined : val === 'free');
                }}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Pricing</option>
                <option value="free">Free</option>
                <option value="paid">Paid</option>
              </select>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <LevelFilterToggle
              isFiltering={personalizedFilter}
              onToggle={setPersonalizedFilter}
            />
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <ListSkeleton count={6} />
        ) : (
          <>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {sortedResources.map((resource: any) => (
                <ResourceCard key={resource.id} resource={resource} isRecommended={resource.isRecommended} />
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

            {sortedResources.length === 0 && (
              <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
                <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No learning resources found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function ResourceCard({ resource, isRecommended }: { resource: LearningResource; isRecommended?: boolean }) {
  const formatDuration = (minutes?: number) => {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes}m`;
    return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
  };

  return (
    <div className={`group bg-white rounded-2xl border overflow-hidden hover:shadow-xl transition-all hover:-translate-y-1 ${
      isRecommended ? 'border-purple-200 ring-2 ring-purple-500/20' : 'border-gray-100'
    }`}>
      {resource.thumbnail_url && (
        <div className="relative h-40 overflow-hidden">
          <img
            src={resource.thumbnail_url}
            alt={resource.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          {resource.resource_type === 'video' && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/30">
              <div className="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center">
                <Play className="h-6 w-6 text-purple-600 ml-1" />
              </div>
            </div>
          )}
          {isRecommended && (
            <div className="absolute top-3 right-3">
              <Badge variant="warning" className="flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                For You
              </Badge>
            </div>
          )}
        </div>
      )}

      <div className="p-5">
        <div className="flex items-start gap-3">
          {!resource.thumbnail_url && (
            <div className="p-2 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 flex-shrink-0">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors line-clamp-2">
              {resource.title}
            </h3>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {isRecommended && !resource.thumbnail_url && (
            <Badge variant="warning" className="flex items-center gap-1">
              <Sparkles className="h-3 w-3" />
              For You
            </Badge>
          )}
          <Badge variant={resource.is_free ? 'success' : 'default'}>
            {resource.is_free ? 'Free' : formatCurrency(resource.price)}
          </Badge>
          {resource.level && (
            <Badge variant="info">{resource.level}</Badge>
          )}
        </div>

        {resource.instructor && (
          <p className="mt-3 text-sm text-gray-600">
            by {resource.instructor}
          </p>
        )}

        <p className="mt-2 text-sm text-gray-500 line-clamp-2">
          {truncate(resource.description || '', 100)}
        </p>

        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            {resource.duration_minutes && (
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {formatDuration(resource.duration_minutes)}
              </span>
            )}
            {resource.rating && (
              <span className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                {resource.rating.toFixed(1)}
              </span>
            )}
            {resource.enrollments > 0 && (
              <span className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                {formatNumber(resource.enrollments)}
              </span>
            )}
          </div>
          <ProtectedLink
            href={resource.url}
            className="p-2 rounded-full bg-purple-50 text-purple-600 hover:bg-purple-100 transition-colors"
          >
            <span className="sr-only">Open resource</span>
          </ProtectedLink>
        </div>
      </div>
    </div>
  );
}
