import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  ChartBarIcon, 
  PlayIcon, 
  StopIcon,
  PlusIcon,
  TrashIcon,
  EyeIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { apiService } from '@/services/api';
import { MLModel, MLStatus, Recommendation } from '@/types/api';

const ML: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [analysisText, setAnalysisText] = useState('');
  const [analysisType, setAnalysisType] = useState<'intent' | 'entities' | 'sentiment'>('intent');
  const [trainingConfig, setTrainingConfig] = useState({
    epochs: 10,
    batchSize: 32,
    learningRate: 0.001,
  });

  const queryClient = useQueryClient();

  // Отримання ML статусу
  const { data: mlStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['ml-status'],
    queryFn: () => apiService.getMLStatus(),
    refetchInterval: 30000,
  });

  // Отримання ML моделей
  const { data: modelsResponse, isLoading: modelsLoading } = useQuery({
    queryKey: ['ml-models'],
    queryFn: () => apiService.getMLModels(),
    refetchInterval: 60000,
  });

  // Отримання ML метрик
  const { data: metricsResponse, isLoading: metricsLoading } = useQuery({
    queryKey: ['ml-metrics'],
    queryFn: () => apiService.getMLMetrics(),
    refetchInterval: 15000,
  });

  // Отримання рекомендацій
  const { data: recommendationsResponse, isLoading: recommendationsLoading } = useQuery({
    queryKey: ['ml-recommendations'],
    queryFn: () => apiService.getRecommendationsSummary(),
    refetchInterval: 30000,
  });

  // Мутація для тренування моделі
  const trainModelMutation = useMutation({
    mutationFn: ({ modelId, config }: { modelId: string; config: any }) =>
      apiService.trainMLModel(modelId, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ml-models'] });
      queryClient.invalidateQueries({ queryKey: ['ml-status'] });
    },
  });

  // Мутація для оцінки моделі
  const evaluateModelMutation = useMutation({
    mutationFn: ({ modelId, testData }: { modelId: string; testData: any }) =>
      apiService.evaluateMLModel(modelId, testData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ml-metrics'] });
    },
  });

  // Мутація для аналізу тексту
  const analyzeTextMutation = useMutation({
    mutationFn: ({ text, type }: { text: string; type: string }) => {
      switch (type) {
        case 'intent':
          return apiService.analyzeIntent(text);
        case 'entities':
          return apiService.extractEntities(text);
        case 'sentiment':
          return apiService.analyzeSentiment(text);
        default:
          return apiService.analyzeIntent(text);
      }
    },
  });

  const models = modelsResponse?.data?.models || [];
  const metrics = metricsResponse?.data;
  const recommendations = recommendationsResponse?.data;

  const handleTrainModel = (modelId: string) => {
    trainModelMutation.mutate({ modelId, config: trainingConfig });
  };

  const handleEvaluateModel = (modelId: string) => {
    const testData = {
      samples: [
        { text: "Зареєструй мене як користувача", expected: "registration" },
        { text: "Покажи погоду", expected: "weather" },
        { text: "Допоможи з налаштуваннями", expected: "help" },
      ]
    };
    evaluateModelMutation.mutate({ modelId, testData });
  };

  const handleAnalyzeText = () => {
    if (analysisText.trim()) {
      analyzeTextMutation.mutate({ text: analysisText, type: analysisType });
    }
  };

  const getModelStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800';
      case 'training':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Machine Learning</h1>
          <p className="mt-1 text-sm text-gray-500">
            Управління ML моделями, тренування та аналіз тексту
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button className="btn btn-primary">
            <PlusIcon className="h-4 w-4 mr-2" />
            Нова модель
          </button>
        </div>
      </div>

      {/* ML Status Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <CpuChipIcon className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">ML Статус</h3>
              <p className="text-sm text-gray-500">
                {statusLoading ? 'Завантаження...' : 
                 mlStatus?.data?.enabled ? 'Активний' : 'Неактивний'}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <ChartBarIcon className="h-4 w-4 text-green-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Моделі</h3>
              <p className="text-sm text-gray-500">
                {modelsLoading ? 'Завантаження...' : `${models.length} активних`}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <DocumentTextIcon className="h-4 w-4 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Точність</h3>
              <p className="text-sm text-gray-500">
                {metricsLoading ? 'Завантаження...' : 
                 `${Math.round((metrics?.accuracy || 0) * 100)}%`}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <EyeIcon className="h-4 w-4 text-orange-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Рекомендації</h3>
              <p className="text-sm text-gray-500">
                {recommendationsLoading ? 'Завантаження...' : 
                 `${recommendations?.total || 0} доступних`}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* ML Models */}
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">ML Моделі</h2>
          {modelsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : models.length === 0 ? (
            <div className="text-center py-8">
              <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Немає доступних моделей</p>
            </div>
          ) : (
            <div className="space-y-3">
              {models.map((model: MLModel) => (
                <div key={model.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{model.name}</h3>
                      <p className="text-sm text-gray-500">
                        Тип: {model.type} | Версія: {model.version}
                      </p>
                      <p className="text-sm text-gray-500">
                        Точність: {Math.round((model.accuracy || 0) * 100)}%
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModelStatusColor(model.active ? 'ready' : 'error')}`}>
                        {model.active ? 'Активна' : 'Неактивна'}
                      </span>
                      <button
                        onClick={() => handleTrainModel(model.id)}
                        className="btn btn-outline btn-sm"
                        disabled={trainModelMutation.isPending}
                      >
                        <PlayIcon className="h-3 w-3 mr-1" />
                        Тренувати
                      </button>
                      <button
                        onClick={() => handleEvaluateModel(model.id)}
                        className="btn btn-outline btn-sm"
                        disabled={evaluateModelMutation.isPending}
                      >
                        <ChartBarIcon className="h-3 w-3 mr-1" />
                        Оцінити
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Text Analysis */}
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Аналіз тексту</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Тип аналізу
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="intent">Розпізнавання намірів</option>
                <option value="entities">Витяг сущностей</option>
                <option value="sentiment">Аналіз настрою</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Текст для аналізу
              </label>
              <textarea
                value={analysisText}
                onChange={(e) => setAnalysisText(e.target.value)}
                placeholder="Введіть текст для аналізу..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <button
              onClick={handleAnalyzeText}
              className="btn btn-primary w-full"
              disabled={!analysisText.trim() || analyzeTextMutation.isPending}
            >
              {analyzeTextMutation.isPending ? 'Аналіз...' : 'Аналізувати'}
            </button>
            
            {analyzeTextMutation.data && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Результат аналізу:</h4>
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(analyzeTextMutation.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Training Configuration */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Налаштування тренування</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Епохи
            </label>
            <input
              type="number"
              value={trainingConfig.epochs}
              onChange={(e) => setTrainingConfig(prev => ({ ...prev, epochs: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="1"
              max="100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Розмір батчу
            </label>
            <input
              type="number"
              value={trainingConfig.batchSize}
              onChange={(e) => setTrainingConfig(prev => ({ ...prev, batchSize: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="1"
              max="128"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Швидкість навчання
            </label>
            <input
              type="number"
              step="0.001"
              value={trainingConfig.learningRate}
              onChange={(e) => setTrainingConfig(prev => ({ ...prev, learningRate: parseFloat(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="0.0001"
              max="1"
            />
          </div>
        </div>
      </div>

      {/* ML Metrics */}
      {metrics && (
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">ML Метрики</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round((metrics.accuracy || 0) * 100)}%
              </div>
              <div className="text-sm text-gray-500">Точність</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {metrics.precision || 0}
              </div>
              <div className="text-sm text-gray-500">Точність (Precision)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {metrics.recall || 0}
              </div>
              <div className="text-sm text-gray-500">Повнота (Recall)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {metrics.f1_score || 0}
              </div>
              <div className="text-sm text-gray-500">F1-міра</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ML; 