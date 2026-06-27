'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, RefreshCw, CheckCircle } from 'lucide-react';
import { chatAPI } from '@/lib/api';

interface SystemStatus {
  status: string;
  services: {
    vector_store: {
      status: string;
      info: {
        name: string;
        vectors_count: number;
        segments_count: number;
      };
    };
    cache: {
      status: string;
    };
  };
}

export default function SettingsPage() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiUrl, setApiUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  );

  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      const data = await chatAPI.getSystemStatus();
      setSystemStatus(data);
    } catch (err) {
      console.error('Error fetching system status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':
        return 'text-green-600 dark:text-green-400';
      case 'online':
        return 'text-green-600 dark:text-green-400';
      default:
        return 'text-red-600 dark:text-red-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Configurações
            </h1>
          </div>
          <button
            onClick={fetchSystemStatus}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-12 space-y-8">
        {/* API Configuration */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
            Configuração da API
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                URL da API
              </label>
              <input
                type="text"
                value={apiUrl}
                readOnly
                className="w-full bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white text-sm"
              />
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Configure através da variável NEXT_PUBLIC_API_URL
              </p>
            </div>
          </div>
        </div>

        {/* System Status */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center gap-2">
              <div className="w-4 h-4 bg-primary rounded-full animate-spin" />
              <span className="text-gray-600 dark:text-gray-400">Carregando...</span>
            </div>
          </div>
        ) : systemStatus ? (
          <>
            {/* Overview */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
                Status do Sistema
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Overall Status */}
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Status Geral
                      </p>
                      <p className={`text-lg font-bold ${getStatusColor(
                        systemStatus.status
                      )}`}>
                        {systemStatus.status.toUpperCase()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Vector Store */}
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle
                      className={`w-6 h-6 ${getStatusColor(
                        systemStatus.services.vector_store.status
                      )}`}
                    />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Vector Store (Qdrant)
                      </p>
                      <p className={`font-bold ${getStatusColor(
                        systemStatus.services.vector_store.status
                      )}`}>
                        {systemStatus.services.vector_store.status.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <p>
                      Vetores:{' '}
                      <span className="font-bold text-gray-900 dark:text-white">
                        {systemStatus.services.vector_store.info.vectors_count}
                      </span>
                    </p>
                    <p>
                      Segmentos:{' '}
                      <span className="font-bold text-gray-900 dark:text-white">
                        {systemStatus.services.vector_store.info.segments_count}
                      </span>
                    </p>
                  </div>
                </div>

                {/* Cache */}
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <div className="flex items-center gap-3">
                    <CheckCircle
                      className={`w-6 h-6 ${getStatusColor(
                        systemStatus.services.cache.status
                      )}`}
                    />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Cache (Redis)
                      </p>
                      <p className={`font-bold ${getStatusColor(
                        systemStatus.services.cache.status
                      )}`}>
                        {systemStatus.services.cache.status.toUpperCase()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Application Info */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <h3 className="font-semibold text-blue-900 dark:text-blue-400 mb-2">
                ℹ️ Informações
              </h3>
              <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                <li>• Backend: FastAPI v2.0.0</li>
                <li>• Frontend: Next.js 14 com TypeScript</li>
                <li>• Vector Database: Qdrant</li>
                <li>• Cache: Redis</li>
                <li>• LLM: OpenAI GPT-3.5-turbo</li>
                <li>• Embeddings: OpenAI text-embedding-3-small</li>
              </ul>
            </div>
          </>
        ) : null}

        {/* About */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Sobre Jarvis AI
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
            Jarvis AI é uma plataforma de chat inteligente com capacidades de
            Retrieval-Augmented Generation (RAG). O sistema permite conversar
            naturalmente enquanto recupera informações de documentos indexados.
          </p>
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <p>
              <strong>Versão:</strong> 2.0.0
            </p>
            <p>
              <strong>Status:</strong> Production Ready
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
