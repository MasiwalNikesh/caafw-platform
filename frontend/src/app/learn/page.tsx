import Link from 'next/link';
import {
  Brain,
  Shield,
  Heart,
  Users,
  Lightbulb,
  HeartHandshake,
  Sparkles,
  ArrowRight,
} from 'lucide-react';

const pillars = [
  {
    name: 'Critical Thinking',
    description: 'Beyond rote learning and memorization',
    icon: Brain,
  },
  {
    name: 'Digital Safety',
    description: 'Navigate the digital world safely',
    icon: Shield,
  },
  {
    name: 'Ethics First',
    description: 'Responsible and thoughtful AI use',
    icon: Heart,
  },
  {
    name: 'Human Judgment',
    description: 'AI assists, humans decide',
    icon: Users,
  },
];

const approaches = [
  {
    name: 'Understanding, Not Just Using',
    description:
      'We help children understand how AI works at a conceptual level—its strengths, limitations, and the human decisions behind every algorithm.',
    icon: Lightbulb,
  },
  {
    name: 'Ethics, Safety, and Responsibility',
    description:
      'From deepfakes to misinformation, children need to navigate a complex digital landscape. We equip them with the awareness to do so safely.',
    icon: HeartHandshake,
  },
  {
    name: 'Human-Centered Approach',
    description:
      'AI should enhance human potential, not replace human thinking. Our programs emphasize creativity, empathy, and judgment—skills AI cannot replicate.',
    icon: Users,
  },
];

export default function LearnPage() {
  return (
    <div className="bg-white dark:bg-gray-900">
      {/* Breadcrumb */}
      <div className="mx-auto max-w-7xl px-6 pt-24 sm:pt-28 lg:px-8">
        <nav className="text-sm text-gray-500">
          <Link href="/" className="hover:text-gray-700">
            Home
          </Link>
          <span className="mx-2">→</span>
          <span className="text-gray-900">LEARN</span>
        </nav>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-amber-50/50 to-white">
        <div className="mx-auto max-w-7xl px-6 py-20 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full bg-white border border-gray-200 px-4 py-2 text-sm text-gray-600 mb-6">
              <Sparkles className="h-4 w-4 text-amber-600" />
              CAAFW Learning Initiative
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              Learning for an AI-Driven Future
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Helping young people grow up informed, responsible, and future-ready.
            </p>
          </div>
        </div>
      </div>

      {/* Why AI Literacy Matters */}
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">
              Why AI Literacy Matters Today
            </h2>
            <div className="mt-6 space-y-4 text-gray-600">
              <p>
                Artificial intelligence is reshaping how we work, learn, and interact with the
                world. Today's children will grow up in a world where AI is woven into everyday
                life—from how they search for information to how they will work and create.
              </p>
              <p>
                Yet most education systems haven't caught up. Children are using AI tools without
                understanding their implications, limitations, or ethical dimensions. At CAAFW, we
                believe AI literacy isn't just about technology—it's about preparing young minds to
                think critically, act responsibly, and lead with integrity.
              </p>
            </div>
            <Link
              href="/about"
              className="inline-flex items-center gap-2 mt-6 text-amber-700 hover:text-amber-800 font-medium"
            >
              <Heart className="h-4 w-4" />
              Education is central to our mission
            </Link>
          </div>

          {/* Pillars Grid */}
          <div className="grid grid-cols-2 gap-4">
            {pillars.map((pillar) => (
              <div
                key={pillar.name}
                className="flex flex-col items-center text-center bg-white rounded-xl border border-gray-200 p-6 hover:border-amber-300 hover:shadow-sm transition-all"
              >
                <pillar.icon className="h-8 w-8 text-gray-700 mb-3" />
                <h3 className="font-semibold text-gray-900">{pillar.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{pillar.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Video */}
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold tracking-tight text-gray-900 text-center mb-8">
            Watch & Learn
          </h2>
          <div className="aspect-video rounded-xl overflow-hidden shadow-lg border border-gray-200">
            <iframe
              src="https://drive.google.com/file/d/1MQ4Pevf_KfcQglR_tv0bocsNhVnwmz0OI9u5n5cpYJQ/preview"
              width="100%"
              height="100%"
              allow="autoplay; encrypted-media"
              allowFullScreen
              className="w-full h-full"
            ></iframe>
          </div>
        </div>
      </div>

      {/* Learning Beyond Coding */}
      <div className="bg-gray-50 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">
              Learning Beyond Coding and Tools
            </h2>
            <p className="mt-4 text-gray-600">
              True AI literacy isn't about learning to code or mastering the latest tools. It's
              about developing the wisdom to use AI thoughtfully and the judgment to know when not
              to.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
            {approaches.map((approach) => (
              <div
                key={approach.name}
                className="bg-white rounded-xl border border-gray-200 p-6 hover:border-amber-300 hover:shadow-md transition-all"
              >
                <div className="p-2 bg-gray-100 rounded-lg w-fit mb-4">
                  <approach.icon className="h-5 w-5 text-gray-700" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{approach.name}</h3>
                <p className="text-sm text-gray-600">{approach.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Aligned with Mission */}
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            Aligned with CAAFW's Mission
          </h2>
          <p className="mt-6 text-gray-600">
            The Centre for Applied AI and Future of Work (CAAFW) was founded with a vision: to help
            individuals, businesses, and communities thrive in an AI-driven world. Our education
            initiatives extend this mission to the next generation—ensuring that children grow up
            not just as consumers of AI, but as thoughtful, responsible citizens who can shape the
            future of technology.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/programs"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-amber-700 px-6 py-3 text-sm font-medium text-white hover:bg-amber-800 transition-colors"
            >
              Explore Future Minds Program
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/about"
              className="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Partner with CAAFW
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
