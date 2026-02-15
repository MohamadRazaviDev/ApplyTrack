'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const res = await api.get('/profile');
      return res.data;
    },
    enabled: !!user,
    refetchOnWindowFocus: false,
  });

  const updateProfileMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.put('/profile', data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      alert('Profile updated!');
    },
  });

  const [formData, setFormData] = useState({
    headline: '',
    summary: '',
    skills_csv: '',
    projects_json: '[]',
  });

  useEffect(() => {
    if (profile) {
      setFormData({
        headline: profile.headline || '',
        summary: profile.summary || '',
        skills_csv: (profile.skills_json || []).join(', '),
        projects_json: JSON.stringify(profile.projects_json || [], null, 2),
      });
    }
  }, [profile]);

  if (authLoading || isLoading) return <div>Loading...</div>;
  if (!user) {
    router.push('/login');
    return null;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const skills = formData.skills_csv.split(',').map(s => s.trim()).filter(Boolean);
      const projects = JSON.parse(formData.projects_json);
      
      updateProfileMutation.mutate({
        headline: formData.headline,
        summary: formData.summary,
        skills_json: skills,
        projects_json: projects,
      });
    } catch (err) {
      alert('Invalid JSON in projects');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded shadow">
      <h1 className="text-2xl font-bold mb-6">My Profile</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium">Headline</label>
          <input
            type="text"
            className="mt-1 block w-full border rounded p-2"
            value={formData.headline}
            onChange={e => setFormData({ ...formData, headline: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Summary</label>
          <textarea
            className="mt-1 block w-full border rounded p-2"
            rows={3}
            value={formData.summary}
            onChange={e => setFormData({ ...formData, summary: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Skills (comma separated)</label>
          <input
            type="text"
            className="mt-1 block w-full border rounded p-2"
            value={formData.skills_csv}
            onChange={e => setFormData({ ...formData, skills_csv: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Projects (JSON)</label>
          <p className="text-xs text-gray-500 mb-1">
            Example: {`[{"name": "Project A", "stack": "Python", "bullets": ["Built X"]}]`}
          </p>
          <textarea
            className="mt-1 block w-full border rounded p-2 font-mono text-sm"
            rows={10}
            value={formData.projects_json}
            onChange={e => setFormData({ ...formData, projects_json: e.target.value })}
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          disabled={updateProfileMutation.isPending}
        >
          {updateProfileMutation.isPending ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
}
