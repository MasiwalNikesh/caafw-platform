'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface OAuthCallbackHandlerProps {
  provider: 'google' | 'microsoft' | 'linkedin';
}

const providerNames = {
  google: 'Google',
  microsoft: 'Microsoft',
  linkedin: 'LinkedIn',
};

export function OAuthCallbackHandler({ provider }: OAuthCallbackHandlerProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshProfile } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const token = searchParams.get('token');
      const error = searchParams.get('error');

      if (error) {
        setStatus('error');
        setErrorMessage(error);
        return;
      }

      if (!token) {
        setStatus('error');
        setErrorMessage('No authentication token received');
        return;
      }

      try {
        // Store the token
        localStorage.setItem('auth_token', token);

        // Set default Authorization header for future requests
        const { api } = await import('@/lib/api');
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        // Refresh user profile
        await refreshProfile();

        setStatus('success');

        // Check for pending external link
        const pendingLink = sessionStorage.getItem('pending_external_link');
        if (pendingLink) {
          sessionStorage.removeItem('pending_external_link');
          window.open(pendingLink, '_blank', 'noopener,noreferrer');
        }

        // Redirect to home or quiz (for new users)
        setTimeout(() => {
          const returnUrl = sessionStorage.getItem('oauth_return_url') || '/';
          sessionStorage.removeItem('oauth_return_url');
          router.push(returnUrl);
        }, 1500);
      } catch (err: any) {
        setStatus('error');
        setErrorMessage(err.message || 'Authentication failed');
      }
    };

    handleCallback();
  }, [searchParams, refreshProfile, router]);

  const providerName = providerNames[provider];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center">
          {status === 'loading' && (
            <>
              <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
                <Loader2 className="h-8 w-8 text-purple-600 animate-spin" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Signing in with {providerName}...
              </h2>
              <p className="text-gray-500">Please wait while we complete your authentication.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Successfully signed in!
              </h2>
              <p className="text-gray-500">Redirecting you to the platform...</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Authentication Failed
              </h2>
              <p className="text-red-600 mb-4">{errorMessage}</p>
              <button
                onClick={() => router.push('/login')}
                className="px-6 py-2.5 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors"
              >
                Try Again
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
