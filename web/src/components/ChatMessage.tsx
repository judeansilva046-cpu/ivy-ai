'use client';

import React from 'react';
import { Message } from '@/lib/store';
import ReactMarkdown from 'react-markdown';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-4 animate-fade-in ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      <div
        className={`max-w-2xl rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-primary text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        }`}
      >
        {isUser ? (
          <p className="text-sm">{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        <div className={`flex items-center gap-2 mt-2 text-xs ${
          isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
        }`}>
          {format(new Date(message.timestamp), 'HH:mm', { locale: ptBR })}
          {message.contextUsed && !isUser && (
            <span className="ml-2 bg-opacity-20 bg-gray-400 px-2 py-1 rounded">
              📚 {message.contextUsed} docs
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
