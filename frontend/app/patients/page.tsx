'use client';

import React from 'react';
import Layout from '@/components/Layout';

const PatientsPage: React.FC = () => {
  return (
    <Layout title="Patient Management">
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Patient Management
        </h1>
        <div className="bg-white p-6 rounded-xl shadow-md">
          <p className="text-gray-600">
            Patient Management system is currently under development. 
            This feature will provide comprehensive patient tracking and management.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default PatientsPage;
