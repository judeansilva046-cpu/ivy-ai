'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { Trash2, Shield, Search, Loader } from 'lucide-react';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}

interface UsersListResponse {
  total: number;
  page: number;
  limit: number;
  users: User[];
}

export default function UsersAdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<UsersListResponse>('/admin/users', {
        params: {
          skip: page * 50,
          limit: 50,
          search,
        },
      });
      setUsers(response.data.users);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [search, page]);

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Tem certeza que deseja desativar este usuário?')) return;

    setActionLoading(userId);
    try {
      await apiClient.delete(`/admin/users/${userId}`);
      await fetchUsers();
    } catch (error) {
      alert('Erro ao deletar usuário');
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleAdmin = async (userId: string) => {
    setActionLoading(userId);
    try {
      await apiClient.post(`/admin/users/${userId}/admin`);
      await fetchUsers();
    } catch (error) {
      alert('Erro ao mudar admin status');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Gerenciamento de Usuários</h1>
        <p className="text-gray-400">Total: {total} usuários</p>
      </div>

      {/* Search */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex gap-2">
          <Search className="w-5 h-5 text-gray-400 mt-1 flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            placeholder="Buscar por email, usuário ou nome..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700 bg-gray-900">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                  Usuário
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                  Acesso
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-400">
                    <Loader className="w-5 h-5 animate-spin mx-auto" />
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-400">
                    Nenhum usuário encontrado
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-700/50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-white font-medium">{user.username}</p>
                        <p className="text-xs text-gray-400">{user.full_name || 'N/A'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-sm">{user.email}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          user.is_active
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}
                      >
                        {user.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium flex w-fit gap-1 items-center ${
                          user.is_admin
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}
                      >
                        {user.is_admin && <Shield className="w-3 h-3" />}
                        {user.is_admin ? 'Admin' : 'Usuário'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleToggleAdmin(user.id)}
                          disabled={actionLoading === user.id}
                          className="px-3 py-1 text-xs bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 rounded transition-colors disabled:opacity-50"
                        >
                          {actionLoading === user.id ? '...' : 'Admin'}
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          disabled={actionLoading === user.id}
                          className="px-3 py-1 text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded transition-colors disabled:opacity-50 flex items-center gap-1"
                        >
                          {actionLoading === user.id ? <Loader className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {!loading && total > 50 && (
          <div className="flex justify-between items-center px-6 py-4 border-t border-gray-700 bg-gray-900">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-4 py-2 bg-gray-700 text-white rounded disabled:opacity-50 hover:bg-gray-600 transition-colors"
            >
              ← Anterior
            </button>
            <span className="text-gray-400">
              Página {page + 1} de {Math.ceil(total / 50)}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * 50 >= total}
              className="px-4 py-2 bg-gray-700 text-white rounded disabled:opacity-50 hover:bg-gray-600 transition-colors"
            >
              Próxima →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
