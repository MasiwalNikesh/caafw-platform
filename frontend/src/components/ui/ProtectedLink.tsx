'use client';

import { useProtectedLink } from '@/hooks/useProtectedLink';
import { ExternalLink, Lock } from 'lucide-react';
import { ReactNode } from 'react';

interface ProtectedLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
  requireAuth?: boolean;
  showLockIcon?: boolean;
  onAuthRequired?: () => void;
}

export function ProtectedLink({
  href,
  children,
  className = '',
  requireAuth = true,
  showLockIcon = false,
  onAuthRequired,
}: ProtectedLinkProps) {
  const { handleClick, isProtected } = useProtectedLink({
    url: href,
    requireAuth,
    onAuthRequired,
  });

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      onClick={handleClick}
      className={className}
    >
      {children}
      {isProtected && showLockIcon ? (
        <Lock className="h-4 w-4 ml-1 inline" />
      ) : (
        <ExternalLink className="h-4 w-4 ml-1 inline" />
      )}
    </a>
  );
}
