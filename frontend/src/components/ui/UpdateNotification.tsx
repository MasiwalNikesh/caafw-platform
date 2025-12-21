'use client';

import { RefreshCw, X, Bell } from 'lucide-react';
import { useState, useEffect } from 'react';
import { usePolling } from '@/hooks/usePolling';

interface UpdateNotificationProps {
  className?: string;
}

export function UpdateNotification({ className = '' }: UpdateNotificationProps) {
  const [dismissed, setDismissed] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const { updates, hasNewUpdates, totalNew, refreshData, isPolling } = usePolling({
    enabled: true,
    interval: 30000,
    onNewUpdates: () => {
      setDismissed(false);
      setShowToast(true);
      // Auto-hide toast after 5 seconds
      setTimeout(() => setShowToast(false), 5000);
    },
  });

  const handleRefresh = async () => {
    await refreshData();
    setDismissed(true);
    setShowToast(false);
  };

  if (!hasNewUpdates || dismissed) {
    return null;
  }

  // Build category message
  const categoryMessages: string[] = [];
  if (updates?.categories.jobs) {
    categoryMessages.push(`${updates.categories.jobs} job${updates.categories.jobs > 1 ? 's' : ''}`);
  }
  if (updates?.categories.learning) {
    categoryMessages.push(`${updates.categories.learning} resource${updates.categories.learning > 1 ? 's' : ''}`);
  }
  if (updates?.categories.events) {
    categoryMessages.push(`${updates.categories.events} event${updates.categories.events > 1 ? 's' : ''}`);
  }
  if (updates?.categories.research) {
    categoryMessages.push(`${updates.categories.research} paper${updates.categories.research > 1 ? 's' : ''}`);
  }

  const message = categoryMessages.length > 0
    ? `New content: ${categoryMessages.join(', ')}`
    : `${totalNew} new item${totalNew > 1 ? 's' : ''} available`;

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 max-w-sm animate-in slide-in-from-bottom-4 duration-300 ${className}`}
    >
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 flex items-start gap-3">
        <div className="p-2 bg-purple-100 rounded-lg flex-shrink-0">
          <Bell className="h-5 w-5 text-purple-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">New Updates Available</p>
          <p className="text-sm text-gray-500 mt-0.5 truncate">{message}</p>
          <button
            onClick={handleRefresh}
            disabled={isPolling}
            className="mt-2 inline-flex items-center gap-1.5 text-sm font-medium text-purple-600 hover:text-purple-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isPolling ? 'animate-spin' : ''}`} />
            Refresh to see new content
          </button>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="p-1 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
