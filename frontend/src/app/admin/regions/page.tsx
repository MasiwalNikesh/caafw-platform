'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { regionsAPI, regionalContentAPI } from '@/lib/adminApi';
import type {
  RegionWithChildren,
  RegionalContent,
  RegionalContentCreate,
  RegionalContentType,
  ContentStatus,
} from '@/types/admin';

const contentTypes: { value: RegionalContentType | ''; label: string }[] = [
  { value: '', label: 'All Types' },
  { value: 'job', label: 'Jobs' },
  { value: 'event', label: 'Events' },
  { value: 'news', label: 'News' },
  { value: 'product', label: 'Products' },
  { value: 'research', label: 'Research' },
  { value: 'learning', label: 'Learning' },
  { value: 'announcement', label: 'Announcements' },
  { value: 'other', label: 'Other' },
];

const statusOptions: { value: ContentStatus | ''; label: string; color: string }[] = [
  { value: '', label: 'All Status', color: 'gray' },
  { value: 'pending', label: 'Pending', color: 'amber' },
  { value: 'approved', label: 'Approved', color: 'green' },
  { value: 'rejected', label: 'Rejected', color: 'red' },
  { value: 'flagged', label: 'Flagged', color: 'orange' },
  { value: 'archived', label: 'Archived', color: 'gray' },
];

