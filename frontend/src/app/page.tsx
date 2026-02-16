'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Kanban, Brain, Bell, Briefcase, ArrowRight } from 'lucide-react';

const FEATURES = [
  {
    icon: Kanban,
    title: 'Kanban Board',
    description: 'Drag-and-drop your applications through every stage from first contact to offer.',
  },
  {
    icon: Brain,
    title: 'AI-Powered Insights',
    description: 'Parse JDs, match your profile, tailor CVs, draft outreach, and prep for interviews.',
  },
  {
    icon: Bell,
    title: 'Smart Reminders',
    description: 'Never miss a follow-up or interview. Set reminders tied to each application.',
  },
  {
    icon: Briefcase,
    title: 'Career Dashboard',
    description: 'Track stats, see recent activity, and stay on top of your entire job search.',
  },
] as const;

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="max-w-5xl mx-auto px-4 py-16">
      {/* hero */}
      <div className="text-center mb-20">
        <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
          Open Source Job Tracker
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight mb-4">
          Track your applications,
          <br />
          <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
            land your dream job
          </span>
        </h1>
        <p className="text-lg text-[var(--fg-muted)] max-w-xl mx-auto mb-8">
          ApplyTrack helps you organize every application with a Kanban board,
          AI-powered resume tailoring, and smart reminders — all in one place.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link
            href={user ? '/dashboard' : '/register'}
            className="inline-flex items-center gap-2 rounded-xl bg-[var(--accent)] px-6 py-3 font-medium text-white shadow-lg shadow-indigo-200 hover:bg-[var(--accent-hover)] transition-all"
          >
            Get Started <ArrowRight size={18} />
          </Link>
          {!user && (
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] px-6 py-3 font-medium text-[var(--fg)] hover:bg-slate-50 transition-colors"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>

      {/* features grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {FEATURES.map(({ icon: Icon, title, description }) => (
          <div
            key={title}
            className="group p-6 rounded-2xl border border-[var(--border)] bg-white hover:shadow-lg hover:border-indigo-200 transition-all"
          >
            <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors">
              <Icon size={20} className="text-indigo-600" />
            </div>
            <h3 className="font-semibold text-lg mb-1">{title}</h3>
            <p className="text-sm text-[var(--fg-muted)] leading-relaxed">{description}</p>
          </div>
        ))}
      </div>

      {/* footer tagline */}
      <div className="text-center mt-20 text-sm text-[var(--fg-muted)]">
        Built with ❤️ — Open Source on{' '}
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--accent)] hover:underline"
        >
          GitHub
        </a>
      </div>
    </div>
  );
}
