'use client';

import React from 'react';
import Layout from '@/components/Layout';
import { 
  UserGroupIcon, 
  HeartIcon, 
  DocumentChartBarIcon, 
  ClipboardDocumentListIcon 
} from '@heroicons/react/24/solid';

const DashboardCard: React.FC<{
  title: string, 
  value: string, 
  icon: React.ReactNode, 
  color: string
}> = ({ title, value, icon, color }) => (
  <div className={`bg-white p-6 rounded-xl shadow-md flex items-center space-x-4 ${color}`}>
    <div className={`p-3 rounded-full ${color} bg-opacity-20`}>
      {icon}
    </div>
    <div>
      <p className="text-gray-500 text-sm">{title}</p>
      <h3 className="text-2xl font-bold">{value}</h3>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const hospitalStats = [
    {
      title: 'Total Patients',
      value: '4,250',
      icon: <UserGroupIcon className="w-8 h-8 text-blue-600" />,
      color: 'text-blue-600'
    },
    {
      title: 'Active Treatments',
      value: '1,350',
      icon: <HeartIcon className="w-8 h-8 text-red-600" />,
      color: 'text-red-600'
    },
    {
      title: 'Medical Reports',
      value: '12,500',
      icon: <DocumentChartBarIcon className="w-8 h-8 text-green-600" />,
      color: 'text-green-600'
    },
    {
      title: 'Pending Consultations',
      value: '287',
      icon: <ClipboardDocumentListIcon className="w-8 h-8 text-purple-600" />,
      color: 'text-purple-600'
    }
  ];

  return (
    <Layout>
      <div className="space-y-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Hospital Dashboard
        </h1>

        <div className="grid grid-cols-4 gap-6">
          {hospitalStats.map((stat, index) => (
            <DashboardCard 
              key={index}
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              color={stat.color}
            />
          ))}
        </div>

        <div className="grid grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-xl font-semibold mb-4">Patient Admissions</h2>
            {/* Add chart or graph component */}
            <div className="h-64 bg-gray-100 flex items-center justify-center">
              Patient Admission Chart Placeholder
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-xl font-semibold mb-4">Department Performance</h2>
            {/* Add chart or graph component */}
            <div className="h-64 bg-gray-100 flex items-center justify-center">
              Department Performance Chart Placeholder
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
