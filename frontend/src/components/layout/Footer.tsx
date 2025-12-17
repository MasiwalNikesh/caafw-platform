import Link from 'next/link';
import { Cpu, Github, Twitter } from 'lucide-react';

const navigation = {
  main: [
    { name: 'Products', href: '/products' },
    { name: 'Jobs', href: '/jobs' },
    { name: 'Research', href: '/research' },
    { name: 'Learning', href: '/learning' },
    { name: 'MCP Servers', href: '/mcp' },
    { name: 'Community', href: '/community' },
    { name: 'Events', href: '/events' },
    { name: 'Investments', href: '/investments' },
  ],
  social: [
    { name: 'GitHub', href: '#', icon: Github },
    { name: 'Twitter', href: '#', icon: Twitter },
  ],
};

export function Footer() {
  return (
    <footer className="bg-gray-900">
      <div className="mx-auto max-w-7xl overflow-hidden px-6 py-20 sm:py-24 lg:px-8">
        <div className="flex flex-col items-center mb-8">
          <Link href="/" className="flex items-center gap-2 text-white">
            <Cpu className="h-8 w-8" />
            <span className="font-bold text-xl">CAAFW</span>
          </Link>
          <p className="text-gray-400 text-sm mt-2">Centre for Applied AI and Future of Work</p>
        </div>
        <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2" aria-label="Footer">
          {navigation.main.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="text-sm leading-6 text-gray-400 hover:text-white transition-colors"
            >
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="mt-10 flex justify-center space-x-10">
          {navigation.social.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <span className="sr-only">{item.name}</span>
              <item.icon className="h-6 w-6" aria-hidden="true" />
            </a>
          ))}
        </div>
        <p className="mt-10 text-center text-xs leading-5 text-gray-500">
          &copy; {new Date().getFullYear()} CAAFW - Centre for Applied AI and Future of Work. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
