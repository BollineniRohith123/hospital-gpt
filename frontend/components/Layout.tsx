'use client';

import React, { ReactNode } from 'react';
import Head from 'next/head';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  title = 'Metropolitan Advanced Medical Center' 
}) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Head>
        <title>{title}</title>
        <meta name="description" content="Advanced Medical Care and Innovation" />
        <link rel="icon" href="/hospital-logo.svg" />
      </Head>
      
      <Sidebar />
      
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-200 p-4">
          <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
        
        <footer className="bg-white shadow p-4 text-center">
          <p className="text-sm text-gray-600">
            2025 Metropolitan Advanced Medical Center. All rights reserved.
          </p>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
