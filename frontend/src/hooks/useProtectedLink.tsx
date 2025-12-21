'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface UseProtectedLinkOptions {
  url: string;
  requireAuth?: boolean;
  onAuthRequired?: () => void;
}

export function useProtectedLink({ url, requireAuth = true, onAuthRequired }: UseProtectedLinkOptions) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (requireAuth && !isAuthenticated) {
      e.preventDefault();

      // Store the intended destination
      const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
      const targetUrl = encodeURIComponent(url);

      // Store the target URL in session storage so we can open it after login
      sessionStorage.setItem('pending_external_link', url);

      // Call optional callback
      if (onAuthRequired) {
        onAuthRequired();
      }

      // Redirect to login with return URL
      router.push(`/login?returnUrl=${returnUrl}&targetUrl=${targetUrl}`);
      return false;
    }

    return true;
  };

  return {
    handleClick,
    isProtected: requireAuth && !isAuthenticated,
    canAccess: !requireAuth || isAuthenticated,
  };
}
