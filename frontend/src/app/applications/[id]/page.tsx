'use client';

import { Application, AIOutput, Reminder, STATUS_META, ApplicationStatus } from '@/lib/types';
import { api, pollTaskUntilDone } from '@/lib/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import Link from 'next/link';
import { AIOutputDisplay } from '@/components/AIOutputDisplay';
import {
  ArrowLeft,
  ExternalLink,
  FileText,
  Target,
  PenTool,
  Mail,
  GraduationCap,
  Loader2,
  Clock,
  Plus,
  CheckCircle,
  Save,
} from 'lucide-react';

const AI_ACTIONS = [
  { kind: 'parse-jd', label: 'Parse JD', icon: FileText, description: 'Extract skills, requirements, and keywords' },
  { kind: 'match', label: 'Match', icon: Target, description: 'Score your profile fit against the JD' },
  { kind: 'tailor-cv', label: 'Tailor CV', icon: PenTool, description: 'Generate tailored bullet points' },
  { kind: 'outreach', label: 'Outreach', icon: Mail, description: 'Draft LinkedIn and email messages' },
  { kind: 'interview-prep', label: 'Interview Prep', icon: GraduationCap, description: 'Questions, checklist, stories' },
] as const;

type TabKey = 'overview' | 'notes' | 'ai' | 'reminders';

