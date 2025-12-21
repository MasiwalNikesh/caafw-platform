'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

interface UpdatesResponse {
  has_updates: boolean;
  total_new: number;
  categories: {
    jobs: number;
    learning: number;
    events: number;
    research: number;
  };
  checked_at: string;
  since: string;
}

interface UsePollingOptions {
  enabled?: boolean;
  interval?: number; // in milliseconds
  onNewUpdates?: (updates: UpdatesResponse) => void;
}

export function usePolling(options: UsePollingOptions = {}) {
  const {
    enabled = true,
    interval = 30000, // 30 seconds default
    onNewUpdates,
  } = options;

  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [updates, setUpdates] = useState<UpdatesResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const queryClient = useQueryClient();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const checkForUpdates = useCallback(async () => {
    if (!enabled) return;

    try {
      setIsPolling(true);
      const response = await api.get<UpdatesResponse>('/updates/check', {
        params: { since: lastChecked },
      });

      const data = response.data;
      setUpdates(data);
      setLastChecked(data.checked_at);

      if (data.has_updates && onNewUpdates) {
        onNewUpdates(data);
      }

      return data;
    } catch (error) {
      console.error('Failed to check for updates:', error);
      return null;
    } finally {
      setIsPolling(false);
    }
  }, [enabled, lastChecked, onNewUpdates]);

  const refreshData = useCallback(async () => {
    // Invalidate all relevant queries to trigger refetch
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['jobs'] }),
      queryClient.invalidateQueries({ queryKey: ['learning'] }),
      queryClient.invalidateQueries({ queryKey: ['events'] }),
      queryClient.invalidateQueries({ queryKey: ['research'] }),
    ]);

    // Reset updates after refresh
    setUpdates(null);
  }, [queryClient]);

  // Start polling
  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Initial check
    checkForUpdates();

    // Set up interval
    intervalRef.current = setInterval(checkForUpdates, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, interval, checkForUpdates]);

  return {
    updates,
    isPolling,
    lastChecked,
    checkForUpdates,
    refreshData,
    hasNewUpdates: updates?.has_updates || false,
    totalNew: updates?.total_new || 0,
  };
}
