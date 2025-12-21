import { Target, Heart, Users, Globe, Lightbulb, GraduationCap, Shield, Info, Sparkles, Building } from 'lucide-react';

const coreValues = [
  {
    name: 'Accessibility',
    description: 'Making AI education and resources available to all organizations, regardless of size or budget.',
    icon: Target,
    color: 'from-blue-500 to-indigo-500',
  },
  {
    name: 'Responsibility',
    description: 'Promoting ethical AI practices and ensuring compliance with evolving regulations.',
    icon: Heart,
    color: 'from-rose-500 to-pink-500',
  },
  {
    name: 'Inclusion',
    description: 'Building a diverse community where all voices are heard and valued.',
    icon: Users,
    color: 'from-amber-500 to-orange-500',
  },
  {
    name: 'Collaboration',
    description: 'Knowledge sharing and collective learning drive innovation forward.',
    icon: Globe,
    color: 'from-emerald-500 to-teal-500',
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
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-amber-500 via-orange-500 to-amber-600 pt-24 sm:pt-28 pb-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 -left-20 h-60 w-60 rounded-full bg-orange-400/20 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-white/10 backdrop-blur-sm">
              <Info className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
              About the Initiative
            </h1>
          </div>
          <p className="text-lg text-amber-100 max-w-2xl">
            A catalyst platform transforming how Small and Medium Businesses adopt AI—responsibly, practically, and sustainably.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Community Initiative
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              UK & EU Focus
            </span>
            <span className="px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium backdrop-blur-sm">
              Non-Profit
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 -mt-8">
        {/* Mission Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50">
                  <Sparkles className="h-6 w-6 text-amber-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Our Mission</h2>
              </div>
              <div className="space-y-4 text-gray-600">
                <p>
                  We exist to bridge the gap between AI innovation and practical business implementation. The rapid advancement of AI has created unprecedented opportunities—and challenges—for small and medium enterprises.
                </p>
                <p>
                  Many organizations lack the resources, expertise, or guidance to navigate this transformation effectively. We provide a trusted platform that democratizes access to AI knowledge, tools, and best practices.
                </p>
              </div>
            </div>
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-8 border border-amber-100">
              <h3 className="text-xl font-semibold text-amber-800 mb-6 flex items-center gap-2">
                <Target className="h-5 w-5" />
                What We Stand For
              </h3>
              <ul className="space-y-4">
                {whatWeStandFor.map((item) => (
                  <li key={item.name} className="flex items-start gap-4 p-3 bg-white/60 rounded-xl">
                    <div className="p-2 bg-amber-100 rounded-lg flex-shrink-0">
                      <item.icon className="h-4 w-4 text-amber-700" />
                    </div>
                    <div>
                      <span className="font-semibold text-gray-900">{item.name}</span>
                      <p className="text-sm text-gray-600 mt-0.5">{item.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Core Values Section */}
        <div className="mb-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Our Core Values</h2>
            <p className="mt-2 text-gray-600">The principles that guide everything we do</p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {coreValues.map((value) => (
              <div
                key={value.name}
                className="group bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-xl transition-all hover:-translate-y-1"
              >
                <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-br ${value.color} mb-4`}>
                  <value.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{value.name}</h3>
                <p className="text-sm text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Delivery Model Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8">
          <div className="max-w-3xl mx-auto text-center">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="p-2 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50">
                <Building className="h-6 w-6 text-amber-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Our Delivery Model</h2>
            </div>
            <div className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-2xl p-8 text-left">
              <p className="text-gray-600 mb-4">
                We operate as a <span className="font-semibold text-amber-700">community initiative</span>, focusing on UK and EU organizations with global collaborators. Our programs are delivered through partnerships with universities, local councils, accelerators, and industry experts.
              </p>
              <p className="text-gray-600">
                We host workshops, labs, and events in collaboration with our partners, ensuring accessibility and relevance to regional ecosystems. No profit motive—just impact, learning, and responsible innovation.
              </p>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-2xl p-8">
          <div className="max-w-3xl mx-auto text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-2 rounded-xl bg-white">
                <Users className="h-6 w-6 text-amber-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Our Team & Advisory</h2>
            </div>
            <p className="text-gray-600 mb-6">
              Led by experienced practitioners, researchers, and industry experts committed to democratizing AI adoption.
            </p>
            <div className="bg-white rounded-xl p-8 border border-gray-200">
              <p className="text-gray-500">Team profiles and advisory board information coming soon.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
