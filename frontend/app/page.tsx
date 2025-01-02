'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/solid';
import Layout from '@/components/Layout';
import ReasoningDropdown from '@/components/ReasoningDropdown';
import { useChatContext } from '@/context/ChatContext';

export default function Home() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { 
    conversations, 
    currentConversationId, 
    addMessageToConversation 
  } = useChatContext();

  // Get current conversation's messages
  const currentConversation = conversations?.find(
    conv => conv.id === currentConversationId
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message
    addMessageToConversation(query, 'user');
    setQuery('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/query', { query });
      
      // Add AI response with reasoning
      addMessageToConversation(
        response.data.response, 
        'assistant', 
        response.data.reasoning
      );
    } catch (error) {
      console.error('Error querying:', error);
      addMessageToConversation(
        'Sorry, something went wrong.', 
        'assistant'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      {/* Chat Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-white">
        {currentConversation?.messages.length === 0 && (
          <div className="h-full flex flex-col justify-center items-center text-center text-gray-400">
            <SparklesIcon className="h-16 w-16 text-blue-300 mb-4" />
            <h2 className="text-2xl font-semibold mb-2">
              Welcome to Medical GPT
            </h2>
            <p className="max-w-md">
              Start a new consultation by typing a medical question below.
              Our AI assistant is ready to help you with medical insights.
            </p>
          </div>
        )}

        <AnimatePresence>
          {currentConversation?.messages.map((msg, index) => (
            <motion.div 
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`
                  max-w-xl p-4 rounded-2xl 
                  ${msg.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-800'}
                  flex flex-col shadow-md
                `}
              >
                <div className="mb-2">{msg.content}</div>
                
                {/* Reasoning Dropdown for AI messages */}
                {msg.role === 'assistant' && (
                  <ReasoningDropdown reasoning={msg.markdownContent} />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-gray-100 p-4 rounded-2xl flex items-center">
              <div className="animate-pulse mr-2">
                <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
              </div>
              <span className="text-gray-600">Thinking...</span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <motion.form 
        onSubmit={handleSubmit} 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 bg-white border-t border-gray-200"
      >
        <div className="flex space-x-2 relative">
          <input 
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a medical question..."
            className="flex-1 p-3 pl-4 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <motion.button 
            type="submit" 
            disabled={isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="absolute right-1 top-1/2 -translate-y-1/2 bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600 disabled:opacity-50 transition-all duration-300"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </motion.button>
        </div>
      </motion.form>
    </Layout>
  );
}
