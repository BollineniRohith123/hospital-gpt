'use client';

import React, { useState } from 'react';
import { 
  BellIcon, 
  MagnifyingGlassIcon, 
  UserCircleIcon 
} from '@heroicons/react/24/solid';

const Header: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const currentDateTime = new Date().toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Implement search functionality
    console.log('Searching for:', searchQuery);
  };

  return (
    <header className="bg-white shadow-md p-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        <form onSubmit={handleSearch} className="relative flex items-center">
          <input 
            type="text" 
            placeholder="Search medical records, patients..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 w-96"
          />
          <MagnifyingGlassIcon 
            className="absolute left-3 w-5 h-5 text-gray-400" 
          />
        </form>
      </div>

      <div className="flex items-center space-x-6">
        <div className="text-sm text-gray-600">
          {currentDateTime}
        </div>

        <div className="relative">
          <BellIcon className="w-6 h-6 text-gray-600 hover:text-blue-600 cursor-pointer" />
          <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full px-2 py-1 text-xs">
            3
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <UserCircleIcon className="w-8 h-8 text-gray-600" />
          <div>
            <p className="text-sm font-semibold">Dr. Emily Rodriguez</p>
            <p className="text-xs text-gray-500">Chief Medical Officer</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
