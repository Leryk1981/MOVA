import React, { useState } from 'react';
import { Search, Filter, Grid, List } from 'lucide-react';

interface WidgetLibraryProps {
  onWidgetSelect: (widget: WidgetTemplate) => void;
  onClose: () => void;
}

interface WidgetTemplate {
  id: string;
  name: string;
  type: WidgetType;
  description: string;
  icon: string;
  category: WidgetCategory;
  config: WidgetConfig;
  preview: string;
}

interface WidgetConfig {
  [key: string]: any;
}

enum WidgetType {
  METRIC = 'metric',
  CHART = 'chart',
  TABLE = 'table',
  TEXT = 'text',
  IMAGE = 'image',
  CUSTOM = 'custom'
}

enum WidgetCategory {
  BASIC = 'basic',
  CHARTS = 'charts',
  DATA = 'data',
  MEDIA = 'media',
  CUSTOM = 'custom'
}

const widgetTemplates: WidgetTemplate[] = [
  // Basic Widgets
  {
    id: 'metric-single',
    name: 'Single Metric',
    type: WidgetType.METRIC,
    description: 'Display a single key metric with optional trend indicator',
    icon: '📊',
    category: WidgetCategory.BASIC,
    config: {
      title: 'Metric',
      value: 0,
      format: 'number',
      showTrend: true,
      trendValue: 0,
      trendDirection: 'up'
    },
    preview: 'metric-single'
  },
  {
    id: 'metric-comparison',
    name: 'Metric Comparison',
    type: WidgetType.METRIC,
    description: 'Compare two metrics side by side',
    icon: '⚖️',
    category: WidgetCategory.BASIC,
    config: {
      title: 'Comparison',
      primaryValue: 0,
      secondaryValue: 0,
      primaryLabel: 'Current',
      secondaryLabel: 'Previous'
    },
    preview: 'metric-comparison'
  },
  
  // Chart Widgets
  {
    id: 'line-chart',
    name: 'Line Chart',
    type: WidgetType.CHART,
    description: 'Display time series data with line chart',
    icon: '📈',
    category: WidgetCategory.CHARTS,
    config: {
      title: 'Line Chart',
      chartType: 'line',
      data: [],
      xAxis: 'time',
      yAxis: 'value'
    },
    preview: 'line-chart'
  },
  {
    id: 'bar-chart',
    name: 'Bar Chart',
    type: WidgetType.CHART,
    description: 'Display categorical data with bar chart',
    icon: '📊',
    category: WidgetCategory.CHARTS,
    config: {
      title: 'Bar Chart',
      chartType: 'bar',
      data: [],
      xAxis: 'category',
      yAxis: 'value'
    },
    preview: 'bar-chart'
  },
  {
    id: 'pie-chart',
    name: 'Pie Chart',
    type: WidgetType.CHART,
    description: 'Display proportions with pie chart',
    icon: '🥧',
    category: WidgetCategory.CHARTS,
    config: {
      title: 'Pie Chart',
      chartType: 'pie',
      data: [],
      showLegend: true
    },
    preview: 'pie-chart'
  },
  {
    id: 'heatmap',
    name: 'Heatmap',
    type: WidgetType.CHART,
    description: 'Display correlation data with heatmap',
    icon: '🔥',
    category: WidgetCategory.CHARTS,
    config: {
      title: 'Heatmap',
      chartType: 'heatmap',
      data: [],
      xAxis: 'category1',
      yAxis: 'category2'
    },
    preview: 'heatmap'
  },
  
  // Data Widgets
  {
    id: 'data-table',
    name: 'Data Table',
    type: WidgetType.TABLE,
    description: 'Display tabular data with sorting and filtering',
    icon: '📋',
    category: WidgetCategory.DATA,
    config: {
      title: 'Data Table',
      columns: [],
      data: [],
      pagination: true,
      sorting: true,
      filtering: true
    },
    preview: 'data-table'
  },
  {
    id: 'summary-table',
    name: 'Summary Table',
    type: WidgetType.TABLE,
    description: 'Display summary statistics in table format',
    icon: '📊',
    category: WidgetCategory.DATA,
    config: {
      title: 'Summary',
      data: [],
      showTotals: true,
      showAverages: true
    },
    preview: 'summary-table'
  },
  
  // Media Widgets
  {
    id: 'text-widget',
    name: 'Text Widget',
    type: WidgetType.TEXT,
    description: 'Display formatted text content',
    icon: '📝',
    category: WidgetCategory.MEDIA,
    config: {
      title: 'Text',
      content: 'Enter your text here...',
      fontSize: 'medium',
      alignment: 'left'
    },
    preview: 'text-widget'
  },
  {
    id: 'image-widget',
    name: 'Image Widget',
    type: WidgetType.IMAGE,
    description: 'Display images with optional captions',
    icon: '🖼️',
    category: WidgetCategory.MEDIA,
    config: {
      title: 'Image',
      imageUrl: '',
      caption: '',
      altText: ''
    },
    preview: 'image-widget'
  },
  
  // Custom Widgets
  {
    id: 'custom-html',
    name: 'Custom HTML',
    type: WidgetType.CUSTOM,
    description: 'Embed custom HTML content',
    icon: '🔧',
    category: WidgetCategory.CUSTOM,
    config: {
      title: 'Custom HTML',
      htmlContent: '<div>Custom content</div>',
      allowScripts: false
    },
    preview: 'custom-html'
  },
  {
    id: 'iframe-widget',
    name: 'IFrame Widget',
    type: WidgetType.CUSTOM,
    description: 'Embed external content via iframe',
    icon: '🌐',
    category: WidgetCategory.CUSTOM,
    config: {
      title: 'IFrame',
      url: '',
      height: 400,
      allowFullscreen: false
    },
    preview: 'iframe-widget'
  }
];

