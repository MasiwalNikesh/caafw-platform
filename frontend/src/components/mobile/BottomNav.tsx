'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Home,
  Compass,
  Briefcase,
  GraduationCap,
  User,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface NavItem {
  name: string;
  href: string;
  icon: any;
  matchPaths?: string[];
}

const navItems: NavItem[] = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Discover', href: '/products', icon: Compass, matchPaths: ['/products', '/research', '/mcp', '/investments'] },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'Learn', href: '/learning-paths', icon: GraduationCap, matchPaths: ['/learning', '/learning-paths', '/learn', '/quiz'] },
  { name: 'Profile', href: '/bookmarks', icon: User, matchPaths: ['/bookmarks', '/login', '/register'] },
];

export function BottomNav() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  const isActive = (item: NavItem) => {
    if (pathname === item.href) return true;
    if (item.matchPaths) {
      return item.matchPaths.some(path => pathname.startsWith(path));
    }
    return false;
  };

  // Hide on admin pages
  if (pathname.startsWith('/admin')) {
    return null;
  }

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 lg:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 safe-area-bottom">
      <div className="flex items-center justify-around h-16 px-2">
        {navItems.map((item) => {
          const active = isActive(item);
          const Icon = item.icon;

          // Special handling for profile/auth
          if (item.name === 'Profile' && !isAuthenticated) {
            return (
              <Link
                key={item.name}
                href="/login"
                className="flex flex-col items-center justify-center flex-1 h-full relative"
              >
                <motion.div
                  whileTap={{ scale: 0.9 }}
                  className={`flex flex-col items-center gap-1 ${
                    active ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="text-[10px] font-medium">Sign In</span>
                </motion.div>
              </Link>
            );
          }

          return (
            <Link
              key={item.name}
              href={item.href}
              className="flex flex-col items-center justify-center flex-1 h-full relative"
            >
              <motion.div
                whileTap={{ scale: 0.9 }}
                className={`flex flex-col items-center gap-1 ${
                  active ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {active && (
                  <motion.div
                    layoutId="bottomNavIndicator"
                    className="absolute -top-0.5 w-8 h-1 bg-purple-600 dark:bg-purple-400 rounded-full"
                    transition={{ type: 'spring', duration: 0.5 }}
                  />
                )}
                <Icon className="h-5 w-5" />
                <span className="text-[10px] font-medium">{item.name}</span>
              </motion.div>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

// Spacer component to prevent content from being hidden behind bottom nav
export function BottomNavSpacer() {
  return <div className="h-16 lg:hidden" />;
}

