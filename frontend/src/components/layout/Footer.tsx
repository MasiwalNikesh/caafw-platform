"use client";

import Link from "next/link";
import Image from "next/image";
import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";

// Import logo for dark background (dark logo works on dark bg)
import logoDark from "@/img/logo-caafw-dark.png";

const quickLinks = [
  { name: "About Us", href: "/about" },
  { name: "Programs", href: "/programs" },
  { name: "Resources", href: "/learning" },
  { name: "Community", href: "/community" },
];

const discoverLinks = [
  { name: "AI Products", href: "/products" },
  { name: "Research", href: "/research" },
  { name: "MCP Servers", href: "/mcp" },
  { name: "Investments", href: "/investments" },
];

const connectLinks = [
  { name: "Contact Us", href: "/contact" },
  { name: "Careers", href: "/jobs" },
  { name: "Events", href: "/events" },
  { name: "AI Quiz", href: "/quiz" },
];

export function Footer() {
  const { theme, resolvedTheme, setTheme } = useTheme();

  const cycleTheme = () => {
    if (theme === "light") setTheme("dark");
    else if (theme === "dark") setTheme("system");
    else setTheme("light");
  };

  const getThemeIcon = () => {
    if (theme === "system") return <Monitor className="h-4 w-4" />;
    if (resolvedTheme === "dark") return <Sun className="h-4 w-4" />;
    return <Moon className="h-4 w-4" />;
  };

  const getThemeLabel = () => {
    if (theme === "system") return "System";
    if (resolvedTheme === "dark") return "Light";
    return "Dark";
  };

  return (
    <footer className="bg-gray-900 text-gray-400">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="inline-block">
              <Image src={logoDark} alt="CAAFW Logo" height={48} />
            </Link>
            <p className="mt-4 text-sm max-w-sm">
              Centre for Applied AI and Future of Work (CAAFW) — A community
              initiative dedicated to empowering organizations with responsible
              AI adoption through education, experimentation, and compliance
              support.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-sm hover:text-white transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Discover */}
          <div>
            <h3 className="font-semibold text-white mb-4">Discover</h3>
            <ul className="space-y-2">
              {discoverLinks.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-sm hover:text-white transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h3 className="font-semibold text-white mb-4">Connect</h3>
            <ul className="space-y-2">
              {connectLinks.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-sm hover:text-white transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm">
            &copy; {new Date().getFullYear()} Centre for Applied AI and Future
            of Work (CAAFW). All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            {/* Theme Toggle */}
            <button
              onClick={cycleTheme}
              className="inline-flex items-center gap-2 text-sm text-gray-400 border border-gray-700 rounded-full px-4 py-2 hover:bg-gray-800 hover:text-white transition-all"
              aria-label="Toggle theme"
            >
              {getThemeIcon()}
              <span>{getThemeLabel()}</span>
            </button>
            <Link
              href="/privacy"
              className="text-sm hover:text-white transition-colors"
            >
              Privacy
            </Link>
            <Link
              href="/terms"
              className="text-sm hover:text-white transition-colors"
            >
              Terms
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
