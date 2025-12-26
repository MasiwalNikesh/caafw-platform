'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { QuizQuestion as QuizQuestionType, QuizResult as QuizResultType } from '@/types';
import { quizAPI } from '@/lib/api';
import { QuizQuestion } from '@/components/quiz/QuizQuestion';
import { QuizResult } from '@/components/quiz/QuizResult';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { Brain, ChevronLeft, ChevronRight, Sparkles, Target, Award, Clock, ArrowRight, CheckCircle2, Circle } from 'lucide-react';

type QuizState = 'intro' | 'quiz' | 'result';

export default function QuizPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, refreshProfile } = useAuth();
  const [quizState, setQuizState] = useState<QuizState>('intro');
  const [questions, setQuestions] = useState<QuizQuestionType[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<QuizResultType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [slideDirection, setSlideDirection] = useState<'left' | 'right'>('right');
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    loadQuestions();
  }, []);

  // Check for stored answers from modal (if user registered after starting quiz)
  useEffect(() => {
    if (isAuthenticated) {
      const storedAnswers = sessionStorage.getItem('quiz_answers');
      if (storedAnswers) {
        try {
          const parsed = JSON.parse(storedAnswers);
          setAnswers(parsed);
          setQuizState('quiz');
          sessionStorage.removeItem('quiz_answers');
        } catch (e) {
          // Ignore parse errors
        }
      }
    }
  }, [isAuthenticated]);

  const loadQuestions = async () => {
    try {
      setIsLoading(true);
      const data = await quizAPI.getQuestions();
      setQuestions(data);
      setCurrentIndex(0);
      setResult(null);
      setError('');
    } catch (err) {
      setError('Failed to load quiz questions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswer = (answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questions[currentIndex].id]: answer,
    }));
  };

  const handleNext = useCallback(() => {
    if (currentIndex < questions.length - 1 && !isAnimating) {
      setIsAnimating(true);
      setSlideDirection('right');
      setTimeout(() => {
        setCurrentIndex((prev) => prev + 1);
        setIsAnimating(false);
      }, 150);
    }
  }, [currentIndex, questions.length, isAnimating]);

  const handlePrevious = useCallback(() => {
    if (currentIndex > 0 && !isAnimating) {
      setIsAnimating(true);
      setSlideDirection('left');
      setTimeout(() => {
        setCurrentIndex((prev) => prev - 1);
        setIsAnimating(false);
      }, 150);
    }
  }, [currentIndex, isAnimating]);

  const handleJumpToQuestion = (idx: number) => {
    if (idx !== currentIndex && !isAnimating) {
      setIsAnimating(true);
      setSlideDirection(idx > currentIndex ? 'right' : 'left');
      setTimeout(() => {
        setCurrentIndex(idx);
        setIsAnimating(false);
      }, 150);
    }
  };

  const handleSubmit = async () => {
    if (!isAuthenticated) {
      // Store answers in session storage and redirect to register
      sessionStorage.setItem('quiz_answers', JSON.stringify(answers));
      router.push('/register');
      return;
    }

    try {
      setIsSubmitting(true);
      const submissionAnswers = Object.entries(answers).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        answer,
      }));
      const response = await quizAPI.submit(submissionAnswers);
      setResult(response.data);
      setQuizState('result');
      await refreshProfile();
    } catch (err) {
      setError('Failed to submit quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setResult(null);
    setQuizState('intro');
    setCurrentIndex(0);
    setAnswers({});
    loadQuestions();
  };

  const handleStartQuiz = () => {
    setQuizState('quiz');
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (quizState !== 'quiz') return;

      if (e.key === 'ArrowRight' || e.key === 'Enter') {
        const currentQuestion = questions[currentIndex];
        const currentAnswer = currentQuestion ? answers[currentQuestion.id] : '';
        if (currentAnswer && currentIndex < questions.length - 1) {
          handleNext();
        }
      } else if (e.key === 'ArrowLeft') {
        handlePrevious();
      } else if (e.key >= '1' && e.key <= '5') {
        // Quick answer for self-assessment questions
        const currentQuestion = questions[currentIndex];
        if (currentQuestion?.question_type === 'self_assessment') {
          handleAnswer(e.key);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [quizState, currentIndex, questions, answers, handleNext, handlePrevious]);

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-950">
        <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-24">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
          </div>
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm inline-block mb-4">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              AI Readiness Quiz
            </h1>
          </div>
        </section>
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-4">
            <svg className="animate-spin h-12 w-12 text-violet-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-gray-500 dark:text-gray-400">Loading quiz...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-950">
        <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-24">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
          </div>
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm inline-block mb-4">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              AI Readiness Quiz
            </h1>
          </div>
        </section>
        <div className="mx-auto max-w-md px-4 sm:px-6 lg:px-8 -mt-16 pb-16">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mx-auto mb-4">
              <svg className="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p className="text-red-600 dark:text-red-400 text-lg mb-4">{error}</p>
            <button
              onClick={loadQuestions}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl hover:opacity-90 transition-all"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const currentAnswer = currentQuestion ? answers[currentQuestion.id] || '' : '';
  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0;
  const answeredCount = Object.keys(answers).length;
  const allAnswered = questions.length > 0 && questions.every((q) => answers[q.id]);
  const estimatedMinutes = Math.ceil(questions.length * 0.5);

  // Intro Screen
  if (quizState === 'intro') {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-950">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-40 sm:pb-44">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-violet-400/10 blur-3xl" />
          </div>
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col items-center text-center">
              <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-sm mb-6 animate-pulse">
                <Brain className="h-12 w-12 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4">
                AI Readiness Quiz
              </h1>
              <p className="text-xl text-violet-100 max-w-2xl">
                Discover your AI expertise level and unlock personalized learning recommendations tailored just for you.
              </p>
            </div>
          </div>
        </section>

        {/* Quiz Info Card */}
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 -mt-28 sm:-mt-32 pb-16 relative z-10">
          <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            {/* Stats Row */}
            <div className="grid grid-cols-3 divide-x divide-gray-100 dark:divide-gray-700 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20">
              <div className="p-6 text-center">
                <div className="flex justify-center mb-2">
                  <Target className="h-6 w-6 text-violet-600 dark:text-violet-400" />
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">{questions.length}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Questions</div>
              </div>
              <div className="p-6 text-center">
                <div className="flex justify-center mb-2">
                  <Clock className="h-6 w-6 text-violet-600 dark:text-violet-400" />
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">{estimatedMinutes}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Minutes</div>
              </div>
              <div className="p-6 text-center">
                <div className="flex justify-center mb-2">
                  <Award className="h-6 w-6 text-violet-600 dark:text-violet-400" />
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">4</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Levels</div>
              </div>
            </div>

            {/* Content */}
            <div className="p-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">What to Expect</h2>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center mt-0.5">
                    <CheckCircle2 className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">Self-Assessment Questions</span>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Rate your familiarity with AI concepts and tools</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center mt-0.5">
                    <CheckCircle2 className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">Multiple Choice</span>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Answer questions about your AI usage and interests</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center mt-0.5">
                    <CheckCircle2 className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">Personalized Results</span>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Get your AI readiness level and tailored recommendations</p>
                  </div>
                </li>
              </ul>

              {/* Start Button */}
              <button
                onClick={handleStartQuiz}
                className="w-full flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-violet-600 to-purple-600 text-white text-lg font-semibold rounded-2xl hover:shadow-xl hover:shadow-violet-500/25 transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <Sparkles className="h-6 w-6" />
                Start Quiz
                <ArrowRight className="h-6 w-6" />
              </button>

              {!isAuthenticated && (
                <p className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  You'll need to sign up to save your results
                </p>
              )}
            </div>
          </div>

          {/* Back to home */}
          <div className="mt-8 text-center">
            <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors">
              ← Back to home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Result Screen
  if (quizState === 'result' && result) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-950">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-40 sm:pb-44">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
            {/* Celebration particles */}
            <div className="absolute inset-0">
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="absolute animate-float"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                    animationDelay: `${Math.random() * 2}s`,
                    animationDuration: `${3 + Math.random() * 2}s`,
                  }}
                >
                  <Sparkles className="h-4 w-4 text-white/30" />
                </div>
              ))}
            </div>
          </div>
          <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col items-center text-center">
              <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-sm mb-6">
                <Award className="h-12 w-12 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4">
                Quiz Complete!
              </h1>
              <p className="text-xl text-violet-100">
                Here are your personalized results
              </p>
            </div>
          </div>
        </section>

        {/* Result Card */}
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 -mt-28 sm:-mt-32 pb-16 relative z-10">
          <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div className="p-8">
              <QuizResult result={result} onRetake={handleRetake} />
            </div>
          </div>

          {/* Back to home */}
          <div className="mt-8 text-center">
            <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors">
              ← Back to home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Quiz Screen
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-32 sm:pb-36">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-purple-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm mb-4">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              AI Readiness Quiz
            </h1>
            <p className="mt-4 text-lg text-violet-100">
              Question {currentIndex + 1} of {questions.length}
            </p>
          </div>
        </div>
      </section>

      {/* Quiz Card */}
      <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 -mt-20 sm:-mt-24 pb-16 relative z-10">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          {/* Progress Section */}
          <div className="p-6 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 border-b border-gray-100 dark:border-gray-700">
            <div className="flex justify-between text-sm mb-3">
              <span className="font-medium text-gray-700 dark:text-gray-300">
                {answeredCount} of {questions.length} answered
              </span>
              <span className="text-violet-600 dark:text-violet-400 font-medium">
                {Math.round(progress)}% complete
              </span>
            </div>

            {/* Progress bar */}
            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Question indicators */}
            <div className="mt-4 flex gap-2 flex-wrap justify-center">
              {questions.map((q, idx) => {
                const isAnswered = !!answers[q.id];
                const isCurrent = idx === currentIndex;

                return (
                  <button
                    key={q.id}
                    onClick={() => handleJumpToQuestion(idx)}
                    className={`
                      w-10 h-10 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-center
                      ${isCurrent
                        ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30 scale-110'
                        : isAnswered
                          ? 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 hover:bg-violet-200 dark:hover:bg-violet-900/60'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }
                    `}
                    title={isAnswered ? 'Answered' : 'Not answered'}
                  >
                    {isAnswered && !isCurrent ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      idx + 1
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Question Content with Animation */}
          <div className="p-6 md:p-8 min-h-[300px]">
            <div
              className={`
                transition-all duration-150 ease-in-out
                ${isAnimating
                  ? slideDirection === 'right'
                    ? 'opacity-0 -translate-x-4'
                    : 'opacity-0 translate-x-4'
                  : 'opacity-100 translate-x-0'
                }
              `}
            >
              {currentQuestion ? (
                <QuizQuestion
                  question={currentQuestion}
                  currentAnswer={currentAnswer}
                  onAnswer={handleAnswer}
                />
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center mx-auto mb-4">
                    <Brain className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 text-lg">No questions available yet.</p>
                  <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Please check back later.</p>
                </div>
              )}
            </div>
          </div>

          {/* Navigation */}
          {questions.length > 0 && (
            <div className="p-4 sm:p-6 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
              <div className="flex justify-between items-center gap-4">
                <button
                  onClick={handlePrevious}
                  disabled={currentIndex === 0 || isAnimating}
                  className="flex items-center gap-2 px-4 py-2.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <ChevronLeft className="h-5 w-5" />
                  <span className="hidden sm:inline">Previous</span>
                </button>

                {/* Mobile progress indicator */}
                <div className="flex items-center gap-1 sm:hidden">
                  {questions.map((_, idx) => (
                    <div
                      key={idx}
                      className={`w-2 h-2 rounded-full transition-all ${
                        idx === currentIndex
                          ? 'bg-violet-600 w-4'
                          : answers[questions[idx]?.id]
                            ? 'bg-violet-300'
                            : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    />
                  ))}
                </div>

                <div className="flex gap-3">
                  {currentIndex < questions.length - 1 ? (
                    <button
                      onClick={handleNext}
                      disabled={!currentAnswer || isAnimating}
                      className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg hover:shadow-violet-500/25 transform hover:scale-105 active:scale-95"
                    >
                      <span className="hidden sm:inline">Next</span>
                      <ChevronRight className="h-5 w-5" />
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={!allAnswered || isSubmitting || isAnimating}
                      className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg hover:shadow-violet-500/25 transform hover:scale-105 active:scale-95"
                    >
                      {isSubmitting ? (
                        <>
                          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span className="hidden sm:inline">Submitting...</span>
                        </>
                      ) : isAuthenticated ? (
                        <>
                          <Award className="h-5 w-5" />
                          <span className="hidden sm:inline">Get Results</span>
                          <span className="sm:hidden">Submit</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-5 w-5" />
                          <span className="hidden sm:inline">Sign Up to Save</span>
                          <span className="sm:hidden">Save</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>

              {/* Keyboard hint - desktop only */}
              <div className="hidden sm:flex justify-center mt-4 text-xs text-gray-400 dark:text-gray-500 gap-4">
                <span>← → Navigate</span>
                <span>Enter: Next</span>
                <span>1-5: Quick answer</span>
              </div>
            </div>
          )}
        </div>

        {/* Not authenticated message */}
        {!isAuthenticated && (
          <div className="mt-6 p-4 bg-violet-50 dark:bg-violet-900/20 rounded-xl border border-violet-100 dark:border-violet-800 text-center">
            <p className="text-sm text-violet-700 dark:text-violet-300">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-violet-600 dark:text-violet-400 hover:text-violet-500 underline">
                Sign in
              </Link>
              {' '}to save your results.
            </p>
          </div>
        )}

        {/* Back to home */}
        <div className="mt-8 text-center">
          <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors">
            ← Back to home
          </Link>
        </div>
      </div>

      {/* Add custom animation styles */}
      <style jsx global>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) rotate(0deg);
            opacity: 0.3;
          }
          50% {
            transform: translateY(-20px) rotate(180deg);
            opacity: 0.6;
          }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
