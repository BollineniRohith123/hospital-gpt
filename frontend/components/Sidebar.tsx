'use client';

import React from 'react';
import Link from 'next/link';
import { 
  HomeIcon, 
  ChatBubbleLeftRightIcon, 
  DocumentTextIcon, 
  UserGroupIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/solid';
import { 
  PlusIcon 
} from '@heroicons/react/24/outline';

const hospitalInfo = {
  name: 'Metropolitan Advanced Medical Center',
  description: 'Pioneering Advanced Medical Care & Innovation',
  foundedYear: 1987,
  specialties: [
    'Precision Oncology',
    'Cardiovascular Research',
    'Neuroscience',
    'Genomic Medicine'
  ]
};

export default function Sidebar() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-blue-900 to-blue-700 text-white p-6 shadow-2xl">
        <div className="mb-8 text-center">
          <img 
            src="/hospital-logo.svg" 
            alt="Hospital Logo" 
            className="mx-auto w-24 h-24 mb-4"
          />
          <h1 className="text-xl font-bold">{hospitalInfo.name}</h1>
          <p className="text-xs text-blue-200 mt-2">{hospitalInfo.description}</p>
        </div>

        <nav className="space-y-2">
          <Link 
            href="/dashboard" 
            className="flex items-center space-x-3 p-2 hover:bg-blue-800 rounded-lg transition-colors"
          >
            <HomeIcon className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>
          <Link 
            href="/chat" 
            className="flex items-center space-x-3 p-2 hover:bg-blue-800 rounded-lg transition-colors"
          >
            <ChatBubbleLeftRightIcon className="w-5 h-5" />
            <span>Medical Assistant</span>
          </Link>
          <Link 
            href="/reports" 
            className="flex items-center space-x-3 p-2 hover:bg-blue-800 rounded-lg transition-colors"
          >
            <DocumentTextIcon className="w-5 h-5" />
            <span>Medical Reports</span>
          </Link>
          <Link 
            href="/patients" 
            className="flex items-center space-x-3 p-2 hover:bg-blue-800 rounded-lg transition-colors"
          >
            <UserGroupIcon className="w-5 h-5" />
            <span>Patient Management</span>
          </Link>
          <Link 
            href="/analytics" 
            className="flex items-center space-x-3 p-2 hover:bg-blue-800 rounded-lg transition-colors"
          >
            <ChartBarIcon className="w-5 h-5" />
            <span>Hospital Analytics</span>
          </Link>
        </nav>

        <div className="mt-8 text-center bg-blue-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold mb-2">Our Specialties</h3>
          <ul className="text-xs space-y-1">
            {hospitalInfo.specialties.map((specialty, index) => (
              <li key={index} className="text-blue-200">{specialty}</li>
            ))}
          </ul>
        </div>

        <div className="mt-4 text-center text-xs text-blue-300">
          <p>Founded: {hospitalInfo.foundedYear}</p>
          <p>Innovative Healthcare Solutions</p>
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-500"></p>
        </div>
      </div>
    </div>
  );
}
