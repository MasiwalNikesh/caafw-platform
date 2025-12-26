'use client';

import { QuizResult as QuizResultType } from '@/types';
import Link from 'next/link';
import { Award, RotateCcw, ArrowRight, TrendingUp, Star, Sparkles } from 'lucide-react';

interface QuizResultProps {
  result: QuizResultType;
  onRetake?: () => void;
}

const levelConfig: Record<string, {
  title: string;
  description: string;
  gradient: string;
  bgGradient: string;
  icon: string;
  badgeColor: string;
}> = {
  novice: {
    title: 'Novice',
    description: "You're just starting your AI journey! We'll show you introductory content, basic tools, and beginner-friendly resources to help you build a strong foundation.",
    gradient: 'from-blue-500 to-cyan-500',
    bgGradient: 'from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20',
    icon: '🌱',
    badgeColor: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  },
  beginner: {
    title: 'Beginner',
    description: "You have some AI familiarity. We'll provide fundamentals, getting-started guides, and practical tutorials to expand your knowledge.",
    gradient: 'from-green-500 to-emerald-500',
    bgGradient: 'from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20',
    icon: '🌿',
    badgeColor: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  },
  intermediate: {
    title: 'Intermediate',
    description: "You're a regular AI user with solid understanding. We'll show you practical applications, deeper learning materials, and more advanced topics.",
    gradient: 'from-amber-500 to-orange-500',
    bgGradient: 'from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20',
    icon: '🌳',
    badgeColor: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  },
  expert: {
    title: 'Expert',
    description: "You have advanced AI knowledge! We'll prioritize cutting-edge research, expert-level content, and professional opportunities.",
    gradient: 'from-purple-500 to-pink-500',
    bgGradient: 'from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20',
    icon: '🌟',
    badgeColor: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  },
};

export function QuizResult({ result, onRetake }: QuizResultProps) {
  const config = levelConfig[result.computed_level] || levelConfig.beginner;

  return (
    <div className="space-y-8">
      {/* Level Badge */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 mb-6">
          <span className="text-4xl">{config.icon}</span>
        </div>
        <div
          className={`inline-block px-6 py-3 rounded-2xl bg-gradient-to-r ${config.gradient} text-white text-2xl font-bold shadow-lg`}
        >
          {config.title}
        </div>
        <h2 className="mt-4 text-xl font-medium text-gray-600 dark:text-gray-400">
          Your AI Readiness Level
        </h2>
      </div>

      {/* Score Card */}
      <div className={`rounded-2xl p-6 bg-gradient-to-br ${config.bgGradient} border border-gray-100 dark:border-gray-700`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            <span className="font-medium text-gray-700 dark:text-gray-300">Overall Score</span>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-gray-900 dark:text-white">{result.percentage}%</span>
            <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
              ({result.total_score}/{result.max_possible_score} pts)
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${config.gradient} transition-all duration-1000 ease-out rounded-full`}
            style={{ width: `${result.percentage}%` }}
          />
        </div>

        {/* Level markers */}
        <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span>Novice</span>
          <span>Beginner</span>
          <span>Intermediate</span>
          <span>Expert</span>
        </div>
      </div>

      {/* Description */}
      <div className="text-center">
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
          {config.description}
        </p>
      </div>

      {/* Category Breakdown */}
      {result.category_scores && Object.keys(result.category_scores).length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
            <Star className="h-4 w-4" />
            Category Breakdown
          </h4>
          <div className="space-y-4">
            {Object.entries(result.category_scores).map(([category, score]) => (
              <div key={category}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {category.replace(/_/g, ' ')}
                  </span>
                  <span className={`text-sm font-bold ${config.badgeColor} px-2 py-0.5 rounded-full`}>
                    {score}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r ${config.gradient} transition-all duration-700 rounded-full`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* What's Next */}
      <div className="bg-violet-50 dark:bg-violet-900/20 rounded-2xl p-6 border border-violet-100 dark:border-violet-800">
        <h4 className="flex items-center gap-2 text-sm font-semibold text-violet-700 dark:text-violet-300 mb-3">
          <Sparkles className="h-4 w-4" />
          What's Next?
        </h4>
        <p className="text-sm text-violet-600 dark:text-violet-400 mb-4">
          Based on your results, we've personalized your content feed. Explore AI tools, research papers, and learning resources tailored to your level.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Link
          href="/"
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
        >
          <Award className="h-5 w-5" />
          Explore Content
          <ArrowRight className="h-5 w-5" />
        </Link>
        {onRetake && (
          <button
            onClick={onRetake}
            className="flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
          >
            <RotateCcw className="h-5 w-5" />
            Retake Quiz
          </button>
        )}
      </div>
    </div>
  );
}
