'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Application } from '@/lib/types';
import Link from 'next/link';

export default function Dashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const { data: applications = [] } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: async () => {
      const res = await api.get('/applications');
      return res.data;
    },
    enabled: !!user,
  });

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return <div className="p-8">Loading...</div>;
  }

  // Simple stats
  const total = applications.length;
  const applied = applications.filter(a => a.status === 'applied').length;
  const interview = applications.filter(a => ['hr_screen', 'tech_screen', 'onsite'].includes(a.status)).length;
  const offers = applications.filter(a => a.status === 'offer').length;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Welcome, {user.email}!</h1>
      <p className="text-gray-600 mb-8">Here is your application overview.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
         <div className="bg-white p-6 rounded shadow border-l-4 border-blue-500">
             <div className="text-gray-500 text-sm font-bold uppercase">Total</div>
             <div className="text-3xl font-bold">{total}</div>
         </div>
         <div className="bg-white p-6 rounded shadow border-l-4 border-yellow-500">
             <div className="text-gray-500 text-sm font-bold uppercase">Applied</div>
             <div className="text-3xl font-bold">{applied}</div>
         </div>
         <div className="bg-white p-6 rounded shadow border-l-4 border-purple-500">
             <div className="text-gray-500 text-sm font-bold uppercase">Interviewing</div>
             <div className="text-3xl font-bold">{interview}</div>
         </div>
         <div className="bg-white p-6 rounded shadow border-l-4 border-green-500">
             <div className="text-gray-500 text-sm font-bold uppercase">Offers</div>
             <div className="text-3xl font-bold">{offers}</div>
         </div>
      </div>
      
      <div className="bg-white p-6 rounded shadow">
         <div className="flex justify-between items-center mb-4">
             <h2 className="text-xl font-bold">Recent Activity</h2>
             <Link href="/applications" className="text-blue-600 hover:underline text-sm">View Board →</Link>
         </div>
         <div className="divide-y">
            {applications.slice(0, 5).map(app => (
                <div key={app.id} className="py-3 flex justify-between items-center">
                    <div>
                        <div className="font-semibold">{app.job_posting?.title}</div>
                        <div className="text-sm text-gray-600">{app.job_posting?.company?.name}</div>
                    </div>
                    <span className="px-2 py-1 bg-gray-100 rounded text-xs capitalize">{app.status}</span>
                </div>
            ))}
            {applications.length === 0 && <div className="text-gray-500 italic py-4">No applications yet.</div>}
         </div>
      </div>
    </div>
  );
}
