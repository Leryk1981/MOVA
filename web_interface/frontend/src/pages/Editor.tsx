import React from 'react';

const Editor: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">File Editor</h1>
        <p className="mt-1 text-sm text-gray-500">
          Edit MOVA protocol files with syntax highlighting and validation.
        </p>
      </div>

      <div className="card p-6">
        <div className="text-center py-12">
          <p className="text-gray-500">Monaco Editor will be integrated here</p>
        </div>
      </div>
    </div>
  );
};

export default Editor; 