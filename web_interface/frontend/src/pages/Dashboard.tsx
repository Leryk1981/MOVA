import React from 'react';
import { DocumentTextIcon, FolderIcon, CpuChipIcon, ChartBarIcon } from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to MOVA Web Interface. Monitor your system and manage protocols.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* System Status Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <div className="h-3 w-3 rounded-full bg-green-600"></div>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">System Status</h3>
              <p className="text-sm text-gray-500">All systems operational</p>
            </div>
          </div>
        </div>

        {/* Active Protocols Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <div className="h-4 w-4 text-blue-600">📋</div>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Active Protocols</h3>
              <p className="text-sm text-gray-500">0 running</p>
            </div>
          </div>
        </div>

        {/* ML Models Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <div className="h-4 w-4 text-purple-600">🤖</div>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">ML Models</h3>
              <p className="text-sm text-gray-500">0 active</p>
            </div>
          </div>
        </div>

        {/* Files Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <div className="h-4 w-4 text-orange-600">📁</div>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Files</h3>
              <p className="text-sm text-gray-500">0 uploaded</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <button className="btn btn-primary">
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            New Protocol
          </button>
          <button className="btn btn-outline">
            <FolderIcon className="h-4 w-4 mr-2" />
            Upload File
          </button>
          <button className="btn btn-outline">
            <CpuChipIcon className="h-4 w-4 mr-2" />
            Train Model
          </button>
          <button className="btn btn-outline">
            <ChartBarIcon className="h-4 w-4 mr-2" />
            View Metrics
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No recent activity</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 