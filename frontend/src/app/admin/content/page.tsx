'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { contentAPI } from '@/lib/adminApi';
import type { ModeratableContent, ContentType, ContentStatus } from '@/types/admin';

const contentTypes: { value: ContentType | ''; label: string }[] = [
  { value: '', label: 'All Types' },
  { value: 'news', label: 'News' },
  { value: 'job', label: 'Jobs' },
  { value: 'product', label: 'Products' },
  { value: 'event', label: 'Events' },
  { value: 'research', label: 'Research' },
];

const statusOptions: { value: ContentStatus | ''; label: string; color: string }[] = [
  { value: '', label: 'All Status', color: 'gray' },
  { value: 'pending', label: 'Pending', color: 'amber' },
  { value: 'approved', label: 'Approved', color: 'green' },
  { value: 'rejected', label: 'Rejected', color: 'red' },
  { value: 'flagged', label: 'Flagged', color: 'orange' },
  { value: 'archived', label: 'Archived', color: 'gray' },
];

export default function ContentModerationPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [content, setContent] = useState<ModeratableContent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState<{ type: ContentType; id: number } | null>(null);

  // Filters from URL
  const typeFilter = (searchParams.get('type') as ContentType) || '';
  const statusFilter = (searchParams.get('status') as ContentStatus) || '';
  const searchQuery = searchParams.get('search') || '';
  const page = parseInt(searchParams.get('page') || '1');

  const fetchContent = useCallback(async () => {
    try {
      setLoading(true);
      const data = await contentAPI.list({
        content_type: typeFilter || undefined,
        status: statusFilter || undefined,
        search: searchQuery || undefined,
        page,
        page_size: 20,
      });
      setContent(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch content:', error);
    } finally {
      setLoading(false);
    }
  }, [typeFilter, statusFilter, searchQuery, page]);

  useEffect(() => {
    fetchContent();
  }, [fetchContent]);

  const updateFilters = (updates: Record<string, string>) => {
    const params = new URLSearchParams(searchParams.toString());
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });
    params.delete('page'); // Reset to page 1 on filter change
    router.push(`/admin/content?${params.toString()}`);
  };

  const handleApprove = async (type: ContentType, id: number) => {
    try {
      setActionLoading(id);
      await contentAPI.approve(type, id);
      fetchContent();
    } catch (error) {
      console.error('Failed to approve:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async () => {
    if (!showRejectModal) return;
    try {
      setActionLoading(showRejectModal.id);
      await contentAPI.reject(showRejectModal.type, showRejectModal.id, rejectReason);
      setShowRejectModal(null);
      setRejectReason('');
      fetchContent();
    } catch (error) {
      console.error('Failed to reject:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleFlag = async (type: ContentType, id: number) => {
    try {
      setActionLoading(id);
      await contentAPI.flag(type, id);
      fetchContent();
    } catch (error) {
      console.error('Failed to flag:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleBulkAction = async (action: 'approve' | 'reject' | 'archive') => {
    if (selectedItems.length === 0 || !typeFilter) return;
    try {
      await contentAPI.bulkAction({
        content_ids: selectedItems,
        content_type: typeFilter,
        action,
      });
      setSelectedItems([]);
      fetchContent();
    } catch (error) {
      console.error('Bulk action failed:', error);
    }
  };

  const getStatusBadge = (status: ContentStatus) => {
    const statusConfig = statusOptions.find(s => s.value === status);
    const colorClasses: Record<string, string> = {
      amber: 'bg-amber-100 text-amber-800',
      green: 'bg-green-100 text-green-800',
      red: 'bg-red-100 text-red-800',
      orange: 'bg-orange-100 text-orange-800',
      gray: 'bg-gray-100 text-gray-800',
    };
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${colorClasses[statusConfig?.color || 'gray']}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Content Moderation</h1>
        {selectedItems.length > 0 && typeFilter && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">{selectedItems.length} selected</span>
            <button
              onClick={() => handleBulkAction('approve')}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
            >
              Approve All
            </button>
            <button
              onClick={() => handleBulkAction('reject')}
              className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reject All
            </button>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
            <select
              value={typeFilter}
              onChange={(e) => updateFilters({ type: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              {contentTypes.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => updateFilters({ status: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              {statusOptions.map((status) => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => updateFilters({ search: e.target.value })}
              placeholder="Search by title..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
        </div>
      </div>

      {/* Content Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
          </div>
        ) : content.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No content found matching your filters
          </div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {typeFilter && (
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedItems.length === content.length}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedItems(content.map((c) => c.id));
                          } else {
                            setSelectedItems([]);
                          }
                        }}
                        className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                      />
                    </th>
                  )}
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {content.map((item) => (
                  <tr key={`${item.content_type}-${item.id}`} className="hover:bg-gray-50">
                    {typeFilter && (
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectedItems.includes(item.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedItems([...selectedItems, item.id]);
                            } else {
                              setSelectedItems(selectedItems.filter((id) => id !== item.id));
                            }
                          }}
                          className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                        />
                      </td>
                    )}
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                        {item.title}
                      </div>
                      {item.rejection_reason && (
                        <p className="text-xs text-red-500 mt-0.5">
                          Reason: {item.rejection_reason}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-500 capitalize">{item.content_type}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-500">{item.source}</span>
                    </td>
                    <td className="px-4 py-3">
                      {getStatusBadge(item.moderation_status)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-500">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {item.moderation_status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(item.content_type, item.id)}
                              disabled={actionLoading === item.id}
                              className="p-1 text-green-600 hover:text-green-800 disabled:opacity-50"
                              title="Approve"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </button>
                            <button
                              onClick={() => setShowRejectModal({ type: item.content_type, id: item.id })}
                              disabled={actionLoading === item.id}
                              className="p-1 text-red-600 hover:text-red-800 disabled:opacity-50"
                              title="Reject"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleFlag(item.content_type, item.id)}
                          disabled={actionLoading === item.id}
                          className="p-1 text-amber-600 hover:text-amber-800 disabled:opacity-50"
                          title="Flag for review"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, total)} of {total} results
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => updateFilters({ page: String(page - 1) })}
                  disabled={page === 1}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 hover:bg-gray-100"
                >
                  Previous
                </button>
                <button
                  onClick={() => updateFilters({ page: String(page + 1) })}
                  disabled={page * 20 >= total}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 hover:bg-gray-100"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Reject Content</h3>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Enter reason for rejection (optional)"
              className="w-full border border-gray-300 rounded-md px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              rows={3}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(null);
                  setRejectReason('');
                }}
                className="px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
