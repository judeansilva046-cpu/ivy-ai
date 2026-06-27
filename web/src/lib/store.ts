import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  contextUsed?: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

interface ChatStore {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // Conversation actions
  createConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  updateConversationTitle: (id: string, title: string) => void;

  // Message actions
  addMessage: (message: Message) => void;
  addMessages: (messages: Message[]) => void;
  clearMessages: () => void;

  // State actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

export const useChatStore = create<ChatStore>((set) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isLoading: false,
  error: null,

  createConversation: () =>
    set((state) => {
      const conversationId = generateId();
      const newConversation: Conversation = {
        id: conversationId,
        title: 'New Conversation',
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      return {
        conversations: [newConversation, ...state.conversations],
        currentConversationId: conversationId,
        messages: [],
      };
    }),

  selectConversation: (id: string) =>
    set((state) => {
      const conversation = state.conversations.find((c) => c.id === id);
      return {
        currentConversationId: id,
        messages: conversation?.messages || [],
      };
    }),

  deleteConversation: (id: string) =>
    set((state) => {
      const newConversations = state.conversations.filter((c) => c.id !== id);
      return {
        conversations: newConversations,
        currentConversationId:
          state.currentConversationId === id ? null : state.currentConversationId,
        messages:
          state.currentConversationId === id ? [] : state.messages,
      };
    }),

  updateConversationTitle: (id: string, title: string) =>
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === id
          ? { ...c, title, updatedAt: new Date().toISOString() }
          : c
      ),
    })),

  addMessage: (message: Message) =>
    set((state) => {
      const updatedConversations = state.conversations.map((c) =>
        c.id === state.currentConversationId
          ? {
              ...c,
              messages: [...c.messages, message],
              updatedAt: new Date().toISOString(),
            }
          : c
      );

      return {
        messages: [...state.messages, message],
        conversations: updatedConversations,
      };
    }),

  addMessages: (messages: Message[]) =>
    set((state) => ({
      messages: [...state.messages, ...messages],
    })),

  clearMessages: () =>
    set(() => ({
      messages: [],
    })),

  setLoading: (loading: boolean) =>
    set(() => ({
      isLoading: loading,
    })),

  setError: (error: string | null) =>
    set(() => ({
      error,
    })),
}));
