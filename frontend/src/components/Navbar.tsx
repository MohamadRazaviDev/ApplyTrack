'use client';

import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="font-bold text-xl">ApplyTrack</Link>
        <div className="space-x-4">
          {user ? (
            <>
              <Link href="/dashboard" className="hover:text-gray-300">Dashboard</Link>
              <Link href="/applications" className="hover:text-gray-300">Applications</Link>
              <Link href="/profile" className="hover:text-gray-300">Profile</Link>
              <button onClick={logout} className="hover:text-red-300">Logout</button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-gray-300">Login</Link>
              <Link href="/register" className="hover:text-gray-300">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
