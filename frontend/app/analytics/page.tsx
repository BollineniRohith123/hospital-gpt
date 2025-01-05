'use client';

import React from 'react';
import Layout from '@/components/Layout';

const AnalyticsPage: React.FC = () => {
  return (
    <Layout title="Hospital Analytics">
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Hospital Analytics
        </h1>
        <div className="bg-white p-6 rounded-xl shadow-md">
          <p className="text-gray-600">
            Hospital Analytics dashboard is currently under development. 
            This feature will provide in-depth insights into hospital performance.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default AnalyticsPage;
