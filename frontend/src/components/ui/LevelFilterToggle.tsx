'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

interface LevelFilterToggleProps {
  isFiltering: boolean;
  onToggle: (enabled: boolean) => void;
}

const levelLabels: Record<string, { label: string; color: string }> = {
  novice: { label: 'Novice', color: 'bg-blue-500' },
  beginner: { label: 'Beginner', color: 'bg-green-500' },
  intermediate: { label: 'Intermediate', color: 'bg-yellow-500' },
  expert: { label: 'Expert', color: 'bg-purple-500' },
};

export function LevelFilterToggle({ isFiltering, onToggle }: LevelFilterToggleProps) {
  const { isAuthenticated, profile } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="flex items-center gap-3 bg-gray-100 rounded-lg px-4 py-2 text-sm">
        <span className="text-gray-600">Get personalized content</span>
        <Link
          href="/quiz"
          className="text-indigo-600 hover:text-indigo-500 font-medium"
        >
          Take Quiz
        </Link>
      </div>
    );
  }

  if (!profile?.has_completed_quiz) {
    return (
      <div className="flex items-center gap-3 bg-gray-100 rounded-lg px-4 py-2 text-sm">
        <span className="text-gray-600">Complete the quiz for personalized content</span>
        <Link
          href="/quiz"
          className="text-indigo-600 hover:text-indigo-500 font-medium"
        >
          Take Quiz
        </Link>
      </div>
    );
  }

  const levelInfo = profile.ai_level ? levelLabels[profile.ai_level] : null;

  return (
    <div className="flex items-center gap-4 bg-gray-100 rounded-lg px-4 py-2">
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Your Level:</span>
        {levelInfo && (
          <span className={`${levelInfo.color} text-white text-xs font-medium px-2 py-0.5 rounded`}>
            {levelInfo.label}
          </span>
        )}
      </div>
      <div className="h-5 w-px bg-gray-300" />
      <label className="flex items-center gap-2 cursor-pointer">
        <span className="text-sm text-gray-600">Personalized</span>
        <button
          onClick={() => onToggle(!isFiltering)}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
            isFiltering ? 'bg-indigo-600' : 'bg-gray-300'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
              isFiltering ? 'translate-x-4' : 'translate-x-1'
            }`}
          />
        </button>
      </label>
      <Link
        href="/quiz"
        className="text-xs text-gray-500 hover:text-indigo-600"
      >
        Retake Quiz
      </Link>
    </div>
  );
}
