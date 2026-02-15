'use client';

import { Application, AIOutput } from '@/lib/types';
import { api } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import Link from 'next/link';
import { AIOutputDisplay } from '@/components/AIOutputDisplay';

export default function ApplicationDetailPage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const isNew = searchParams.get('new') === 'true';
  
  const [activeTab, setActiveTab] = useState<'overview' | 'notes' | 'ai'>('overview');

  const { data: application, isLoading } = useQuery<Application>({
    queryKey: ['application', id],
    queryFn: async () => {
      const res = await api.get(`/applications/${id}`);
      return res.data;
    },
    enabled: !!id,
  });

  const { data: aiOutputs = [], refetch: refetchAI } = useQuery<AIOutput[]>({
    queryKey: ['ai-outputs', id],
    queryFn: async () => {
      const res = await api.get(`/applications/${id}/ai-outputs`);
      return res.data;
    },
    enabled: !!id,
  });
  
  const [parsing, setParsing] = useState(false);
  const handleRunAI = async (kind: 'parse-jd' | 'match' | 'tailor-cv') => {
    setParsing(true);
    try {
        if (kind === 'parse-jd') {
             await api.post(`/ai/applications/${id}/parse-jd`);
        } else if (kind === 'match') {
             await api.post(`/ai/applications/${id}/match`);
        } else if (kind === 'tailor-cv') {
             await api.post(`/ai/applications/${id}/tailor-cv`);
        }
        
        setTimeout(() => {
            refetchAI();
            setParsing(false);
        }, 2000);
    } catch (e) {
        console.error(e);
        setParsing(false);
    }
  };

  if (isLoading || !application) return <div className="p-8">Loading...</div>;

  const job = application.job_posting;

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white shadow rounded-lg mt-6 min-h-[80vh]">
      <div className="flex justify-between items-start mb-6 border-b pb-4">
        <div>
           <Link href="/applications" className="text-sm text-gray-500 hover:underline mb-2 block">← Back to Board</Link>
           <h1 className="text-3xl font-bold">{job?.title}</h1>
           <p className="text-lg text-gray-600">{job?.company?.name}</p>
           <div className="flex gap-2 mt-2 text-sm text-gray-500">
             <span>{job?.location}</span>
             {job?.remote_type && <span className="bg-gray-100 px-2 rounded">{job.remote_type}</span>}
             <span className="capitalize px-2 bg-blue-50 text-blue-700 rounded">{application.status}</span>
           </div>
        </div>
        <div className="flex gap-2">
            <a href={job?.posting_url} target="_blank" className="px-4 py-2 border rounded hover:bg-gray-50 text-sm">View Job Post ↗</a>
        </div>
      </div>

      {isNew && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded mb-6 flex justify-between items-center">
            <div>
                <h3 className="font-semibold text-blue-900">Application Created!</h3>
                <p className="text-sm text-blue-700">Would you like to parse the job description to get started?</p>
            </div>
            <button 
                onClick={() => {
                    setActiveTab('ai');
                    handleRunAI('parse-jd');
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
            >
                Run AI Parse
            </button>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b mb-6">
        <nav className="-mb-px flex space-x-8">
          {(['overview', 'notes', 'ai'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`
                whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
              {tab === 'ai' ? 'AI Outputs' : tab}
            </button>
          ))}
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
           {activeTab === 'overview' && (
             <div className="prose max-w-none">
                <h3 className="text-lg font-semibold mb-2">Job Description</h3>
                <div className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded border font-mono">
                    {job?.description_raw || "No description provided."}
                </div>
             </div>
           )}
           
           {activeTab === 'notes' && (
             <div className="space-y-4">
                 <textarea 
                    className="w-full h-64 p-4 border rounded bg-yellow-50 focus:ring-2 focus:ring-yellow-400 focus:border-transparent" 
                    defaultValue={application.notes}
                    placeholder="Add your notes here..."
                 ></textarea>
                 <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Save Notes</button>
             </div>
           )}
           
           {activeTab === 'ai' && (
             <div className="space-y-6">
                <div className="flex gap-4 mb-4">
                    <button 
                        onClick={() => handleRunAI('parse-jd')}
                        disabled={parsing}
                        className="px-3 py-1.5 bg-gray-100 border rounded hover:bg-gray-200 text-sm font-medium disabled:opacity-50"
                    >
                        Parse JD
                    </button>
                    <button 
                         onClick={() => handleRunAI('match')}
                         disabled={parsing}
                         className="px-3 py-1.5 bg-gray-100 border rounded hover:bg-gray-200 text-sm font-medium disabled:opacity-50"
                    >
                        Analyze Match
                    </button>
                    <button 
                         onClick={() => handleRunAI('tailor-cv')}
                         disabled={parsing}
                         className="px-3 py-1.5 bg-gray-100 border rounded hover:bg-gray-200 text-sm font-medium disabled:opacity-50"
                    >
                        Tailor CV
                    </button>
                </div>
                
                {parsing && <div className="text-blue-600 animate-pulse text-sm font-medium">AI is processing...</div>}
                
                <div className="space-y-4">
                    {aiOutputs.map((output) => (
                        <div key={output.id} className="border rounded-lg p-4 shadow-sm bg-gray-50">
                            <div className="flex justify-between mb-2 border-b pb-2">
                                <span className="font-bold text-sm uppercase text-gray-700">{output.kind.replace('_', ' ')}</span>
                                <span className="text-xs text-gray-400">{new Date(output.created_at).toLocaleString()}</span>
                            </div>
                            <AIOutputDisplay output={output} />
                        </div>
                    ))}
                    {aiOutputs.length === 0 && !parsing && (
                        <div className="text-gray-500 italic text-center py-8 bg-gray-50 rounded border border-dashed">
                            No AI outputs yet. Try running parsing or matching.
                        </div>
                    )}
                </div>
             </div>
           )}
        </div>

        <div className="lg:col-span-1 border-l pl-8">
            <div className="bg-gray-50 p-4 rounded-lg border">
                <h3 className="font-semibold mb-4 text-gray-900">Application Details</h3>
                <dl className="space-y-3 text-sm">
                    <div className="flex justify-between border-b border-gray-200 pb-2">
                        <dt className="text-gray-500">Applied At</dt>
                        <dd>{application.applied_at ? new Date(application.applied_at).toLocaleDateString() : '-'}</dd>
                    </div>
                    <div className="flex justify-between border-b border-gray-200 pb-2">
                        <dt className="text-gray-500">Priority</dt>
                        <dd className="capitalize font-medium">{application.priority}</dd>
                    </div>
                    <div className="flex justify-between border-b border-gray-200 pb-2">
                        <dt className="text-gray-500">Source</dt>
                        <dd className="capitalize">{job?.source}</dd>
                    </div>
                     <div className="flex justify-between">
                        <dt className="text-gray-500">Salary Exp.</dt>
                        <dd>{application.salary_expectation ? `$${application.salary_expectation.toLocaleString()}` : '-'}</dd>
                    </div>
                </dl>
                
                <div className="mt-6 pt-4 border-t border-gray-200">
                    <h3 className="font-semibold mb-2 text-gray-900">Reminders</h3>
                    <p className="text-gray-500 text-xs italic mb-2">No reminders set.</p>
                    <button className="text-blue-600 text-xs hover:underline font-medium">+ Add Reminder</button>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
