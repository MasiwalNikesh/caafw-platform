'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ExternalLink, Star, MessageSquare, Package, Sparkles, X } from 'lucide-react';
import { productsAPI } from '@/lib/api';
import { Product, PaginatedResponse } from '@/types';
import { formatNumber, formatRelativeTime, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [pricingFilter, setPricingFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [tagFilter, setTagFilter] = useState<string>('');

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['product-categories'],
    queryFn: () => productsAPI.categories(),
  });

  // Fetch popular tags
  const { data: popularTags } = useQuery({
    queryKey: ['product-tags'],
    queryFn: () => productsAPI.tags(15),
  });

  const { data, isLoading } = useQuery<PaginatedResponse<Product>>({
    queryKey: ['products', page, search, pricingFilter, categoryFilter, tagFilter],
    queryFn: () =>
      productsAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        pricing_type: pricingFilter || undefined,
        category: categoryFilter || undefined,
        tag: tagFilter || undefined,
      }),
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-600 to-blue-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-blue-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Package className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              AI Products
            </h1>
          </div>
          <p className="text-lg text-blue-100 max-w-2xl">
            Discover the latest AI tools and products from Product Hunt and more
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Products
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Free & Paid Options
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Trending Tools
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Filters Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex flex-col gap-4">
            {/* Primary filters row */}
            <div className="flex flex-col sm:flex-row gap-4">
              <SearchInput
                value={search}
                onChange={setSearch}
                placeholder="Search products..."
                className="flex-1 max-w-md"
              />
              {categories && categories.length > 0 && (
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat.slug} value={cat.slug}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              )}
              <select
                value={pricingFilter}
                onChange={(e) => setPricingFilter(e.target.value)}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Pricing</option>
                <option value="free">Free</option>
                <option value="freemium">Freemium</option>
                <option value="paid">Paid</option>
              </select>
            </div>

            {/* Tag filter chips */}
            {popularTags && popularTags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-gray-500 py-1">Tags:</span>
                {popularTags.map((tag) => (
                  <button
                    key={tag.name}
                    onClick={() => setTagFilter(tagFilter === tag.name ? '' : tag.name)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                      tagFilter === tag.name
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {tag.name}
                    {tagFilter === tag.name && <X className="inline h-3 w-3 ml-1" />}
                  </button>
                ))}
              </div>
            )}

            {/* Active filters indicator */}
            {(categoryFilter || tagFilter || pricingFilter) && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Active filters:</span>
                {categoryFilter && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                    Category: {categories?.find(c => c.slug === categoryFilter)?.name}
                    <button onClick={() => setCategoryFilter('')} className="hover:text-blue-900">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {tagFilter && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                    Tag: {tagFilter}
                    <button onClick={() => setTagFilter('')} className="hover:text-blue-900">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {pricingFilter && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                    {pricingFilter}
                    <button onClick={() => setPricingFilter('')} className="hover:text-blue-900">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}
                <button
                  onClick={() => {
                    setCategoryFilter('');
                    setTagFilter('');
                    setPricingFilter('');
                  }}
                  className="text-xs text-gray-500 hover:text-gray-700 underline"
                >
                  Clear all
                </button>
              </div>
            )}
          </div>
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
              <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
                <Package className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No products found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
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
    <div className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
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
        <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center hidden">
          <span className="text-blue-600 font-bold text-lg">
            {product.name.charAt(0)}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900">{product.name}</h3>
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

      <p className="mt-4 text-sm text-gray-600 line-clamp-2">
        {truncate(product.tagline || product.description || '', 120)}
      </p>

      {product.tags && product.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {product.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center gap-4 text-sm text-gray-500">
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
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-blue-500/25"
          >
            Visit
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        )}
      </div>
    </div>
  );
}