export default function ApplicationDetailPage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const isNew = searchParams.get('new') === 'true';
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<TabKey>(isNew ? 'ai' : 'overview');
  const [runningKind, setRunningKind] = useState<string | null>(null);
  const [notesValue, setNotesValue] = useState<string | null>(null);
  const [notesSaved, setNotesSaved] = useState(false);

  // reminder form
  const [showReminderForm, setShowReminderForm] = useState(false);
  const [reminderText, setReminderText] = useState('');
  const [reminderDue, setReminderDue] = useState('');

  // — queries —
  const { data: application, isLoading } = useQuery<Application>({
    queryKey: ['application', id],
    queryFn: async () => (await api.get(`/applications/${id}`)).data,
    enabled: !!id,
  });

  const { data: aiOutputs = [], refetch: refetchAI } = useQuery<AIOutput[]>({
    queryKey: ['ai-outputs', id],
    queryFn: async () => (await api.get(`/applications/${id}/ai-outputs`)).data,
    enabled: !!id,
  });

  const { data: reminders = [], refetch: refetchReminders } = useQuery<Reminder[]>({
    queryKey: ['reminders', id],
    queryFn: async () => {
      const all: Reminder[] = (await api.get('/reminders')).data;
      return all.filter((r) => r.application_id === id);
    },
    enabled: !!id,
  });

  // — mutations —
  const saveNotesMutation = useMutation({
    mutationFn: async (notes: string) => {
      await api.patch(`/applications/${id}`, { notes });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      setNotesSaved(true);
      setTimeout(() => setNotesSaved(false), 2000);
    },
  });

  const createReminderMutation = useMutation({
    mutationFn: async (body: { text: string; due_at: string }) => {
      await api.post(`/applications/${id}/reminders`, body);
    },
    onSuccess: () => {
      refetchReminders();
      setShowReminderForm(false);
      setReminderText('');
      setReminderDue('');
    },
  });

  const toggleReminderMutation = useMutation({
    mutationFn: async ({ rid, done }: { rid: string; done: boolean }) => {
      await api.patch(`/reminders/${rid}`, { done });
    },
    onSuccess: () => refetchReminders(),
  });

  // — AI runner —
  const handleRunAI = async (kind: string) => {
    setRunningKind(kind);
    try {
      const res = await api.post(`/ai/${kind}/${id}`);
      const taskId = res.data.task_id;
      await pollTaskUntilDone(taskId);
      refetchAI();
    } catch (e) {
      console.error(e);
    } finally {
      setRunningKind(null);
    }
  };

  // — loading / not found —
  if (isLoading || !application) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-10">
        <div className="skeleton h-8 w-64 mb-4" />
        <div className="skeleton h-4 w-48 mb-8" />
        <div className="skeleton h-96 rounded-xl" />
      </div>
    );
  }

  const job = application.job_posting;
  const sm = STATUS_META[application.status as ApplicationStatus];
  const currentNotes = notesValue ?? application.notes;

  const TABS: { key: TabKey; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'notes', label: 'Notes' },
    { key: 'ai', label: 'AI Outputs' },
    { key: 'reminders', label: `Reminders (${reminders.length})` },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* header */}
      <div className="flex items-start justify-between mb-6 pb-4 border-b border-[var(--border)]">
        <div>
          <Link
            href="/applications"
            className="text-xs text-[var(--fg-muted)] hover:text-[var(--accent)] flex items-center gap-1 mb-2"
          >
            <ArrowLeft size={12} /> Back to Board
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">{job?.title}</h1>
          <p className="text-[var(--fg-muted)]">{job?.company?.name}</p>
          <div className="flex items-center gap-2 mt-2">
            {job?.location && <span className="text-xs text-[var(--fg-muted)]">{job.location}</span>}
            {job?.remote_type && (
              <span className="badge bg-blue-50 text-blue-600 border-blue-100">{job.remote_type}</span>
            )}
            <span className={`badge ${sm?.color || ''}`}>{sm?.label || application.status}</span>
          </div>
        </div>
        {job?.posting_url && (
          <a
            href={job.posting_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-sm hover:bg-slate-50 transition-colors"
          >
            View Posting <ExternalLink size={14} />
          </a>
        )}
      </div>

      {/* new application prompt */}
      {isNew && (
        <div className="bg-indigo-50 border border-indigo-200 p-4 rounded-xl mb-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-indigo-900">Application created!</h3>
            <p className="text-sm text-indigo-700">Run AI Parse to extract skills and requirements from the JD.</p>
          </div>
          <button
            onClick={() => handleRunAI('parse-jd')}
            disabled={!!runningKind}
            className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--accent-hover)] disabled:opacity-60"
          >
            Run AI Parse
          </button>
        </div>
      )}

      {/* tabs */}
      <div className="border-b border-[var(--border)] mb-6">
        <nav className="-mb-px flex space-x-6">
          {TABS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`pb-3 text-sm font-medium transition-colors border-b-2 ${activeTab === key
                  ? 'border-[var(--accent)] text-[var(--accent)]'
                  : 'border-transparent text-[var(--fg-muted)] hover:text-[var(--fg)]'
                }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {/* OVERVIEW */}
          {activeTab === 'overview' && (
            <div>
              <h3 className="text-sm font-semibold mb-2">Job Description</h3>
              <div className="whitespace-pre-wrap text-sm text-[var(--fg-muted)] bg-slate-50 p-4 rounded-xl border border-[var(--border)] font-mono leading-relaxed max-h-[60vh] overflow-y-auto">
                {job?.description_raw || 'No description provided.'}
              </div>
            </div>
          )}

          {/* NOTES */}
          {activeTab === 'notes' && (
            <div className="space-y-4">
              <textarea
                className="w-full h-64 p-4 rounded-xl border border-[var(--border)] bg-amber-50/50 focus:ring-2 focus:ring-amber-200 focus:border-amber-300 outline-none text-sm transition"
                value={currentNotes}
                onChange={(e) => setNotesValue(e.target.value)}
                placeholder="Add your notes here…"
              />
              <button
                onClick={() => saveNotesMutation.mutate(currentNotes)}
                disabled={saveNotesMutation.isPending}
                className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--accent-hover)] disabled:opacity-60"
              >
                {notesSaved ? (
                  <>
                    <CheckCircle size={14} /> Saved!
                  </>
                ) : (
                  <>
                    <Save size={14} /> {saveNotesMutation.isPending ? 'Saving…' : 'Save Notes'}
                  </>
                )}
              </button>
            </div>
          )}

          {/* AI */}
          {activeTab === 'ai' && (
            <div className="space-y-6">
              {/* action buttons */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                {AI_ACTIONS.map(({ kind, label, icon: Icon }) => (
                  <button
                    key={kind}
                    onClick={() => handleRunAI(kind)}
                    disabled={!!runningKind}
                    className="flex flex-col items-center gap-1 rounded-xl border border-[var(--border)] p-3 text-xs font-medium hover:bg-indigo-50 hover:border-indigo-200 transition-colors disabled:opacity-50"
                  >
                    {runningKind === kind ? (
                      <Loader2 size={18} className="animate-spin text-[var(--accent)]" />
                    ) : (
                      <Icon size={18} className="text-[var(--accent)]" />
                    )}
                    {label}
                  </button>
                ))}
              </div>

              {runningKind && (
                <div className="flex items-center gap-2 text-sm text-[var(--accent)] font-medium">
                  <Loader2 size={16} className="animate-spin" /> Processing…
                </div>
              )}

              {/* outputs */}
              <div className="space-y-4">
                {aiOutputs.map((output) => (
                  <div key={output.id} className="border border-[var(--border)] rounded-xl p-4 bg-white">
                    <div className="flex justify-between items-center mb-3 pb-2 border-b border-[var(--border)]">
                      <span className="font-semibold text-xs uppercase text-[var(--fg-muted)] tracking-wide">
                        {output.kind.replace('_', ' ')}
                      </span>
                      <div className="flex items-center gap-2 text-[10px] text-[var(--fg-muted)]">
                        <span>{output.model}</span>
                        <span>•</span>
                        <span>{output.latency_seconds.toFixed(1)}s</span>
                        <span>•</span>
                        <span>{new Date(output.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <AIOutputDisplay output={output} />
                  </div>
                ))}
                {aiOutputs.length === 0 && !runningKind && (
                  <div className="text-center py-12 text-sm text-[var(--fg-muted)] bg-slate-50 rounded-xl border border-dashed border-[var(--border)]">
                    No AI outputs yet. Click a button above to get started.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* REMINDERS */}
          {activeTab === 'reminders' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-semibold">Reminders</h3>
                <button
                  onClick={() => setShowReminderForm(!showReminderForm)}
                  className="flex items-center gap-1 text-xs text-[var(--accent)] font-medium hover:underline"
                >
                  <Plus size={14} /> Add Reminder
                </button>
              </div>

              {showReminderForm && (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (reminderText && reminderDue) {
                      createReminderMutation.mutate({
                        text: reminderText,
                        due_at: new Date(reminderDue).toISOString(),
                      });
                    }
                  }}
                  className="flex flex-col sm:flex-row gap-2 bg-slate-50 p-3 rounded-xl border border-[var(--border)]"
                >
                  <input
                    type="text"
                    placeholder="Reminder text…"
                    className="flex-1 rounded-lg border border-[var(--border)] px-3 py-2 text-sm outline-none focus:border-[var(--accent)]"
                    value={reminderText}
                    onChange={(e) => setReminderText(e.target.value)}
                    required
                  />
                  <input
                    type="datetime-local"
                    className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm outline-none focus:border-[var(--accent)]"
                    value={reminderDue}
                    onChange={(e) => setReminderDue(e.target.value)}
                    required
                  />
                  <button
                    type="submit"
                    disabled={createReminderMutation.isPending}
                    className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--accent-hover)] disabled:opacity-60"
                  >
                    Add
                  </button>
                </form>
              )}

              <div className="space-y-2">
                {reminders.map((r) => (
                  <div
                    key={r.id}
                    className={`flex items-center gap-3 p-3 rounded-xl border border-[var(--border)] bg-white transition-opacity ${r.done ? 'opacity-50' : ''
                      }`}
                  >
                    <button
                      onClick={() => toggleReminderMutation.mutate({ rid: r.id, done: !r.done })}
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${r.done
                          ? 'bg-emerald-500 border-emerald-500'
                          : 'border-[var(--border)] hover:border-[var(--accent)]'
                        }`}
                    >
                      {r.done && <CheckCircle size={12} className="text-white" />}
                    </button>
                    <div className="flex-1">
                      <span className={`text-sm ${r.done ? 'line-through' : ''}`}>{r.text}</span>
                      <div className="text-xs text-[var(--fg-muted)] flex items-center gap-1 mt-0.5">
                        <Clock size={10} />
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
                  <p className="text-sm text-[var(--fg-muted)] italic text-center py-8">No reminders set.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-[var(--border)] p-5 sticky top-20">
            <h3 className="font-semibold mb-4">Details</h3>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-[var(--border)] pb-2">
                <dt className="text-[var(--fg-muted)]">Status</dt>
                <dd className={`badge ${sm?.color || ''}`}>{sm?.label || application.status}</dd>
              </div>
              <div className="flex justify-between border-b border-[var(--border)] pb-2">
                <dt className="text-[var(--fg-muted)]">Priority</dt>
                <dd className="capitalize font-medium">{application.priority}</dd>
              </div>
              <div className="flex justify-between border-b border-[var(--border)] pb-2">
                <dt className="text-[var(--fg-muted)]">Applied</dt>
                <dd>{application.applied_at ? new Date(application.applied_at).toLocaleDateString() : '—'}</dd>
              </div>
              <div className="flex justify-between border-b border-[var(--border)] pb-2">
                <dt className="text-[var(--fg-muted)]">Source</dt>
                <dd className="capitalize">{job?.source || '—'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[var(--fg-muted)]">Salary Exp.</dt>
                <dd>
                  {application.salary_expectation
                    ? `$${application.salary_expectation.toLocaleString()}`
                    : '—'}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
