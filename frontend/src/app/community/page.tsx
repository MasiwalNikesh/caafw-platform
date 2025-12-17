'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MessageSquare, ArrowUp, Star, GitFork, ExternalLink, Heart, Repeat2, CheckCircle, Flame } from 'lucide-react';
import { communityAPI } from '@/lib/api';
import { HackerNewsItem, GitHubRepo, Tweet, PaginatedResponse } from '@/types';
import { formatNumber, formatRelativeTime, truncate } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';

type Tab = 'hackernews' | 'github' | 'tweets';

export default function CommunityPage() {
  const [activeTab, setActiveTab] = useState<Tab>('hackernews');

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Community</h1>
        <p className="mt-2 text-gray-600">
          Trending discussions from Hacker News, GitHub, and AI Twitter
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('hackernews')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'hackernews'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Hacker News
          </button>
          <button
            onClick={() => setActiveTab('github')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'github'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            GitHub Trending
          </button>
          <button
            onClick={() => setActiveTab('tweets')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tweets'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            AI Social Feed
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'hackernews' && <HackerNewsTab />}
      {activeTab === 'github' && <GitHubTab />}
      {activeTab === 'tweets' && <TweetsTab />}
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
        <Card key={item.id}>
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
                  className="text-gray-900 font-medium hover:text-indigo-600"
                >
                  {item.title}
                </a>
                {item.url && (
                  <span className="text-xs text-gray-400">
                    ({new URL(item.url).hostname})
                  </span>
                )}
              </div>
              <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
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
                  className="flex items-center gap-1 hover:text-indigo-600"
                >
                  <MessageSquare className="h-4 w-4" />
                  {formatNumber(item.comments_count)} comments
                </a>
              </div>
            </div>
          </div>
        </Card>
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
        <Card key={repo.id}>
          <CardHeader>
            <div className="flex items-start gap-3">
              {repo.owner_avatar && (
                <img
                  src={repo.owner_avatar}
                  alt={repo.owner}
                  className="h-10 w-10 rounded-full"
                />
              )}
              <div className="flex-1 min-w-0">
                <a
                  href={repo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-600 font-semibold hover:underline"
                >
                  {repo.full_name}
                </a>
                {repo.language && (
                  <Badge className="ml-2" size="sm">
                    {repo.language}
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>

          <CardDescription>
            {truncate(repo.description || '', 200)}
          </CardDescription>

          {repo.topics && repo.topics.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {repo.topics.slice(0, 5).map((topic) => (
                <Badge key={topic} size="sm" variant="info">
                  {topic}
                </Badge>
              ))}
            </div>
          )}

          <CardFooter className="text-sm text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <Star className="h-4 w-4" />
                {formatNumber(repo.stars)}
              </span>
              <span className="flex items-center gap-1">
                <GitFork className="h-4 w-4" />
                {formatNumber(repo.forks)}
              </span>
              {repo.stars_today > 0 && (
                <span className="text-green-600">
                  +{formatNumber(repo.stars_today)} today
                </span>
              )}
            </div>
            <a
              href={repo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-indigo-600 hover:text-indigo-500"
            >
              View
              <ExternalLink className="h-4 w-4" />
            </a>
          </CardFooter>
        </Card>
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
      <div className="text-center py-12">
        <Flame className="h-12 w-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 mb-2">No AI social content collected yet</p>
        <p className="text-sm text-gray-400">
          Use the API endpoint <code className="bg-gray-100 px-1 rounded">/api/v1/community/tweets/collect</code> to fetch AI content from Reddit
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {data?.items.map((tweet) => (
        <Card key={tweet.id}>
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
              <p className="mt-1 text-gray-800 whitespace-pre-wrap">
                {tweet.text}
              </p>
              {tweet.topic && (
                <Badge className="mt-2" size="sm" variant="info">
                  {tweet.topic}
                </Badge>
              )}
              <div className="mt-3 flex items-center gap-6 text-sm text-gray-500">
                <span className="flex items-center gap-1 hover:text-red-500 cursor-pointer">
                  <Heart className="h-4 w-4" />
                  {formatNumber(tweet.likes)}
                </span>
                <span className="flex items-center gap-1 hover:text-green-500 cursor-pointer">
                  <Repeat2 className="h-4 w-4" />
                  {formatNumber(tweet.retweets)}
                </span>
                <span className="flex items-center gap-1 hover:text-blue-500 cursor-pointer">
                  <MessageSquare className="h-4 w-4" />
                  {formatNumber(tweet.replies)}
                </span>
                <a
                  href={`https://reddit.com/r/${tweet.topic}/comments/${tweet.tweet_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-indigo-600 hover:text-indigo-500 ml-auto"
                >
                  View on Reddit
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
