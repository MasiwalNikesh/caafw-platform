'use client';

import { motion, HTMLMotionProps } from 'framer-motion';
import { ReactNode } from 'react';
import Link from 'next/link';

interface AnimatedButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'ghost';
}

export function AnimatedButton({
  children,
  className = '',
  variant = 'primary',
  ...props
}: AnimatedButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
      className={className}
      {...props}
    >
      {children}
    </motion.button>
  );
}

interface AnimatedLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
  external?: boolean;
}

export function AnimatedLink({
  href,
  children,
  className = '',
  external = false,
}: AnimatedLinkProps) {
  const MotionLink = motion(Link);

  if (external) {
    return (
      <motion.a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.15 }}
        className={className}
      >
        {children}
      </motion.a>
    );
  }

  return (
    <MotionLink
      href={href}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
      className={className}
    >
      {children}
    </MotionLink>
  );
}

// Loading button with spinner animation
interface LoadingButtonProps extends AnimatedButtonProps {
  isLoading?: boolean;
  loadingText?: string;
}

export function LoadingButton({
  children,
  isLoading = false,
  loadingText = 'Loading...',
  className = '',
  disabled,
  ...props
}: LoadingButtonProps) {
  return (
    <AnimatedButton
      className={className}
      disabled={isLoading || disabled}
      {...props}
    >
      {isLoading ? (
        <span className="inline-flex items-center gap-2">
          <motion.span
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="inline-block"
          >
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </motion.span>
          {loadingText}
        </span>
      ) : (
        children
      )}
    </AnimatedButton>
  );
}

