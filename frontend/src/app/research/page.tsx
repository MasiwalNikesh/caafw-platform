'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Code, ExternalLink, Quote, Star, GraduationCap } from 'lucide-react';
import { researchAPI } from '@/lib/api';
import { ResearchPaper, PaginatedResponse } from '@/types';
import { formatRelativeTime, formatNumber, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { ProtectedLink } from '@/components/ui/ProtectedLink';

export default function ResearchPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [hasCode, setHasCode] = useState<boolean | undefined>();

  const { data, isLoading } = useQuery<PaginatedResponse<ResearchPaper>>({
    queryKey: ['research', page, search, hasCode],
    queryFn: () =>
      researchAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        has_code: hasCode,
      }),
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-teal-600 via-cyan-600 to-teal-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-cyan-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Research Papers
            </h1>
          </div>
          <p className="text-lg text-teal-100 max-w-2xl">
            Latest AI and ML research from arXiv and Papers With Code
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Papers
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Code Available
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Latest Research
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Filters Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Search papers..."
              className="flex-1 max-w-md"
            />
            <select
              value={hasCode === undefined ? '' : hasCode ? 'yes' : 'no'}
              onChange={(e) => {
                const val = e.target.value;
                setHasCode(val === '' ? undefined : val === 'yes');
              }}
              className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-gray-50"
            >
              <option value="">All Papers</option>
              <option value="yes">With Code</option>
              <option value="no">Without Code</option>
            </select>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <ListSkeleton count={6} />
        ) : (
          <>
            <div className="space-y-4">
              {data?.items.map((paper) => (
                <PaperCard key={paper.id} paper={paper} />
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
                <GraduationCap className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No papers found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function PaperCard({ paper }: { paper: ResearchPaper }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-br from-teal-100 to-teal-50">
          <FileText className="h-5 w-5 text-teal-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 leading-tight">
            {paper.title}
          </h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {paper.primary_category && (
              <Badge variant="info">{paper.primary_category}</Badge>
            )}
            {paper.has_code && (
              <Badge variant="success">
                <Code className="h-3 w-3 mr-1" />
                Has Code
              </Badge>
            )}
            {paper.arxiv_id && (
              <Badge variant="default">arXiv: {paper.arxiv_id}</Badge>
            )}
          </div>
        </div>
      </div>

      {paper.authors && paper.authors.length > 0 && (
        <p className="mt-3 text-sm text-gray-600">
          {paper.authors.map((a) => a.name).join(', ')}
        </p>
      )}

      <p className="mt-3 text-sm text-gray-600 line-clamp-3">
        {truncate(paper.abstract || '', 300)}
      </p>

      {paper.tasks && paper.tasks.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Tasks:</p>
          <div className="flex flex-wrap gap-2">
            {paper.tasks.slice(0, 5).map((task) => (
              <span key={task} className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
                {task}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <Quote className="h-4 w-4" />
            {formatNumber(paper.citations)}
          </span>
          {paper.stars > 0 && (
            <span className="flex items-center gap-1">
              <Star className="h-4 w-4" />
              {formatNumber(paper.stars)}
            </span>
          )}
          {paper.published_at && (
            <span>{formatRelativeTime(paper.published_at)}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {paper.pdf_url && (
            <ProtectedLink
              href={paper.pdf_url}
              className="inline-flex items-center gap-1 text-sm text-teal-600 hover:text-teal-500"
            >
              <FileText className="h-4 w-4" />
              PDF
            </ProtectedLink>
          )}
          {paper.code_url && (
            <ProtectedLink
              href={paper.code_url}
              className="inline-flex items-center gap-1 text-sm text-teal-600 hover:text-teal-500"
            >
              <Code className="h-4 w-4" />
              Code
            </ProtectedLink>
          )}
          <ProtectedLink
            href={paper.paper_url}
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-teal-600 to-cyan-600 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-teal-500/25"
          >
            View Paper
          </ProtectedLink>
        </div>
      </div>
    </div>
  );
}
