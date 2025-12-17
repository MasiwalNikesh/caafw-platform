'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Building2, MapPin, Users, DollarSign, TrendingUp, ExternalLink } from 'lucide-react';
import { investmentsAPI } from '@/lib/api';
import { Company, PaginatedResponse } from '@/types';
import { formatCurrency, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function InvestmentsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [fundingStatus, setFundingStatus] = useState<string>('');

  const { data, isLoading } = useQuery<PaginatedResponse<Company>>({
    queryKey: ['companies', page, search, fundingStatus],
    queryFn: () =>
      investmentsAPI.companies({
        page,
        page_size: 20,
        search: search || undefined,
        funding_status: fundingStatus || undefined,
      }),
  });

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Companies & Investments</h1>
        <p className="mt-2 text-gray-600">
          Discover AI startups and their funding rounds
        </p>
      </div>

      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search companies..."
          className="flex-1 max-w-md"
        />
        <select
          value={fundingStatus}
          onChange={(e) => setFundingStatus(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm"
        >
          <option value="">All Stages</option>
          <option value="seed">Seed</option>
          <option value="series_a">Series A</option>
          <option value="series_b">Series B</option>
          <option value="series_c">Series C+</option>
        </select>
      </div>

      {isLoading ? (
        <ListSkeleton count={6} />
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2">
            {data?.items.map((company) => (
              <CompanyCard key={company.id} company={company} />
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

function CompanyCard({ company }: { company: Company }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-4">
          {company.logo_url ? (
            <img
              src={company.logo_url}
              alt={company.name}
              className="h-14 w-14 rounded-lg object-cover"
            />
          ) : (
            <div className="h-14 w-14 rounded-lg bg-gray-100 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-gray-400" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <CardTitle>{company.name}</CardTitle>
            <div className="mt-1 flex flex-wrap gap-2">
              {company.funding_status && (
                <Badge variant="info">
                  {company.funding_status.replace('_', ' ').toUpperCase()}
                </Badge>
              )}
              {company.founded_year && (
                <Badge variant="default">Founded {company.founded_year}</Badge>
              )}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardDescription>
        {truncate(company.short_description || company.description || '', 150)}
      </CardDescription>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        {company.headquarters && (
          <div className="flex items-center gap-2 text-gray-600">
            <MapPin className="h-4 w-4" />
            <span>{company.headquarters}</span>
          </div>
        )}
        {company.employee_count && (
          <div className="flex items-center gap-2 text-gray-600">
            <Users className="h-4 w-4" />
            <span>{company.employee_count} employees</span>
          </div>
        )}
        {company.total_funding && (
          <div className="flex items-center gap-2 text-green-600 font-medium">
            <DollarSign className="h-4 w-4" />
            <span>{formatCurrency(company.total_funding)} raised</span>
          </div>
        )}
        {company.valuation && (
          <div className="flex items-center gap-2 text-gray-600">
            <TrendingUp className="h-4 w-4" />
            <span>{formatCurrency(company.valuation)} valuation</span>
          </div>
        )}
      </div>

      {company.industries && company.industries.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1">
          {company.industries.slice(0, 3).map((industry) => (
            <Badge key={industry} size="sm">
              {industry}
            </Badge>
          ))}
        </div>
      )}

      <CardFooter>
        <div className="flex items-center gap-2">
          {company.lead_investors && company.lead_investors.length > 0 && (
            <span className="text-sm text-gray-500">
              Investors: {company.lead_investors.slice(0, 2).join(', ')}
            </span>
          )}
        </div>
        {company.website_url && (
          <a
            href={company.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-indigo-600 hover:text-indigo-500 text-sm"
          >
            Website
            <ExternalLink className="h-4 w-4" />
          </a>
        )}
      </CardFooter>
    </Card>
  );
}
