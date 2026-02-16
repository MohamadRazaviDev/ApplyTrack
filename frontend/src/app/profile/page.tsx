'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Save, CheckCircle } from 'lucide-react';

export default function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => (await api.get('/profile')).data,
    enabled: !!user,
  });

  const updateMutation = useMutation({
    mutationFn: async (data: Record<string, unknown>) => (await api.put('/profile', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    headline: '',
    summary: '',
    skills_csv: '',
    experience_json: '[]',
    projects_json: '[]',
  });

  useEffect(() => {
    if (profile) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setForm({
        headline: profile.headline || '',
        summary: profile.summary || '',
        skills_csv: (profile.skills_json || []).join(', '),
        experience_json: JSON.stringify(profile.experience_json || [], null, 2),
        projects_json: JSON.stringify(profile.projects_json || [], null, 2),
      });
    }
  }, [profile]);

  if (authLoading || isLoading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10">
        <div className="skeleton h-8 w-48 mb-6" />
        {[1, 2, 3].map((i) => <div key={i} className="skeleton h-20 mb-4 rounded-xl" />)}
      </div>
    );
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const skills = form.skills_csv
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
      const projects = JSON.parse(form.projects_json);
      const experience = JSON.parse(form.experience_json);

      updateMutation.mutate({
        headline: form.headline,
        summary: form.summary,
        skills_json: skills,
        projects_json: projects,
        experience_json: experience,
      });
    } catch {
      alert('Invalid JSON in projects or experience field.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight mb-6">My Profile</h1>
      <div className="bg-white rounded-xl border border-[var(--border)] p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* headline */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Headline</label>
            <input
              type="text"
              className="w-full rounded-lg border border-[var(--border)] px-3 py-2.5 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none transition"
              value={form.headline}
              onChange={(e) => setForm({ ...form, headline: e.target.value })}
              placeholder="e.g. Full-Stack Developer"
            />
          </div>

          {/* summary */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Summary</label>
            <textarea
              className="w-full rounded-lg border border-[var(--border)] px-3 py-2.5 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none transition"
              rows={3}
              value={form.summary}
              onChange={(e) => setForm({ ...form, summary: e.target.value })}
              placeholder="A short paragraph about your background and interests"
            />
          </div>

          {/* skills */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Skills (comma separated)</label>
            <input
              type="text"
              className="w-full rounded-lg border border-[var(--border)] px-3 py-2.5 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none transition"
              value={form.skills_csv}
              onChange={(e) => setForm({ ...form, skills_csv: e.target.value })}
              placeholder="Python, TypeScript, React, PostgreSQL"
            />
          </div>

          {/* experience */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Experience (JSON)</label>
            <p className="text-xs text-[var(--fg-muted)] mb-1">
              {`[{"company": "Acme", "role": "Engineer", "start_date": "2023-01", "bullets": [...]}]`}
            </p>
            <textarea
              className="w-full rounded-lg border border-[var(--border)] px-3 py-2.5 text-sm font-mono focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none transition"
              rows={6}
              value={form.experience_json}
              onChange={(e) => setForm({ ...form, experience_json: e.target.value })}
            />
          </div>

          {/* projects */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Projects (JSON)</label>
            <p className="text-xs text-[var(--fg-muted)] mb-1">
              {`[{"name": "My App", "stack": "React, Node", "bullets": ["Built X"]}]`}
            </p>
            <textarea
              className="w-full rounded-lg border border-[var(--border)] px-3 py-2.5 text-sm font-mono focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none transition"
              rows={8}
              value={form.projects_json}
              onChange={(e) => setForm({ ...form, projects_json: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-white hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-60"
          >
            {saved ? (
              <>
                <CheckCircle size={16} /> Saved!
              </>
            ) : (
              <>
                <Save size={16} /> {updateMutation.isPending ? 'Saving…' : 'Save Profile'}
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
