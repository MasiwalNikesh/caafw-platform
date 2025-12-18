import Link from 'next/link';
import { Cpu } from 'lucide-react';

const quickLinks = [
  { name: 'About Us', href: '/about' },
  { name: 'Programs', href: '/programs' },
  { name: 'Resources', href: '/learn' },
  { name: 'Community', href: '/community' },
];

const connectLinks = [
  { name: 'Contact Us', href: '/contact' },
  { name: 'Careers', href: '/jobs' },
  { name: 'Success Stories', href: '/community' },
  { name: 'Events', href: '/events' },
];

export function Footer() {
  return (
    <footer className="bg-gray-100 border-t border-gray-200">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <Link href="/" className="flex items-center gap-2 text-gray-900">
              <Cpu className="h-6 w-6" />
              <span className="font-bold">Centre for Applied AI and Future of Work (CAAFW)</span>
            </Link>
            <p className="mt-4 text-sm text-gray-600">
              A community initiative dedicated to empowering organizations with responsible AI
              adoption through education, experimentation, and compliance support.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Connect</h3>
            <ul className="space-y-2">
              {connectLinks.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Centre for Applied AI and Future of Work (CAAFW). All
            rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <button className="inline-flex items-center gap-1 text-sm text-gray-600 border border-gray-300 rounded-full px-3 py-1">
              <span className="text-xs">🌐</span> Global
            </button>
            <button className="inline-flex items-center gap-1 text-sm text-gray-600 border border-gray-300 rounded-full px-3 py-1">
              <span className="text-xs">✨</span> Modern
            </button>
            <Link href="/privacy" className="text-sm text-gray-600 hover:text-gray-900">
              Privacy Policy
            </Link>
            <Link href="/terms" className="text-sm text-gray-600 hover:text-gray-900">
              Terms of Use
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
