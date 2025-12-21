'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MessageSquare, ArrowUp, Star, GitFork, ExternalLink, Heart, Repeat2, CheckCircle, Flame, Users } from 'lucide-react';
import { communityAPI } from '@/lib/api';
import { HackerNewsItem, GitHubRepo, Tweet, PaginatedResponse } from '@/types';
import { formatNumber, formatRelativeTime, truncate } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';

type Tab = 'hackernews' | 'github' | 'tweets';

export default function CommunityPage() {
  const [activeTab, setActiveTab] = useState<Tab>('hackernews');

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-green-600 via-emerald-600 to-green-700 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-emerald-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Users className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Community
            </h1>
          </div>
          <p className="text-lg text-green-100 max-w-2xl">
            Trending discussions from Hacker News, GitHub, and AI Twitter
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Latest Discussions
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Trending Repos
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              AI Social Feed
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Tabs Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('hackernews')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'hackernews'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Hacker News
              </button>
              <button
                onClick={() => setActiveTab('github')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'github'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                GitHub Trending
              </button>
              <button
                onClick={() => setActiveTab('tweets')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'tweets'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                AI Social Feed
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'hackernews' && <HackerNewsTab />}
        {activeTab === 'github' && <GitHubTab />}
        {activeTab === 'tweets' && <TweetsTab />}
      </div>
    </div>
  );
}

function HackerNewsTab() {
  const { data, isLoading } = useQuery<PaginatedResponse<HackerNewsItem>>({
    queryKey: ['hackernews'],
    queryFn: () => communityAPI.hackernews({ page: 1, page_size: 30 }),
  });

  if (isLoading) return <ListSkeleton count={10} />;

  return (
    <div className="space-y-4">
      {data?.items.map((item, index) => (
        <div key={item.id} className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
          <div className="flex items-start gap-4">
            <div className="text-center text-gray-500 min-w-[40px]">
              <div className="text-lg font-semibold">{index + 1}</div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start gap-2">
                <a
                  href={item.url || `https://news.ycombinator.com/item?id=${item.hn_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-900 font-medium hover:text-green-600 transition-colors"
                >
                  {item.title}
                </a>
                {item.url && (
                  <span className="text-xs text-gray-400">
                    ({new URL(item.url).hostname})
                  </span>
                )}
              </div>
              <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <ArrowUp className="h-4 w-4" />
                  {formatNumber(item.score)} points
                </span>
                <span>by {item.author}</span>
                <span>{formatRelativeTime(item.posted_at)}</span>
                <a
                  href={`https://news.ycombinator.com/item?id=${item.hn_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-green-600 transition-colors"
                >
                  <MessageSquare className="h-4 w-4" />
                  {formatNumber(item.comments_count)} comments
                </a>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function GitHubTab() {
  const { data, isLoading } = useQuery<PaginatedResponse<GitHubRepo>>({
    queryKey: ['github'],
    queryFn: () => communityAPI.github({ page: 1, page_size: 30 }),
  });

  if (isLoading) return <ListSkeleton count={10} />;

  return (
    <div className="space-y-4">
      {data?.items.map((repo) => (
        <div key={repo.id} className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
          <div className="flex items-start gap-3">
            {repo.owner_avatar && (
              <img
                src={repo.owner_avatar}
                alt={repo.owner}
                className="h-10 w-10 rounded-full"
              />
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <a
                  href={repo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 font-semibold hover:underline"
                >
                  {repo.full_name}
                </a>
                {repo.language && (
                  <Badge className="ml-2" size="sm">
                    {repo.language}
                  </Badge>
                )}
              </div>

              <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                {truncate(repo.description || '', 200)}
              </p>

              {repo.topics && repo.topics.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {repo.topics.slice(0, 5).map((topic) => (
                    <span key={topic} className="px-3 py-1 rounded-full bg-green-50 text-green-600 text-xs font-medium">
                      {topic}
                    </span>
                  ))}
                </div>
              )}

              <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Star className="h-4 w-4" />
                    {formatNumber(repo.stars)}
                  </span>
                  <span className="flex items-center gap-1">
                    <GitFork className="h-4 w-4" />
                    {formatNumber(repo.forks)}
                  </span>
                  {repo.stars_today > 0 && (
                    <span className="text-green-600 font-medium">
                      +{formatNumber(repo.stars_today)} today
                    </span>
                  )}
                </div>
                <a
                  href={repo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-green-600 to-emerald-600 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-green-500/25"
                >
                  View
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function TweetsTab() {
  const { data, isLoading } = useQuery<PaginatedResponse<Tweet>>({
    queryKey: ['tweets'],
    queryFn: () => communityAPI.tweets({ page: 1, page_size: 30 }),
  });

  if (isLoading) return <ListSkeleton count={10} />;

  if (!data?.items?.length) {
    return (
      <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
        <Flame className="h-12 w-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 text-lg mb-2">No AI social content collected yet</p>
        <p className="text-sm text-gray-400">
          Use the API endpoint <code className="bg-gray-100 px-1 rounded">/api/v1/community/tweets/collect</code> to fetch AI content from Reddit
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {data?.items.map((tweet) => (
        <div key={tweet.id} className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg transition-all hover:-translate-y-0.5">
          <div className="flex items-start gap-3">
            <img
              src={tweet.author_profile_image || `https://ui-avatars.com/api/?name=${tweet.author_username}&background=random`}
              alt={tweet.author_username}
              className="h-12 w-12 rounded-full"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900">
                  {tweet.author_name || tweet.author_username}
                </span>
                {tweet.author_verified && (
                  <CheckCircle className="h-4 w-4 text-blue-500" />
                )}
                <span className="text-gray-500">@{tweet.author_username}</span>
                <span className="text-gray-400">·</span>
                <span className="text-gray-500 text-sm">
                  {formatRelativeTime(tweet.tweeted_at)}
                </span>
              </div>
              <p className="mt-2 text-gray-800 whitespace-pre-wrap">
                {tweet.text}
              </p>
              {tweet.topic && (
                <Badge className="mt-2" size="sm" variant="info">
                  {tweet.topic}
                </Badge>
              )}
              <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="flex items-center gap-6 text-sm text-gray-500">
                  <span className="flex items-center gap-1 hover:text-red-500 cursor-pointer transition-colors">
                    <Heart className="h-4 w-4" />
                    {formatNumber(tweet.likes)}
                  </span>
                  <span className="flex items-center gap-1 hover:text-green-500 cursor-pointer transition-colors">
                    <Repeat2 className="h-4 w-4" />
                    {formatNumber(tweet.retweets)}
                  </span>
                  <span className="flex items-center gap-1 hover:text-blue-500 cursor-pointer transition-colors">
                    <MessageSquare className="h-4 w-4" />
                    {formatNumber(tweet.replies)}
                  </span>
                </div>
                <a
                  href={`https://reddit.com/r/${tweet.topic}/comments/${tweet.tweet_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-green-600 to-emerald-600 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-all hover:shadow-lg hover:shadow-green-500/25"
                >
                  View on Reddit
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
