'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { Users, FileText, ActivitySquare, TrendingUp } from 'lucide-react';

interface DashboardStats {
  users: {
    total_users: number;
    active_users: number;
    admin_users: number;
    new_users_today: number;
  };
  documents: {
    total_documents: number;
    total_vectors: number;
    total_segments: number;
    avg_vectors_per_doc: number;
  };
  system: {
    uptime_hours: number;
    total_requests: number;
    avg_response_time_ms: number;
    error_rate_percent: number;
  };
  timestamp: string;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.get<DashboardStats>('/admin/dashboard/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-white text-center py-12">Carregando...</div>;
  }

  if (!stats) {
    return <div className="text-white text-center py-12">Erro ao carregar estatísticas</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard Admin</h1>
        <p className="text-gray-400">Bem-vindo ao painel de administração</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Users Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-2">Total de Usuários</p>
              <p className="text-3xl font-bold text-white">{stats.users.total_users}</p>
              <p className="text-xs text-green-400 mt-2">
                {stats.users.active_users} ativo
              </p>
            </div>
            <Users className="w-12 h-12 text-indigo-500 opacity-20" />
          </div>
        </div>

        {/* Documents Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-2">Documentos Indexados</p>
              <p className="text-3xl font-bold text-white">{stats.documents.total_documents}</p>
              <p className="text-xs text-green-400 mt-2">
                {stats.documents.total_vectors} vetores
              </p>
            </div>
            <FileText className="w-12 h-12 text-green-500 opacity-20" />
          </div>
        </div>

        {/* Admin Users Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-2">Admins</p>
              <p className="text-3xl font-bold text-white">{stats.users.admin_users}</p>
              <p className="text-xs text-yellow-400 mt-2">
                {stats.users.new_users_today} novo hoje
              </p>
            </div>
            <ActivitySquare className="w-12 h-12 text-yellow-500 opacity-20" />
          </div>
        </div>

        {/* Requests Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-2">Taxa de Erro</p>
              <p className="text-3xl font-bold text-white">
                {stats.system.error_rate_percent.toFixed(2)}%
              </p>
              <p className="text-xs text-red-400 mt-2">
                {stats.system.avg_response_time_ms.toFixed(0)}ms latência
              </p>
            </div>
            <TrendingUp className="w-12 h-12 text-red-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Users Details */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Usuários</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-gray-700">
              <span className="text-gray-400">Total</span>
              <span className="text-white font-bold">{stats.users.total_users}</span>
            </div>
            <div className="flex justify-between items-center pb-3 border-b border-gray-700">
              <span className="text-gray-400">Ativos</span>
              <span className="text-green-400 font-bold">{stats.users.active_users}</span>
            </div>
            <div className="flex justify-between items-center pb-3 border-b border-gray-700">
              <span className="text-gray-400">Administradores</span>
              <span className="text-yellow-400 font-bold">{stats.users.admin_users}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Novos Hoje</span>
              <span className="text-blue-400 font-bold">{stats.users.new_users_today}</span>
            </div>
          </div>
        </div>

        {/* Documents Details */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Documentos & Vetores</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-gray-700">
              <span className="text-gray-400">Documentos</span>
              <span className="text-white font-bold">{stats.documents.total_documents}</span>
            </div>
            <div className="flex justify-between items-center pb-3 border-b border-gray-700">
              <span className="text-gray-400">Total de Vetores</span>
              <span className="text-green-400 font-bold">{stats.documents.total_vectors}</span>
            </div>
            <div className="flex justify-between items-center pb-3 border-b border-gray-700">
              <span className="text-gray-400">Segmentos</span>
              <span className="text-blue-400 font-bold">{stats.documents.total_segments}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Média Vetores/Doc</span>
              <span className="text-purple-400 font-bold">
                {stats.documents.avg_vectors_per_doc.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
        <p className="text-blue-400 text-sm">
          💡 Última atualização: {new Date(stats.timestamp).toLocaleString('pt-BR')}
        </p>
      </div>
    </div>
  );
}
