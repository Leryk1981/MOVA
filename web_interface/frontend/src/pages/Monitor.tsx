import React from 'react';

const Monitor: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">System Monitor</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor system performance, metrics, and real-time data.
        </p>
      </div>

      <div className="card p-6">
        <div className="text-center py-12">
          <p className="text-gray-500">System monitoring charts will be displayed here</p>
        </div>
      </div>
    </div>
  );
};

export default Monitor; 