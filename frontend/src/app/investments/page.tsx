'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Building2, MapPin, Users, DollarSign, TrendingUp, ExternalLink, Coins, ArrowUpDown } from 'lucide-react';
import { investmentsAPI } from '@/lib/api';
import { Company, PaginatedResponse } from '@/types';
import { formatCurrency, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

type SortOption = 'total_funding' | 'last_funding_date';

export default function InvestmentsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [fundingStatus, setFundingStatus] = useState<string>('');
  const [sortBy, setSortBy] = useState<SortOption>('total_funding');

  const { data, isLoading } = useQuery<PaginatedResponse<Company>>({
    queryKey: ['companies', page, search, fundingStatus, sortBy],
    queryFn: () =>
      investmentsAPI.companies({
        page,
        page_size: 20,
        search: search || undefined,
        funding_status: fundingStatus || undefined,
        sort_by: sortBy,
        sort_order: 'desc',
      }),
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-600 via-green-600 to-emerald-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-green-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Coins className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              AI Companies & Investments
            </h1>
          </div>
          <p className="text-lg text-emerald-100 max-w-2xl">
            Discover AI startups and their funding rounds
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Companies
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              All Funding Stages
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Investment Insights
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
              placeholder="Search companies..."
              className="flex-1 max-w-md"
            />
            <select
              value={fundingStatus}
              onChange={(e) => setFundingStatus(e.target.value)}
              className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-gray-50"
            >
              <option value="">All Stages</option>
              <option value="seed">Seed</option>
              <option value="series_a">Series A</option>
              <option value="series_b">Series B</option>
              <option value="series_c">Series C+</option>
            </select>
            {/* Sort Toggle */}
            <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-gray-50 p-1">
              <button
                onClick={() => setSortBy('total_funding')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  sortBy === 'total_funding'
                    ? 'bg-white text-emerald-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <DollarSign className="h-4 w-4" />
                Largest
              </button>
              <button
                onClick={() => setSortBy('last_funding_date')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  sortBy === 'last_funding_date'
                    ? 'bg-white text-emerald-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <ArrowUpDown className="h-4 w-4" />
                Recent
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
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

            {data?.items.length === 0 && (
              <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
                <Coins className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No companies found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function CompanyCard({ company }: { company: Company }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
      <div className="flex items-start gap-4">
        {company.logo_url ? (
          <img
            src={company.logo_url}
            alt={company.name}
            className="h-14 w-14 rounded-lg object-cover"
          />
        ) : (
          <div className="h-14 w-14 rounded-lg bg-gradient-to-br from-emerald-100 to-emerald-50 flex items-center justify-center">
            <Building2 className="h-6 w-6 text-emerald-600" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
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

      <p className="mt-4 text-sm text-gray-600 line-clamp-2">
        {truncate(company.short_description || company.description || '', 150)}
      </p>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        {company.headquarters && (
          <div className="flex items-center gap-2 text-gray-600">
            <MapPin className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{company.headquarters}</span>
          </div>
        )}
        {company.employee_count && (
          <div className="flex items-center gap-2 text-gray-600">
            <Users className="h-4 w-4 flex-shrink-0" />
            <span>{company.employee_count} employees</span>
          </div>
        )}
        {company.total_funding && (
          <div className="flex items-center gap-2 text-emerald-600 font-medium">
            <DollarSign className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{formatCurrency(company.total_funding)} raised</span>
          </div>
        )}
        {company.valuation && (
          <div className="flex items-center gap-2 text-gray-600">
            <TrendingUp className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{formatCurrency(company.valuation)} valuation</span>
          </div>
        )}
      </div>

      {company.industries && company.industries.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {company.industries.slice(0, 3).map((industry) => (
            <span key={industry} className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
              {industry}
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex-1 min-w-0">
          {company.lead_investors && company.lead_investors.length > 0 && (
            <span className="text-sm text-gray-500 truncate block">
              Investors: {company.lead_investors.slice(0, 2).join(', ')}
            </span>
          )}
        </div>
        {company.website_url && (
          <a
            href={company.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-emerald-600 to-green-600 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-emerald-500/25 ml-4"
          >
            Website
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        )}
      </div>
    </div>
  );
}
