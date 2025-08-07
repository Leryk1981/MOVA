import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { DocumentTextIcon, FolderIcon, CpuChipIcon, ChartBarIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { apiService } from '@/services/api';
import LiveActivityFeed from '../components/common/LiveActivityFeed';
import { useSystemStatus, useSystemMetrics } from '../hooks/useWebSocket';

const Dashboard: React.FC = () => {
  // WebSocket real-time data
  const realTimeStatus = useSystemStatus();
  const realTimeMetrics = useSystemMetrics();

  // Отримання системного статусу
  const { data: systemStatus, isLoading: systemLoading, error: systemError } = useQuery({
    queryKey: ['system-status'],
    queryFn: () => apiService.getSystemStatus(),
    refetchInterval: 30000,
  });

  // Отримання ML моделей
  const { data: mlModelsResponse, isLoading: mlLoading } = useQuery({
    queryKey: ['ml-models'],
    queryFn: () => apiService.getMLModels(),
    refetchInterval: 60000,
  });

  // Отримання системних метрик
  const { data: metricsResponse, isLoading: metricsLoading } = useQuery({
    queryKey: ['system-metrics'],
    queryFn: () => apiService.getSystemMetrics(),
    refetchInterval: 15000,
  });

  // Use real-time data if available, fallback to API data
  const currentStatus = realTimeStatus || systemStatus;
  const currentMetrics = realTimeMetrics || metricsResponse?.data;

  const mlModels = mlModelsResponse?.data?.models || [];
  const metrics = metricsResponse?.data;

  // Обробка стану завантаження
  if (systemLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Обробка помилок
  if (systemError) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Помилка підключення</h3>
              <p className="text-sm text-red-700 mt-1">
                Не вдалося підключитися до системи. Перевірте, чи запущений backend сервер.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-600';
      case 'pending':
        return 'bg-yellow-100 text-yellow-600';
      case 'error':
        return 'bg-red-100 text-red-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <div className="h-3 w-3 rounded-full bg-green-600"></div>;
      case 'pending':
        return <div className="h-3 w-3 rounded-full bg-yellow-600"></div>;
      case 'error':
        return <div className="h-3 w-3 rounded-full bg-red-600"></div>;
      default:
        return <div className="h-3 w-3 rounded-full bg-gray-600"></div>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Ласкаво просимо до MOVA Web Interface. Моніторте вашу систему та керуйте протоколами.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* System Status Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center ${getStatusColor(systemStatus?.overall_status || 'unknown')}`}>
                {getStatusIcon(systemStatus?.overall_status || 'unknown')}
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Статус системи</h3>
              <p className="text-sm text-gray-500">
                {currentStatus?.overall_status === 'success' ? 'Всі системи працюють' : 
                 currentStatus?.overall_status === 'pending' ? 'Є попередження' : 
                 currentStatus?.overall_status === 'error' ? 'Є помилки' : 'Невідомо'}
              </p>
            </div>
          </div>
        </div>

        {/* Active Protocols Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <DocumentTextIcon className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Активні протоколи</h3>
              <p className="text-sm text-gray-500">
                {currentMetrics?.mova?.requests_total || 0} запитів
              </p>
            </div>
          </div>
        </div>

        {/* ML Models Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <CpuChipIcon className="h-4 w-4 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">ML моделі</h3>
              <p className="text-sm text-gray-500">
                {mlLoading ? 'Завантаження...' : `${mlModels?.length || 0} активних`}
              </p>
            </div>
          </div>
        </div>

        {/* Performance Card */}
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <ChartBarIcon className="h-4 w-4 text-green-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Продуктивність</h3>
              <p className="text-sm text-gray-500">
                {metricsLoading ? 'Завантаження...' : 
                 `${Math.round((currentMetrics?.mova?.average_response_time || 0) * 1000)}ms`}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* System Metrics */}
      {currentMetrics && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Системні ресурси</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm">
                  <span>CPU</span>
                  <span>{Math.round(currentMetrics.cpu || 0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${Math.min(currentMetrics.cpu || 0, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm">
                  <span>Пам'ять</span>
                  <span>{Math.round(currentMetrics.memory || 0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${Math.min(currentMetrics.memory || 0, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm">
                  <span>Диск</span>
                  <span>{Math.round(currentMetrics.disk || 0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className="bg-orange-600 h-2 rounded-full" 
                    style={{ width: `${Math.min(currentMetrics.disk || 0, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">MOVA метрики</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Всього запитів:</span>
                <span className="text-sm font-medium">{currentMetrics.mova?.requests_total || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Успішних:</span>
                <span className="text-sm font-medium text-green-600">{currentMetrics.mova?.requests_success || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Помилок:</span>
                <span className="text-sm font-medium text-red-600">{currentMetrics.mova?.requests_error || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Середній час відповіді:</span>
                <span className="text-sm font-medium">{Math.round((currentMetrics.mova?.average_response_time || 0) * 1000)}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Кеш хітів:</span>
                <span className="text-sm font-medium">{Math.round((currentMetrics.mova?.cache_hit_rate || 0) * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Швидкі дії</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <button 
            className="btn btn-primary"
            onClick={() => window.location.href = '/editor'}
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            Новий протокол
          </button>
          <button 
            className="btn btn-outline"
            onClick={() => window.location.href = '/files'}
          >
            <FolderIcon className="h-4 w-4 mr-2" />
            Завантажити файл
          </button>
          <button 
            className="btn btn-outline"
            onClick={() => window.location.href = '/ml'}
          >
            <CpuChipIcon className="h-4 w-4 mr-2" />
            Тренувати модель
          </button>
          <button 
            className="btn btn-outline"
            onClick={() => window.location.href = '/monitor'}
          >
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Переглянути метрики
          </button>
        </div>
      </div>

      {/* System Components Status */}
      {currentStatus?.components && (
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Статус компонентів</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {currentStatus.components.map((component: any, index: number) => (
              <div key={index} className="flex items-center space-x-3">
                <div className={`h-3 w-3 rounded-full ${getStatusColor(component.status)}`}></div>
                <span className="text-sm font-medium text-gray-900">{component.name}</span>
                <span className="text-xs text-gray-500">
                  {component.status === 'success' ? 'OK' : 
                   component.status === 'pending' ? '⚠️' : '❌'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live Activity Feed - Phase 4 Feature */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <LiveActivityFeed maxItems={20} className="h-96" />
        
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Real-time статус</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">WebSocket з'єднання:</span>
              <span className={`text-sm font-medium ${realTimeStatus ? 'text-green-600' : 'text-gray-500'}`}>
                {realTimeStatus ? 'Активне' : 'Неактивне'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Останнє оновлення:</span>
              <span className="text-sm text-gray-500">
                {realTimeStatus ? 'Щойно' : 'Н/Д'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Реальний час:</span>
              <span className={`text-sm font-medium ${realTimeStatus ? 'text-green-600' : 'text-yellow-600'}`}>
                {realTimeStatus ? 'Увімкнено' : 'Вимкнено'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 