import React, { useState, useEffect } from 'react';
import { Settings, Palette, BarChart3, Type, Image, Code } from 'lucide-react';

interface WidgetConfigPanelProps {
  widget: Widget | null;
  onConfigChange: (config: WidgetConfig) => void;
  onClose: () => void;
}

interface Widget {
  id: string;
  type: WidgetType;
  title: string;
  config: WidgetConfig;
  data: WidgetData;
  position: WidgetPosition;
}

interface WidgetConfig {
  [key: string]: any;
}

interface WidgetData {
  [key: string]: any;
}

interface WidgetPosition {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

enum WidgetType {
  METRIC = 'metric',
  CHART = 'chart',
  TABLE = 'table',
  TEXT = 'text',
  IMAGE = 'image',
  CUSTOM = 'custom'
}

const WidgetConfigPanel: React.FC<WidgetConfigPanelProps> = ({
  widget,
  onConfigChange,
  onClose
}) => {
  const [config, setConfig] = useState<WidgetConfig>({});
  const [activeTab, setActiveTab] = useState('general');

  useEffect(() => {
    if (widget) {
      setConfig(widget.config);
    }
  }, [widget]);

  const handleConfigChange = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  const renderGeneralTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Widget Title
        </label>
        <input
          type="text"
          value={config.title || ''}
          onChange={(e) => handleConfigChange('title', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          value={config.description || ''}
          onChange={(e) => handleConfigChange('description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Width
          </label>
          <input
            type="number"
            min="1"
            max="12"
            value={config.width || 3}
            onChange={(e) => handleConfigChange('width', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Height
          </label>
          <input
            type="number"
            min="1"
            max="8"
            value={config.height || 2}
            onChange={(e) => handleConfigChange('height', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderMetricTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Value
        </label>
        <input
          type="text"
          value={config.value || ''}
          onChange={(e) => handleConfigChange('value', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Format
        </label>
        <select
          value={config.format || 'number'}
          onChange={(e) => handleConfigChange('format', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="number">Number</option>
          <option value="currency">Currency</option>
          <option value="percentage">Percentage</option>
          <option value="text">Text</option>
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="showTrend"
          checked={config.showTrend || false}
          onChange={(e) => handleConfigChange('showTrend', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="showTrend" className="text-sm font-medium text-gray-700">
          Show Trend Indicator
        </label>
      </div>

      {config.showTrend && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Trend Value
          </label>
          <input
            type="number"
            value={config.trendValue || 0}
            onChange={(e) => handleConfigChange('trendValue', parseFloat(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}
    </div>
  );

  const renderChartTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Chart Type
        </label>
        <select
          value={config.chartType || 'line'}
          onChange={(e) => handleConfigChange('chartType', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="line">Line Chart</option>
          <option value="bar">Bar Chart</option>
          <option value="pie">Pie Chart</option>
          <option value="doughnut">Doughnut Chart</option>
          <option value="scatter">Scatter Plot</option>
          <option value="heatmap">Heatmap</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Data Source
        </label>
        <select
          value={config.dataSource || 'static'}
          onChange={(e) => handleConfigChange('dataSource', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="static">Static Data</option>
          <option value="api">API Endpoint</option>
          <option value="query">Database Query</option>
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="showLegend"
          checked={config.showLegend || false}
          onChange={(e) => handleConfigChange('showLegend', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="showLegend" className="text-sm font-medium text-gray-700">
          Show Legend
        </label>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="showGrid"
          checked={config.showGrid || false}
          onChange={(e) => handleConfigChange('showGrid', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="showGrid" className="text-sm font-medium text-gray-700">
          Show Grid
        </label>
      </div>
    </div>
  );

  const renderTableTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Data Source
        </label>
        <select
          value={config.dataSource || 'static'}
          onChange={(e) => handleConfigChange('dataSource', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="static">Static Data</option>
          <option value="api">API Endpoint</option>
          <option value="query">Database Query</option>
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="pagination"
          checked={config.pagination || false}
          onChange={(e) => handleConfigChange('pagination', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="pagination" className="text-sm font-medium text-gray-700">
          Enable Pagination
        </label>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="sorting"
          checked={config.sorting || false}
          onChange={(e) => handleConfigChange('sorting', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="sorting" className="text-sm font-medium text-gray-700">
          Enable Sorting
        </label>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="filtering"
          checked={config.filtering || false}
          onChange={(e) => handleConfigChange('filtering', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="filtering" className="text-sm font-medium text-gray-700">
          Enable Filtering
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Page Size
        </label>
        <input
          type="number"
          min="5"
          max="100"
          value={config.pageSize || 10}
          onChange={(e) => handleConfigChange('pageSize', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );

  const renderTextTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Content
        </label>
        <textarea
          value={config.content || ''}
          onChange={(e) => handleConfigChange('content', e.target.value)}
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Font Size
        </label>
        <select
          value={config.fontSize || 'medium'}
          onChange={(e) => handleConfigChange('fontSize', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Text Alignment
        </label>
        <select
          value={config.alignment || 'left'}
          onChange={(e) => handleConfigChange('alignment', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="left">Left</option>
          <option value="center">Center</option>
          <option value="right">Right</option>
          <option value="justify">Justify</option>
        </select>
      </div>
    </div>
  );

  const renderImageTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Image URL
        </label>
        <input
          type="url"
          value={config.imageUrl || ''}
          onChange={(e) => handleConfigChange('imageUrl', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Alt Text
        </label>
        <input
          type="text"
          value={config.altText || ''}
          onChange={(e) => handleConfigChange('altText', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Caption
        </label>
        <input
          type="text"
          value={config.caption || ''}
          onChange={(e) => handleConfigChange('caption', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Fit Mode
        </label>
        <select
          value={config.fitMode || 'contain'}
          onChange={(e) => handleConfigChange('fitMode', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="contain">Contain</option>
          <option value="cover">Cover</option>
          <option value="fill">Fill</option>
        </select>
      </div>
    </div>
  );

  const renderCustomTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Custom Code
        </label>
        <textarea
          value={config.customCode || ''}
          onChange={(e) => handleConfigChange('customCode', e.target.value)}
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          placeholder="Enter your custom HTML/JavaScript code..."
        />
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="allowScripts"
          checked={config.allowScripts || false}
          onChange={(e) => handleConfigChange('allowScripts', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="allowScripts" className="text-sm font-medium text-gray-700">
          Allow Scripts (use with caution)
        </label>
      </div>
    </div>
  );

  const renderStyleTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Background Color
        </label>
        <input
          type="color"
          value={config.backgroundColor || '#ffffff'}
          onChange={(e) => handleConfigChange('backgroundColor', e.target.value)}
          className="w-full h-10 border border-gray-300 rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Border Color
        </label>
        <input
          type="color"
          value={config.borderColor || '#e5e7eb'}
          onChange={(e) => handleConfigChange('borderColor', e.target.value)}
          className="w-full h-10 border border-gray-300 rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Border Width
        </label>
        <input
          type="number"
          min="0"
          max="10"
          value={config.borderWidth || 1}
          onChange={(e) => handleConfigChange('borderWidth', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Border Radius
        </label>
        <input
          type="number"
          min="0"
          max="20"
          value={config.borderRadius || 8}
          onChange={(e) => handleConfigChange('borderRadius', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Padding
        </label>
        <input
          type="number"
          min="0"
          max="50"
          value={config.padding || 16}
          onChange={(e) => handleConfigChange('padding', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );

  const getTabs = () => {
    const baseTabs = [
      { id: 'general', name: 'General', icon: Settings },
      { id: 'style', name: 'Style', icon: Palette }
    ];

    if (widget) {
      switch (widget.type) {
        case WidgetType.METRIC:
          return [...baseTabs, { id: 'metric', name: 'Metric', icon: BarChart3 }];
        case WidgetType.CHART:
          return [...baseTabs, { id: 'chart', name: 'Chart', icon: BarChart3 }];
        case WidgetType.TABLE:
          return [...baseTabs, { id: 'table', name: 'Table', icon: BarChart3 }];
        case WidgetType.TEXT:
          return [...baseTabs, { id: 'text', name: 'Text', icon: Type }];
        case WidgetType.IMAGE:
          return [...baseTabs, { id: 'image', name: 'Image', icon: Image }];
        case WidgetType.CUSTOM:
          return [...baseTabs, { id: 'custom', name: 'Custom', icon: Code }];
        default:
          return baseTabs;
      }
    }

    return baseTabs;
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralTab();
      case 'metric':
        return renderMetricTab();
      case 'chart':
        return renderChartTab();
      case 'table':
        return renderTableTab();
      case 'text':
        return renderTextTab();
      case 'image':
        return renderImageTab();
      case 'custom':
        return renderCustomTab();
      case 'style':
        return renderStyleTab();
      default:
        return renderGeneralTab();
    }
  };

  if (!widget) {
    return null;
  }

  const tabs = getTabs();

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white border-l border-gray-200 shadow-lg z-40">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800">Widget Settings</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-1">{widget.title}</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <tab.icon size={16} />
                <span>{tab.name}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default WidgetConfigPanel; 