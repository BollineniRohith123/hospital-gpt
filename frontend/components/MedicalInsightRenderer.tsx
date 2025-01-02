import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';

interface MedicalInsightProps {
  content: string;
}

const MedicalInsightRenderer: React.FC<MedicalInsightProps> = ({ content }) => {
  // Custom components for different markdown elements
  const components = {
    h1: ({ node, ...props }) => (
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-3xl font-bold text-blue-700 mb-6 border-b-2 border-blue-200 pb-3"
        {...props}
      />
    ),
    h2: ({ node, ...props }) => (
      <motion.h2
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className="text-2xl font-semibold text-blue-600 mt-6 mb-4"
        {...props}
      />
    ),
    h3: ({ node, ...props }) => (
      <motion.h3
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="text-xl font-medium text-blue-500 mt-4 mb-3"
        {...props}
      />
    ),
    ul: ({ node, ...props }) => (
      <motion.ul
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1 }}
        className="list-disc list-inside space-y-2 pl-4 text-gray-700"
        {...props}
      />
    ),
    ol: ({ node, ...props }) => (
      <motion.ol
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1 }}
        className="list-decimal list-inside space-y-2 pl-4 text-gray-700"
        {...props}
      />
    ),
    li: ({ node, ...props }) => (
      <motion.li
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="py-1"
        {...props}
      />
    ),
    p: ({ node, ...props }) => (
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="mb-4 leading-relaxed text-gray-800"
        {...props}
      />
    ),
    strong: ({ node, ...props }) => (
      <strong className="font-bold text-blue-700" {...props} />
    ),
  };

  return (
    <div className="medical-insight-container bg-white p-8 rounded-xl shadow-lg max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        <ReactMarkdown
          components={components}
          remarkPlugins={[remarkGfm]}
          className="markdown-content"
        >
          {content}
        </ReactMarkdown>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700"
        >
          <p className="font-semibold">⚠️ Medical Disclaimer</p>
          <ul className="list-disc list-inside text-sm">
            <li>Information is for educational purposes only</li>
            <li>Always consult healthcare professionals for personalized advice</li>
          </ul>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default MedicalInsightRenderer;
