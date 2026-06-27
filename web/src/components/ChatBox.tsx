'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useChatStore, Message } from '@/lib/store';
import { chatAPI } from '@/lib/api';
import { ChatMessage } from './ChatMessage';
import { Send, Loader } from 'lucide-react';

interface ChatBoxProps {
  conversationId: string;
}

export const ChatBox: React.FC<ChatBoxProps> = ({ conversationId }) => {
  const {
    messages,
    isLoading,
    error,
    addMessage,
    setLoading,
    setError,
  } = useChatStore();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Send to API
      const response = await chatAPI.sendMessage({
        query: input,
        session_id: conversationId,
      });

      // Add assistant response
      const assistantMessage: Message = {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        contextUsed: response.context_used,
      };

      addMessage(assistantMessage);
    } catch (err: any) {
      setError(err.message || 'Erro ao enviar mensagem');
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Bem-vindo ao Jarvis AI
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-sm">
                Comece a conversar ou faça uma pergunta sobre seus documentos.
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-2 items-center text-gray-500">
                <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                  <Loader className="w-4 h-4 animate-spin" />
                </div>
                <span>Pensando...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-6 mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="border-t border-gray-200 dark:border-gray-800 p-6">
        <div className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua pergunta..."
            disabled={isLoading}
            className="flex-1 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-3 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-3 flex items-center gap-2 transition-colors"
          >
            {isLoading ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
