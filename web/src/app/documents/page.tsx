'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Upload, ArrowLeft, RefreshCw } from 'lucide-react';
import { chatAPI } from '@/lib/api';

interface DocumentStatus {
  status: string;
  vector_store: {
    name: string;
    vectors_count: number;
    segments_count: number;
  };
}

export default function DocumentsPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState<DocumentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await chatAPI.getDocumentsStatus();
      setStatus(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => {
        formData.append('files', file);
      });

      await chatAPI.uploadDocuments(formData);
      await fetchStatus();
    } catch (err: any) {
      setError(err.message || 'Erro ao fazer upload dos documentos');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Gerenciador de Documentos
            </h1>
          </div>
          <button
            onClick={fetchStatus}
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
        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
            Upload de Documentos
          </h2>

          <label className="flex items-center justify-center w-full px-6 py-10 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer">
            <div className="text-center">
              <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Clique para selecionar ou arraste arquivos PDF
              </p>
            </div>
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={isUploading}
              className="hidden"
            />
          </label>

          {isUploading && (
            <div className="mt-4 text-center">
              <div className="inline-flex items-center gap-2">
                <div className="w-4 h-4 bg-primary rounded-full animate-spin" />
                <span className="text-gray-600 dark:text-gray-400">Fazendo upload...</span>
              </div>
            </div>
          )}
        </div>

        {/* Status Section */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center gap-2">
              <div className="w-4 h-4 bg-primary rounded-full animate-spin" />
              <span className="text-gray-600 dark:text-gray-400">Carregando...</span>
            </div>
          </div>
        ) : status ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                Vetores Indexados
              </h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {status.vector_store.vectors_count}
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                Segmentos
              </h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {status.vector_store.segments_count}
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                Coleção
              </h3>
              <p className="text-lg font-bold text-gray-900 dark:text-white truncate">
                {status.vector_store.name}
              </p>
            </div>
          </div>
        ) : null}

        {/* Info */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-blue-900 dark:text-blue-400 text-sm">
            <strong>ℹ️ Dica:</strong> Faça upload de arquivos PDF para indexar e usar com o chat.
            Os documentos serão automaticamente quebrados em chunks e indexados no Qdrant.
          </p>
        </div>
      </div>
    </div>
  );
}
