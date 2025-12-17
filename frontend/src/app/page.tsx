import Link from 'next/link';
import {
  Cpu,
  Briefcase,
  FileText,
  BookOpen,
  Server,
  Users,
  Calendar,
  TrendingUp,
} from 'lucide-react';

const features = [
  {
    name: 'AI Products',
    description: 'Discover the latest AI tools and products',
    href: '/products',
    icon: Cpu,
    color: 'bg-blue-500',
  },
  {
    name: 'Jobs',
    description: 'Find AI and ML job opportunities',
    href: '/jobs',
    icon: Briefcase,
    color: 'bg-green-500',
  },
  {
    name: 'Research',
    description: 'Latest papers from arXiv and more',
    href: '/research',
    icon: FileText,
    color: 'bg-purple-500',
  },
  {
    name: 'Learning',
    description: 'Courses and tutorials to level up',
    href: '/learning',
    icon: BookOpen,
    color: 'bg-orange-500',
  },
  {
    name: 'MCP Servers',
    description: 'Model Context Protocol servers',
    href: '/mcp',
    icon: Server,
    color: 'bg-pink-500',
  },
  {
    name: 'Community',
    description: 'HN, Reddit, and GitHub trending',
    href: '/community',
    icon: Users,
    color: 'bg-cyan-500',
  },
  {
    name: 'Events',
    description: 'AI conferences and meetups',
    href: '/events',
    icon: Calendar,
    color: 'bg-yellow-500',
  },
  {
    name: 'Investments',
    description: 'AI startup funding and companies',
    href: '/investments',
    icon: TrendingUp,
    color: 'bg-red-500',
  },
];

export default function HomePage() {
  return (
    <div className="bg-white">
      {/* Hero section */}
      <div className="relative isolate overflow-hidden bg-gradient-to-b from-indigo-100/20">
        <div className="mx-auto max-w-7xl px-6 pb-24 pt-10 sm:pb-32 lg:flex lg:px-8 lg:py-40">
          <div className="mx-auto max-w-2xl lg:mx-0 lg:max-w-xl lg:flex-shrink-0 lg:pt-8">
            <h1 className="mt-10 text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Centre for Applied AI and Future of Work
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Your comprehensive hub for AI products, jobs, research, learning resources,
              and community insights. Preparing you for the future of work.
            </p>
            <div className="mt-10 flex items-center gap-x-6">
              <Link
                href="/products"
                className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Explore Products
              </Link>
              <Link
                href="/research"
                className="text-sm font-semibold leading-6 text-gray-900"
              >
                Browse Research <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features section */}
      <div className="mx-auto max-w-7xl px-6 lg:px-8 pb-24">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-indigo-600">
            Everything AI
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            All the resources you need
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            From discovering new tools to finding your next job, we aggregate
            the best AI resources from across the web.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-4 md:grid-cols-2">
            {features.map((feature) => (
              <Link
                key={feature.name}
                href={feature.href}
                className="group relative rounded-2xl border border-gray-200 p-6 hover:border-indigo-500 hover:shadow-lg transition-all duration-200"
              >
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <div
                    className={`${feature.color} rounded-lg p-2 text-white group-hover:scale-110 transition-transform`}
                  >
                    <feature.icon className="h-5 w-5" aria-hidden="true" />
                  </div>
                  {feature.name}
                </dt>
                <dd className="mt-4 text-base leading-7 text-gray-600">
                  {feature.description}
                </dd>
              </Link>
            ))}
          </dl>
        </div>
      </div>

      {/* Stats section */}
      <div className="bg-gray-900 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:max-w-none">
            <div className="text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Trusted by AI enthusiasts worldwide
              </h2>
              <p className="mt-4 text-lg leading-8 text-gray-300">
                We aggregate data from the best sources to bring you quality content
              </p>
            </div>
            <dl className="mt-16 grid grid-cols-1 gap-0.5 overflow-hidden rounded-2xl text-center sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: 'AI Products', value: '20,000+' },
                { label: 'Research Papers', value: '100,000+' },
                { label: 'Jobs Listed', value: '10,000+' },
                { label: 'MCP Servers', value: '1,000+' },
              ].map((stat) => (
                <div key={stat.label} className="flex flex-col bg-white/5 p-8">
                  <dt className="text-sm font-semibold leading-6 text-gray-300">
                    {stat.label}
                  </dt>
                  <dd className="order-first text-3xl font-semibold tracking-tight text-white">
                    {stat.value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
