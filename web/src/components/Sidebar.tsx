'use client';

import React from 'react';
import { useChatStore } from '@/lib/store';
import { Plus, Trash2, Edit2 } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import Link from 'next/link';

export const Sidebar: React.FC = () => {
  const {
    conversations,
    currentConversationId,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
  } = useChatStore();

  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editingTitle, setEditingTitle] = React.useState('');

  const handleStartEdit = (id: string, title: string) => {
    setEditingId(id);
    setEditingTitle(title);
  };

  const handleSaveTitle = (id: string) => {
    if (editingTitle.trim()) {
      updateConversationTitle(id, editingTitle);
    }
    setEditingId(null);
  };

  return (
    <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col h-screen">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">J</span>
          </div>
          <div>
            <h1 className="font-bold text-gray-900 dark:text-white">Jarvis AI</h1>
            <p className="text-xs text-gray-500">v2.0.0</p>
          </div>
        </div>
        <button
          onClick={createConversation}
          className="w-full bg-primary hover:bg-primary/90 text-white rounded-lg py-2 px-4 flex items-center justify-center gap-2 font-medium transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nova Conversa
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {conversations.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 text-sm py-8">
            <p>Nenhuma conversa ainda</p>
            <p className="text-xs mt-2">Clique em "Nova Conversa" para começar</p>
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`group p-3 rounded-lg cursor-pointer transition-colors ${
                currentConversationId === conversation.id
                  ? 'bg-primary text-white'
                  : 'hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-900 dark:text-gray-100'
              }`}
            >
              {editingId === conversation.id ? (
                <input
                  type="text"
                  value={editingTitle}
                  onChange={(e) => setEditingTitle(e.target.value)}
                  onBlur={() => handleSaveTitle(conversation.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveTitle(conversation.id);
                    if (e.key === 'Escape') setEditingId(null);
                  }}
                  autoFocus
                  className="w-full bg-transparent border-b border-current outline-none text-sm font-medium"
                />
              ) : (
                <>
                  <div
                    onClick={() => selectConversation(conversation.id)}
                    className="flex-1"
                  >
                    <p className="text-sm font-medium truncate">
                      {conversation.title}
                    </p>
                    <p className={`text-xs mt-1 ${
                      currentConversationId === conversation.id
                        ? 'text-blue-100'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}>
                      {format(new Date(conversation.updatedAt), 'dd MMM HH:mm', {
                        locale: ptBR,
                      })}
                    </p>
                  </div>

                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity mt-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartEdit(conversation.id, conversation.title);
                      }}
                      className="p-1 hover:bg-gray-300 dark:hover:bg-gray-700 rounded transition-colors"
                      title="Editar título"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Tem certeza?')) {
                          deleteConversation(conversation.id);
                        }
                      }}
                      className="p-1 hover:bg-red-500 hover:text-white rounded transition-colors"
                      title="Deletar conversa"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4 space-y-2 text-sm">
        <Link
          href="/documents"
          className="block text-center text-gray-600 dark:text-gray-400 hover:text-primary transition-colors"
        >
          📚 Documentos
        </Link>
        <Link
          href="/settings"
          className="block text-center text-gray-600 dark:text-gray-400 hover:text-primary transition-colors"
        >
          ⚙️ Configurações
        </Link>
      </div>
    </div>
  );
};
