'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ExternalLink, Star, MessageSquare } from 'lucide-react';
import { productsAPI } from '@/lib/api';
import { Product, PaginatedResponse } from '@/types';
import { formatNumber, formatRelativeTime, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [pricingFilter, setPricingFilter] = useState<string>('');

  const { data, isLoading } = useQuery<PaginatedResponse<Product>>({
    queryKey: ['products', page, search, pricingFilter],
    queryFn: () =>
      productsAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        pricing_type: pricingFilter || undefined,
      }),
  });

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Products</h1>
        <p className="mt-2 text-gray-600">
          Discover the latest AI tools and products from Product Hunt and more
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search products..."
          className="flex-1 max-w-md"
        />
        <select
          value={pricingFilter}
          onChange={(e) => setPricingFilter(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">All Pricing</option>
          <option value="free">Free</option>
          <option value="freemium">Freemium</option>
          <option value="paid">Paid</option>
        </select>
      </div>

      {/* Results */}
      {isLoading ? (
        <ListSkeleton count={6} />
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {data?.items.map((product) => (
              <ProductCard key={product.id} product={product} />
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
              <p className="text-gray-500">No products found</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function getProductImage(product: Product): string {
  // Priority: logo_url > thumbnail_url > placeholder
  if (product.logo_url) return product.logo_url;
  if (product.thumbnail_url) return product.thumbnail_url;
  // Use picsum.photos with product id as seed for consistent placeholder
  const seed = product.id || product.name.length;
  return `https://picsum.photos/seed/${seed}/200/200`;
}

function ProductCard({ product }: { product: Product }) {
  const imageUrl = getProductImage(product);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <img
            src={imageUrl}
            alt={product.name}
            className="h-12 w-12 rounded-lg object-cover"
            onError={(e) => {
              // Fallback to initial letter if image fails to load
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.nextElementSibling?.classList.remove('hidden');
            }}
          />
          <div className="h-12 w-12 rounded-lg bg-indigo-100 flex items-center justify-center hidden">
            <span className="text-indigo-600 font-bold text-lg">
              {product.name.charAt(0)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base">{product.name}</CardTitle>
            {product.pricing_type && (
              <Badge
                variant={product.pricing_type === 'free' ? 'success' : 'default'}
                className="mt-1"
              >
                {product.pricing_type}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardDescription>
        {truncate(product.tagline || product.description || '', 120)}
      </CardDescription>

      {product.tags && product.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {product.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} size="sm">
              {tag}
            </Badge>
          ))}
        </div>
      )}

      <CardFooter className="text-sm text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            {formatNumber(product.upvotes)}
          </span>
          <span className="flex items-center gap-1">
            <MessageSquare className="h-4 w-4" />
            {formatNumber(product.comments_count)}
          </span>
        </div>
        {product.website_url && (
          <a
            href={product.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-indigo-600 hover:text-indigo-500"
          >
            <ExternalLink className="h-4 w-4" />
            Visit
          </a>
        )}
      </CardFooter>
    </Card>
  );
}
