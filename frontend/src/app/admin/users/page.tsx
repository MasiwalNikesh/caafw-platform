'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { usersAPI } from '@/lib/adminApi';
import type { AdminUser, UserRole } from '@/types/admin';

const roleOptions: { value: UserRole | ''; label: string; color: string }[] = [
  { value: '', label: 'All Roles', color: 'gray' },
  { value: 'user', label: 'User', color: 'gray' },
  { value: 'moderator', label: 'Moderator', color: 'blue' },
  { value: 'admin', label: 'Admin', color: 'purple' },
  { value: 'super_admin', label: 'Super Admin', color: 'red' },
];

export default function UsersManagementPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [showBanModal, setShowBanModal] = useState<AdminUser | null>(null);
  const [banReason, setBanReason] = useState('');
  const [showRoleModal, setShowRoleModal] = useState<AdminUser | null>(null);
  const [newRole, setNewRole] = useState<UserRole>('user');

  // Filters from URL
  const searchQuery = searchParams.get('search') || '';
  const roleFilter = (searchParams.get('role') as UserRole) || '';
  const activeFilter = searchParams.get('active');
  const bannedFilter = searchParams.get('banned');
  const page = parseInt(searchParams.get('page') || '1');

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await usersAPI.list({
        search: searchQuery || undefined,
        role: roleFilter || undefined,
        is_active: activeFilter === 'true' ? true : activeFilter === 'false' ? false : undefined,
        is_banned: bannedFilter === 'true' ? true : bannedFilter === 'false' ? false : undefined,
        page,
        page_size: 20,
      });
      setUsers(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, roleFilter, activeFilter, bannedFilter, page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

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
    router.push(`/admin/users?${params.toString()}`);
  };

  const handleBan = async () => {
    if (!showBanModal) return;
    try {
      setActionLoading(showBanModal.id);
      await usersAPI.ban(showBanModal.id, { reason: banReason });
      setShowBanModal(null);
      setBanReason('');
      fetchUsers();
    } catch (error) {
      console.error('Failed to ban user:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleUnban = async (userId: number) => {
    try {
      setActionLoading(userId);
      await usersAPI.unban(userId);
      fetchUsers();
    } catch (error) {
      console.error('Failed to unban user:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleActivate = async (userId: number) => {
    try {
      setActionLoading(userId);
      await usersAPI.activate(userId);
      fetchUsers();
    } catch (error) {
      console.error('Failed to activate user:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeactivate = async (userId: number) => {
    try {
      setActionLoading(userId);
      await usersAPI.deactivate(userId);
      fetchUsers();
    } catch (error) {
      console.error('Failed to deactivate user:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRoleChange = async () => {
    if (!showRoleModal) return;
    try {
      setActionLoading(showRoleModal.id);
      await usersAPI.updateRole(showRoleModal.id, { role: newRole });
      setShowRoleModal(null);
      fetchUsers();
    } catch (error) {
      console.error('Failed to change role:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const getRoleBadge = (role: UserRole) => {
    const roleConfig = roleOptions.find(r => r.value === role);
    const colorClasses: Record<string, string> = {
      gray: 'bg-gray-100 text-gray-800',
      blue: 'bg-blue-100 text-blue-800',
      purple: 'bg-purple-100 text-purple-800',
      red: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${colorClasses[roleConfig?.color || 'gray']}`}>
        {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Users Management</h1>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => updateFilters({ search: e.target.value })}
              placeholder="Search by email or name..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select
              value={roleFilter}
              onChange={(e) => updateFilters({ role: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              {roleOptions.map((role) => (
                <option key={role.value} value={role.value}>{role.label}</option>
              ))}
            </select>
          </div>

          <div className="flex items-end space-x-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={bannedFilter === 'true'}
                onChange={(e) => updateFilters({ banned: e.target.checked ? 'true' : '' })}
                className="rounded border-gray-300 text-cyan-600 focus:ring-cyan-500"
              />
              <span className="text-sm text-gray-700">Banned only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No users found matching your filters
          </div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Joined
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                          {user.avatar_url ? (
                            <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />
                          ) : (
                            <span className="text-sm font-medium text-gray-600">
                              {user.name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                            </span>
                          )}
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">{user.name || 'No name'}</p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {getRoleBadge(user.role)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col space-y-1">
                        {user.is_banned ? (
                          <span className="px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded-full w-fit">
                            Banned
                          </span>
                        ) : user.is_active ? (
                          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded-full w-fit">
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-800 rounded-full w-fit">
                            Inactive
                          </span>
                        )}
                        {user.is_verified && (
                          <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full w-fit">
                            Verified
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {user.last_login_at
                        ? new Date(user.last_login_at).toLocaleDateString()
                        : 'Never'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setShowRoleModal(user);
                            setNewRole(user.role);
                          }}
                          disabled={actionLoading === user.id}
                          className="p-1 text-gray-400 hover:text-purple-600 disabled:opacity-50"
                          title="Change role"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                        </button>

                        {user.is_banned ? (
                          <button
                            onClick={() => handleUnban(user.id)}
                            disabled={actionLoading === user.id}
                            className="p-1 text-green-600 hover:text-green-800 disabled:opacity-50"
                            title="Unban user"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>
                        ) : (
                          <button
                            onClick={() => setShowBanModal(user)}
                            disabled={actionLoading === user.id}
                            className="p-1 text-red-600 hover:text-red-800 disabled:opacity-50"
                            title="Ban user"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                            </svg>
                          </button>
                        )}

                        {user.is_active ? (
                          <button
                            onClick={() => handleDeactivate(user.id)}
                            disabled={actionLoading === user.id}
                            className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                            title="Deactivate user"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>
                        ) : (
                          <button
                            onClick={() => handleActivate(user.id)}
                            disabled={actionLoading === user.id}
                            className="p-1 text-green-600 hover:text-green-800 disabled:opacity-50"
                            title="Activate user"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, total)} of {total} users
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

      {/* Ban Modal */}
      {showBanModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Ban User</h3>
            <p className="text-sm text-gray-500 mb-4">
              You are about to ban <strong>{showBanModal.email}</strong>. This will prevent them from accessing the platform.
            </p>
            <textarea
              value={banReason}
              onChange={(e) => setBanReason(e.target.value)}
              placeholder="Enter reason for ban..."
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              rows={3}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowBanModal(null);
                  setBanReason('');
                }}
                className="px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={handleBan}
                disabled={!banReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                Ban User
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Role Change Modal */}
      {showRoleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Change User Role</h3>
            <p className="text-sm text-gray-500 mb-4">
              Change role for <strong>{showRoleModal.email}</strong>
            </p>
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value as UserRole)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              {roleOptions.filter(r => r.value).map((role) => (
                <option key={role.value} value={role.value}>{role.label}</option>
              ))}
            </select>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowRoleModal(null)}
                className="px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={handleRoleChange}
                className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700"
              >
                Update Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
