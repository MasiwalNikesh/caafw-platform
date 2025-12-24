'use client';

import Link from 'next/link';
import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  MessageSquare,
  Mail,
  Globe,
  Users,
  Sparkles,
  BookOpen,
  Shield,
  Briefcase,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  Star,
  Play,
  Compass,
  Rocket,
  GraduationCap,
  Building2,
  Lightbulb,
  Target,
  Brain,
  Zap,
  BarChart3,
  Award,
  Clock,
  CheckCircle2,
  Quote,
  Calendar,
  TrendingUp,
  FileText,
  Monitor,
  UserPlus,
  Send,
  Link2,
} from 'lucide-react';
import { FadeIn, AnimatedStat, StaggeredList, StaggeredItem } from '@/components/ui/animations';

// Stats
const stats = [
  { value: '100+', label: 'Organizations Impacted' },
  { value: '50+', label: 'Workshops Delivered' },
  { value: '15+', label: 'Project Partners' },
];

// Community Pillars
const pillars = [
  {
    name: 'Discover',
    description: 'Explore AI opportunities and possibilities through curated resources, success stories, and insights from industry leaders and practitioners.',
    icon: Compass,
    features: ['AI Learning Library', 'Industry Insights', 'Success Stories', 'Emerging trends & tools', 'AI Marketplace'],
    color: 'from-blue-500 to-cyan-500',
  },
  {
    name: 'LEARN',
    description: 'Comprehensive training programs, workshops, and resources designed to build AI literacy and technical capabilities across all organizational levels.',
    icon: BookOpen,
    features: ['Interactive workshops and seminars', 'Online learning resources', 'Certification programs', 'Custom training for teams'],
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'Experiment',
    description: 'Safe sandbox environments and practical labs where organizations can test, prototype, and validate AI solutions before full-scale deployment.',
    icon: Lightbulb,
    features: ['Sandboxes and servers', 'Proof-of-concept support', 'Innovation labs', 'Guided prototyping'],
    color: 'from-orange-500 to-amber-500',
  },
  {
    name: 'Comply',
    description: 'Expert guidance on navigating AI regulations, ethical frameworks, and industry standards to ensure responsible and compliant AI adoption.',
    icon: Shield,
    features: ['Regulatory guidance', 'Ethics Resources', 'Risk assessment tools', 'Compliance documentation'],
    color: 'from-green-500 to-emerald-500',
  },
  {
    name: 'Grow',
    description: 'Scale your startup with strategic support covering startup spotlight, investor insights, and innovation cohorts to accelerate your growth journey.',
    icon: TrendingUp,
    features: ['Startup showcase', 'Investor network', 'Innovation Scouts with CFIs', 'Startup accelerator'],
    color: 'from-indigo-500 to-violet-500',
  },
  {
    name: 'Work',
    description: 'Connect to opportunities, collaborate on projects, and access tools and resources to implement AI solutions in real-world business scenarios.',
    icon: Briefcase,
    features: ['Project collaborator', 'Job connections', 'Partnership integration', 'Opportunity support'],
    color: 'from-rose-500 to-red-500',
  },
];

// Programs
const programs = [
  {
    title: 'Community Workshops',
    frequency: 'Monthly',
    description: 'Regular collaborative sessions bringing together AI practitioners, business leaders, and technology enthusiasts to share knowledge and experiences.',
    icon: Users,
    badge: null,
  },
  {
    title: 'Innovation Incubator',
    frequency: 'Quarterly Cohorts',
    description: 'Structured programs supporting Small and Medium Businesses in developing and implementing AI-driven solutions with expert mentorship and technical resources.',
    icon: Rocket,
    badge: 'Applications Open',
  },
  {
    title: 'Executive Briefings',
    frequency: 'Bi-monthly',
    description: 'Focused sessions for leadership teams on AI strategy, governance, and organizational transformation in the age of artificial intelligence.',
    icon: Monitor,
    badge: null,
  },
  {
    title: 'Industry Partnerships',
    frequency: 'Ongoing',
    description: 'Collaborative initiatives with industry leaders, academic institutions, and regulatory bodies to advance AI best practices and standards.',
    icon: Link2,
    badge: 'Now accepting applications',
  },
];

