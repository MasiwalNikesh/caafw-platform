'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Code, ExternalLink, Quote, Star } from 'lucide-react';
import { researchAPI } from '@/lib/api';
import { ResearchPaper, PaginatedResponse } from '@/types';
import { formatRelativeTime, formatNumber, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

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
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Research Papers</h1>
        <p className="mt-2 text-gray-600">
          Latest AI and ML research from arXiv and Papers With Code
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">All Papers</option>
          <option value="yes">With Code</option>
          <option value="no">Without Code</option>
        </select>
      </div>

      {/* Results */}
      {isLoading ? (
        <ListSkeleton count={6} />
      ) : (
        <>
          <div className="space-y-6">
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
            <div className="text-center py-12">
              <p className="text-gray-500">No papers found</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function PaperCard({ paper }: { paper: ResearchPaper }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex-1">
          <div className="flex items-start gap-2">
            <FileText className="h-5 w-5 text-indigo-600 flex-shrink-0 mt-1" />
            <CardTitle className="text-lg">{paper.title}</CardTitle>
          </div>
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
      </CardHeader>

      {paper.authors && paper.authors.length > 0 && (
        <p className="mt-3 text-sm text-gray-600">
          {paper.authors.map((a) => a.name).join(', ')}
        </p>
      )}

      <CardDescription className="mt-3">
        {truncate(paper.abstract || '', 300)}
      </CardDescription>

      {paper.tasks && paper.tasks.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Tasks:</p>
          <div className="flex flex-wrap gap-1">
            {paper.tasks.slice(0, 5).map((task) => (
              <Badge key={task} size="sm">
                {task}
              </Badge>
            ))}
          </div>
        </div>
      )}

      <CardFooter>
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <Quote className="h-4 w-4" />
            {formatNumber(paper.citations)} citations
          </span>
          {paper.stars > 0 && (
            <span className="flex items-center gap-1">
              <Star className="h-4 w-4" />
              {formatNumber(paper.stars)} stars
            </span>
          )}
          {paper.published_at && (
            <span>{formatRelativeTime(paper.published_at)}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {paper.pdf_url && (
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-500"
            >
              <FileText className="h-4 w-4" />
              PDF
            </a>
          )}
          {paper.code_url && (
            <a
              href={paper.code_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-500"
            >
              <Code className="h-4 w-4" />
              Code
            </a>
          )}
          <a
            href={paper.paper_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
          >
            View Paper
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </CardFooter>
    </Card>
  );
}
