import React, { useState, useEffect } from 'react';
import { RefreshCw, Download, Share, Settings, Eye, EyeOff } from 'lucide-react';

interface DashboardViewerProps {
  dashboard: Dashboard;
  isEditable?: boolean;
  onEdit?: () => void;
  onRefresh?: () => void;
}

interface Dashboard {
  id: string;
  name: string;
  description: string;
  layout: DashboardLayout;
  widgets: Widget[];
  template?: string;
  isPublic: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface DashboardLayout {
  grid: GridConfig;
  widgets: WidgetPosition[];
  theme: DashboardTheme;
}

interface GridConfig {
  columns: number;
  rows: number;
  cellWidth: number;
  cellHeight: number;
}

interface WidgetPosition {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
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

interface DashboardTheme {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
}

enum WidgetType {
  METRIC = 'metric',
  CHART = 'chart',
  TABLE = 'table',
  TEXT = 'text',
  IMAGE = 'image',
  CUSTOM = 'custom'
}

const DashboardViewer: React.FC<DashboardViewerProps> = ({
  dashboard,
  isEditable = false,
  onEdit,
  onRefresh
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showGrid, setShowGrid] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (autoRefresh && onRefresh) {
      interval = setInterval(() => {
        onRefresh();
      }, refreshInterval * 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [autoRefresh, refreshInterval, onRefresh]);

  const handleRefresh = async () => {
    if (onRefresh) {
      setIsLoading(true);
      try {
        await onRefresh();
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleExport = () => {
    // Export dashboard as image or PDF
    const dashboardElement = document.getElementById('dashboard-container');
    if (dashboardElement) {
      // Implementation for export functionality
      console.log('Exporting dashboard...');
    }
  };

  const handleShare = () => {
    // Share dashboard functionality
    if (navigator.share) {
      navigator.share({
        title: dashboard.name,
        text: dashboard.description,
        url: window.location.href
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  const renderMetricWidget = (widget: Widget) => {
    const { config, data } = widget;
    const value = data.value || config.value || '0';
    const format = config.format || 'number';
    const showTrend = config.showTrend || false;
    const trendValue = data.trendValue || config.trendValue || 0;

    const formatValue = (val: any) => {
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
          }).format(parseFloat(val));
        case 'percentage':
          return `${parseFloat(val).toFixed(1)}%`;
        default:
          return new Intl.NumberFormat('en-US').format(parseFloat(val));
      }
    };

    return (
      <div className="p-4 bg-white rounded-lg shadow border">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">{widget.title}</h3>
        <div className="flex items-end space-x-2">
          <div className="text-3xl font-bold text-blue-600">
            {formatValue(value)}
          </div>
          {showTrend && (
            <div className={`text-sm font-medium ${
              trendValue > 0 ? 'text-green-600' : trendValue < 0 ? 'text-red-600' : 'text-gray-500'
            }`}>
              {trendValue > 0 ? '+' : ''}{trendValue}%
            </div>
          )}
        </div>
        {config.description && (
          <div className="text-sm text-gray-500 mt-2">{config.description}</div>
        )}
      </div>
    );
  };

  const renderChartWidget = (widget: Widget) => {
    const { config, data } = widget;
    const chartType = config.chartType || 'line';
    const chartData = data.chartData || config.chartData || [];

    return (
      <div className="p-4 bg-white rounded-lg shadow border">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{widget.title}</h3>
        <div className="h-48 bg-gray-50 rounded flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-2">
              {chartType === 'line' && '📈'}
              {chartType === 'bar' && '📊'}
              {chartType === 'pie' && '🥧'}
              {chartType === 'doughnut' && '🍩'}
              {chartType === 'scatter' && '🔵'}
              {chartType === 'heatmap' && '🔥'}
            </div>
            <div className="text-sm text-gray-500">{chartType.toUpperCase()} Chart</div>
            <div className="text-xs text-gray-400 mt-1">
              {chartData.length} data points
            </div>
          </div>
        </div>
        {config.description && (
          <div className="text-sm text-gray-500 mt-2">{config.description}</div>
        )}
      </div>
    );
  };

  const renderTableWidget = (widget: Widget) => {
    const { config, data } = widget;
    const tableData = data.tableData || config.tableData || [];
    const columns = data.columns || config.columns || [];
    const showPagination = config.pagination || false;
    const pageSize = config.pageSize || 10;

    return (
      <div className="p-4 bg-white rounded-lg shadow border">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{widget.title}</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((column: any, index: number) => (
                  <th
                    key={index}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {column.label || column.key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tableData.slice(0, pageSize).map((row: any, rowIndex: number) => (
                <tr key={rowIndex}>
                  {columns.map((column: any, colIndex: number) => (
                    <td
                      key={colIndex}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {row[column.key] || ''}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {showPagination && tableData.length > pageSize && (
          <div className="mt-4 text-sm text-gray-500">
            Showing 1-{pageSize} of {tableData.length} results
          </div>
        )}
        {config.description && (
          <div className="text-sm text-gray-500 mt-2">{config.description}</div>
        )}
      </div>
    );
  };

  const renderTextWidget = (widget: Widget) => {
    const { config, data } = widget;
    const content = data.content || config.content || '';
    const fontSize = config.fontSize || 'medium';
    const alignment = config.alignment || 'left';

    const fontSizeClasses = {
      small: 'text-sm',
      medium: 'text-base',
      large: 'text-lg'
    };

    const alignmentClasses = {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
      justify: 'text-justify'
    };

    return (
      <div className="p-4 bg-white rounded-lg shadow border">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">{widget.title}</h3>
        <div
          className={`${fontSizeClasses[fontSize as keyof typeof fontSizeClasses]} ${alignmentClasses[alignment as keyof typeof alignmentClasses]} text-gray-700`}
          dangerouslySetInnerHTML={{ __html: content }}
        />
        {config.description && (
          <div className="text-sm text-gray-500 mt-2">{config.description}</div>
        )}
      </div>
    );
  };

  const renderImageWidget = (widget: Widget) => {
    const { config, data } = widget;
    const imageUrl = data.imageUrl || config.imageUrl || '';
    const altText = data.altText || config.altText || '';
    const caption = data.caption || config.caption || '';
    const fitMode = config.fitMode || 'contain';

    const fitModeClasses = {
      contain: 'object-contain',
      cover: 'object-cover',
      fill: 'object-fill'
    };

    return (
      <div className="p-4 bg-white rounded-lg shadow border">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">{widget.title}</h3>
        <div className="relative">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={altText}
              className={`w-full h-48 ${fitModeClasses[fitMode as keyof typeof fitModeClasses]} rounded`}
            />
          ) : (
            <div className="w-full h-48 bg-gray-100 rounded flex items-center justify-center">
              <div className="text-gray-400">No image</div>
            </div>
          )}
          {caption && (
            <div className="text-sm text-gray-500 mt-2 text-center">{caption}</div>
          )}
        </div>
        {config.description && (
          <div className="text-sm text-gray-500 mt-2">{config.description}</div>
        )}
      </div>
    );
  };

  const renderCustomWidget = (widget: Widget) => {
    const { config, data } = widget;
    const customCode = data.customCode || config.customCode || '';
    const allowScripts = config.allowScripts || false;

    return (
      <div className="p-4 bg-white rounded-lg shadow border">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">{widget.title}</h3>
        <div
          className="custom-widget-content"
          dangerouslySetInnerHTML={{ __html: customCode }}
        />
        {config.description && (
          <div className="text-sm text-gray-500 mt-2">{config.description}</div>
        )}
      </div>
    );
  };

  const renderWidget = (widget: Widget) => {
    switch (widget.type) {
      case WidgetType.METRIC:
        return renderMetricWidget(widget);
      case WidgetType.CHART:
        return renderChartWidget(widget);
      case WidgetType.TABLE:
        return renderTableWidget(widget);
      case WidgetType.TEXT:
        return renderTextWidget(widget);
      case WidgetType.IMAGE:
        return renderImageWidget(widget);
      case WidgetType.CUSTOM:
        return renderCustomWidget(widget);
      default:
        return (
          <div className="p-4 bg-white rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-800">{widget.title}</h3>
            <div className="text-gray-500">Unknown widget type: {widget.type}</div>
          </div>
        );
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">{dashboard.name}</h1>
            {dashboard.description && (
              <p className="text-gray-600 mt-1">{dashboard.description}</p>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Grid Toggle */}
            <button
              onClick={() => setShowGrid(!showGrid)}
              className={`p-2 rounded ${
                showGrid ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:text-gray-700'
              }`}
              title="Toggle Grid"
            >
              {showGrid ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>

            {/* Auto Refresh */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="autoRefresh" className="text-sm text-gray-700">
                Auto
              </label>
            </div>

            {/* Refresh Interval */}
            {autoRefresh && (
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value={15}>15s</option>
                <option value={30}>30s</option>
                <option value={60}>1m</option>
                <option value={300}>5m</option>
              </select>
            )}

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
              title="Refresh Dashboard"
            >
              <RefreshCw size={20} className={isLoading ? 'animate-spin' : ''} />
            </button>

            {/* Export Button */}
            <button
              onClick={handleExport}
              className="p-2 text-gray-500 hover:text-gray-700"
              title="Export Dashboard"
            >
              <Download size={20} />
            </button>

            {/* Share Button */}
            <button
              onClick={handleShare}
              className="p-2 text-gray-500 hover:text-gray-700"
              title="Share Dashboard"
            >
              <Share size={20} />
            </button>

            {/* Edit Button */}
            {isEditable && onEdit && (
              <button
                onClick={onEdit}
                className="p-2 text-gray-500 hover:text-gray-700"
                title="Edit Dashboard"
              >
                <Settings size={20} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="flex-1 overflow-auto p-4">
        <div
          id="dashboard-container"
          className="relative bg-white rounded-lg border border-gray-200 min-h-full"
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${dashboard.layout.grid.columns}, 1fr)`,
            gridTemplateRows: `repeat(${dashboard.layout.grid.rows}, 1fr)`,
            gap: '8px',
            padding: '16px',
            backgroundColor: dashboard.layout.theme.backgroundColor,
            color: dashboard.layout.theme.textColor
          }}
        >
          {showGrid && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage: `
                  linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)
                `,
                backgroundSize: `${dashboard.layout.grid.cellWidth}px ${dashboard.layout.grid.cellHeight}px`
              }}
            />
          )}
          
          {dashboard.widgets.map((widget) => (
            <div
              key={widget.id}
              className="relative"
              style={{
                gridColumn: `span ${widget.position.width}`,
                gridRow: `span ${widget.position.height}`
              }}
            >
              {renderWidget(widget)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardViewer; 