'use client';

import { useChatContext } from '@/context/ChatContext';
import MedicalInsightRenderer from './MedicalInsightRenderer';
import { 
  PlusIcon, 
  ChatBubbleLeftIcon, 
  TrashIcon, 
  PencilIcon, 
  EllipsisHorizontalIcon 
} from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

export default function Sidebar() {
  const { 
    conversations, 
    currentConversationId, 
    startNewChat, 
    selectConversation,
    deleteConversation,
    renameConversation  
  } = useChatContext();

  const [isHovered, setIsHovered] = useState<string | null>(null);
  const [editingConversationId, setEditingConversationId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState<string>('');
  const [activeOptionsId, setActiveOptionsId] = useState<string | null>(null);
  const [selectedInsightContent, setSelectedInsightContent] = useState<string | null>(null);

  // Sort conversations by creation date, most recent first
  const sortedConversations = [...(conversations || [])].sort((a, b) => 
    b.createdAt - a.createdAt
  );

  // Prevent deleting the last conversation
  const handleDeleteConversation = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    // Prevent deleting if it's the last conversation
    if (conversations.length > 1) {
      deleteConversation(conversationId);
      setActiveOptionsId(null);
    } else {
      console.warn('Cannot delete the last conversation');
    }
  };

  // Handle renaming a conversation
  const handleRenameConversation = (conversationId: string) => {
    if (editTitle.trim()) {
      renameConversation(conversationId, editTitle.trim());
      setEditingConversationId(null);
      setEditTitle('');
      setActiveOptionsId(null);
    }
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-80 bg-gradient-to-br from-blue-50 to-blue-100 p-4 flex flex-col shadow-xl border-r border-gray-200">
        {/* New Chat Button */}
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={startNewChat}
          className="w-full flex items-center justify-center bg-blue-500 text-white py-3 rounded-xl hover:bg-blue-600 mb-6 shadow-md transition-all duration-300 ease-in-out"
        >
          <PlusIcon className="h-6 w-6 mr-2" />
          Start New Medical Consultation
        </motion.button>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          <h3 className="text-sm font-semibold text-gray-500 mb-2 pl-2">
            Previous Consultations
          </h3>
          <AnimatePresence>
            {sortedConversations.map((conversation) => (
              <motion.div
                key={conversation.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="w-full"
              >
                <div 
                  onMouseEnter={() => setIsHovered(conversation.id)}
                  onMouseLeave={() => {
                    setIsHovered(null);
                    if (!editingConversationId) setActiveOptionsId(null);
                  }}
                  className={`
                    relative flex items-center p-3 rounded-xl cursor-pointer 
                    transition-all duration-300 ease-in-out
                    ${conversation.id === currentConversationId 
                      ? 'bg-blue-100 text-blue-700 shadow-sm' 
                      : 'hover:bg-blue-50 text-gray-700'}
                  `}
                  onClick={() => {
                    if (editingConversationId) setEditingConversationId(null);
                    selectConversation(conversation.id);
                    setActiveOptionsId(null);
                    
                    // Find the first medical insight message in the conversation
                    const medicalInsight = conversation.messages.find(
                      msg => msg.markdownContent
                    );
                    setSelectedInsightContent(
                      medicalInsight?.markdownContent || null
                    );
                  }}
                >
                  {/* Conversation Title */}
                  {editingConversationId === conversation.id ? (
                    <div className="flex items-center w-full">
                      <input 
                        type="text" 
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRenameConversation(conversation.id);
                          if (e.key === 'Escape') {
                            setEditingConversationId(null);
                            setEditTitle('');
                          }
                        }}
                        autoFocus
                        className="flex-1 px-2 py-1 border rounded text-sm mr-2"
                        placeholder="Enter new title"
                      />
                      <button 
                        onClick={() => handleRenameConversation(conversation.id)}
                        className="text-green-500 hover:text-green-700"
                      >
                        ✓
                      </button>
                      <button 
                        onClick={() => {
                          setEditingConversationId(null);
                          setEditTitle('');
                        }}
                        className="text-red-500 hover:text-red-700 ml-2"
                      >
                        ✗
                      </button>
                    </div>
                  ) : (
                    <>
                      <ChatBubbleLeftIcon className="h-6 w-6 mr-3 text-blue-400" />
                      <span className="flex-1 truncate text-sm font-medium">
                        {conversation.title || 'Untitled Consultation'}
                      </span>
                    </>
                  )}
                  
                  {/* Action Buttons */}
                  {isHovered === conversation.id && !editingConversationId && (
                    <div className="absolute right-2">
                      {/* Options Dropdown */}
                      <motion.button
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className={`
                          text-gray-500 hover:text-gray-700 
                          ${activeOptionsId === conversation.id ? 'text-blue-600' : ''}
                        `}
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveOptionsId(
                            activeOptionsId === conversation.id ? null : conversation.id
                          );
                        }}
                      >
                        <EllipsisHorizontalIcon className="h-5 w-5" />
                      </motion.button>

                      {/* Dropdown Menu */}
                      {activeOptionsId === conversation.id && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="absolute right-0 top-full mt-1 bg-white shadow-lg rounded-md border border-gray-200 z-10"
                        >
                          {/* Rename Option */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingConversationId(conversation.id);
                              setEditTitle(conversation.title || '');
                              setActiveOptionsId(null);
                            }}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <PencilIcon className="h-4 w-4 mr-2" />
                            Rename
                          </button>

                          {/* Delete Option */}
                          {conversations.length > 1 && (
                            <button
                              onClick={(e) => handleDeleteConversation(conversation.id, e)}
                              className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                            >
                              <TrashIcon className="h-4 w-4 mr-2" />
                              Delete
                            </button>
                          )}
                        </motion.div>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-500">
            Medical GPT Assistant
          </p>
        </div>
      </div>

      {/* Medical Insight Renderer */}
      {selectedInsightContent && (
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          <MedicalInsightRenderer content={selectedInsightContent} />
        </div>
      )}
    </div>
  );
}
