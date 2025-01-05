'use client';

import React from 'react';
import Layout from '@/components/Layout';

const ReportsPage: React.FC = () => {
  return (
    <Layout title="Medical Reports">
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Medical Reports
        </h1>
        <div className="bg-white p-6 rounded-xl shadow-md">
          <p className="text-gray-600">
            Medical Reports section is currently under development. 
            This feature will provide comprehensive medical documentation.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default ReportsPage;
