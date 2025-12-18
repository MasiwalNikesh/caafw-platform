'use client';

import { useState } from 'react';
import {
  GraduationCap,
  FlaskConical,
  Shield,
  BookOpen,
  Users,
  Clock,
  Award,
  Beaker,
  MessageSquare,
  Briefcase,
  ShoppingCart,
  BadgeCheck,
  FileCheck,
  Search,
  FileText,
  Sparkles
} from 'lucide-react';

type TabId = 'education' | 'labs' | 'compliance';

const tabs = [
  { id: 'education' as TabId, name: 'Education', icon: GraduationCap },
  { id: 'labs' as TabId, name: 'Applied Labs', icon: FlaskConical },
  { id: 'compliance' as TabId, name: 'Compliance', icon: Shield },
];

const educationPrograms = {
  title: 'Education & Reskilling',
  description: 'Comprehensive training programs, workshops, and resources designed to build AI literacy and technical capabilities across all organizational levels.',
  programs: [
    {
      name: 'Short Courses (CPD)',
      duration: '4-6 weeks',
      icon: BookOpen,
      items: [
        'AI for SME Leaders',
        'Generative AI for Marketing & Sales',
        'No-Code Automation for Operations',
        'Data-Driven Decision-Making',
      ],
      cta: 'View Courses',
    },
    {
      name: 'Bootcamps',
      duration: '8-12 weeks',
      icon: Users,
      items: [
        'AI Operations & Prompt Engineering',
        'Applied Analytics for SMEs',
        'Automation & RPA for Back-Office',
        'Responsible AI in Practice',
      ],
      cta: 'Join a Cohort',
    },
    {
      name: 'Digital Apprenticeships',
      icon: Briefcase,
      description: 'Structured pathways combining on-the-job learning with formal training, preparing your team for AI-driven roles.',
      cta: 'Learn More',
    },
    {
      name: 'Microcredentials',
      icon: Award,
      description: 'Earn CPD-accredited badges and certificates that validate your AI skills and knowledge.',
      cta: 'Browse Credentials',
    },
  ],
  featured: {
    name: 'Future Minds Program',
    icon: Sparkles,
    badge: 'Classes 4-11',
    description: 'AI Literacy & Future Skills for School Students. Ethics-first, facilitator-led programs focused on critical thinking, responsible AI use, digital safety, and career exploration—not coding pressure.',
    cta: 'Know More',
  },
};

const labsPrograms = {
  title: 'Applied AI Labs',
  description: 'Safe sandbox environments and practical labs where you can test, prototype, and validate AI solutions before full-scale deployment.',
  labs: [
    {
      name: 'Customer Support Copilot Lab',
      icon: MessageSquare,
      description: 'Build and test AI assistants for customer service, exploring chatbot frameworks and LLM integration.',
      cta: 'Book Session',
    },
    {
      name: 'SME Finance Automation Lab',
      icon: Briefcase,
      description: 'Experiment with invoice processing, expense management, and financial forecasting automation.',
      cta: 'Book Session',
    },
    {
      name: 'HR & Talent AI Assistant Lab',
      icon: Users,
      description: 'Prototype recruitment screening, candidate matching, and employee engagement tools.',
      cta: 'Book Session',
    },
    {
      name: 'Retail & eCommerce AI Lab',
      icon: ShoppingCart,
      description: 'Test personalization engines, inventory optimization, and demand forecasting models.',
      cta: 'Book Session',
    },
  ],
};

const compliancePrograms = {
  title: 'Responsible AI & Compliance',
  description: 'Expert guidance on navigating AI regulations, ethical frameworks, and industry standards to ensure responsible and compliant AI adoption.',
  programs: [
    {
      name: 'AI Trust Seal Certification',
      icon: BadgeCheck,
      description: 'Earn Bronze, Silver, or Gold certification demonstrating your commitment to responsible AI practices.',
      badges: ['Bronze', 'Silver', 'Gold'],
      cta: 'Apply Now',
    },
    {
      name: 'Responsible AI Readiness Workshop',
      icon: FileCheck,
      description: 'Interactive session covering ethics, bias detection, transparency, and governance frameworks.',
      cta: 'Register',
    },
    {
      name: 'Bias & Transparency Mini-Audit',
      icon: Search,
      description: 'Quick assessment of your AI systems for fairness, bias, and explainability issues.',
      cta: 'Request Audit',
    },
    {
      name: 'AI Governance Templates Pack',
      icon: FileText,
      description: 'Ready-to-use policy templates, risk assessments, and compliance documentation.',
      cta: 'Download Pack',
    },
  ],
};

