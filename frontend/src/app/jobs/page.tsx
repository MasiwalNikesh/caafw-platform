'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapPin, DollarSign, Clock, Building2, ExternalLink } from 'lucide-react';
import { jobsAPI } from '@/lib/api';
import { Job, PaginatedResponse } from '@/types';
import { formatRelativeTime, formatCurrency, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isRemote, setIsRemote] = useState<boolean | undefined>();

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

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Jobs</h1>
        <p className="mt-2 text-gray-600">
          Find your next AI and machine learning job opportunity
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">All Locations</option>
          <option value="remote">Remote Only</option>
          <option value="onsite">On-site</option>
        </select>
      </div>

      {/* Results */}
      {isLoading ? (
        <ListSkeleton count={6} />
      ) : (
        <>
          <div className="space-y-4">
            {data?.items.map((job) => (
              <JobCard key={job.id} job={job} />
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
              <p className="text-gray-500">No jobs found</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function JobCard({ job }: { job: Job }) {
  const salaryRange =
    job.salary_min && job.salary_max
      ? `${formatCurrency(job.salary_min)} - ${formatCurrency(job.salary_max)}`
      : job.salary_min
      ? `From ${formatCurrency(job.salary_min)}`
      : job.salary_max
      ? `Up to ${formatCurrency(job.salary_max)}`
      : null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-4 w-full">
          {job.company_logo ? (
            <img
              src={job.company_logo}
              alt={job.company_name}
              className="h-14 w-14 rounded-lg object-cover"
            />
          ) : (
            <div className="h-14 w-14 rounded-lg bg-gray-100 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-gray-400" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <CardTitle>{job.title}</CardTitle>
            <p className="text-sm text-gray-600 mt-1">{job.company_name}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            {job.is_remote && (
              <Badge variant="success">Remote</Badge>
            )}
            {job.is_featured && (
              <Badge variant="info">Featured</Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-500">
        {job.location && (
          <span className="flex items-center gap-1">
            <MapPin className="h-4 w-4" />
            {job.location}
          </span>
        )}
        {salaryRange && (
          <span className="flex items-center gap-1">
            <DollarSign className="h-4 w-4" />
            {salaryRange}
          </span>
        )}
        {job.job_type && (
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            {job.job_type}
          </span>
        )}
      </div>

      {job.skills && job.skills.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {job.skills.slice(0, 5).map((skill) => (
            <Badge key={skill} variant="default">
              {skill}
            </Badge>
          ))}
        </div>
      )}

      <CardFooter>
        <span className="text-sm text-gray-500">
          {job.posted_at && formatRelativeTime(job.posted_at)}
        </span>
        {job.apply_url && (
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          >
            Apply
            <ExternalLink className="h-4 w-4" />
          </a>
        )}
      </CardFooter>
    </Card>
  );
}
