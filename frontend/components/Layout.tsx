'use client';

import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import { motion, AnimatePresence } from 'framer-motion';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area */}
      <AnimatePresence>
        <motion.main 
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="flex-1 flex flex-col bg-white shadow-lg rounded-tl-3xl rounded-bl-3xl overflow-hidden"
        >
          {children}
        </motion.main>
      </AnimatePresence>
    </div>
  );
}
