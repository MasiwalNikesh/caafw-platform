'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { UserPlus, Mail, Lock, User, Sparkles, ArrowRight, CheckCircle } from 'lucide-react';
import { OAuthButtons } from '@/components/auth/OAuthButtons';

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { register, isAuthenticated } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Get return URL from query params, default to quiz for new registrations
  const returnUrl = searchParams.get('returnUrl') || '/quiz';

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push(returnUrl);
    }
  }, [isAuthenticated, router, returnUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, password, name || undefined);
      // Redirect to return URL (quiz by default for new users)
      router.push(returnUrl);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-500 via-teal-500 to-emerald-600 pt-24 sm:pt-28 pb-24">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-teal-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm mb-4">
              <UserPlus className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              Join the Community
            </h1>
            <p className="mt-4 text-lg text-emerald-100 max-w-lg">
              Create your account to get personalized AI recommendations, track your learning journey, and connect with fellow AI enthusiasts.
            </p>
          </div>
        </div>
      </section>

      {/* Form Section */}
      <div className="mx-auto max-w-md px-4 sm:px-6 lg:px-8 -mt-16 pb-16">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Name <span className="text-gray-400">(optional)</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="block w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                  placeholder="Your name"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                  placeholder="At least 6 characters"
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="block w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                  placeholder="Confirm your password"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-white font-medium bg-gradient-to-r from-emerald-500 to-teal-500 hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg hover:shadow-emerald-500/25"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>

            <div className="flex items-center gap-2 text-sm text-gray-500 bg-emerald-50 rounded-xl p-3">
              <Sparkles className="h-4 w-4 text-emerald-600 flex-shrink-0" />
              <span>After registration, take a quick quiz to personalize your experience!</span>
            </div>
          </form>

          {/* Divider */}
          <div className="mt-6 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="mt-6">
            <OAuthButtons mode="register" disabled={isLoading} />
          </div>

          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-emerald-600 hover:text-emerald-500">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Benefits */}
        <div className="mt-8 space-y-3">
          {[
            'Personalized AI content based on your skill level',
            'Track your learning progress over time',
            'Get job recommendations matching your expertise',
            'Connect with the AI community',
          ].map((benefit, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
              <CheckCircle className="h-5 w-5 text-emerald-500 flex-shrink-0" />
              <span className="text-sm text-gray-700">{benefit}</span>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
