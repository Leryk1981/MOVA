import React, { useState, useEffect } from 'react';
import { checkApiHealth } from '../services/api';
import { dashboardApi } from '../services/dashboardApi';
import { pluginApi } from '../services/pluginApi';

const IntegrationTest: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      const isHealthy = await checkApiHealth();
      setApiStatus(isHealthy ? 'connected' : 'error');
    } catch (error) {
      setApiStatus('error');
      console.error('API connection failed:', error);
    }
  };

  const runIntegrationTests = async () => {
    setLoading(true);
    const results: Record<string, any> = {};

    try {
      // Test 1: Dashboard API
      console.log('Testing Dashboard API...');
      try {
        const dashboards = await dashboardApi.getDashboards(1, 5);
        results.dashboard = { status: 'success', data: dashboards };
        console.log('Dashboard API test passed:', dashboards);
      } catch (error) {
        results.dashboard = { status: 'error', error: error instanceof Error ? error.message : 'Unknown error' };
        console.error('Dashboard API test failed:', error);
      }

      // Test 2: Plugin API
      console.log('Testing Plugin API...');
      try {
        const plugins = await pluginApi.getPlugins(1, 5);
        results.plugin = { status: 'success', data: plugins };
        console.log('Plugin API test passed:', plugins);
      } catch (error) {
        results.plugin = { status: 'error', error: error instanceof Error ? error.message : 'Unknown error' };
        console.error('Plugin API test failed:', error);
      }

      // Test 3: Marketplace API
      console.log('Testing Marketplace API...');
      try {
        const marketplace = await pluginApi.getMarketplace(1, 5);
        results.marketplace = { status: 'success', data: marketplace };
        console.log('Marketplace API test passed:', marketplace);
      } catch (error) {
        results.marketplace = { status: 'error', error: error instanceof Error ? error.message : 'Unknown error' };
        console.error('Marketplace API test failed:', error);
      }

    } catch (error) {
      console.error('Integration tests failed:', error);
    }

    setTestResults(results);
    setLoading(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">API Integration Test</h2>
      
      {/* API Status */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">API Connection Status</h3>
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
          apiStatus === 'connected' ? 'bg-green-100 text-green-800' :
          apiStatus === 'error' ? 'bg-red-100 text-red-800' :
          'bg-yellow-100 text-yellow-800'
        }`}>
          {apiStatus === 'connected' ? '✅ Connected' :
           apiStatus === 'error' ? '❌ Connection Failed' :
           '⏳ Checking...'}
        </div>
      </div>

      {/* Test Button */}
      <div className="mb-6">
        <button
          onClick={runIntegrationTests}
          disabled={loading || apiStatus !== 'connected'}
          className={`px-4 py-2 rounded-md font-medium ${
            loading || apiStatus !== 'connected'
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {loading ? 'Running Tests...' : 'Run Integration Tests'}
        </button>
      </div>

      {/* Test Results */}
      {Object.keys(testResults).length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Test Results</h3>
          
          {Object.entries(testResults).map(([testName, result]) => (
            <div key={testName} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium capitalize">{testName} API</h4>
                <span className={`font-medium ${getStatusColor(result.status)}`}>
                  {getStatusIcon(result.status)} {result.status}
                </span>
              </div>
              
              {result.status === 'success' && (
                <div className="text-sm text-gray-600">
                  <p>✅ API endpoint accessible</p>
                  {result.data && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-blue-600">View Response Data</summary>
                      <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              )}
              
              {result.status === 'error' && (
                <div className="text-sm text-red-600">
                  <p>❌ {result.error}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">Instructions</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Make sure the backend server is running on http://localhost:8000</li>
          <li>• Click "Run Integration Tests" to test API connectivity</li>
          <li>• Green checkmarks indicate successful API calls</li>
          <li>• Red X marks indicate API errors (check backend logs)</li>
        </ul>
      </div>
    </div>
  );
};

export default IntegrationTest; 