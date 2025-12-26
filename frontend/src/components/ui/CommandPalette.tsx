'use client';

import { useState, useEffect, useRef, useCallback, Fragment } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Command,
  Package,
  Briefcase,
  FileText,
  GraduationCap,
  Route,
  Calendar,
  Server,
  Newspaper,
  Users,
  Sparkles,
  Settings,
  LogOut,
  ArrowRight,
  Clock,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface CommandItem {
  id: string;
  name: string;
  description?: string;
  icon: any;
  href?: string;
  action?: () => void;
  category: string;
  keywords?: string[];
}

const navigationCommands: CommandItem[] = [
  { id: 'home', name: 'Home', icon: Command, href: '/', category: 'Navigation', keywords: ['main', 'landing'] },
  { id: 'products', name: 'AI Products', description: 'Browse AI tools and products', icon: Package, href: '/products', category: 'Discover', keywords: ['tools', 'apps'] },
  { id: 'jobs', name: 'AI Jobs', description: 'Find AI job opportunities', icon: Briefcase, href: '/jobs', category: 'Discover', keywords: ['careers', 'work', 'employment'] },
  { id: 'research', name: 'Research Papers', description: 'Latest AI research', icon: FileText, href: '/research', category: 'Discover', keywords: ['papers', 'arxiv', 'academic'] },
  { id: 'learning', name: 'Learning Resources', description: 'Courses and tutorials', icon: GraduationCap, href: '/learning', category: 'Learn', keywords: ['courses', 'tutorials', 'education'] },
  { id: 'learning-paths', name: 'Learning Paths', description: 'Curated learning journeys', icon: Route, href: '/learning-paths', category: 'Learn', keywords: ['path', 'journey', 'curriculum'] },
  { id: 'events', name: 'Events', description: 'AI conferences and meetups', icon: Calendar, href: '/events', category: 'Community', keywords: ['meetups', 'conferences', 'workshops'] },
  { id: 'mcp', name: 'MCP Servers', description: 'Model Context Protocol', icon: Server, href: '/mcp', category: 'Discover', keywords: ['model', 'context', 'protocol'] },
  { id: 'community', name: 'Community', description: 'HN, GitHub, Reddit', icon: Users, href: '/community', category: 'Community', keywords: ['discussions', 'social'] },
  { id: 'quiz', name: 'AI Readiness Quiz', description: 'Test your AI knowledge', icon: Sparkles, href: '/quiz', category: 'Actions', keywords: ['test', 'assessment'] },
];

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();

  // Load recent searches from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('recentSearches');
    if (stored) {
      try {
        setRecentSearches(JSON.parse(stored));
      } catch (e) {
        // Ignore parse errors
      }
    }
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Open with Cmd/Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(true);
      }
      // Also open with just /
      if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        e.preventDefault();
        setIsOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Build commands list including auth commands
  const allCommands = [...navigationCommands];
  if (isAuthenticated) {
    allCommands.push(
      { id: 'bookmarks', name: 'My Bookmarks', icon: Package, href: '/bookmarks', category: 'Actions', keywords: ['saved', 'favorites'] },
      { id: 'logout', name: 'Sign Out', icon: LogOut, action: () => { logout(); setIsOpen(false); }, category: 'Actions', keywords: ['signout', 'exit'] },
    );
  } else {
    allCommands.push(
      { id: 'login', name: 'Sign In', icon: Users, href: '/login', category: 'Actions', keywords: ['signin', 'account'] },
      { id: 'register', name: 'Join Us', icon: Users, href: '/register', category: 'Actions', keywords: ['signup', 'create account'] },
    );
  }

  // Filter commands based on query
  const filteredCommands = query
    ? allCommands.filter((cmd) => {
        const searchStr = `${cmd.name} ${cmd.description || ''} ${cmd.keywords?.join(' ') || ''}`.toLowerCase();
        return searchStr.includes(query.toLowerCase());
      })
    : allCommands;

  // Group by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = [];
    }
    acc[cmd.category].push(cmd);
    return acc;
  }, {} as Record<string, CommandItem[]>);

  const flatCommands = Object.values(groupedCommands).flat();

  // Handle selection
  const handleSelect = useCallback((command: CommandItem) => {
    if (command.action) {
      command.action();
    } else if (command.href) {
      router.push(command.href);
    }
    setIsOpen(false);

    // Add to recent searches
    if (query) {
      const newRecent = [query, ...recentSearches.filter(s => s !== query)].slice(0, 5);
      setRecentSearches(newRecent);
      localStorage.setItem('recentSearches', JSON.stringify(newRecent));
    }
  }, [router, query, recentSearches]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((i) => (i + 1) % flatCommands.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((i) => (i - 1 + flatCommands.length) % flatCommands.length);
        break;
      case 'Enter':
        e.preventDefault();
        if (flatCommands[selectedIndex]) {
          handleSelect(flatCommands[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  }, [flatCommands, selectedIndex, handleSelect]);

  return (
    <>
      {/* Trigger button in Navbar */}
      <button
        onClick={() => setIsOpen(true)}
        className="hidden sm:flex items-center gap-2 rounded-full px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all group"
      >
        <Search className="h-4 w-4" />
        <span className="text-gray-400 dark:text-gray-500">Search...</span>
        <kbd className="hidden lg:inline-flex items-center gap-1 px-2 py-0.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-xs text-gray-500 dark:text-gray-400">
          <Command className="h-3 w-3" />K
        </kbd>
      </button>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
            />

            {/* Command Palette */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-x-4 top-[15%] z-50 mx-auto max-w-xl"
            >
              <div className="overflow-hidden rounded-2xl bg-white dark:bg-gray-900 shadow-2xl ring-1 ring-gray-900/10 dark:ring-gray-100/10">
                {/* Search input */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                  <Search className="h-5 w-5 text-gray-400" />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      setSelectedIndex(0);
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Search commands, pages..."
                    className="flex-1 bg-transparent outline-none text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                  />
                  <kbd className="hidden sm:inline-flex px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-500 dark:text-gray-400">
                    ESC
                  </kbd>
                </div>

                {/* Results */}
                <div className="max-h-80 overflow-y-auto p-2">
                  {flatCommands.length === 0 ? (
                    <div className="py-8 text-center text-gray-500 dark:text-gray-400">
                      No results found for "{query}"
                    </div>
                  ) : (
                    Object.entries(groupedCommands).map(([category, commands]) => (
                      <div key={category} className="mb-2">
                        <div className="px-3 py-1.5 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                          {category}
                        </div>
                        {commands.map((command) => {
                          const isSelected = flatCommands.indexOf(command) === selectedIndex;
                          const Icon = command.icon;
                          return (
                            <button
                              key={command.id}
                              onClick={() => handleSelect(command)}
                              onMouseEnter={() => setSelectedIndex(flatCommands.indexOf(command))}
                              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                                isSelected
                                  ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                              }`}
                            >
                              <div className={`p-2 rounded-lg ${
                                isSelected
                                  ? 'bg-purple-100 dark:bg-purple-800/50'
                                  : 'bg-gray-100 dark:bg-gray-800'
                              }`}>
                                <Icon className="h-4 w-4" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="font-medium truncate">{command.name}</p>
                                {command.description && (
                                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                                    {command.description}
                                  </p>
                                )}
                              </div>
                              {isSelected && (
                                <ArrowRight className="h-4 w-4 text-purple-500" />
                              )}
                            </button>
                          );
                        })}
                      </div>
                    ))
                  )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center gap-2">
                    <span>↑↓ Navigate</span>
                    <span>↵ Select</span>
                    <span>ESC Close</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    CAAFW
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

