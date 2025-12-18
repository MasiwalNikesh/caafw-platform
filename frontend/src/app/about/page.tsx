import { Target, Heart, Users, Globe, Lightbulb, GraduationCap, Shield } from 'lucide-react';

const coreValues = [
  {
    name: 'Accessibility',
    description: 'Making AI education and resources available to all organizations, regardless of size or budget.',
    icon: Target,
  },
  {
    name: 'Responsibility',
    description: 'Promoting ethical AI practices and ensuring compliance with evolving regulations.',
    icon: Heart,
  },
  {
    name: 'Inclusion',
    description: 'Building a diverse community where all voices are heard and valued.',
    icon: Users,
  },
  {
    name: 'Collaboration',
    description: 'Knowledge sharing and collective learning drive innovation forward.',
    icon: Globe,
  },
];

const whatWeStandFor = [
  {
    name: 'Empowerment',
    description: 'Helping businesses adopt AI with confidence',
    icon: Lightbulb,
  },
  {
    name: 'Education',
    description: 'Building AI literacy across all organizational levels',
    icon: GraduationCap,
  },
  {
    name: 'Ethics',
    description: 'Ensuring AI adoption follows responsible principles',
    icon: Shield,
  },
];

export default function AboutPage() {
  return (
    <div className="bg-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-amber-50 to-white">
        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
              About the Initiative
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              A catalyst platform transforming how Small and Medium Businesses adopt AI—responsibly, practically, and sustainably.
            </p>
          </div>
        </div>
      </div>

      {/* Mission Section */}
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">Our Mission</h2>
            <div className="mt-6 space-y-4 text-gray-600">
              <p>
                We exist to bridge the gap between AI innovation and practical business implementation. The rapid advancement of AI has created unprecedented opportunities—and challenges—for small and medium enterprises.
              </p>
              <p>
                Many organizations lack the resources, expertise, or guidance to navigate this transformation effectively. We provide a trusted platform that democratizes access to AI knowledge, tools, and best practices.
              </p>
            </div>
          </div>
          <div className="bg-amber-50 rounded-2xl p-8">
            <h3 className="text-xl font-semibold text-amber-800 mb-6">What We Stand For</h3>
            <ul className="space-y-4">
              {whatWeStandFor.map((item) => (
                <li key={item.name} className="flex items-start gap-3">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <div>
                    <span className="font-semibold text-amber-800">{item.name}:</span>{' '}
                    <span className="text-gray-700">{item.description}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Core Values Section */}
      <div className="bg-gray-50 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">Our Core Values</h2>
            <p className="mt-4 text-gray-600">The principles that guide everything we do</p>
          </div>
          <div className="mx-auto mt-12 grid max-w-5xl gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {coreValues.map((value) => (
              <div
                key={value.name}
                className="flex flex-col items-center text-center bg-white rounded-xl p-6 shadow-sm border border-gray-100"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-amber-700">
                  <value.icon className="h-6 w-6" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-gray-900">{value.name}</h3>
                <p className="mt-2 text-sm text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Delivery Model Section */}
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">Our Delivery Model</h2>
          <div className="mt-8 bg-gray-50 rounded-2xl p-8 text-left">
            <p className="text-gray-600 mb-4">
              We operate as a <span className="font-semibold text-amber-700">community initiative</span>, focusing on UK and EU organizations with global collaborators. Our programs are delivered through partnerships with universities, local councils, accelerators, and industry experts.
            </p>
            <p className="text-gray-600">
              We host workshops, labs, and events in collaboration with our partners, ensuring accessibility and relevance to regional ecosystems. No profit motive— just impact, learning, and responsible innovation.
            </p>
          </div>
        </div>
      </div>

      {/* Team Section */}
      <div className="bg-gray-50 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">Our Team & Advisory</h2>
            <p className="mt-4 text-gray-600">
              Led by experienced practitioners, researchers, and industry experts committed to democratizing AI adoption.
            </p>
            <div className="mt-8 bg-white rounded-xl p-8 border border-gray-200">
              <p className="text-gray-500">Team profiles and advisory board information coming soon.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
