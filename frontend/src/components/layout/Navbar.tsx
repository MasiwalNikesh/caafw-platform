"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { usePathname } from "next/navigation";
import {
  Menu,
  X,
  Search,
  User,
  LogOut,
  Sparkles,
  ChevronDown,
  Compass,
  BookOpen,
  Users,
  Briefcase,
  Cpu,
  FileText,
  Server,
  TrendingUp,
  Calendar,
  GraduationCap,
  MessageSquare,
  Github,
  Newspaper,
  Building2,
  Info,
  Target,
  Route,
  Bookmark,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { CommandPalette } from "@/components/ui/CommandPalette";

// Import logos (light logo for light backgrounds, dark logo for dark backgrounds)
import logoLight from "@/img/logo-caafw-light.png";
import logoDark from "@/img/logo-caafw-dark.png";

interface NavItem {
  name: string;
  href?: string;
  icon?: any;
  description?: string;
  children?: NavItem[];
}

const navigation: NavItem[] = [
  { name: "About", href: "/about", icon: Info },
  {
    name: "Discover",
    icon: Compass,
    children: [
      {
        name: "AI Products",
        href: "/products",
        icon: Cpu,
        description: "Latest AI tools and products",
      },
      {
        name: "Research",
        href: "/research",
        icon: FileText,
        description: "Papers from arXiv & more",
      },
      {
        name: "MCP Servers",
        href: "/mcp",
        icon: Server,
        description: "Model Context Protocol",
      },
      {
        name: "Investments",
        href: "/investments",
        icon: TrendingUp,
        description: "AI startup funding",
      },
    ],
  },
  {
    name: "Learn",
    icon: BookOpen,
    children: [
      {
        name: "AI Literacy",
        href: "/learn",
        icon: GraduationCap,
        description: "Learn about AI responsibly",
      },
      {
        name: "Learning Paths",
        href: "/learning-paths",
        icon: Route,
        description: "Curated learning journeys",
      },
      {
        name: "Courses & Resources",
        href: "/learning",
        icon: BookOpen,
        description: "Tutorials and courses",
      },
      {
        name: "Programs",
        href: "/programs",
        icon: Target,
        description: "Workshops & incubators",
      },
    ],
  },
  {
    name: "Community",
    icon: Users,
    children: [
      {
        name: "Discussions",
        href: "/community",
        icon: MessageSquare,
        description: "HN, Reddit & GitHub",
      },
      {
        name: "Events",
        href: "/events",
        icon: Calendar,
        description: "Meetups & conferences",
      },
    ],
  },
  { name: "Jobs", href: "/jobs", icon: Briefcase },
];

const levelColors: Record<string, string> = {
  novice: "bg-blue-500",
  beginner: "bg-green-500",
  intermediate: "bg-yellow-500",
  expert: "bg-purple-500",
};

function DropdownMenu({
  item,
  isOpen,
  onToggle,
}: {
  item: NavItem;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        if (isOpen) onToggle();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onToggle]);

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={onToggle}
        className={`flex items-center gap-1 text-sm font-medium leading-6 transition-colors ${
          isOpen
            ? "text-purple-600 dark:text-purple-400"
            : "text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400"
        }`}
      >
        {item.name}
        <ChevronDown
          className={`h-4 w-4 transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Dropdown */}
      <div
        className={`absolute left-1/2 -translate-x-1/2 mt-4 w-72 origin-top transition-all duration-200 ${
          isOpen
            ? "opacity-100 scale-100 translate-y-0"
            : "opacity-0 scale-95 -translate-y-2 pointer-events-none"
        }`}
      >
        <div className="rounded-2xl bg-white dark:bg-gray-800 shadow-xl ring-1 ring-gray-900/5 dark:ring-gray-700 overflow-hidden">
          <div className="p-2">
            {item.children?.map((child) => (
              <Link
                key={child.name}
                href={child.href || "#"}
                onClick={onToggle}
                className="group flex items-start gap-3 rounded-xl p-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                {child.icon && (
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700 group-hover:bg-purple-100 dark:group-hover:bg-purple-900/50 transition-colors">
                    <child.icon className="h-5 w-5 text-gray-600 dark:text-gray-300 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors" />
                  </div>
                )}
                <div>
                  <p className="font-medium text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                    {child.name}
                  </p>
                  {child.description && (
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {child.description}
                    </p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const { user, profile, isAuthenticated, isLoading, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    setUserMenuOpen(false);
  };

  const isHomePage = pathname === "/";

  // Always use light navbar style (dark text) since our backgrounds are light
  const useDarkText = true;

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm"
          : "bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm"
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-4 lg:px-8">
        {/* Logo */}
        <div className="flex lg:flex-1">
          <Link href="/" className="flex items-center group">
            {/* Logo for light mode (light logo on light bg) */}
            <Image
              src={logoLight}
              alt="CAAFW Logo"
              height={48}
              className="block dark:hidden"
              priority
            />
            {/* Logo for dark mode (dark logo on dark bg) */}
            <Image
              src={logoDark}
              alt="CAAFW Logo"
              height={48}
              className="hidden dark:block"
              priority
            />
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-lg p-2.5 text-gray-700 hover:bg-gray-100 transition-colors"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex lg:items-center lg:gap-x-8">
          {navigation.map((item) =>
            item.children ? (
              <DropdownMenu
                key={item.name}
                item={item}
                isOpen={openDropdown === item.name}
                onToggle={() =>
                  setOpenDropdown(openDropdown === item.name ? null : item.name)
                }
              />
            ) : (
              <Link
                key={item.name}
                href={item.href || "#"}
                className="text-sm font-medium leading-6 text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
              >
                {item.name}
              </Link>
            )
          )}
        </div>

        {/* Right side actions */}
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:items-center lg:gap-x-3">
          {/* Search - Command Palette */}
          <CommandPalette />

          {/* AI Quiz Button */}
          <Link
            href="/quiz"
            className="flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-all hover:scale-105 hover:shadow-lg hover:shadow-purple-500/25"
          >
            <Sparkles className="h-4 w-4" />
            <span className="hidden xl:inline">AI Quiz</span>
          </Link>

          {/* Auth */}
          {!isLoading && (
            <>
              {isAuthenticated ? (
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-2 rounded-full px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
                  >
                    {user?.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.name || "User"}
                        className="h-6 w-6 rounded-full"
                      />
                    ) : (
                      <div className="h-6 w-6 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <User className="h-3.5 w-3.5 text-white" />
                      </div>
                    )}
                    <span className="max-w-20 truncate hidden xl:inline">
                      {user?.name || user?.email?.split("@")[0]}
                    </span>
                    {profile?.ai_level && (
                      <span
                        className={`px-1.5 py-0.5 text-xs font-medium text-white rounded ${
                          levelColors[profile.ai_level] || "bg-gray-500"
                        }`}
                      >
                        {profile.ai_level.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </button>

                  {/* User Dropdown */}
                  {userMenuOpen && (
                    <>
                      <div
                        className="fixed inset-0 z-40"
                        onClick={() => setUserMenuOpen(false)}
                      />
                      <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-white dark:bg-gray-800 shadow-xl ring-1 ring-gray-900/5 dark:ring-gray-700 z-50 overflow-hidden">
                        <div className="p-3 border-b border-gray-100 dark:border-gray-700">
                          <p className="font-medium text-gray-900 dark:text-white">
                            {user?.name || "User"}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                            {user?.email}
                          </p>
                          {profile?.ai_level && (
                            <span
                              className={`inline-block mt-2 px-2 py-0.5 text-xs font-medium text-white rounded-full ${
                                levelColors[profile.ai_level] || "bg-gray-500"
                              }`}
                            >
                              {profile.ai_level.charAt(0).toUpperCase() +
                                profile.ai_level.slice(1)}{" "}
                              Level
                            </span>
                          )}
                        </div>
                        <div className="p-2">
                          <Link
                            href="/bookmarks"
                            onClick={() => setUserMenuOpen(false)}
                            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                          >
                            <Bookmark className="h-4 w-4 text-purple-500" />
                            My Bookmarks
                          </Link>
                          <Link
                            href="/quiz"
                            onClick={() => setUserMenuOpen(false)}
                            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                          >
                            <Sparkles className="h-4 w-4 text-purple-500" />
                            {profile?.has_completed_quiz
                              ? "Retake Quiz"
                              : "Take AI Quiz"}
                          </Link>
                          <button
                            onClick={handleLogout}
                            className="flex items-center gap-3 w-full rounded-xl px-3 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                          >
                            <LogOut className="h-4 w-4 text-gray-400" />
                            Sign out
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Link
                    href="/login"
                    className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
                  >
                    Sign in
                  </Link>
                  <Link
                    href="/register"
                    className="rounded-full px-4 py-2 text-sm font-medium bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 transition-all hover:scale-105"
                  >
                    Join Us
                  </Link>
                </div>
              )}
            </>
          )}
        </div>
      </nav>

      {/* Mobile menu */}
      <div
        className={`lg:hidden fixed inset-0 z-50 transition-opacity duration-300 ${
          mobileMenuOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
      >
        <div
          className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm"
          onClick={() => setMobileMenuOpen(false)}
        />
        <div
          className={`fixed inset-y-0 right-0 z-50 w-full max-w-sm bg-white dark:bg-gray-900 shadow-2xl transition-transform duration-300 isolate ${
            mobileMenuOpen ? "translate-x-0" : "translate-x-full"
          }`}
        >
          <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
            <Link
              href="/"
              className="flex items-center"
              onClick={() => setMobileMenuOpen(false)}
            >
              {/* Logo for light mode */}
              <Image
                src={logoLight}
                alt="CAAFW Logo"
                height={40}
                className="block dark:hidden"
              />
              {/* Logo for dark mode */}
              <Image
                src={logoDark}
                alt="CAAFW Logo"
                height={40}
                className="hidden dark:block"
              />
            </Link>
            <button
              type="button"
              className="rounded-lg p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
              onClick={() => setMobileMenuOpen(false)}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="overflow-y-auto h-[calc(100vh-80px)] p-4 bg-white dark:bg-gray-900">
            {/* AI Quiz CTA */}
            <Link
              href="/quiz"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-center gap-2 w-full rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-3 text-white font-medium mb-6"
            >
              <Sparkles className="h-5 w-5" />
              Take AI Readiness Quiz
            </Link>

            {/* Navigation */}
            <div className="space-y-1">
              {navigation.map((item) => (
                <div key={item.name}>
                  {item.children ? (
                    <div className="py-2">
                      <p className="px-3 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2">
                        {item.name}
                      </p>
                      <div className="space-y-1">
                        {item.children.map((child) => (
                          <Link
                            key={child.name}
                            href={child.href || "#"}
                            onClick={() => setMobileMenuOpen(false)}
                            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
                          >
                            {child.icon && (
                              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-800">
                                <child.icon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                              </div>
                            )}
                            <div>
                              <p className="font-medium">{child.name}</p>
                              {child.description && (
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  {child.description}
                                </p>
                              )}
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <Link
                      href={item.href || "#"}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-3 rounded-xl px-3 py-3 text-gray-900 dark:text-white font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      {item.icon && (
                        <item.icon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                      )}
                      {item.name}
                    </Link>
                  )}
                </div>
              ))}
            </div>

            {/* Search */}
            <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800">
              <Link
                href="/search"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-3 rounded-xl px-3 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <Search className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                Search
              </Link>
            </div>

            {/* Auth Section */}
            <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800">
              {!isLoading && (
                <>
                  {isAuthenticated ? (
                    <div className="space-y-3">
                      <div className="flex items-center gap-3 px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded-xl">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                          <User className="h-5 w-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 dark:text-white truncate">
                            {user?.name || user?.email?.split("@")[0]}
                          </p>
                          {profile?.ai_level && (
                            <span
                              className={`inline-block px-2 py-0.5 text-xs font-medium text-white rounded-full ${
                                levelColors[profile.ai_level] || "bg-gray-500"
                              }`}
                            >
                              {profile.ai_level.charAt(0).toUpperCase() +
                                profile.ai_level.slice(1)}
                            </span>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          logout();
                          setMobileMenuOpen(false);
                        }}
                        className="flex items-center gap-3 w-full rounded-xl px-3 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                        <LogOut className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                        Sign out
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Link
                        href="/login"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block text-center rounded-xl px-4 py-3 text-gray-700 dark:text-gray-200 font-medium border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                        Sign in
                      </Link>
                      <Link
                        href="/register"
                        onClick={() => setMobileMenuOpen(false)}
                        className="block text-center rounded-xl px-4 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium hover:bg-gray-800 dark:hover:bg-gray-100"
                      >
                        Join Us
                      </Link>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
