'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Clock, Star, Users, ExternalLink, Play } from 'lucide-react';
import { learningAPI } from '@/lib/api';
import { LearningResource, PaginatedResponse } from '@/types';
import { formatNumber, formatCurrency, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function LearningPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isFree, setIsFree] = useState<boolean | undefined>();
  const [level, setLevel] = useState<string>('');

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

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Learning Resources</h1>
        <p className="mt-2 text-gray-600">
          Courses, tutorials, and videos to level up your AI skills
        </p>
      </div>

      <div className="mb-6 flex flex-col sm:flex-row gap-4">
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm"
        >
          <option value="">All Pricing</option>
          <option value="free">Free</option>
          <option value="paid">Paid</option>
        </select>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm"
        >
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      {isLoading ? (
        <ListSkeleton count={6} />
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {data?.items.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
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
        </>
      )}
    </div>
  );
}

function ResourceCard({ resource }: { resource: LearningResource }) {
  const formatDuration = (minutes?: number) => {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes}m`;
    return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
  };

  return (
    <Card>
      {resource.thumbnail_url && (
        <div className="relative -mx-6 -mt-6 mb-4">
          <img
            src={resource.thumbnail_url}
            alt={resource.title}
            className="w-full h-40 object-cover rounded-t-lg"
          />
          {resource.resource_type === 'video' && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-t-lg">
              <Play className="h-12 w-12 text-white" />
            </div>
          )}
        </div>
      )}

      <CardHeader className="p-0">
        <div className="flex items-start gap-2">
          <BookOpen className="h-5 w-5 text-orange-500 flex-shrink-0 mt-0.5" />
          <CardTitle className="text-base">{resource.title}</CardTitle>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge variant={resource.is_free ? 'success' : 'default'}>
            {resource.is_free ? 'Free' : formatCurrency(resource.price)}
          </Badge>
          {resource.level && (
            <Badge variant="info">{resource.level}</Badge>
          )}
        </div>
      </CardHeader>

      {resource.instructor && (
        <p className="mt-2 text-sm text-gray-600">
          by {resource.instructor}
        </p>
      )}

      <CardDescription>
        {truncate(resource.description || '', 100)}
      </CardDescription>

      <CardFooter className="text-sm text-gray-500">
        <div className="flex items-center gap-3">
          {resource.duration_minutes && (
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {formatDuration(resource.duration_minutes)}
            </span>
          )}
          {resource.rating && (
            <span className="flex items-center gap-1">
              <Star className="h-4 w-4 text-yellow-400" />
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
        <a
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-indigo-600 hover:text-indigo-500"
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </CardFooter>
    </Card>
  );
}
