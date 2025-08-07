import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  ServerIcon, 
  DatabaseIcon,
  GlobeAltIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { apiService } from '@/services/api';
import { SystemStatus, ComponentStatus } from '@/types/api';

const Monitor: React.FC = () => {
  const [timeRange, setTimeRange] = useState('1h');
  const [selectedMetric, setSelectedMetric] = useState('cpu');

  // Отримання системного статусу
  const { data: systemStatus, isLoading: statusLoading } = useQuery<SystemStatus>({
    queryKey: ['system-status'],
    queryFn: () => apiService.getSystemStatus(),
    refetchInterval: 10000, // Оновлення кожні 10 секунд
  });

  // Отримання системних метрик
  const { data: metricsResponse, isLoading: metricsLoading } = useQuery({
    queryKey: ['system-metrics', timeRange],
    queryFn: () => apiService.getSystemMetrics(timeRange),
    refetchInterval: 5000, // Оновлення кожні 5 секунд
  });

  // Отримання системної інформації
  const { data: systemInfo, isLoading: infoLoading } = useQuery({
    queryKey: ['system-info'],
    queryFn: () => apiService.getSystemInfo(),
    refetchInterval: 60000, // Оновлення кожну хвилину
  });

  // Симуляція даних для графіків (в реальному проекті це буде з API)
  const generateChartData = (metric: string, count: number = 20) => {
    const data = [];
    const now = new Date();
    
    for (let i = count - 1; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60000); // кожна точка кожну хвилину
      let value = 0;
      
      switch (metric) {
        case 'cpu':
          value = Math.random() * 100;
          break;
        case 'memory':
          value = 60 + Math.random() * 30;
          break;
        case 'disk':
          value = 40 + Math.random() * 40;
          break;
        case 'network':
          value = Math.random() * 1000;
          break;
        default:
          value = Math.random() * 100;
      }
      
      data.push({
        time: time.toLocaleTimeString(),
        value: Math.round(value * 10) / 10,
      });
    }
    
    return data;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ServerIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}д ${hours}г ${minutes}хв`;
    if (hours > 0) return `${hours}г ${minutes}хв`;
    return `${minutes}хв`;
  };

  const chartData = generateChartData(selectedMetric);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Системний моніторинг</h1>
          <p className="mt-1 text-sm text-gray-500">
            Моніторинг системи в реальному часі
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="15m">Останні 15 хвилин</option>
            <option value="1h">Остання година</option>
            <option value="6h">Останні 6 годин</option>
            <option value="24h">Останні 24 години</option>
          </select>
        </div>
      </div>

      {/* System Status Overview */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <ServerIcon className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Загальний статус</h3>
              <p className={`text-sm font-medium ${getStatusColor(systemStatus?.overall_status || 'unknown')}`}>
                {systemStatus?.overall_status === 'success' ? 'Працює' : 
                 systemStatus?.overall_status === 'error' ? 'Помилка' : 
                 systemStatus?.overall_status === 'pending' ? 'Очікування' : 'Невідомо'}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <CpuChipIcon className="h-4 w-4 text-green-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">CPU</h3>
              <p className="text-sm text-gray-500">
                {metricsLoading ? 'Завантаження...' : 
                 `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'cpu')?.value || 0) * 100)}%`}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <DatabaseIcon className="h-4 w-4 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Пам'ять</h3>
              <p className="text-sm text-gray-500">
                {metricsLoading ? 'Завантаження...' : 
                 `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'memory')?.value || 0) * 100)}%`}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <GlobeAltIcon className="h-4 w-4 text-orange-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Мережа</h3>
              <p className="text-sm text-gray-500">
                {metricsLoading ? 'Завантаження...' : 
                 `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'network')?.value || 0) / 1024)} KB/s`}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Performance Chart */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Продуктивність</h2>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="cpu">CPU</option>
              <option value="memory">Пам'ять</option>
              <option value="disk">Диск</option>
              <option value="network">Мережа</option>
            </select>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  fillOpacity={0.3} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Information */}
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Системна інформація</h2>
          {infoLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Версія:</span>
                <span className="text-sm font-medium">{systemStatus?.version || 'Невідомо'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Час роботи:</span>
                <span className="text-sm font-medium">
                  {systemStatus?.uptime ? formatUptime(systemStatus.uptime) : 'Невідомо'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Останнє оновлення:</span>
                <span className="text-sm font-medium">
                  {systemStatus?.timestamp ? new Date(systemStatus.timestamp).toLocaleString() : 'Невідомо'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Компонентів:</span>
                <span className="text-sm font-medium">{systemStatus?.components?.length || 0}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Component Status */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Статус компонентів</h2>
        {statusLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : systemStatus?.components && systemStatus.components.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {systemStatus.components.map((component: ComponentStatus, index: number) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {getStatusIcon(component.status)}
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">{component.name}</h3>
                      <p className={`text-xs font-medium ${getStatusColor(component.status)}`}>
                        {component.status === 'success' ? 'Працює' : 
                         component.status === 'error' ? 'Помилка' : 
                         component.status === 'pending' ? 'Очікування' : 'Невідомо'}
                      </p>
                    </div>
                  </div>
                  {component.version && (
                    <span className="text-xs text-gray-500">v{component.version}</span>
                  )}
                </div>
                {component.details && Object.keys(component.details).length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="text-xs text-gray-500">
                      {Object.entries(component.details).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span>{key}:</span>
                          <span className="font-medium">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <ServerIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Немає доступних компонентів</p>
          </div>
        )}
      </div>

      {/* Real-time Metrics */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Метрики в реальному часі</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {metricsLoading ? '...' : 
               `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'cpu')?.value || 0) * 100)}%`}
            </div>
            <div className="text-sm text-gray-500">CPU Використання</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {metricsLoading ? '...' : 
               `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'memory')?.value || 0) * 100)}%`}
            </div>
            <div className="text-sm text-gray-500">Пам'ять</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {metricsLoading ? '...' : 
               `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'disk')?.value || 0) * 100)}%`}
            </div>
            <div className="text-sm text-gray-500">Диск</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {metricsLoading ? '...' : 
               `${Math.round((metricsResponse?.data?.metrics?.find(m => m.category === 'network')?.value || 0) / 1024)}`}
            </div>
            <div className="text-sm text-gray-500">Мережа (KB/s)</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Monitor; 