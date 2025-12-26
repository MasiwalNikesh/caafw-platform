'use client';

import { useEffect, useState, useCallback } from 'react';
import { sourcesAPI } from '@/lib/adminApi';
import type { APISource, APISourceCreate, APISourceUpdate, SourceType } from '@/types/admin';

const sourceTypes: { value: SourceType; label: string }[] = [
  { value: 'rss', label: 'RSS Feed' },
  { value: 'api', label: 'API' },
  { value: 'scrape', label: 'Web Scrape' },
];

export default function APISourcesPage() {
  const [sources, setSources] = useState<APISource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSource, setEditingSource] = useState<APISource | null>(null);
  const [formData, setFormData] = useState<APISourceCreate>({
    name: '',
    source_type: 'rss',
    url: '',
    is_active: true,
    requires_api_key: false,
    auto_approve: false,
    fetch_frequency: 3600,
  });
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  const [filterType, setFilterType] = useState<SourceType | ''>('');

  const fetchSources = useCallback(async () => {
    try {
      setLoading(true);
      const data = await sourcesAPI.list({
        is_active: filterActive ?? undefined,
        source_type: filterType || undefined,
      });
      setSources(data.items);
    } catch (error) {
      console.error('Failed to fetch sources:', error);
    } finally {
      setLoading(false);
    }
  }, [filterActive, filterType]);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  const openCreateModal = () => {
    setEditingSource(null);
    setFormData({
      name: '',
      source_type: 'rss',
      url: '',
      is_active: true,
      requires_api_key: false,
      auto_approve: false,
      fetch_frequency: 3600,
    });
    setTestResult(null);
    setShowModal(true);
  };

  const openEditModal = (source: APISource) => {
    setEditingSource(source);
    setFormData({
      name: source.name,
      source_type: source.source_type,
      url: source.url,
      is_active: source.is_active,
      requires_api_key: source.requires_api_key,
      auto_approve: source.auto_approve,
      fetch_frequency: source.fetch_frequency,
      config: source.config,
    });
    setTestResult(null);
    setShowModal(true);
  };

  const handleTest = async () => {
    try {
      setTesting(true);
      const result = await sourcesAPI.test({
        url: formData.url,
        source_type: formData.source_type,
        config: formData.config,
      });
      setTestResult(result);
    } catch (error: any) {
      setTestResult({ success: false, message: error.message || 'Test failed' });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      if (editingSource) {
        await sourcesAPI.update(editingSource.id, formData);
      } else {
        await sourcesAPI.create(formData);
      }
      setShowModal(false);
      fetchSources();
    } catch (error) {
      console.error('Failed to save source:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (id: number) => {
    try {
      await sourcesAPI.toggle(id);
      fetchSources();
    } catch (error) {
      console.error('Failed to toggle source:', error);
    }
  };

  const handleFetch = async (id: number) => {
    try {
      await sourcesAPI.fetch(id);
      fetchSources();
    } catch (error) {
      console.error('Failed to fetch from source:', error);
    }
  };

  const handleResetErrors = async (id: number) => {
    try {
      await sourcesAPI.resetErrors(id);
      fetchSources();
    } catch (error) {
      console.error('Failed to reset errors:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this API source?')) return;
    try {
      await sourcesAPI.delete(id);
      fetchSources();
    } catch (error) {
      console.error('Failed to delete source:', error);
    }
  };

  const getStatusColor = (source: APISource) => {
    if (!source.is_active) return 'gray';
    if (source.error_count >= 5) return 'red';
    if (source.error_count > 0) return 'amber';
    return 'green';
  };

  const formatFrequency = (seconds: number) => {
    if (seconds < 3600) return `${Math.round(seconds / 60)} min`;
    if (seconds < 86400) return `${Math.round(seconds / 3600)} hr`;
    return `${Math.round(seconds / 86400)} day`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">API Sources</h1>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700"
        >
          Add Source
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as SourceType | '')}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Types</option>
              {sourceTypes.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filterActive === null ? '' : filterActive.toString()}
              onChange={(e) => setFilterActive(e.target.value === '' ? null : e.target.value === 'true')}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sources List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
          </div>
        ) : sources.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No API sources configured yet
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {sources.map((source) => {
              const statusColor = getStatusColor(source);
              const colorClasses: Record<string, string> = {
                gray: 'bg-gray-100 text-gray-800',
                green: 'bg-green-100 text-green-800',
                amber: 'bg-amber-100 text-amber-800',
                red: 'bg-red-100 text-red-800',
              };

              return (
                <div key={source.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-medium text-gray-900">{source.name}</h3>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${colorClasses[statusColor]}`}>
                          {!source.is_active ? 'Inactive' : source.error_count >= 5 ? 'Error' : source.error_count > 0 ? 'Warning' : 'OK'}
                        </span>
                        <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
                          {sourceTypes.find(t => t.value === source.source_type)?.label}
                        </span>
                        {source.auto_approve && (
                          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
                            Auto-approve
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 mt-1 truncate">{source.url}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                        <span>Fetch: every {formatFrequency(source.fetch_frequency)}</span>
                        <span>Items: {source.items_fetched}</span>
                        {source.last_fetched_at && (
                          <span>Last fetch: {new Date(source.last_fetched_at).toLocaleString()}</span>
                        )}
                        {source.error_count > 0 && (
                          <span className="text-red-500">Errors: {source.error_count}</span>
                        )}
                      </div>
                      {source.last_error && (
                        <p className="text-xs text-red-500 mt-1 truncate">
                          Error: {source.last_error}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleFetch(source.id)}
                        className="p-2 text-gray-400 hover:text-cyan-600"
                        title="Fetch now"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleToggle(source.id)}
                        className={`p-2 ${source.is_active ? 'text-green-600' : 'text-gray-400'} hover:text-gray-600`}
                        title={source.is_active ? 'Deactivate' : 'Activate'}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
                        </svg>
                      </button>
                      {source.error_count > 0 && (
                        <button
                          onClick={() => handleResetErrors(source.id)}
                          className="p-2 text-amber-500 hover:text-amber-700"
                          title="Reset errors"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      )}
                      <button
                        onClick={() => openEditModal(source)}
                        className="p-2 text-gray-400 hover:text-cyan-600"
                        title="Edit"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDelete(source.id)}
                        className="p-2 text-gray-400 hover:text-red-600"
                        title="Delete"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {editingSource ? 'Edit API Source' : 'Add API Source'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={formData.source_type}
                  onChange={(e) => setFormData({ ...formData, source_type: e.target.value as SourceType })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                >
                  {sourceTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fetch Frequency (seconds)</label>
                <input
                  type="number"
                  value={formData.fetch_frequency}
                  onChange={(e) => setFormData({ ...formData, fetch_frequency: Number(e.target.value) })}
                  min="60"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formatFrequency(formData.fetch_frequency || 3600)}
                </p>
              </div>

              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  />
                  <span className="text-sm text-gray-700">Active</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.auto_approve}
                    onChange={(e) => setFormData({ ...formData, auto_approve: e.target.checked })}
                    className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  />
                  <span className="text-sm text-gray-700">Auto-approve content from this source</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.requires_api_key}
                    onChange={(e) => setFormData({ ...formData, requires_api_key: e.target.checked })}
                    className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
                  />
                  <span className="text-sm text-gray-700">Requires API key</span>
                </label>
              </div>

              {/* Test Button */}
              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleTest}
                  disabled={testing || !formData.url}
                  className="w-full px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  {testing ? 'Testing...' : 'Test Connection'}
                </button>
                {testResult && (
                  <div className={`mt-2 p-3 rounded text-sm ${testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                    {testResult.message}
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
