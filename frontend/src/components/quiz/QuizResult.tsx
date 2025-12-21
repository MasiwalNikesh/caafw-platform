'use client';

import { QuizResult as QuizResultType } from '@/types';
import Link from 'next/link';

interface QuizResultProps {
  result: QuizResultType;
  onRetake?: () => void;
}

const levelDescriptions: Record<string, { title: string; description: string; color: string }> = {
  novice: {
    title: 'Novice',
    description:
      "You're just starting your AI journey! We'll show you introductory content, basic tools, and beginner-friendly resources to help you build a strong foundation.",
    color: 'from-blue-500 to-cyan-500',
  },
  beginner: {
    title: 'Beginner',
    description:
      "You have some AI familiarity. We'll provide fundamentals, getting-started guides, and practical tutorials to expand your knowledge.",
    color: 'from-green-500 to-emerald-500',
  },
  intermediate: {
    title: 'Intermediate',
    description:
      "You're a regular AI user with solid understanding. We'll show you practical applications, deeper learning materials, and more advanced topics.",
    color: 'from-yellow-500 to-orange-500',
  },
  expert: {
    title: 'Expert',
    description:
      "You have advanced AI knowledge! We'll prioritize cutting-edge research, expert-level content, and professional opportunities.",
    color: 'from-purple-500 to-pink-500',
  },
};

export function QuizResult({ result, onRetake }: QuizResultProps) {
  const levelInfo = levelDescriptions[result.computed_level] || levelDescriptions.beginner;

  return (
    <div className="text-center space-y-8">
      <div className="space-y-4">
        <div
          className={`inline-block px-6 py-2 rounded-full bg-gradient-to-r ${levelInfo.color} text-white text-lg font-bold`}
        >
          {levelInfo.title}
        </div>
        <h2 className="text-3xl font-bold text-white">Your AI Readiness Level</h2>
      </div>

      <div className="max-w-md mx-auto">
        <div className="relative pt-1">
          <div className="flex mb-3 items-center justify-between">
            <div>
              <span className="text-sm font-semibold inline-block text-purple-400">
                Score: {result.percentage}%
              </span>
            </div>
            <div className="text-right">
              <span className="text-sm font-semibold inline-block text-gray-400">
                {result.total_score} / {result.max_possible_score} points
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-3 mb-4 text-xs flex rounded-full bg-gray-700">
            <div
              style={{ width: `${result.percentage}%` }}
              className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r ${levelInfo.color} transition-all duration-500`}
            />
          </div>
        </div>
      </div>

      <p className="text-gray-300 max-w-lg mx-auto">{levelInfo.description}</p>

      {result.category_scores && Object.keys(result.category_scores).length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
          <h4 className="text-sm font-semibold text-gray-400 mb-4">Category Breakdown</h4>
          <div className="space-y-4">
            {Object.entries(result.category_scores).map(([category, score]) => (
              <div key={category} className="flex justify-between items-center">
                <span className="text-gray-300 capitalize">{category.replace('_', ' ')}</span>
                <span className="text-purple-400 font-medium">{score}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
        <Link
          href="/"
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
        >
          Explore Personalized Content
        </Link>
        {onRetake && (
          <button
            onClick={onRetake}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
          >
            Retake Quiz
          </button>
        )}
      </div>
    </div>
  );
}
