'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { dashboardAPI } from '@/lib/adminApi';
import type {
  DashboardStats,
  DashboardResponse,
  PendingReviewItem,
  RecentActivity,
  SourceHealth,
} from '@/types/admin';

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pendingReview, setPendingReview] = useState<PendingReviewItem[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [sourceHealth, setSourceHealth] = useState<SourceHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [statsResponse, pendingData, activityData, healthData] = await Promise.all([
          dashboardAPI.getStats(),
          dashboardAPI.getPendingReview(10),
          dashboardAPI.getRecentActivity(10),
          dashboardAPI.getSourceHealth(),
        ]);
        // Handle both direct stats or wrapped in DashboardResponse
        const response = statsResponse as DashboardResponse;
        const statsData: DashboardStats = response.stats ? response.stats : response as unknown as DashboardStats;
        setStats(statsData);
        setPendingReview(pendingData || []);
        setRecentActivity(activityData || []);
        setSourceHealth(healthData || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  const contentTypeLabels: Record<string, string> = {
    news: 'News',
    jobs: 'Jobs',
    products: 'Products',
    events: 'Events',
    research: 'Research',
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Pending Review */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pending Review</p>
              <p className="text-2xl font-bold text-amber-600">
                {stats?.pending_review.total || 0}
              </p>
            </div>
            <div className="p-3 bg-amber-100 rounded-full">
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <Link href="/admin/content?status=pending" className="text-sm text-cyan-600 hover:underline mt-2 block">
            View all pending
          </Link>
        </div>

        {/* Total Users */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.total_users || 0}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
          <p className="text-sm text-green-600 mt-2">
            +{stats?.new_users_today || 0} today
          </p>
        </div>

        {/* Active Sources */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Sources</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.api_sources.active || 0}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
            </div>
          </div>
          {(stats?.api_sources.with_errors || 0) > 0 && (
            <p className="text-sm text-red-600 mt-2">
              {stats?.api_sources.with_errors} with errors
            </p>
          )}
        </div>

        {/* Total Content */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Content</p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.values(stats?.total_content || {}).reduce((a, b) => a + b, 0)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Content Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Content by Type</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(stats?.total_content || {}).map(([type, count]) => (
            <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{count}</p>
              <p className="text-sm text-gray-500 capitalize">{type}</p>
              {stats?.pending_review[type as keyof typeof stats.pending_review] ? (
                <span className="inline-block mt-1 px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full">
                  {stats.pending_review[type as keyof typeof stats.pending_review]} pending
                </span>
              ) : null}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Review Items */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Pending Review</h2>
            <Link href="/admin/content?status=pending" className="text-sm text-cyan-600 hover:underline">
              View all
            </Link>
          </div>
          {pendingReview.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No items pending review</p>
          ) : (
            <div className="space-y-3">
              {pendingReview.map((item) => (
                <div key={`${item.content_type}-${item.id}`} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
                    <p className="text-xs text-gray-500">
                      {contentTypeLabels[item.content_type]} from {item.source}
                    </p>
                  </div>
                  <Link
                    href={`/admin/content?type=${item.content_type}&id=${item.id}`}
                    className="ml-4 px-3 py-1 text-xs font-medium text-cyan-600 bg-cyan-50 rounded-full hover:bg-cyan-100"
                  >
                    Review
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
            <Link href="/admin/audit" className="text-sm text-cyan-600 hover:underline">
              View all
            </Link>
          </div>
          {recentActivity.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((item) => (
                <div key={item.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-600">
                      {item.admin_name?.[0]?.toUpperCase() || 'A'}
                    </span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">{item.admin_name || 'Admin'}</span>
                      {' '}{item.action.replace(/_/g, ' ')}{' '}
                      <span className="text-gray-500">{item.entity_type} #{item.entity_id}</span>
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Source Health */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">API Source Health</h2>
          <Link href="/admin/sources" className="text-sm text-cyan-600 hover:underline">
            Manage sources
          </Link>
        </div>
        {sourceHealth.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No API sources configured</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sourceHealth.map((source) => (
              <div
                key={source.id}
                className={`p-4 rounded-lg border ${
                  source.status === 'ok'
                    ? 'border-green-200 bg-green-50'
                    : source.status === 'warning'
                    ? 'border-amber-200 bg-amber-50'
                    : 'border-red-200 bg-red-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{source.name}</span>
                  <span
                    className={`px-2 py-0.5 text-xs rounded-full ${
                      source.status === 'ok'
                        ? 'bg-green-200 text-green-800'
                        : source.status === 'warning'
                        ? 'bg-amber-200 text-amber-800'
                        : 'bg-red-200 text-red-800'
                    }`}
                  >
                    {source.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Last fetched: {source.last_fetched_at
                    ? new Date(source.last_fetched_at).toLocaleString()
                    : 'Never'}
                </p>
                {source.error_count > 0 && (
                  <p className="text-xs text-red-600 mt-1">
                    {source.error_count} errors
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
