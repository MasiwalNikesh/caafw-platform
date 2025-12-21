'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const QUIZ_DISMISSED_KEY = 'quiz_modal_dismissed';

export function useFirstVisitQuiz() {
  const { isAuthenticated, profile, isLoading } = useAuth();
  const [showQuizModal, setShowQuizModal] = useState(false);

  useEffect(() => {
    // Don't show during initial load
    if (isLoading) return;

    // Check if user has already dismissed the modal this session
    const dismissed = sessionStorage.getItem(QUIZ_DISMISSED_KEY);
    if (dismissed) return;

    // If authenticated and has completed quiz, don't show
    if (isAuthenticated && profile?.has_completed_quiz) return;

    // If not authenticated or hasn't completed quiz, show after a short delay
    const timer = setTimeout(() => {
      setShowQuizModal(true);
    }, 2000); // 2 second delay

    return () => clearTimeout(timer);
  }, [isLoading, isAuthenticated, profile?.has_completed_quiz]);

  const dismissQuizModal = () => {
    setShowQuizModal(false);
    sessionStorage.setItem(QUIZ_DISMISSED_KEY, 'true');
  };

  return {
    showQuizModal,
    dismissQuizModal,
  };
}