export default function ProgramsPage() {
  const [activeTab, setActiveTab] = useState<TabId>('education');

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-amber-50 to-white">
        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              Our Programs
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              From foundational learning to advanced labs and compliance support— everything you need for responsible AI adoption.
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="flex justify-center">
          <div className="inline-flex rounded-full bg-gray-100 p-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 rounded-full px-6 py-3 text-sm font-medium transition-all
                  ${activeTab === tab.id
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                <tab.icon className="h-4 w-4" />
                {tab.name}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="mt-12 pb-24">
          {activeTab === 'education' && <EducationTab />}
          {activeTab === 'labs' && <LabsTab />}
          {activeTab === 'compliance' && <ComplianceTab />}
        </div>
      </div>
    </div>
  );
}

function EducationTab() {
  return (
    <div>
      <div className="text-center mb-12">
        <h2 className="text-2xl font-bold text-gray-900">{educationPrograms.title}</h2>
        <p className="mt-4 text-gray-600 max-w-2xl mx-auto">{educationPrograms.description}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 max-w-5xl mx-auto">
        {educationPrograms.programs.map((program) => (
          <div
            key={program.name}
            className="rounded-xl border border-gray-200 bg-white p-6 hover:border-amber-300 hover:shadow-md transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-amber-50 rounded-lg">
                  <program.icon className="h-5 w-5 text-amber-700" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">{program.name}</h3>
              </div>
              {program.duration && (
                <span className="flex items-center gap-1 text-sm text-amber-700">
                  <Clock className="h-4 w-4" />
                  {program.duration}
                </span>
              )}
            </div>

            {program.items ? (
              <ul className="space-y-2 mb-6">
                {program.items.map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="text-amber-600">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-600 mb-6">{program.description}</p>
            )}

            <button className="w-full rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
              {program.cta}
            </button>
          </div>
        ))}
      </div>

      {/* Featured Program */}
      <div className="mt-8 max-w-5xl mx-auto">
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <educationPrograms.featured.icon className="h-5 w-5 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{educationPrograms.featured.name}</h3>
            </div>
            <span className="flex items-center gap-1 text-sm text-amber-700 bg-amber-100 px-2 py-1 rounded">
              {educationPrograms.featured.badge}
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-6">{educationPrograms.featured.description}</p>
          <button className="w-full rounded-lg border border-gray-300 bg-white py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
            {educationPrograms.featured.cta}
          </button>
        </div>
      </div>

      <div className="mt-8 text-center">
        <button className="rounded-lg bg-amber-700 px-8 py-3 text-sm font-medium text-white hover:bg-amber-800 transition-colors">
          Download Prospectus
        </button>
      </div>
    </div>
  );
}

function LabsTab() {
  return (
    <div>
      <div className="text-center mb-12">
        <h2 className="text-2xl font-bold text-gray-900">{labsPrograms.title}</h2>
        <p className="mt-4 text-gray-600 max-w-2xl mx-auto">{labsPrograms.description}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 max-w-5xl mx-auto">
        {labsPrograms.labs.map((lab) => (
          <div
            key={lab.name}
            className="rounded-xl border border-gray-200 bg-white p-6 hover:border-amber-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-amber-50 rounded-lg">
                <lab.icon className="h-5 w-5 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{lab.name}</h3>
            </div>
            <p className="text-sm text-gray-600 mb-6">{lab.description}</p>
            <button className="w-full rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
              {lab.cta}
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <button className="rounded-lg bg-amber-700 px-8 py-3 text-sm font-medium text-white hover:bg-amber-800 transition-colors">
          Submit a Use Case
        </button>
      </div>
    </div>
  );
}

function ComplianceTab() {
  return (
    <div>
      <div className="text-center mb-12">
        <h2 className="text-2xl font-bold text-gray-900">{compliancePrograms.title}</h2>
        <p className="mt-4 text-gray-600 max-w-2xl mx-auto">{compliancePrograms.description}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 max-w-5xl mx-auto">
        {compliancePrograms.programs.map((program) => (
          <div
            key={program.name}
            className="rounded-xl border border-gray-200 bg-white p-6 hover:border-amber-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-amber-50 rounded-lg">
                <program.icon className="h-5 w-5 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{program.name}</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">{program.description}</p>

            {program.badges && (
              <div className="flex gap-2 mb-6">
                {program.badges.map((badge) => (
                  <span
                    key={badge}
                    className="text-xs px-2 py-1 rounded border border-amber-200 text-amber-700 bg-amber-50"
                  >
                    {badge}
                  </span>
                ))}
              </div>
            )}

            <button className="w-full rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors mt-auto">
              {program.cta}
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <button className="rounded-lg bg-amber-700 px-8 py-3 text-sm font-medium text-white hover:bg-amber-800 transition-colors">
          Apply for AI Trust Seal
        </button>
      </div>
    </div>
  );
}
