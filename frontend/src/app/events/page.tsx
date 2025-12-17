'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Calendar, MapPin, Globe, Users, DollarSign, ExternalLink } from 'lucide-react';
import { eventsAPI } from '@/lib/api';
import { Event, PaginatedResponse } from '@/types';
import { formatDate, formatCurrency, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function EventsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isOnline, setIsOnline] = useState<boolean | undefined>();

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

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Events</h1>
        <p className="mt-2 text-gray-600">
          AI conferences, meetups, and workshops
        </p>
      </div>

      <div className="mb-6 flex flex-col sm:flex-row gap-4">
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm"
        >
          <option value="">All Events</option>
          <option value="online">Online</option>
          <option value="inperson">In-Person</option>
        </select>
      </div>

      {isLoading ? (
        <ListSkeleton count={6} />
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {data?.items.map((event) => (
              <EventCard key={event.id} event={event} />
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

function EventCard({ event }: { event: Event }) {
  return (
    <Card>
      {event.image_url && (
        <div className="relative -mx-6 -mt-6 mb-4">
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-40 object-cover rounded-t-lg"
          />
        </div>
      )}

      <CardHeader className="p-0">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{event.title}</CardTitle>
          {event.is_online ? (
            <Badge variant="info">
              <Globe className="h-3 w-3 mr-1" />
              Online
            </Badge>
          ) : (
            <Badge variant="default">In-Person</Badge>
          )}
        </div>
      </CardHeader>

      <div className="mt-3 space-y-2 text-sm text-gray-600">
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

      <CardDescription>
        {truncate(event.short_description || event.description || '', 100)}
      </CardDescription>

      <CardFooter className="text-sm">
        <div className="flex items-center gap-3 text-gray-500">
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
        <a
          href={event.registration_url || event.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
        >
          Register
          <ExternalLink className="h-4 w-4" />
        </a>
      </CardFooter>
    </Card>
  );
}
