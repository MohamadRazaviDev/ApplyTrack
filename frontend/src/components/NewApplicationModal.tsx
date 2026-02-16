'use client';

import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useState } from 'react';
import { api } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { X } from 'lucide-react';

export default function NewApplicationModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [formData, setFormData] = useState({
    company_name: '',
    role_title: '',
    job_url: '',
    job_description: '',
    notes: '',
  });

  const queryClient = useQueryClient();
  const router = useRouter();

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      // flat creation — backend auto-creates company + job posting
      const res = await api.post('/applications', {
        company_name: data.company_name,
        role_title: data.role_title,
        job_url: data.job_url || undefined,
        job_description: data.job_description || undefined,
        notes: data.notes,
      });
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      onClose();
      setFormData({ company_name: '', role_title: '', job_url: '', job_description: '', notes: '' });
      router.push(`/applications/${data.id}?new=true`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
                <div className="flex items-center justify-between mb-5">
                  <Dialog.Title className="text-lg font-semibold">New Application</Dialog.Title>
                  <button onClick={onClose} className="text-[var(--fg-muted)] hover:text-[var(--fg)]">
                    <X size={18} />
                  </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Company Name *</label>
                    <input
                      type="text"
                      required
                      className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none"
                      value={formData.company_name}
                      onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                      placeholder="Acme Corp"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Role Title *</label>
                    <input
                      type="text"
                      required
                      className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none"
                      value={formData.role_title}
                      onChange={(e) => setFormData({ ...formData, role_title: e.target.value })}
                      placeholder="Backend Engineer"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Job URL</label>
                    <input
                      type="url"
                      className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none"
                      value={formData.job_url}
                      onChange={(e) => setFormData({ ...formData, job_url: e.target.value })}
                      placeholder="https://linkedin.com/jobs/..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Job Description</label>
                    <textarea
                      rows={4}
                      className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none"
                      value={formData.job_description}
                      onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
                      placeholder="Paste the full job description here…"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Notes</label>
                    <textarea
                      rows={2}
                      className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none"
                      value={formData.notes}
                      onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                      placeholder="Referral? Deadline? Any personal notes…"
                    />
                  </div>

                  {createMutation.isError && (
                    <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                      Failed to create application.
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="w-full rounded-lg bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-white hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-60"
                  >
                    {createMutation.isPending ? 'Creating…' : 'Create Application'}
                  </button>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
