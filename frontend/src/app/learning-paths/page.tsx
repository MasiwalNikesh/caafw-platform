'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  Route,
  Clock,
  BookOpen,
  Star,
  Sparkles,
  ChevronRight,
  GraduationCap,
  Play,
  Trophy
} from 'lucide-react';
import { learningPathsAPI } from '@/lib/api';
import { LearningPath, PaginatedResponse, RecommendationsResponse } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { SearchInput } from '@/components/ui/SearchInput';
import { Pagination } from '@/components/ui/Pagination';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { useAuth } from '@/contexts/AuthContext';

const levelColors: Record<string, string> = {
  novice: 'bg-green-100 text-green-700',
  beginner: 'bg-blue-100 text-blue-700',
  intermediate: 'bg-purple-100 text-purple-700',
  expert: 'bg-red-100 text-red-700',
};

const levelLabels: Record<string, string> = {
  novice: 'Novice',
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  expert: 'Expert',
};

export default function LearningPathsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [level, setLevel] = useState<string>('');
  const { isAuthenticated, user } = useAuth();

  const { data, isLoading } = useQuery<PaginatedResponse<LearningPath>>({
    queryKey: ['learning-paths', page, search, level],
    queryFn: () =>
      learningPathsAPI.list({
        page,
        page_size: 12,
        search: search || undefined,
        level: level || undefined,
      }),
  });

  const { data: recommendations } = useQuery<RecommendationsResponse>({
    queryKey: ['learning-paths-recommendations'],
    queryFn: () => learningPathsAPI.recommendations(),
    enabled: true,
  });

  const { data: myProgress } = useQuery({
    queryKey: ['my-learning-progress'],
    queryFn: () => learningPathsAPI.myProgress(),
    enabled: isAuthenticated,
  });

  const userLevel = user?.profile?.ai_level;
  const hasCompletedQuiz = user?.profile?.has_completed_quiz;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Route className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Learning Paths
            </h1>
          </div>
          <p className="text-lg text-indigo-100 max-w-2xl">
            Curated learning journeys designed to take you from beginner to expert. Follow structured paths with handpicked resources.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              {data?.total || 0}+ Paths
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              All Skill Levels
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Track Progress
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Recommendations Section */}
        {recommendations && recommendations.recommendations.length > 0 && (
          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-2xl border border-purple-100 p-6 mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="h-5 w-5 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                Recommended for You
                {userLevel && <span className="text-purple-600 ml-2">({levelLabels[userLevel]} Level)</span>}
              </h2>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {recommendations.recommendations.slice(0, 3).map((rec) => (
                <Link
                  key={rec.path.id}
                  href={`/learning-paths/${rec.path.id}`}
                  className="bg-white rounded-xl p-4 border border-purple-100 hover:shadow-lg hover:-translate-y-1 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 line-clamp-1">{rec.path.title}</h3>
                      <p className="text-sm text-purple-600 mt-1">{rec.reason}</p>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0" />
                  </div>
                  <div className="mt-3 flex items-center gap-2 text-sm text-gray-500">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${levelColors[rec.path.level]}`}>
                      {levelLabels[rec.path.level]}
                    </span>
                    <span className="flex items-center gap-1">
                      <BookOpen className="h-3.5 w-3.5" />
                      {rec.path.resource_count} resources
                    </span>
                  </div>
                </Link>
              ))}
            </div>
            {!hasCompletedQuiz && (
              <div className="mt-4 text-center">
                <Link
                  href="/quiz"
                  className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 text-sm font-medium"
                >
                  <GraduationCap className="h-4 w-4" />
                  Take the AI Readiness Quiz for personalized recommendations
                </Link>
              </div>
            )}
          </div>
        )}

        {/* My Progress Section */}
        {isAuthenticated && myProgress && (myProgress as any[]).length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Play className="h-5 w-5 text-indigo-600" />
                <h2 className="text-lg font-semibold text-gray-900">Continue Learning</h2>
              </div>
            </div>
            <div className="space-y-3">
              {(myProgress as any[]).slice(0, 3).map((item: any) => (
                <Link
                  key={item.path.id}
                  href={`/learning-paths/${item.path.id}`}
                  className="flex items-center gap-4 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 line-clamp-1">{item.path.title}</h3>
                    <div className="mt-1 flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all"
                          style={{ width: `${item.progress.progress_percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 font-medium">
                        {item.progress.progress_percentage}%
                      </span>
                      {item.progress.completed_at && (
                        <Trophy className="h-4 w-4 text-yellow-500" />
                      )}
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-gray-400" />
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Filters Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1 w-full sm:w-auto">
              <SearchInput
                value={search}
                onChange={setSearch}
                placeholder="Search learning paths..."
                className="flex-1 max-w-md"
              />
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-gray-50"
              >
                <option value="">All Levels</option>
                <option value="novice">Novice</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="expert">Expert</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <ListSkeleton count={6} />
        ) : (
          <>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {data?.items.map((path) => (
                <PathCard key={path.id} path={path} />
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
                <Route className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No learning paths found</p>
                <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function PathCard({ path }: { path: LearningPath }) {
  return (
    <Link
      href={`/learning-paths/${path.id}`}
      className="group bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-xl transition-all hover:-translate-y-1"
    >
      <div className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 flex-shrink-0">
            <Route className="h-6 w-6 text-indigo-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {path.is_featured && (
                <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
              )}
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${levelColors[path.level]}`}>
                {levelLabels[path.level]}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
              {path.title}
            </h3>
          </div>
        </div>

        <p className="mt-4 text-sm text-gray-500 line-clamp-2">
          {path.description || 'A curated learning path to help you master new skills.'}
        </p>

        {path.topics && path.topics.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            {path.topics.slice(0, 3).map((topic) => (
              <span
                key={topic}
                className="px-2 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs"
              >
                {topic}
              </span>
            ))}
            {path.topics.length > 3 && (
              <span className="px-2 py-1 text-gray-400 text-xs">
                +{path.topics.length - 3} more
              </span>
            )}
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <BookOpen className="h-4 w-4" />
              {path.resource_count} resources
            </span>
            {path.duration_hours && (
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {path.duration_hours}h
              </span>
            )}
          </div>
          <span className="text-indigo-600 text-sm font-medium group-hover:translate-x-1 transition-transform flex items-center gap-1">
            Start <ChevronRight className="h-4 w-4" />
          </span>
        </div>
      </div>
    </Link>
  );
}
