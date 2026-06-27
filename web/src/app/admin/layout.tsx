'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { Loader, LogOut } from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        if (!authService.isAuthenticated()) {
          router.push('/login');
          return;
        }

        const user = await authService.getCurrentUser();
        if (!user.is_admin) {
          router.push('/');
          return;
        }

        setIsAdmin(true);
      } catch (error) {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAdmin();
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  const handleLogout = () => {
    authService.logout();
    router.push('/login');
  };

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-xl font-bold text-white">Jarvis Admin</h1>
        </div>

        <nav className="p-4 space-y-2">
          <Link
            href="/admin"
            className="block px-4 py-2 text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            📊 Dashboard
          </Link>
          <Link
            href="/admin/users"
            className="block px-4 py-2 text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            👥 Usuários
          </Link>
          <Link
            href="/admin/documents"
            className="block px-4 py-2 text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            📄 Documentos
          </Link>
          <Link
            href="/admin/analytics"
            className="block px-4 py-2 text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            📈 Análiticas
          </Link>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700 w-64">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Sair
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gray-900">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
