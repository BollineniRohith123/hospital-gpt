'use client';

import React, { 
  createContext, 
  useState, 
  useContext, 
  useCallback, 
  ReactNode,
  useEffect
} from 'react';
import { v4 as uuidv4 } from 'uuid';

// Define types for our context
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  markdownContent?: string;
  timestamp: number;
  medicalContext?: MedicalContext;
  confidence?: number;
  sources?: string[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  department?: string;
  medicalCategory?: string;
  relevantMetrics?: Record<string, any>;
}

interface MedicalContext {
  department?: string;
  specialty?: string;
  urgency?: 'low' | 'medium' | 'high';
  relatedDocs?: string[];
}

interface ChatContextType {
  conversations: Conversation[];
  currentConversationId: string | null;
  addMessageToConversation: (content: string, role: 'user' | 'assistant', markdownContent?: string, medicalContext?: MedicalContext) => void;
  startNewChat: () => void;
  selectConversation: (conversationId: string) => void;
  deleteConversation: (conversationId: string) => void;
  renameConversation: (conversationId: string, newTitle: string) => void;
  addMedicalContext: (messageId: string, context: MedicalContext) => void;
  getDepartmentHistory: (department: string) => Message[];
  getRelevantMetrics: (conversationId: string) => Record<string, any>;
  categorizeConversation: (conversationId: string, category: string) => void;
}

// Create the context
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Provider component
export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isClient, setIsClient] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    // Only run on the client
    if (typeof window !== 'undefined') {
      const savedConversations = localStorage.getItem('chatConversations');
      return savedConversations 
        ? JSON.parse(savedConversations) 
        : [createNewConversation()];
    }
    return [createNewConversation()];
  });

  const [currentConversationId, setCurrentConversationId] = useState<string | null>(() => {
    // Only run on the client
    if (typeof window !== 'undefined') {
      const savedCurrentConversationId = localStorage.getItem('currentConversationId');
      return savedCurrentConversationId || conversations[0].id;
    }
    return conversations[0].id;
  });

  const [medicalMetrics, setMedicalMetrics] = useState<Record<string, any>>({});

  // Ensure client-side rendering
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Function to create a new conversation
  function createNewConversation(department?: string): Conversation {
    const newConversation: Conversation = {
      id: uuidv4(),
      title: `New Chat ${new Date().toLocaleString()}`,
      messages: [],
      createdAt: Date.now(),
      department,
      medicalCategory: 'general',
      relevantMetrics: {}
    };
    return newConversation;
  }

  // Update localStorage whenever conversations change
  useEffect(() => {
    if (isClient) {
      localStorage.setItem('chatConversations', JSON.stringify(conversations));
    }
  }, [conversations, isClient]);

  // Update localStorage whenever current conversation changes
  useEffect(() => {
    if (isClient && currentConversationId) {
      localStorage.setItem('currentConversationId', currentConversationId);
    }
  }, [currentConversationId, isClient]);

  // Add a message to the current conversation
  const addMessageToConversation = useCallback((
    content: string, 
    role: 'user' | 'assistant', 
    markdownContent?: string,
    medicalContext?: MedicalContext
  ) => {
    setConversations(prevConversations => 
      prevConversations.map(conv => 
        conv.id === currentConversationId 
          ? {
              ...conv, 
              messages: [
                ...conv.messages, 
                { 
                  id: uuidv4(), 
                  role, 
                  content, 
                  markdownContent, 
                  medicalContext,
                  timestamp: Date.now() 
                }
              ]
            }
          : conv
      )
    );
  }, [currentConversationId]);

  // Start a new chat
  const startNewChat = useCallback(() => {
    const newConversation = createNewConversation();
    setConversations(prev => [...prev, newConversation]);
    setCurrentConversationId(newConversation.id);
  }, []);

  // Select a specific conversation
  const selectConversation = useCallback((conversationId: string) => {
    setCurrentConversationId(conversationId);
  }, []);

  // Delete a specific conversation
  const deleteConversation = useCallback((conversationId: string) => {
    setConversations(prev => {
      // Filter out the conversation to be deleted
      const updatedConversations = prev.filter(conv => conv.id !== conversationId);
      
      // If no conversations remain, create a new one
      if (updatedConversations.length === 0) {
        const newConversation = createNewConversation();
        updatedConversations.push(newConversation);
        setCurrentConversationId(newConversation.id);
      } else if (currentConversationId === conversationId) {
        // If the current conversation is deleted, select the first remaining conversation
        setCurrentConversationId(updatedConversations[0].id);
      }
      
      return updatedConversations;
    });
  }, [currentConversationId]);

  // Rename a specific conversation
  const renameConversation = useCallback((conversationId: string, newTitle: string) => {
    setConversations(prev => 
      prev.map(conv => 
        conv.id === conversationId 
          ? { ...conv, title: newTitle.trim() || `Consultation ${new Date().toLocaleString()}` }
          : conv
      )
    );
  }, []);

  // Add medical context to a message
  const addMedicalContext = useCallback((messageId: string, context: MedicalContext) => {
    setConversations(prev => 
      prev.map(conv => ({
        ...conv,
        messages: conv.messages.map(msg => 
          msg.id === messageId 
            ? { ...msg, medicalContext: context }
            : msg
        )
      }))
    );
  }, []);

  // Get message history for a specific department
  const getDepartmentHistory = useCallback((department: string): Message[] => {
    return conversations.flatMap(conv => 
      conv.department === department ? conv.messages : []
    );
  }, [conversations]);

  // Get relevant metrics for a conversation
  const getRelevantMetrics = useCallback((conversationId: string) => {
    const conversation = conversations.find(conv => conv.id === conversationId);
    return conversation?.relevantMetrics || {};
  }, [conversations]);

  // Categorize a conversation
  const categorizeConversation = useCallback((conversationId: string, category: string) => {
    setConversations(prev => 
      prev.map(conv => 
        conv.id === conversationId 
          ? { ...conv, medicalCategory: category }
          : conv
      )
    );
  }, []);

  // Prevent rendering on server
  if (!isClient) {
    return null;
  }

  return (
    <ChatContext.Provider 
      value={{ 
        conversations, 
        currentConversationId, 
        addMessageToConversation, 
        startNewChat, 
        selectConversation,
        deleteConversation,
        renameConversation,
        addMedicalContext,
        getDepartmentHistory,
        getRelevantMetrics,
        categorizeConversation
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

// Custom hook to use the chat context
export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};
