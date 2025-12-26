'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import {
  Route,
  Clock,
  BookOpen,
  Star,
  ArrowLeft,
  Play,
  Check,
  CheckCircle2,
  ExternalLink,
  Trophy,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { learningPathsAPI } from '@/lib/api';
import { LearningPathDetail, LearningResource } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedLink } from '@/components/ui/ProtectedLink';
import { formatNumber } from '@/lib/utils';

const levelColors: Record<string, string> = {
  novice: 'bg-green-100 text-green-700 border-green-200',
  beginner: 'bg-blue-100 text-blue-700 border-blue-200',
  intermediate: 'bg-purple-100 text-purple-700 border-purple-200',
  expert: 'bg-red-100 text-red-700 border-red-200',
};

const levelLabels: Record<string, string> = {
  novice: 'Novice',
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  expert: 'Expert',
};

export default function LearningPathDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathId = parseInt(params.id as string);
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const { data: path, isLoading, error } = useQuery<LearningPathDetail>({
    queryKey: ['learning-path', pathId],
    queryFn: () => learningPathsAPI.get(pathId),
    enabled: !isNaN(pathId),
  });

  const startMutation = useMutation({
    mutationFn: () => learningPathsAPI.start(pathId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-path', pathId] });
      queryClient.invalidateQueries({ queryKey: ['my-learning-progress'] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: (resourceId: number) => learningPathsAPI.completeResource(pathId, resourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-path', pathId] });
      queryClient.invalidateQueries({ queryKey: ['my-learning-progress'] });
    },
  });

  const resetMutation = useMutation({
    mutationFn: () => learningPathsAPI.resetProgress(pathId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-path', pathId] });
      queryClient.invalidateQueries({ queryKey: ['my-learning-progress'] });
    },
  });

  const handleStart = () => {
    if (!isAuthenticated) {
      router.push(`/login?returnUrl=/learning-paths/${pathId}`);
      return;
    }
    startMutation.mutate();
  };

  const handleComplete = (resourceId: number) => {
    completeMutation.mutate(resourceId);
  };

  const handleReset = () => {
    if (confirm('Are you sure you want to reset your progress on this path?')) {
      resetMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white pt-24">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-48 bg-gray-200 rounded" />
            <div className="h-12 w-3/4 bg-gray-200 rounded" />
            <div className="h-24 bg-gray-200 rounded" />
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-24 bg-gray-200 rounded-xl" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !path) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white pt-24">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
          <Route className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Learning Path Not Found</h1>
          <p className="text-gray-500 mb-6">The learning path you're looking for doesn't exist.</p>
          <Link
            href="/learning-paths"
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Learning Paths
          </Link>
        </div>
      </div>
    );
  }

  const progress = path.user_progress;
  const completedIds = progress?.completed_resource_ids || [];
  const isStarted = !!progress;
  const isCompleted = progress?.completed_at != null;
  const progressPercent = progress?.progress_percentage || 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <Link
            href="/learning-paths"
            className="inline-flex items-center gap-2 text-indigo-200 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Learning Paths
          </Link>

          <div className="flex items-center gap-3 mb-4">
            {path.is_featured && (
              <Star className="h-5 w-5 text-yellow-400 fill-yellow-400" />
            )}
            <span className={`px-3 py-1 rounded-full text-sm font-medium border ${levelColors[path.level]}`}>
              {levelLabels[path.level]}
            </span>
            {isCompleted && (
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700 border border-green-200 flex items-center gap-1">
                <Trophy className="h-4 w-4" />
                Completed
              </span>
            )}
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            {path.title}
          </h1>

          <p className="text-lg text-indigo-100 max-w-2xl mb-6">
            {path.description}
          </p>

          <div className="flex flex-wrap items-center gap-4 text-indigo-100">
            <span className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              {path.resource_count} resources
            </span>
            {path.duration_hours && (
              <span className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                ~{path.duration_hours} hours
              </span>
            )}
          </div>

          {path.topics && path.topics.length > 0 && (
            <div className="mt-6 flex flex-wrap gap-2">
              {path.topics.map((topic) => (
                <span
                  key={topic}
                  className="px-3 py-1 bg-white/10 text-white rounded-full text-sm backdrop-blur-sm"
                >
                  {topic}
                </span>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Progress Bar */}
      {isStarted && (
        <div className="bg-white border-b border-gray-100 sticky top-16 z-10">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                Your Progress
              </span>
              <span className="text-sm font-bold text-indigo-600">
                {progressPercent}% Complete
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
              <span>{completedIds.length} of {path.resource_count} resources completed</span>
              <button
                onClick={handleReset}
                className="flex items-center gap-1 text-gray-400 hover:text-red-500 transition-colors"
              >
                <RotateCcw className="h-3 w-3" />
                Reset Progress
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Start Button */}
        {!isStarted && (
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100 p-6 mb-8 text-center">
            <Sparkles className="h-8 w-8 text-indigo-600 mx-auto mb-3" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Ready to start your journey?
            </h2>
            <p className="text-gray-600 mb-4">
              Begin this learning path to track your progress and stay motivated.
            </p>
            <button
              onClick={handleStart}
              disabled={startMutation.isPending}
              className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              <Play className="h-5 w-5" />
              {startMutation.isPending ? 'Starting...' : 'Start Learning Path'}
            </button>
          </div>
        )}

        {/* Resources List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Learning Resources
          </h2>

          {path.resources.map((resource, index) => {
            const isResourceCompleted = completedIds.includes(resource.id);
            const isCurrent = progress?.current_resource_id === resource.id;

            return (
              <ResourceCard
                key={resource.id}
                resource={resource}
                index={index + 1}
                isCompleted={isResourceCompleted}
                isCurrent={isCurrent}
                isStarted={isStarted}
                onComplete={() => handleComplete(resource.id)}
                isCompleting={completeMutation.isPending}
              />
            );
          })}
        </div>

        {/* Completion Message */}
        {isCompleted && (
          <div className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border border-green-100 p-8 text-center">
            <Trophy className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Congratulations!
            </h2>
            <p className="text-gray-600 mb-4">
              You've completed this learning path. Keep up the great work!
            </p>
            <Link
              href="/learning-paths"
              className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
            >
              Explore More Paths
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

function ResourceCard({
  resource,
  index,
  isCompleted,
  isCurrent,
  isStarted,
  onComplete,
  isCompleting,
}: {
  resource: LearningResource;
  index: number;
  isCompleted: boolean;
  isCurrent: boolean;
  isStarted: boolean;
  onComplete: () => void;
  isCompleting: boolean;
}) {
  const formatDuration = (minutes?: number) => {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return (
    <div
      className={`bg-white rounded-xl border p-5 transition-all ${
        isCompleted
          ? 'border-green-200 bg-green-50/30'
          : isCurrent
          ? 'border-indigo-200 ring-2 ring-indigo-500/20'
          : 'border-gray-100 hover:border-gray-200'
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Step Number / Check */}
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm ${
            isCompleted
              ? 'bg-green-500 text-white'
              : isCurrent
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-500'
          }`}
        >
          {isCompleted ? <Check className="h-5 w-5" /> : index}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-semibold text-gray-900 line-clamp-1">
                  {resource.title}
                </h3>
                {isCurrent && !isCompleted && (
                  <Badge variant="info" className="text-xs">Current</Badge>
                )}
              </div>

              <div className="mt-1 flex items-center gap-3 text-sm text-gray-500 flex-wrap">
                <span className="capitalize">{resource.resource_type}</span>
                {resource.provider && (
                  <span>by {resource.provider}</span>
                )}
                {resource.duration_minutes && (
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {formatDuration(resource.duration_minutes)}
                  </span>
                )}
                {resource.rating && (
                  <span className="flex items-center gap-1">
                    <Star className="h-3.5 w-3.5 text-yellow-400 fill-yellow-400" />
                    {resource.rating.toFixed(1)}
                  </span>
                )}
              </div>

              <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                {resource.description}
              </p>

              {/* Badges */}
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <Badge variant={resource.is_free ? 'success' : 'default'}>
                  {resource.is_free ? 'Free' : 'Paid'}
                </Badge>
                {resource.level && (
                  <Badge variant="info">{resource.level}</Badge>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 flex-shrink-0">
              {isStarted && !isCompleted && (
                <button
                  onClick={onComplete}
                  disabled={isCompleting}
                  className="p-2 rounded-lg text-gray-400 hover:text-green-600 hover:bg-green-50 transition-colors disabled:opacity-50"
                  title="Mark as complete"
                >
                  <CheckCircle2 className="h-5 w-5" />
                </button>
              )}
              <ProtectedLink
                href={resource.url}
                className="p-2 rounded-lg text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                title="Open resource"
              >
                <ExternalLink className="h-5 w-5" />
              </ProtectedLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