const WidgetLibrary: React.FC<WidgetLibraryProps> = ({
  onWidgetSelect,
  onClose
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<WidgetCategory | 'all'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const filteredWidgets = widgetTemplates.filter(widget => {
    const matchesSearch = widget.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         widget.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || widget.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = [
    { id: 'all', name: 'All Widgets', count: widgetTemplates.length },
    { id: WidgetCategory.BASIC, name: 'Basic', count: widgetTemplates.filter(w => w.category === WidgetCategory.BASIC).length },
    { id: WidgetCategory.CHARTS, name: 'Charts', count: widgetTemplates.filter(w => w.category === WidgetCategory.CHARTS).length },
    { id: WidgetCategory.DATA, name: 'Data', count: widgetTemplates.filter(w => w.category === WidgetCategory.DATA).length },
    { id: WidgetCategory.MEDIA, name: 'Media', count: widgetTemplates.filter(w => w.category === WidgetCategory.MEDIA).length },
    { id: WidgetCategory.CUSTOM, name: 'Custom', count: widgetTemplates.filter(w => w.category === WidgetCategory.CUSTOM).length }
  ];

  const renderWidgetPreview = (widget: WidgetTemplate) => {
    switch (widget.preview) {
      case 'metric-single':
        return (
          <div className="p-3 bg-blue-50 rounded">
            <div className="text-sm text-blue-600 font-medium">Metric</div>
            <div className="text-2xl font-bold text-blue-800">1,234</div>
            <div className="text-xs text-green-600">+12.5%</div>
          </div>
        );
      
      case 'line-chart':
        return (
          <div className="p-3 bg-green-50 rounded">
            <div className="text-sm text-green-600 font-medium">Line Chart</div>
            <div className="h-16 bg-green-100 rounded mt-2 flex items-center justify-center">
              <div className="text-xs text-green-700">📈</div>
            </div>
          </div>
        );
      
      case 'bar-chart':
        return (
          <div className="p-3 bg-purple-50 rounded">
            <div className="text-sm text-purple-600 font-medium">Bar Chart</div>
            <div className="h-16 bg-purple-100 rounded mt-2 flex items-center justify-center">
              <div className="text-xs text-purple-700">📊</div>
            </div>
          </div>
        );
      
      case 'data-table':
        return (
          <div className="p-3 bg-gray-50 rounded">
            <div className="text-sm text-gray-600 font-medium">Data Table</div>
            <div className="h-16 bg-gray-100 rounded mt-2 flex items-center justify-center">
              <div className="text-xs text-gray-700">📋</div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="p-3 bg-gray-50 rounded">
            <div className="text-sm text-gray-600 font-medium">{widget.name}</div>
            <div className="h-16 bg-gray-100 rounded mt-2 flex items-center justify-center">
              <div className="text-xs text-gray-700">{widget.icon}</div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-4/5 h-4/5 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-800">Widget Library</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search widgets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter size={20} className="text-gray-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value as WidgetCategory | 'all')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name} ({category.count})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <Grid size={20} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <List size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Widget Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredWidgets.map(widget => (
                <div
                  key={widget.id}
                  onClick={() => onWidgetSelect(widget)}
                  className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="text-2xl">{widget.icon}</div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{widget.name}</h3>
                      <p className="text-sm text-gray-500">{widget.type}</p>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-4">{widget.description}</p>
                  
                  {renderWidgetPreview(widget)}
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredWidgets.map(widget => (
                <div
                  key={widget.id}
                  onClick={() => onWidgetSelect(widget)}
                  className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-center space-x-4">
                    <div className="text-2xl">{widget.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800">{widget.name}</h3>
                      <p className="text-sm text-gray-500">{widget.type}</p>
                      <p className="text-sm text-gray-600 mt-1">{widget.description}</p>
                    </div>
                    <div className="w-20">
                      {renderWidgetPreview(widget)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {filteredWidgets.length} of {widgetTemplates.length} widgets
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WidgetLibrary; 