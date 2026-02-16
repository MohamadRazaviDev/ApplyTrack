'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Application, Reminder, STATUS_META, ApplicationStatus } from '@/lib/types';
import Link from 'next/link';
import { Briefcase, CheckCircle, MessageSquare, Trophy, Clock, ArrowRight } from 'lucide-react';

const STAT_CARDS: {
  key: string;
  label: string;
  icon: typeof Briefcase;
  color: string;
  filter: (a: Application) => boolean;
}[] = [
    { key: 'total', label: 'Total', icon: Briefcase, color: 'border-indigo-400', filter: () => true },
    { key: 'applied', label: 'Applied', icon: CheckCircle, color: 'border-blue-400', filter: (a) => a.status === 'applied' },
    { key: 'interview', label: 'Interviewing', icon: MessageSquare, color: 'border-violet-400', filter: (a) => a.status === 'interview' },
    { key: 'offer', label: 'Offers', icon: Trophy, color: 'border-emerald-400', filter: (a) => a.status === 'offer' },
  ];

export default function Dashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const { data: applications = [] } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: async () => (await api.get('/applications')).data,
    enabled: !!user,
  });

  const { data: reminders = [] } = useQuery<Reminder[]>({
    queryKey: ['reminders', 'pending'],
    queryFn: async () => (await api.get('/reminders', { params: { done: false } })).data,
    enabled: !!user,
  });

  useEffect(() => {
    if (!loading && !user) router.push('/login');
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="skeleton h-8 w-64 mb-8" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton h-24 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* greeting */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">
          Welcome back{user.email ? `, ${user.email.split('@')[0]}` : ''}
        </h1>
        <p className="text-sm text-[var(--fg-muted)] mt-1">
          Here&apos;s your application overview.
        </p>
      </div>

      {/* stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {STAT_CARDS.map(({ key, label, icon: Icon, color, filter }) => {
          const count = applications.filter(filter).length;
          return (
            <div
              key={key}
              className={`bg-white rounded-xl border border-[var(--border)] ${color} border-l-4 p-5 transition hover:shadow-md`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase text-[var(--fg-muted)]">{label}</span>
                <Icon size={16} className="text-[var(--fg-muted)]" />
              </div>
              <div className="text-3xl font-bold">{count}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* recent activity */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-[var(--border)] p-5">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-base font-semibold">Recent Applications</h2>
            <Link
              href="/applications"
              className="text-xs text-[var(--accent)] font-medium hover:underline flex items-center gap-1"
            >
              View Board <ArrowRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {applications.slice(0, 6).map((app) => {
              const sm = STATUS_META[app.status as ApplicationStatus];
              return (
                <Link
                  key={app.id}
                  href={`/applications/${app.id}`}
                  className="flex items-center justify-between py-3 hover:bg-slate-50 rounded -mx-2 px-2 transition-colors"
                >
                  <div>
                    <div className="font-medium text-sm">{app.job_posting?.title}</div>
                    <div className="text-xs text-[var(--fg-muted)]">
                      {app.job_posting?.company?.name}
                    </div>
                  </div>
                  <span className={`badge ${sm?.color || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                    {sm?.label || app.status}
                  </span>
                </Link>
              );
            })}
            {applications.length === 0 && (
              <div className="text-center py-8 text-sm text-[var(--fg-muted)]">
                No applications yet.{' '}
                <Link href="/applications" className="text-[var(--accent)] hover:underline">
                  Create one
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* reminders */}
        <div className="bg-white rounded-xl border border-[var(--border)] p-5">
          <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
            <Clock size={16} className="text-[var(--accent)]" /> Upcoming Reminders
          </h2>
          <div className="space-y-3">
            {reminders.slice(0, 5).map((r) => (
              <div key={r.id} className="flex items-start gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0" />
                <div>
                  <div className="font-medium">{r.text}</div>
                  <div className="text-xs text-[var(--fg-muted)]">
                    {new Date(r.due_at).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>
              </div>
            ))}
            {reminders.length === 0 && (
              <p className="text-sm text-[var(--fg-muted)] italic">No pending reminders.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
