'use client';

import React from 'react';
import Link from 'next/link';
import { 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon, 
  DocumentTextIcon, 
  UserGroupIcon 
} from '@heroicons/react/24/solid';

const HomePage: React.FC = () => {
  const features = [
    {
      name: 'Dashboard',
      description: 'Comprehensive hospital overview and key metrics',
      icon: <ChartBarIcon className="w-12 h-12 text-blue-600" />,
      href: '/dashboard'
    },
    {
      name: 'Medical Assistant',
      description: 'AI-powered medical consultation and insights',
      icon: <ChatBubbleLeftRightIcon className="w-12 h-12 text-green-600" />,
      href: '/chat'
    },
    {
      name: 'Medical Reports',
      description: 'Detailed patient and hospital documentation',
      icon: <DocumentTextIcon className="w-12 h-12 text-purple-600" />,
      href: '/reports'
    },
    {
      name: 'Patient Management',
      description: 'Comprehensive patient tracking system',
      icon: <UserGroupIcon className="w-12 h-12 text-red-600" />,
      href: '/patients'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-white shadow-md p-6">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <img 
              src="/hospital-logo.svg" 
              alt="Hospital Logo" 
              className="w-12 h-12"
            />
            <h1 className="text-2xl font-bold text-gray-800">
              Metropolitan Advanced Medical Center
            </h1>
          </div>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-12">
        <section className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Welcome to Our Advanced Medical Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Innovative healthcare solutions powered by cutting-edge technology
          </p>
        </section>

        <div className="grid grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <Link 
              key={index} 
              href={feature.href}
              className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all group"
            >
              <div className="flex items-center space-x-6">
                {feature.icon}
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">
                    {feature.name}
                  </h3>
                  <p className="text-gray-600 mt-2">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>

      <footer className="bg-white shadow-md p-6 text-center">
        <p className="text-gray-600">
          2025 Metropolitan Advanced Medical Center. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default HomePage;