export default function RegionalContentPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Region tree state
  const [regions, setRegions] = useState<RegionWithChildren[]>([]);
  const [regionsLoading, setRegionsLoading] = useState(true);

  // Content state
  const [content, setContent] = useState<RegionalContent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  // UI state
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingItem, setEditingItem] = useState<RegionalContent | null>(null);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // Filters from URL
  const regionId = searchParams.get('region') ? parseInt(searchParams.get('region')!) : undefined;
  const typeFilter = (searchParams.get('type') as RegionalContentType) || '';
  const statusFilter = (searchParams.get('status') as ContentStatus) || '';
  const searchQuery = searchParams.get('search') || '';
  const page = parseInt(searchParams.get('page') || '1');

  // Fetch regions tree
  useEffect(() => {
    const fetchRegions = async () => {
      try {
        setRegionsLoading(true);
        const data = await regionsAPI.getTree({ is_active: true });
        setRegions(data.regions);
      } catch (error) {
        console.error('Failed to fetch regions:', error);
      } finally {
        setRegionsLoading(false);
      }
    };
    fetchRegions();
  }, []);

  // Fetch content
  const fetchContent = useCallback(async () => {
    try {
      setLoading(true);
      const data = await regionalContentAPI.list({
        region_id: regionId,
        content_type: typeFilter || undefined,
        moderation_status: statusFilter || undefined,
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
  }, [regionId, typeFilter, statusFilter, searchQuery, page]);

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
    params.delete('page');
    router.push(`/admin/regions?${params.toString()}`);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    try {
      setActionLoading(id);
      await regionalContentAPI.delete(id);
      fetchContent();
    } catch (error) {
      console.error('Failed to delete:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleStatusUpdate = async (id: number, status: ContentStatus) => {
    try {
      setActionLoading(id);
      await regionalContentAPI.updateStatus(id, { status });
      fetchContent();
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedItems.length === 0) return;
    if (!confirm(`Delete ${selectedItems.length} items?`)) return;
    try {
      await regionalContentAPI.bulkDelete({ ids: selectedItems });
      setSelectedItems([]);
      fetchContent();
    } catch (error) {
      console.error('Bulk delete failed:', error);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await regionalContentAPI.exportCsv({
        region_id: regionId,
        content_type: typeFilter || undefined,
      });
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `regional_content_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const getStatusBadge = (status: ContentStatus) => {
    const colorClasses: Record<string, string> = {
      pending: 'bg-amber-100 text-amber-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      flagged: 'bg-orange-100 text-orange-800',
      archived: 'bg-gray-100 text-gray-800',
    };
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${colorClasses[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  // Flatten region tree for dropdown
  const flattenRegions = (items: RegionWithChildren[], level = 0): { id: number; name: string; level: number }[] => {
    const result: { id: number; name: string; level: number }[] = [];
    items.forEach(item => {
      result.push({ id: item.id, name: item.name, level });
      if (item.children?.length) {
        result.push(...flattenRegions(item.children, level + 1));
      }
    });
    return result;
  };

  const flatRegions = flattenRegions(regions);
  const totalPages = Math.ceil(total / 20);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Regional Content</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage region-specific content entries
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExport}
            className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Export CSV
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add Content
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Region Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
            <select
              value={regionId || ''}
              onChange={(e) => updateFilters({ region: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              disabled={regionsLoading}
            >
              <option value="">All Regions</option>
              {flatRegions.map(r => (
                <option key={r.id} value={r.id}>
                  {'  '.repeat(r.level)}{r.name}
                </option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
            <select
              value={typeFilter}
              onChange={(e) => updateFilters({ type: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              {contentTypes.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => updateFilters({ status: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              {statusOptions.map(s => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search by title..."
              value={searchQuery}
              onChange={(e) => updateFilters({ search: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4 flex justify-between items-center">
          <span className="text-sm text-blue-800">
            {selectedItems.length} items selected
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedItems([])}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              Clear
            </button>
            <button
              onClick={handleBulkDelete}
              className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
            >
              Delete Selected
            </button>
          </div>
        </div>
      )}

      {/* Content Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : content.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No content found. Click &quot;Add Content&quot; to create your first entry.
          </div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedItems.length === content.length && content.length > 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedItems(content.map(c => c.id));
                        } else {
                          setSelectedItems([]);
                        }
                      }}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Region</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {content.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedItems.includes(item.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedItems([...selectedItems, item.id]);
                          } else {
                            setSelectedItems(selectedItems.filter(id => id !== item.id));
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                        {item.title}
                      </div>
                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          {new URL(item.url).hostname}
                        </a>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600">
                        {item.region?.name || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-800 rounded">
                        {item.content_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {getStatusBadge(item.moderation_status)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-1">
                        {item.moderation_status === 'pending' && (
                          <button
                            onClick={() => handleStatusUpdate(item.id, 'approved')}
                            disabled={actionLoading === item.id}
                            className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                          >
                            Approve
                          </button>
                        )}
                        <button
                          onClick={() => setEditingItem(item)}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          disabled={actionLoading === item.id}
                          className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 disabled:opacity-50"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-4 py-3 border-t flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, total)} of {total}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => updateFilters({ page: String(page - 1) })}
                    disabled={page === 1}
                    className="px-3 py-1 text-sm border rounded disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => updateFilters({ page: String(page + 1) })}
                    disabled={page >= totalPages}
                    className="px-3 py-1 text-sm border rounded disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingItem) && (
        <ContentModal
          item={editingItem}
          regions={flatRegions}
          onClose={() => {
            setShowAddModal(false);
            setEditingItem(null);
          }}
          onSave={() => {
            setShowAddModal(false);
            setEditingItem(null);
            fetchContent();
          }}
        />
      )}
    </div>
  );
}

// Content Modal Component
function ContentModal({
  item,
  regions,
  onClose,
  onSave,
}: {
  item: RegionalContent | null;
  regions: { id: number; name: string; level: number }[];
  onClose: () => void;
  onSave: () => void;
}) {
  const [formData, setFormData] = useState<RegionalContentCreate>({
    region_id: item?.region_id || (regions[0]?.id || 0),
    content_type: item?.content_type || 'announcement',
    title: item?.title || '',
    description: item?.description || '',
    url: item?.url || '',
    image_url: item?.image_url || '',
    is_active: item?.is_active ?? true,
    is_featured: item?.is_featured ?? false,
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      if (item) {
        await regionalContentAPI.update(item.id, formData);
      } else {
        await regionalContentAPI.create(formData);
      }
      onSave();
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-lg font-bold mb-4">
            {item ? 'Edit Content' : 'Add Content'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Region *</label>
              <select
                value={formData.region_id}
                onChange={(e) => setFormData({ ...formData, region_id: parseInt(e.target.value) })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                required
              >
                {regions.map(r => (
                  <option key={r.id} value={r.id}>
                    {'  '.repeat(r.level)}{r.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content Type *</label>
              <select
                value={formData.content_type}
                onChange={(e) => setFormData({ ...formData, content_type: e.target.value as RegionalContentType })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                required
              >
                {contentTypes.filter(t => t.value).map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
              <input
                type="url"
                value={formData.url || ''}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="https://..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
              <input
                type="url"
                value={formData.image_url || ''}
                onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="https://..."
              />
            </div>

            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Active</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_featured}
                  onChange={(e) => setFormData({ ...formData, is_featured: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Featured</span>
              </label>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : item ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
