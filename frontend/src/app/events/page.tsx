'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Calendar, MapPin, Globe, Users, DollarSign, ExternalLink, Sparkles } from 'lucide-react';
import { eventsAPI } from '@/lib/api';
import { Event, PaginatedResponse } from '@/types';
import { formatDate, formatCurrency, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { LevelFilterToggle } from '@/components/ui/LevelFilterToggle';
import { useLevelFilter } from '@/hooks/useLevelFilter';
import { ProtectedLink } from '@/components/ui/ProtectedLink';

export default function EventsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isOnline, setIsOnline] = useState<boolean | undefined>();
  const [personalizedFilter, setPersonalizedFilter] = useState(true);

  const { isRecommendedContent, hasCompletedQuiz } = useLevelFilter();

  const { data, isLoading } = useQuery<PaginatedResponse<Event>>({
    queryKey: ['events', page, search, isOnline],
    queryFn: () =>
      eventsAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        is_online: isOnline,
      }),
  });

  const processedEvents = useMemo(() => {
    if (!data?.items) return [];
    if (!personalizedFilter || !hasCompletedQuiz) return data.items;

    return data.items.map((event: any) => ({
      ...event,
      isRecommended: isRecommendedContent(event.level),
    }));
  }, [data?.items, personalizedFilter, hasCompletedQuiz, isRecommendedContent]);

  const sortedEvents = useMemo(() => {
    if (!personalizedFilter || !hasCompletedQuiz) return processedEvents;
    return [...processedEvents].sort((a, b) => {
      if (a.isRecommended && !b.isRecommended) return -1;
      if (!a.isRecommended && b.isRecommended) return 1;
      return 0;
    });
  }, [processedEvents, personalizedFilter, hasCompletedQuiz]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-orange-500 via-rose-500 to-orange-600 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-rose-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Calendar className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Events
            </h1>
          </div>
          <p className="text-lg text-orange-100 max-w-2xl">
            AI conferences, meetups, and workshops. Connect with the community and stay ahead of the curve.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Events
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Online & In-Person
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Free & Paid
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
                placeholder="Search events..."
                className="flex-1 max-w-md"
              />
              <select
                value={isOnline === undefined ? '' : isOnline ? 'online' : 'inperson'}
                onChange={(e) => {
                  const val = e.target.value;
                  setIsOnline(val === '' ? undefined : val === 'online');
                }}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Events</option>
                <option value="online">Online</option>
                <option value="inperson">In-Person</option>
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
              {sortedEvents.map((event: any) => (
                <EventCard key={event.id} event={event} isRecommended={event.isRecommended} />
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

            {sortedEvents.length === 0 && (
              <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
                <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No events found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function EventCard({ event, isRecommended }: { event: Event; isRecommended?: boolean }) {
  return (
    <div className={`group bg-white rounded-2xl border overflow-hidden hover:shadow-xl transition-all hover:-translate-y-1 ${
      isRecommended ? 'border-orange-200 ring-2 ring-orange-500/20' : 'border-gray-100'
    }`}>
      {event.image_url && (
        <div className="relative h-40 overflow-hidden">
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
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
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-gray-900 group-hover:text-orange-600 transition-colors line-clamp-2">
            {event.title}
          </h3>
          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            {isRecommended && !event.image_url && (
              <Badge variant="warning" className="flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                For You
              </Badge>
            )}
            {event.is_online ? (
              <Badge variant="info">
                <Globe className="h-3 w-3 mr-1" />
                Online
              </Badge>
            ) : (
              <Badge variant="default">In-Person</Badge>
            )}
          </div>
        </div>

        <div className="mt-3 space-y-2 text-sm text-gray-500">
          {event.starts_at && (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(event.starts_at)}</span>
            </div>
          )}
          {event.city && (
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              <span>{[event.city, event.country].filter(Boolean).join(', ')}</span>
            </div>
          )}
        </div>

        <p className="mt-3 text-sm text-gray-500 line-clamp-2">
          {truncate(event.short_description || event.description || '', 100)}
        </p>

        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            {event.attendees_count > 0 && (
              <span className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                {event.attendees_count}
              </span>
            )}
            <span className="flex items-center gap-1">
              {event.is_free ? (
                <Badge variant="success" size="sm">Free</Badge>
              ) : event.price_min ? (
                <>
                  <DollarSign className="h-4 w-4" />
                  {formatCurrency(event.price_min)}
                </>
              ) : null}
            </span>
          </div>
          <ProtectedLink
            href={event.registration_url || event.url}
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-rose-500 px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-all"
          >
            Register
          </ProtectedLink>
        </div>
      </div>
    </div>
  );
}
