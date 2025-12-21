'use client';

import { useAuth } from '@/contexts/AuthContext';

// Maps user levels to content level tags they should see
const LEVEL_CONTENT_MAPPING: Record<string, string[]> = {
  novice: ['novice', 'intro', 'awareness', 'beginner-friendly', 'getting-started'],
  beginner: ['novice', 'beginner', 'fundamentals', 'intro', 'getting-started'],
  intermediate: ['beginner', 'intermediate', 'practical', 'applied'],
  expert: ['intermediate', 'advanced', 'expert', 'research', 'professional'],
};

// Maps user levels to job experience levels
const LEVEL_JOB_MAPPING: Record<string, string[]> = {
  novice: ['internship', 'entry', 'junior', 'trainee'],
  beginner: ['entry', 'junior', 'associate'],
  intermediate: ['mid', 'mid-level', 'senior'],
  expert: ['senior', 'lead', 'principal', 'director', 'manager'],
};

// Maps user levels to learning resource levels
const LEVEL_LEARNING_MAPPING: Record<string, string[]> = {
  novice: ['beginner', 'intro', 'introductory', 'fundamentals'],
  beginner: ['beginner', 'fundamentals', 'intermediate'],
  intermediate: ['intermediate', 'advanced'],
  expert: ['advanced', 'expert', 'professional'],
};

export function useLevelFilter() {
  const { profile, isAuthenticated } = useAuth();

  const userLevel = profile?.ai_level || null;
  const autoFilter = profile?.auto_filter_content ?? false;

  // Get recommended content levels based on user's AI level
  const getRecommendedLevels = () => {
    if (!userLevel) return null;
    return LEVEL_CONTENT_MAPPING[userLevel] || null;
  };

  // Get recommended job levels based on user's AI level
  const getRecommendedJobLevels = () => {
    if (!userLevel) return null;
    return LEVEL_JOB_MAPPING[userLevel] || null;
  };

  // Get recommended learning levels based on user's AI level
  const getRecommendedLearningLevels = () => {
    if (!userLevel) return null;
    return LEVEL_LEARNING_MAPPING[userLevel] || null;
  };

  // Check if content matches user's level
  const isRecommendedContent = (contentLevel?: string | null) => {
    if (!userLevel || !contentLevel) return true; // Show all if no filtering
    const recommended = LEVEL_CONTENT_MAPPING[userLevel] || [];
    return recommended.some((level) =>
      contentLevel.toLowerCase().includes(level)
    );
  };

  // Check if job matches user's level
  const isRecommendedJob = (experienceLevel?: string | null) => {
    if (!userLevel || !experienceLevel) return true;
    const recommended = LEVEL_JOB_MAPPING[userLevel] || [];
    return recommended.some((level) =>
      experienceLevel.toLowerCase().includes(level)
    );
  };

  // Check if learning resource matches user's level
  const isRecommendedLearning = (resourceLevel?: string | null) => {
    if (!userLevel || !resourceLevel) return true;
    const recommended = LEVEL_LEARNING_MAPPING[userLevel] || [];
    return recommended.some((level) =>
      resourceLevel.toLowerCase().includes(level)
    );
  };

  return {
    userLevel,
    autoFilter,
    isAuthenticated,
    hasCompletedQuiz: profile?.has_completed_quiz ?? false,
    getRecommendedLevels,
    getRecommendedJobLevels,
    getRecommendedLearningLevels,
    isRecommendedContent,
    isRecommendedJob,
    isRecommendedLearning,
  };
}
