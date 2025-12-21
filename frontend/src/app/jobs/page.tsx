'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapPin, DollarSign, Clock, Building2, ExternalLink, Sparkles, Briefcase, Search } from 'lucide-react';
import { jobsAPI } from '@/lib/api';
import { Job, PaginatedResponse } from '@/types';
import { formatRelativeTime, formatCurrency, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { LevelFilterToggle } from '@/components/ui/LevelFilterToggle';
import { useLevelFilter } from '@/hooks/useLevelFilter';

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isRemote, setIsRemote] = useState<boolean | undefined>();
  const [personalizedFilter, setPersonalizedFilter] = useState(true);

  const { isRecommendedJob, hasCompletedQuiz, userLevel } = useLevelFilter();

  const { data, isLoading } = useQuery<PaginatedResponse<Job>>({
    queryKey: ['jobs', page, search, isRemote],
    queryFn: () =>
      jobsAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        is_remote: isRemote,
      }),
  });

  const filteredJobs = useMemo(() => {
    if (!data?.items) return [];
    if (!personalizedFilter || !hasCompletedQuiz) return data.items;

    return data.items.map((job) => ({
      ...job,
      isRecommended: isRecommendedJob(job.experience_level),
    }));
  }, [data?.items, personalizedFilter, hasCompletedQuiz, isRecommendedJob]);

  const sortedJobs = useMemo(() => {
    if (!personalizedFilter || !hasCompletedQuiz) return filteredJobs;
    return [...filteredJobs].sort((a, b) => {
      if (a.isRecommended && !b.isRecommended) return -1;
      if (!a.isRecommended && b.isRecommended) return 1;
      return 0;
    });
  }, [filteredJobs, personalizedFilter, hasCompletedQuiz]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Briefcase className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              AI Jobs
            </h1>
          </div>
          <p className="text-lg text-indigo-100 max-w-2xl">
            Find your next AI and machine learning job opportunity. Browse thousands of positions from top companies.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Jobs Available
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Remote & On-site
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              All Experience Levels
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
                placeholder="Search jobs, companies..."
                className="flex-1 max-w-md"
              />
              <select
                value={isRemote === undefined ? '' : isRemote ? 'remote' : 'onsite'}
                onChange={(e) => {
                  const val = e.target.value;
                  setIsRemote(val === '' ? undefined : val === 'remote');
                }}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Locations</option>
                <option value="remote">Remote Only</option>
                <option value="onsite">On-site</option>
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
            <div className="space-y-4">
              {sortedJobs.map((job: any) => (
                <JobCard key={job.id} job={job} isRecommended={job.isRecommended} />
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

            {sortedJobs.length === 0 && (
              <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
                <Briefcase className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No jobs found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function JobCard({ job, isRecommended }: { job: Job; isRecommended?: boolean }) {
  const salaryRange =
    job.salary_min && job.salary_max
      ? `${formatCurrency(job.salary_min)} - ${formatCurrency(job.salary_max)}`
      : job.salary_min
      ? `From ${formatCurrency(job.salary_min)}`
      : job.salary_max
      ? `Up to ${formatCurrency(job.salary_max)}`
      : null;

  return (
    <div className={`bg-white rounded-2xl border p-6 hover:shadow-lg transition-all hover:-translate-y-0.5 ${
      isRecommended ? 'border-purple-200 ring-2 ring-purple-500/20' : 'border-gray-100'
    }`}>
      <div className="flex items-start gap-4">
        {job.company_logo ? (
          <img
            src={job.company_logo}
            alt={job.company_name}
            className="h-14 w-14 rounded-xl object-cover"
          />
        ) : (
          <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-gray-100 to-gray-50 flex items-center justify-center">
            <Building2 className="h-6 w-6 text-gray-400" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 hover:text-purple-600 transition-colors">
                {job.title}
              </h3>
              <p className="text-sm text-gray-600 mt-0.5">{job.company_name}</p>
            </div>
            <div className="flex flex-wrap gap-2 justify-end">
              {isRecommended && (
                <Badge variant="warning" className="flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  For You
                </Badge>
              )}
              {job.is_remote && (
                <Badge variant="success">Remote</Badge>
              )}
              {job.is_featured && (
                <Badge variant="info">Featured</Badge>
              )}
            </div>
          </div>

          <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-500">
            {job.location && (
              <span className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" />
                {job.location}
              </span>
            )}
            {salaryRange && (
              <span className="flex items-center gap-1.5">
                <DollarSign className="h-4 w-4" />
                {salaryRange}
              </span>
            )}
            {job.job_type && (
              <span className="flex items-center gap-1.5">
                <Clock className="h-4 w-4" />
                {job.job_type}
              </span>
            )}
          </div>

          {job.skills && job.skills.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {job.skills.slice(0, 5).map((skill) => (
                <span key={skill} className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
                  {skill}
                </span>
              ))}
            </div>
          )}

          <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
            <span className="text-sm text-gray-400">
              {job.posted_at && formatRelativeTime(job.posted_at)}
            </span>
            {job.apply_url && (
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-5 py-2 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-purple-500/25"
              >
                Apply Now
                <ExternalLink className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
