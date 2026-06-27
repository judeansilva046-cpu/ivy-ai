'use client';

import React, { useEffect } from 'react';
import { useChatStore } from '@/lib/store';
import { Sidebar } from '@/components/Sidebar';
import { ChatBox } from '@/components/ChatBox';

export default function ChatPage() {
  const { currentConversationId, createConversation } = useChatStore();

  useEffect(() => {
    // Create initial conversation if none exists
    if (!currentConversationId) {
      createConversation();
    }
  }, [currentConversationId, createConversation]);

  if (!currentConversationId) {
    return <div>Carregando...</div>;
  }

  return (
    <div className="flex h-screen bg-white dark:bg-gray-900">
      <Sidebar />
      <main className="flex-1">
        <ChatBox conversationId={currentConversationId} />
      </main>
    </div>
  );
}
