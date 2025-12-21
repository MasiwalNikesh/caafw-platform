'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { QuizQuestion as QuizQuestionType, QuizResult as QuizResultType } from '@/types';
import { quizAPI } from '@/lib/api';
import { QuizQuestion } from '@/components/quiz/QuizQuestion';
import { QuizResult } from '@/components/quiz/QuizResult';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { Brain, ChevronLeft, ChevronRight, Sparkles, Target, Award } from 'lucide-react';

export default function QuizPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, refreshProfile } = useAuth();
  const [questions, setQuestions] = useState<QuizQuestionType[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<QuizResultType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

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

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
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
      await refreshProfile();
    } catch (err) {
      setError('Failed to submit quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setResult(null);
    setCurrentIndex(0);
    setAnswers({});
    loadQuestions();
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
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
            <p className="text-gray-500">Loading quiz...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
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
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <svg className="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p className="text-red-600 text-lg mb-4">{error}</p>
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
  const allAnswered = questions.length > 0 && questions.every((q) => answers[q.id]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-violet-700 pt-24 sm:pt-28 pb-24">
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
            <p className="mt-4 text-lg text-violet-100 max-w-lg">
              Discover your AI readiness level and get personalized content recommendations tailored to your expertise.
            </p>
            {!result && (
              <div className="mt-6 flex flex-wrap justify-center gap-3">
                <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  {questions.length} Questions
                </span>
                <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Personalized Results
                </span>
                <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm flex items-center gap-2">
                  <Award className="h-4 w-4" />
                  4 Skill Levels
                </span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Quiz Card */}
      <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 -mt-16 pb-16">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
          {/* Progress */}
          {!result && questions.length > 0 && (
            <div className="p-6 bg-gradient-to-r from-violet-50 to-purple-50 border-b border-gray-100">
              <div className="flex justify-between text-sm text-gray-600 mb-3">
                <span className="font-medium">Question {currentIndex + 1} of {questions.length}</span>
                <span className="text-violet-600 font-medium">{Math.round(progress)}% complete</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              {/* Question indicators */}
              <div className="mt-4 flex gap-1.5 flex-wrap">
                {questions.map((q, idx) => (
                  <button
                    key={q.id}
                    onClick={() => setCurrentIndex(idx)}
                    className={`w-8 h-8 rounded-lg text-xs font-medium transition-all ${
                      idx === currentIndex
                        ? 'bg-violet-600 text-white'
                        : answers[q.id]
                        ? 'bg-violet-100 text-violet-700'
                        : 'bg-gray-100 text-gray-400'
                    }`}
                  >
                    {idx + 1}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Content */}
          <div className="p-6 md:p-8">
            {result ? (
              <QuizResult result={result} onRetake={handleRetake} />
            ) : currentQuestion ? (
              <QuizQuestion
                question={currentQuestion}
                currentAnswer={currentAnswer}
                onAnswer={handleAnswer}
              />
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                  <Brain className="h-8 w-8 text-gray-400" />
                </div>
                <p className="text-gray-600 text-lg">No questions available yet.</p>
                <p className="text-gray-400 text-sm mt-2">Please check back later.</p>
              </div>
            )}
          </div>

          {/* Navigation */}
          {!result && questions.length > 0 && (
            <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-between items-center">
              <button
                onClick={handlePrevious}
                disabled={currentIndex === 0}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="h-5 w-5" />
                Previous
              </button>
              <div className="flex gap-3">
                {currentIndex < questions.length - 1 ? (
                  <button
                    onClick={handleNext}
                    disabled={!currentAnswer}
                    className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg hover:shadow-violet-500/25"
                  >
                    Next
                    <ChevronRight className="h-5 w-5" />
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    disabled={!allAnswered || isSubmitting}
                    className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg hover:shadow-violet-500/25"
                  >
                    {isSubmitting ? (
                      <>
                        <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Submitting...
                      </>
                    ) : isAuthenticated ? (
                      <>
                        <Award className="h-5 w-5" />
                        Get Results
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        Sign Up to Save
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Not authenticated message */}
        {!isAuthenticated && !result && (
          <div className="mt-6 p-4 bg-violet-50 rounded-xl border border-violet-100 text-center">
            <p className="text-sm text-violet-700">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-violet-600 hover:text-violet-500 underline">
                Sign in
              </Link>
              {' '}to save your results.
            </p>
          </div>
        )}

        {/* Back to home */}
        <div className="mt-8 text-center">
          <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
