'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bookmark, BookmarkCheck, Loader2 } from 'lucide-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { bookmarksAPI, BookmarkContentType } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface BookmarkButtonProps {
  contentType: BookmarkContentType;
  contentId: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'icon' | 'button';
  showText?: boolean;
}

export function BookmarkButton({
  contentType,
  contentId,
  className = '',
  size = 'md',
  variant = 'icon',
  showText = false,
}: BookmarkButtonProps) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [optimisticBookmarked, setOptimisticBookmarked] = useState<boolean | null>(null);

  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  const buttonSizeClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-2.5',
  };

  // Check if bookmarked
  const { data: bookmarkStatus, isLoading: checking } = useQuery({
    queryKey: ['bookmark-check', contentType, contentId],
    queryFn: () => bookmarksAPI.check(contentType, contentId),
    enabled: isAuthenticated,
    staleTime: 30000,
  });

  const isBookmarked = optimisticBookmarked ?? bookmarkStatus?.is_bookmarked ?? false;

  // Create bookmark mutation
  const createMutation = useMutation({
    mutationFn: () => bookmarksAPI.create({ content_type: contentType, content_id: contentId }),
    onMutate: () => {
      setOptimisticBookmarked(true);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmark-check', contentType, contentId] });
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
    },
    onError: () => {
      setOptimisticBookmarked(null);
    },
  });

  // Delete bookmark mutation
  const deleteMutation = useMutation({
    mutationFn: () => bookmarksAPI.deleteByContent(contentType, contentId),
    onMutate: () => {
      setOptimisticBookmarked(false);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmark-check', contentType, contentId] });
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
    },
    onError: () => {
      setOptimisticBookmarked(null);
    },
  });

  const isLoading = createMutation.isPending || deleteMutation.isPending;

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isBookmarked) {
      deleteMutation.mutate();
    } else {
      createMutation.mutate();
    }
  };

  if (variant === 'button') {
    return (
      <motion.button
        onClick={handleClick}
        disabled={isLoading || checking}
        whileTap={{ scale: 0.95 }}
        className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all ${
          isBookmarked
            ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-900/50'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
        } ${className}`}
      >
        {isLoading ? (
          <Loader2 className={`${sizeClasses[size]} animate-spin`} />
        ) : isBookmarked ? (
          <BookmarkCheck className={sizeClasses[size]} />
        ) : (
          <Bookmark className={sizeClasses[size]} />
        )}
        {showText && (isBookmarked ? 'Saved' : 'Save')}
      </motion.button>
    );
  }

  return (
    <motion.button
      onClick={handleClick}
      disabled={isLoading || checking}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className={`${buttonSizeClasses[size]} rounded-full transition-all ${
        isBookmarked
          ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-gray-200'
      } ${className}`}
      title={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
    >
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
          >
            <Loader2 className={`${sizeClasses[size]} animate-spin`} />
          </motion.div>
        ) : isBookmarked ? (
          <motion.div
            key="bookmarked"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
          >
            <BookmarkCheck className={`${sizeClasses[size]} fill-current`} />
          </motion.div>
        ) : (
          <motion.div
            key="not-bookmarked"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
          >
            <Bookmark className={sizeClasses[size]} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}