// Get Involved options
const getInvolvedOptions = [
  {
    title: 'Subscribe',
    description: 'Get updates on events and resources',
    icon: Mail,
    href: '/subscribe',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    title: 'Events',
    description: 'Join workshops, webinars & meetups',
    icon: Calendar,
    href: '/events',
    color: 'from-purple-500 to-pink-500',
  },
  {
    title: 'Join Community',
    description: 'Connect with peers and practitioners',
    icon: Users,
    href: '/community',
    color: 'from-orange-500 to-amber-500',
  },
];

// Values
const values = [
  {
    title: 'Accessibility',
    description: 'Making AI education and resources available to all organizations regardless of size or budget',
    icon: Users,
  },
  {
    title: 'Responsibility',
    description: 'Promoting ethical AI practices and ensuring compliance with evolving regulations',
    icon: Shield,
  },
  {
    title: 'Collaboration',
    description: 'Building a community where knowledge sharing and connections drive innovation',
    icon: Link2,
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-white dark:from-gray-800 dark:to-gray-900 pt-24 sm:pt-28 pb-16">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-purple-100 dark:bg-purple-900/30 opacity-50 blur-3xl" />
          <div className="absolute top-20 -left-20 h-60 w-60 rounded-full bg-blue-100 dark:bg-blue-900/30 opacity-50 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-4">
          {/* Main headline */}
          <div className="text-center max-w-4xl mx-auto">
            <FadeIn delay={0.1}>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white tracking-tight">
                Centre for{' '}
                <span className="bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 bg-clip-text text-transparent">
                  Applied AI
                </span>
              </h1>
            </FadeIn>
            <FadeIn delay={0.2}>
              <p className="mt-4 text-xl sm:text-2xl font-medium text-gray-700 dark:text-gray-200">
                Applied AI Community for Future-Ready SMBs & Innovators
              </p>
            </FadeIn>
            <FadeIn delay={0.3}>
              <p className="mt-6 text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
                Building an inclusive community for SMB and AI enthusiasts—learn, experiment, and adopt AI responsibly to save time, grow sustainably, and build customer trust.
              </p>
            </FadeIn>

            {/* Tags */}
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <span className="px-4 py-2 rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm font-medium border border-purple-100 dark:border-purple-800">
                Education & Reskilling
              </span>
              <span className="px-4 py-2 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium border border-blue-100 dark:border-blue-800">
                Applied AI Labs
              </span>
              <span className="px-4 py-2 rounded-full bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-sm font-medium border border-green-100 dark:border-green-800">
                Responsible AI & Compliance
              </span>
            </div>

            {/* CTA buttons */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all hover:-translate-y-0.5"
              >
                Join Us
              </Link>
              <Link
                href="/quiz"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-white dark:bg-gray-800 px-8 py-4 text-base font-semibold text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all"
              >
                <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                AI Readiness Quiz
              </Link>
              <Link
                href="/events"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-white dark:bg-gray-800 px-8 py-4 text-base font-semibold text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all"
              >
                <Calendar className="h-5 w-5" />
                Events
              </Link>
            </div>

            {/* Stats */}
            <div className="mt-12 flex flex-wrap justify-center gap-8 sm:gap-12">
              {stats.map((stat, index) => (
                <AnimatedStat
                  key={stat.label}
                  value={stat.value}
                  label={stat.label}
                  delay={0.5 + index * 0.1}
                  className="text-center"
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
              Our Mission
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              We bridge the gap between AI innovation and practical business implementation, ensuring Small and Medium Businesses can harness AI's potential while maintaining ethical standards and regulatory compliance.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 mt-12">
            {/* Why We Exist */}
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-3xl p-8 border border-purple-100 dark:border-purple-800">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Why We Exist</h3>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                The rapid advancement of AI technology has created both unprecedented opportunities and challenges for small and medium enterprises. Many organizations lack the resources, expertise, or guidance to navigate this transformation effectively.
              </p>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed mt-4">
                We provide a trusted platform that democratizes access to AI knowledge, tools, and best practices, ensuring no business is left behind in the AI revolution.
              </p>
            </div>

            {/* What We Stand For */}
            <div className="bg-gradient-to-br from-slate-50 to-gray-50 dark:from-gray-800 dark:to-gray-800 rounded-3xl p-8 border border-gray-100 dark:border-gray-700">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">What We Stand For</h3>
              <div className="space-y-6">
                {values.map((value) => (
                  <div key={value.title} className="flex gap-4">
                    <div className="p-2 rounded-xl bg-white dark:bg-gray-700 shadow-sm h-fit">
                      <value.icon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">{value.title}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{value.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Community Pillars Section */}
      <section className="py-20 bg-gradient-to-b from-white to-slate-50 dark:from-gray-900 dark:to-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
              Key Community Pillars
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              A comprehensive approach to responsible AI adoption
            </p>
          </div>

          <StaggeredList className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pillars.map((pillar) => (
              <StaggeredItem
                key={pillar.name}
                className="group bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 p-6 hover:shadow-xl hover:shadow-purple-500/10 transition-all"
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${pillar.color}`}>
                    <pillar.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{pillar.name}</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">{pillar.description}</p>
                <ul className="space-y-2">
                  {pillar.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </StaggeredItem>
            ))}
          </StaggeredList>
        </div>
      </section>

      {/* Programs Section */}
      <section className="py-20 bg-slate-50 dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
              Our Programs
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Diverse initiatives designed to support your AI journey at every stage
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {programs.map((program) => (
              <div
                key={program.title}
                className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/30 dark:to-indigo-900/30">
                      <program.icon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">{program.title}</h3>
                      <p className="text-sm text-purple-600 dark:text-purple-400 font-medium">{program.frequency}</p>
                    </div>
                  </div>
                  {program.badge && (
                    <span className="px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium">
                      {program.badge}
                    </span>
                  )}
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">{program.description}</p>
              </div>
            ))}
          </div>

          <div className="mt-10 text-center">
            <Link
              href="/events"
              className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-4 font-semibold text-white shadow-lg shadow-purple-500/30 hover:shadow-xl transition-all"
            >
              View All Programs & Events
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Get Involved Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
              Get Involved
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Join our community and start your AI transformation journey today
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {getInvolvedOptions.map((option) => (
              <Link
                key={option.title}
                href={option.href}
                className="group flex flex-col items-center p-8 rounded-2xl bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 border border-gray-100 dark:border-gray-700 hover:border-purple-200 dark:hover:border-purple-700 hover:shadow-lg transition-all hover:-translate-y-1"
              >
                <div className={`p-4 rounded-2xl bg-gradient-to-br ${option.color} mb-4`}>
                  <option.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">{option.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm text-center mt-2">{option.description}</p>
                <span className="mt-4 text-purple-600 dark:text-purple-400 font-medium group-hover:underline">
                  Learn more →
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Partner With Us Section */}
      <section className="py-20 bg-gradient-to-b from-white to-slate-50 dark:from-gray-900 dark:to-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 to-indigo-700 p-8 md:p-12 text-center">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-indigo-400/20 rounded-full blur-2xl" />

            <div className="relative">
              <div className="inline-flex p-4 rounded-2xl bg-white/10 backdrop-blur-sm mb-6">
                <Link2 className="h-10 w-10 text-white" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Partner With Us
              </h2>
              <p className="text-lg text-purple-100 max-w-2xl mx-auto mb-8">
                Are you an organization, academic institution, or industry expert interested in collaborating? Let's work together to shape the future of responsible AI adoption.
              </p>
              <Link
                href="/partnerships"
                className="inline-flex items-center gap-2 rounded-full bg-white px-8 py-4 text-lg font-semibold text-purple-700 shadow-xl hover:shadow-2xl hover:-translate-y-0.5 transition-all"
              >
                Explore Partnership Opportunities
                <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
