'use client';

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Layout from '@/components/Layout';
import { 
  PaperAirplaneIcon, 
  SparklesIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/react/24/solid';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  reasoning?: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) return;

    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: query,
      role: 'user',
      timestamp: Date.now()
    };

    // Update messages with user query
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setQuery('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/query', { 
        query: query
      });

      // Create assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        content: response.data.response || 'No information found.',
        role: 'assistant',
        timestamp: Date.now(),
        reasoning: response.data.reasoning
      };

      // Update messages with AI response
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error querying:', error);
      
      // Handle error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Sorry, something went wrong. Please try again.',
        role: 'assistant',
        timestamp: Date.now()
      };

      setMessages(prevMessages => [...prevMessages, errorMessage]);
      setError('Failed to get response. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: string) => {
    // Function to create structured output
    const createStructuredOutput = (text: string) => {
      // Define sections and their corresponding headings
      const sections = [
        { 
          heading: 'Hospital Overview', 
          keywords: ['Metropolitan Advanced Medical Center', 'established', 'healthcare facility']
        },
        { 
          heading: 'Facility Capacity', 
          keywords: ['beds', 'hospital rooms', 'medical facilities']
        },
        { 
          heading: 'Patient Care and Innovation', 
          keywords: ['patient volume', 'research impact', 'global health innovation']
        },
        { 
          heading: 'Resource Management', 
          keywords: ['bed allocation', 'utilization', 'treatment']
        }
      ];

      // Split the text into lines
      const lines = text.split('\n');
      
      // Create a structured output
      return (
        <div className="space-y-4">
          {sections.map((section, sectionIndex) => {
            // Find lines related to this section
            const sectionLines = lines.filter(line => 
              section.keywords.some(keyword => 
                line.toLowerCase().includes(keyword.toLowerCase())
              )
            );

            if (sectionLines.length === 0) return null;

            return (
              <div key={sectionIndex} className="mb-4">
                <h3 className="text-lg font-bold text-blue-700 mb-2">
                  {section.heading}
                </h3>
                <ul className="list-disc list-outside pl-5 space-y-2">
                  {sectionLines.map((line, lineIndex) => {
                    // Remove any remaining Markdown-like formatting
                    const cleanLine = line
                      .replace(/^#+\s*/, '')
                      .replace(/\*\*/g, '')
                      .replace(/^[-•]\s*/, '')
                      .trim();

                    return cleanLine ? (
                      <li key={lineIndex} className="text-gray-700">
                        {cleanLine}
                      </li>
                    ) : null;
                  }).filter(Boolean)}
                </ul>
              </div>
            );
          })}
          
          {/* Preserve the original last line */}
          {lines[lines.length - 1] && (
            <div className="mt-4 text-sm text-gray-600">
              {lines[lines.length - 1]}
            </div>
          )}
        </div>
      );
    };

    return createStructuredOutput(message);
  };

  return (
    <Layout title="Medical AI Assistant">
      <div className="flex flex-col h-[calc(100vh-120px)] bg-white rounded-xl shadow-md overflow-hidden">
        {/* Chat Messages Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex flex-col justify-center items-center text-center text-gray-400">
              <SparklesIcon className="h-16 w-16 text-blue-300 mb-4" />
              <h2 className="text-2xl font-semibold mb-2">
                Medical AI Assistant
              </h2>
              <p className="max-w-md">
                Ask any questions about our hospital, medical services, 
                patient care, or health-related inquiries.
              </p>
            </div>
          )}

          <AnimatePresence>
            {messages.map((msg, index) => (
              <motion.div 
                key={msg.id}
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
                  {renderMessage(msg.content)}
                  
                  {msg.reasoning && (
                    <details className="text-sm text-gray-500 mt-2">
                      <summary>Show Reasoning</summary>
                      <div className="mt-2 p-2 bg-white/20 rounded">
                        {msg.reasoning}
                      </div>
                    </details>
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

          {error && (
            <div className="flex justify-start">
              <div className="bg-red-50 p-4 rounded-2xl flex items-center text-red-600">
                <ExclamationTriangleIcon className="h-6 w-6 mr-2" />
                <span>{error}</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
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
              placeholder="Ask a question about our hospital or medical services..."
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
      </div>
    </Layout>
  );
};

export default ChatPage;
