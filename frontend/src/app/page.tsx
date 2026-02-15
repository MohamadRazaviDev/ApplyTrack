'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 text-center">
      <h1 className="text-5xl font-bold mb-6">ApplyTrack</h1>
      <p className="text-xl mb-8 max-w-2xl">
        A personal "mini-ATS" to track your job applications, parse descriptions, and tailor your CV with AI.
      </p>
      
      <div className="flex gap-4">
        <Link 
          href="/login" 
          className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-blue-700"
        >
          Login
        </Link>
        <Link 
          href="/register" 
          className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg text-lg font-medium hover:bg-gray-300"
        >
          Register
        </Link>
      </div>
    </main>
  );
}
